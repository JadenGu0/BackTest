# encoding=utf8
from EventEngine.EventEngine import Event
from EventEngine.EventType import EVENT_CLOSEORDER, EVENT_MODIFYORDER, EVENT_NEWORDER, EVENT_NEWDATA
from DataHandler.MongoHandler import MongoHandler
from Enums.OrderType import OrderType
from Enums.OrderStatus import OrderStatus


class BaseStrategy(object):
    def __init__(self, magic):
        # self.__eventEngine = eventEngine
        # self.__eventEngine.AddEventListener(type_=EVENT_NEWORDER, handler=self.SendOrder)
        # # self.__eventEngine.AddEventListener(type_=EVENT_CLOSEORDER, handler=self.CloseOrder)
        # self.__eventEngine.AddEventListener(type_=EVENT_MODIFYORDER, handler=self.ModifyOrder)
        self.__magic = magic
        self.__mongohandler = MongoHandler(self.__magic)

    def OrderProcess(self, Spread=None, DataSlice=None, OrderInfo=None, AccountMount=None):
        # 在策略逻辑执行之前判断当前价位针对于持仓单是否会触发止盈和止损
        mount = self.MountCalculate(Mount=AccountMount)
        for item in OrderInfo['buy_order']:
            if item['type'] == OrderType.BUY.value and 'stoploss' in item:
                if DataSlice['low'] <= item['stoploss']:
                    # 多单止损出场  修改数据库记录
                    value = round((round(item['stoploss'], 5) - item['openprice']) * item['lot'] * 1000 * 100, 2)
                    new_mount = mount + value
                    mount = new_mount
                    res = dict(id=item['_id'],
                               modifyinfo=dict(mount=new_mount, value=value, status=OrderStatus.CLOSED.value,
                                               closetime=DataSlice['time'],
                                               closeprice=round(item['stoploss'], 5)))

                    self.ModifyOrder(res)
            if item['type'] == OrderType.BUY.value and 'takeprofit' in item:
                if DataSlice['high'] >= item['takeprofit']:
                    # 多单止盈出场 修改数据库记录
                    value = round((round(item['takeprofit'], 5) - item['openprice']) * item['lot'] * 1000 * 100, 2)
                    new_mount = mount + value
                    mount = new_mount
                    res = dict(id=item['_id'],
                               modifyinfo=dict(mount=new_mount, value=value, status=OrderStatus.CLOSED.value,
                                               closetime=DataSlice['time'],
                                               closeprice=round(item['takeprofit'], 5)))
                    self.ModifyOrder(res)
        for item in OrderInfo['sell_order']:
            if item['type'] == OrderType.SELL.value and 'stoploss' in item:
                if DataSlice['high'] >= item['stoploss']:
                    # 空单止损出场 修改数据库记录
                    value = round((item['openprice']-round(item['stoploss'],5)) * item['lot'] * 1000 * 100, 2)
                    new_mount = mount + value
                    mount = new_mount
                    res = dict(id=item['_id'],
                               modifyinfo=dict(mount=new_mount, value=value, status=OrderStatus.CLOSED.value,
                                               closetime=DataSlice['time'],
                                               closeprice=round(item['stoploss'], 5)))
                    self.ModifyOrder(res)
            if item['type'] == OrderType.SELL.value and 'takeprofit' in item:
                if DataSlice['low'] <= item['takeprofit']:
                    # 多单止盈出场 修改数据库记录
                    value = round((item['openprice']-round(item['takeprofit'],5)) * item['lot'] * 1000 * 100, 2)
                    new_mount = mount + value
                    mount = new_mount
                    res = dict(id=item['_id'],
                               modifyinfo=dict(mount=new_mount, value=value, status=OrderStatus.CLOSED.value,
                                               closetime=DataSlice['time'],
                                               closeprice=round(item['takeprofit'], 5)))
                    self.ModifyOrder(res)

    def GetNewData(self, data=None):
        """

        :param data:
        :return:
        """

    def SendOrder(self, orderinfo=None):

        self.__mongohandler.save_orderinfo(orderinfo)

    # def CloseOrder(self, ticket, dataslice=None):
    #     res = False
    #     orderinfo = {}
    #     if res == True:
    #         self.SendEvent(type=EVENT_CLOSEORDER, orderinfo=orderinfo)

    def ModifyOrder(self, modifyinfo=None):
        self.__mongohandler.modify_order(modifyinfo)

        # def SendOrderEvent(self, type=None, orderinfo=None):
        #     OrderEvent = Event(type=type)
        #     OrderEvent.dict = orderinfo
        #     self.__eventEngine.SendEvent(OrderEvent)

    def Holdingorder_Statistic(self, Ask=None, Bid=None):
        return self.__mongohandler.holdingorder_statistic(Ask=Ask, Bid=Bid)

    def All_HoldingOrderinfo(self):
        return self.__mongohandler.all_holdingorder()

    def TimeInfo(self, Time=None, Mount=None, High=None, Low=None):
        # 用来计算每个时刻的净值，余额，最大净值和最小净值
        holdingorder_info = self.All_HoldingOrderinfo()
        mount = self.MountCalculate(Mount=Mount)
        high_mount = 0
        low_mount = 0
        order_info=self.__mongohandler.search(opentime=Time)
        buy_lot=0
        sell_lot=0
        if order_info is not None:
            for item in order_info:
                if item['type'] == OrderType.SELL.value:
                    sell_lot=sell_lot+item['lot']
                if item['type'] == OrderType.BUY.value:
                    buy_lot=buy_lot+item['lot']
        if holdingorder_info['buy_order'] is not None:
            for i in holdingorder_info['buy_order']:
                high_mount = high_mount + (High - i['openprice']) * i['lot'] * 1000 * 100
                low_mount = low_mount + (Low - i['openprice']) * i['lot'] * 1000 * 100
        if holdingorder_info['sell_order'] is not None:
            for i in holdingorder_info['sell_order']:
                high_mount = high_mount + (i['openprice'] - High) * i['lot'] * 1000 * 100
                low_mount = low_mount + (i['openprice'] - Low) * i['lot'] * 1000 * 100
        max_mount = max(mount + high_mount, mount + low_mount)
        min_mount = min(mount + high_mount, mount + low_mount)
        res=dict(
                time=Time,
                mount=mount,
                max_mount=max_mount,
                min_mount=min_mount,
                buy_lot=buy_lot,
                sell_lot=sell_lot
        )
        self.__mongohandler.save_timeinfo(
            info=res
        )


    def MountCalculate(self, Mount=None):
        # 计算当前账户净值
        pipline = [{'$group': {'_id': '$value', 'count': {'$sum': 1}}}]
        arrge_res = self.__mongohandler.arrgegate(pipline)
        mount = Mount
        if arrge_res is not None:
            for item in arrge_res:

                if item['_id'] is not None:
                    mount = mount + item['count'] * item['_id']
        return mount
