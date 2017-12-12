# encoding=utf8
from EventEngine.EventType import EVENT_NEWDATA, EVENT_NEWORDER
from EventEngine.EventEngine import EventEngine
from Strategy.Strategy import BaseStrategy
from DataHandler.DataHandle import DataSliceHandle, DataHandle
from Enums.OrderType import OrderType
from Enums.OrderStatus import OrderStatus
import ConfigParser


class MyStrategy(BaseStrategy):
    def __init__(self):
        BaseStrategy.__init__(self)
        self.__conf = ConfigParser.ConfigParser()
        self.__conf.read('D:\Github\BackTest\config\\a.config')
        self.__marting = float(self.__conf.get('strategy', 'marting'))
        self.__lot = float(self.__conf.get('strategy', 'lot'))
        self.__distance = float(self.__conf.get('strategy', 'distance'))
        self.__profit = float(self.__conf.get('strategy', 'profit'))

    def GetNewData(self, event):
        Bid = event.dict['data']['open']
        print event.dict['data']['time']
        Ask = Bid + self.spread
        orderstatistic = self.Holdingorder_Statistic(Ask=Ask, Bid=Bid)
        # 首选进行策略逻辑判断，由于测试策略不需要依照当前持仓单做判断，所有不需要调用self.Holdingorder_Statistic(）
        if orderstatistic['sell_number'] == 0:
            res = dict(
                status=OrderStatus.HOLDING.value,
                type=OrderType.SELL.value,
                opentime=event.dict['data']['time'],
                magic=self.magic,
                lot=self.__lot,
                openprice=Bid,
                takeprofit=Bid - self.__profit,
            )
            self.SendOrder(res)
        if orderstatistic['buy_number'] == 0:
            res = dict(
                status=OrderStatus.HOLDING.value,
                type=OrderType.BUY.value,
                opentime=event.dict['data']['time'],
                magic=self.magic,
                lot=self.__lot,
                openprice=Ask,
                takeprofit=Ask + self.__profit,
            )
            self.SendOrder(res)
        if orderstatistic['buy_number'] != 0 and (orderstatistic['last_buy_openprice'] - Ask) >= self.__distance:
            newlot = round(orderstatistic['max_buy_lot'] * self.__marting, 2)
            if newlot == orderstatistic['max_buy_lot']:
                newlot = newlot + 0.01
            res = dict(
                status=OrderStatus.HOLDING.value,
                type=OrderType.BUY.value,
                opentime=event.dict['data']['time'],
                magic=self.magic,
                lot=newlot,
                openprice=Ask,
            )
            self.SendOrder(res)
            # 重新计算止盈并修改
            orderinfo = self.All_HoldingOrderinfo()
            all_price = 0.0
            all_lot = 0.0
            for i in orderinfo['buy_order']:
                all_price = all_price + i['openprice'] * i['lot']
                all_lot = all_lot + i['lot']
            new_profit = round((all_price / all_lot), 5) + self.__profit
            for item in orderinfo['buy_order']:
                res = dict(
                    id=item['_id'],
                    modifyinfo=dict(
                        takeprofit=new_profit
                    )
                )
                self.ModifyOrder(res)
        if orderstatistic['sell_number'] != 0 and (Bid - orderstatistic['last_sell_openprice']) >= self.__distance:
            newlot = round(orderstatistic['max_sell_lot'] * self.__marting, 2)
            if newlot == orderstatistic['max_sell_lot']:
                newlot = newlot + 0.01
            res = dict(
                status=OrderStatus.HOLDING.value,
                type=OrderType.SELL.value,
                opentime=event.dict['data']['time'],
                magic=self.magic,
                lot=newlot,
                openprice=Ask,
            )
            self.SendOrder(res)
            orderinfo = self.All_HoldingOrderinfo()
            all_price = 0.0
            all_lot = 0.0
            for i in orderinfo['sell_order']:
                all_price = all_price + i['openprice'] * i['lot']
                all_lot = all_lot + i['lot']
            new_profit = round((all_price / all_lot), 5) - self.__profit
            for item in orderinfo['sell_order']:
                res = dict(
                    id=item['_id'],
                    modifyinfo=dict(
                        takeprofit=new_profit
                    )
                )
                self.ModifyOrder(res)
            res = dict(
                id=i['_id'],
                modifyinfo=dict(
                    takeprofit=new_profit
                )
            )
            self.ModifyOrder(res)

        # 经过策略判断之后调用self.All_HoldingOrderinfo()统计当前持仓单
        orderinfo = self.All_HoldingOrderinfo()
        # 调用时间处理函数保存当前时刻账户净值，最大净值以及最小净值
        self.TimeInfo(Time=event.dict['data']['time'], High=event.dict['data']['high'],
                      Low=event.dict['data']['low'])
        # 调用OrderProcece函数判断持仓单知否触发了止盈或者止损条件
        if orderinfo is not None:
            self.OrderProcess(DataSlice=event.dict['data'], OrderInfo=orderinfo)


def test(eventEngine):
    # mystrategy类的实例
    data_1 = MyStrategy()
    # 制定EVENT_NEWDATA类型时间由data_1.GetNewData函数处理
    eventEngine.AddEventListener(type_=EVENT_NEWDATA, handler=data_1.GetNewData)
    # 启动引擎
    eventEngine.Start()
    # 获取数据

    data = DataHandle().SplitData()
    for i in data:
        # 获取迭代产生的每一个数据切片
        new_data = DataSliceHandle(eventEngine=eventEngine, data=i)
        # 调用实例的发送事件接口，并指定事件类型
        new_data.SendDataEvent(type=EVENT_NEWDATA)
    # eventEngine.Stop()


if __name__ == '__main__':
    eventEngine = EventEngine()
    test(eventEngine)
    # eventEngine.Stop()
