# encoding=utf8
import ConfigParser

from DataHandler.DataHandle import DataSliceHandle, DataHandle
from Enums.OrderStatus import OrderStatus
from Enums.OrderType import OrderType
from EventEngine.EventEngine import EventEngine
from EventEngine.EventType import EVENT_NEWDATA
from Strategy.Strategy import BaseStrategy
from Error.error import LotError, StartEndError
from Technology.Indicators.PreCalculate import PreCalculate
import logging


class MyStrategy(BaseStrategy):
    try:
        conf = ConfigParser.ConfigParser()
        conf.read('D:\Github\BackTest\config\\pattern.config')
    except (ConfigParser.NoSectionError, IOError), e:
        logging.error(e)
        raise

    def __init__(self):
        try:
            BaseStrategy.__init__(self)
            self.__lot = float(self.conf.get('strategy', 'lot'))
            self.__takeprofit = float(self.conf.get('strategy', 'takeprofit'))
            self.__stoploss = float(self.conf.get('strategy', 'stoploss'))
            self.__long_period = int(self.conf.get('strategy', 'long_period'))
            self.__short_period = int(self.conf.get('strategy', 'short_period'))
            self.__call_back = float(self.conf.get('strategy', 'call_back'))
            self.__move = float(self.conf.get('strategy', 'move'))
            self.__proportion = float(self.conf.get('strategy', 'proportion'))
        except (ConfigParser.NoSectionError, IOError), e:
            logging.error(e)
            raise

    def GetNewData(self, event):
        print event.dict['data']['time']
        # 计算策略逻辑需要用到的变量
        long_high = High(period=self.__long_period, shift=1, time=event.dict['data']['time']).get_High()
        long_low = Low(period=self.__long_period, shift=1, time=event.dict['data']['time']).get_Low()
        close_high = High(period=self.__short_period, shift=2, time=event.dict['data']['time']).get_High()
        close_low = Low(period=self.__short_period, shift=2, time=event.dict['data']['time']).get_Low()
        last_close = BarInfo(shift=1, time=event.dict['data']['time']).get_barinfo()['close']
        open_price = event.dict['data']['open']
        long_move = long_high - long_low
        Bid = event.dict['data']['open']
        Ask = Bid + self.spread
        orderstatistic = self.Holdingorder_Statistic(Ask=Ask, Bid=Bid)
        if long_move != 0 and orderstatistic['buy_number'] == 0:
            # 多单开单
            if long_move > self.__move and last_close < close_low and last_close > (
                        long_low + (long_high - long_low) * self.__proportion):
                res = dict(
                    status=OrderStatus.HOLDING.value,
                    type=OrderType.BUY.value,
                    opentime=event.dict['data']['time'],
                    magic=self.magic,
                    lot=self.__lot,
                    openprice=Ask,
                    takeprofit=Ask + self.__takeprofit,
                    stoploss=Ask - self.__stoploss
                )
                self.SendOrder(orderinfo=res)
        if long_move != 0 and orderstatistic['sell_number'] == 0:
            # 空单开单
            if long_move > self.__move and last_close > close_high and last_close < (
                        long_high - (long_high - long_low) * self.__proportion):
                res = dict(
                    status=OrderStatus.HOLDING.value,
                    type=OrderType.SELL.value,
                    opentime=event.dict['data']['time'],
                    magic=self.magic,
                    lot=self.__lot,
                    openprice=Bid,
                    takeprofit=Bid - self.__takeprofit,
                    stoploss=Bid + self.__stoploss
                )
                self.SendOrder(orderinfo=res)
        # 经过策略判断之后调用self.All_HoldingOrderinfo()统计当前持仓单
        orderinfo = self.All_HoldingOrderinfo()
        # 判断是否满足平仓条件
        if orderstatistic['buy_number'] != 0:
            if open_price > close_high:
                # 平仓多单
                for item in orderinfo['buy_order']:
                    res = dict(
                        id=item['_id'],
                        modifyinfo=dict(
                            closetime=event.dict['data']['time'],
                            closeprice=event.dict['data']['open'],
                            type=OrderType.BUY.value
                        )
                    )
                    self.CloseOrder(res)
        if orderstatistic['sell_number'] != 0:
            if open_price < close_low:
                # 平仓空单
                for item in orderinfo['sell_order']:
                    res = dict(
                        id=item['_id'],
                        modifyinfo=dict(
                            closetime=event.dict['data']['time'],
                            closeprice=event.dict['data']['open'],
                            type=OrderType.SELL.value
                        )
                    )
                    self.CloseOrder(res)

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
    # 策略回测运行提前计算用到的指标数据，目的是加快回测过程中速度
    try:
        pre_handler = PreCalculate(delta=170)
        pre_handler.high_calculate(period=40, shift=1)
        pre_handler.low_calculate(period=40, shift=1)
        pre_handler.high_calculate(period=7, shift=2)
        pre_handler.low_calculate(period=7, shift=2)
    except (LotError, StartEndError), e:
        print e
    from Technology.Indicators.Indicators import High, Low, BarInfo

    eventEngine = EventEngine()
    test(eventEngine)
    # eventEngine.Stop()
