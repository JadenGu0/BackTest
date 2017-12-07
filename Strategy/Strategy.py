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
        self.mongohandler = MongoHandler(self.__magic)

    def OrderPreProcess(self, Ask=None, Bid=None, DataSlice=None, OrderInfo=None,AccountMount=None):
        # 在策略逻辑执行之前判断当前价位针对于持仓单是否会触发止盈和止损
        pipline = [{'$group': {'_id': '$value', 'count': {'$sum': 1}}}]
        arrge_res = self.mongohandler.arrgegate(pipline)
        mount = AccountMount
        print arrge_res
        if arrge_res is not None:
            for item in arrge_res:

                if item['_id'] is not None:
                    mount=mount+item['count']*item['_id']

        for item in OrderInfo['buy_order']:
            if item['type'] == OrderType.BUY.value and item['stoploss'] is not None:
                if DataSlice['low'] <= item['stoploss']:
                    # 多单止损出场  修改数据库记录
                    value = round((round(item['stoploss'], 5) - item['openprice']) * item['lot'] * 1000 * 100, 2)
                    new_mount=mount+value
                    mount=new_mount
                    res = dict(id=item['_id'],
                               modifyinfo=dict(mount=new_mount,value=value, status=OrderStatus.CLOSED.value,
                                               closetime=DataSlice['time'],
                                               closeprice=round(item['stoploss'], 5)))

                    self.mongohandler.modify_order(res)
            if item['type'] == OrderType.BUY.value and item['takeprofit'] is not None:
                if DataSlice['high'] >= item['takeprofit']:
                    # 多单止盈出场 修改数据库记录
                    value = round((round(item['takeprofit'], 5) - item['openprice']) * item['lot'] * 1000 * 100, 2)
                    new_mount = mount + value
                    mount = new_mount
                    res = dict(id=item['_id'],
                               modifyinfo=dict(mount=new_mount,value=value, status=OrderStatus.CLOSED.value,
                                               closetime=DataSlice['time'],
                                               closeprice=round(item['takeprofit'], 5)))
                    self.mongohandler.modify_order(res)
        for item in OrderInfo['sell_order']:
            if item['type'] == OrderType.SELL.value and item['stoploss'] is not None:
                if DataSlice['high'] >= item['stoploss']:
                    # 空单止损出场 修改数据库记录
                    value = round((round(item['stoploss'], 5) - item['openprice']) * item['lot'] * 1000 * 100, 2)
                    new_mount = mount + value
                    mount = new_mount
                    res = dict(id=item['_id'],
                               modifyinfo=dict(mount=new_mount,value=value, status=OrderStatus.CLOSED.value,
                                               closetime=DataSlice['time'],
                                               closeprice=round(item['stoploss'], 5)))
                    self.mongohandler.modify_order(res)
            if item['type'] == OrderType.SELL.value and item['takeprofit'] is not None:
                if DataSlice['low'] <= item['takeprofit']:
                    # 多单止盈出场 修改数据库记录
                    value = round((round(item['takeprofit'], 5) - item['openprice']) * item['lot'] * 1000 * 100, 2)
                    new_mount = mount + value
                    mount = new_mount
                    res = dict(id=item['_id'],
                               modifyinfo=dict(mount=new_mount,value=value, status=OrderStatus.CLOSED.value,
                                               closetime=DataSlice['time'],
                                               closeprice=round(item['takeprofit'], 5)))
                    self.mongohandler.modify_order(res)

    def GetNewData(self, data=None):
        """

        :param data:
        :return:
        """

    def SendOrder(self, orderinfo=None):

        self.mongohandler.save_orderinfo(orderinfo)

    # def CloseOrder(self, ticket, dataslice=None):
    #     res = False
    #     orderinfo = {}
    #     if res == True:
    #         self.SendEvent(type=EVENT_CLOSEORDER, orderinfo=orderinfo)

    def ModifyOrder(self, modifyinfo=None):
        self.mongohandler.modify_order(modifyinfo)

        # def SendOrderEvent(self, type=None, orderinfo=None):
        #     OrderEvent = Event(type=type)
        #     OrderEvent.dict = orderinfo
        #     self.__eventEngine.SendEvent(OrderEvent)
