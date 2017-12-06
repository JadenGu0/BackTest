# encoing=utf8
from EventEngine.EventEngine import Event
from EventEngine.EventType import EVENT_CLOSEORDER,EVENT_MODIFYORDER,EVENT_NEWORDER,EVENT_NEWDATA
from DataHandler.MongoHandler import MongoHandler
from Enums.OrderType import OrderType
from Enums.OrderStatus import  OrderStatus

class BaseStrategy(object):
    def __init__(self, eventEngine,magic):
        self.__eventEngine = eventEngine
        self.__eventEngine.AddEventListener(type_=EVENT_NEWORDER, handler=self.SendOrder)
        self.__eventEngine.AddEventListener(type_=EVENT_CLOSEORDER, handler=self.CloseOrder)
        self.__eventEngine.AddEventListener(type_=EVENT_MODIFYORDER, handler=self.ModifyOrder)
        self.__magic=magic
        self.__mongohandler = MongoHandler(self.__magic)

    def OrderPreProcess(self,Ask=None,Bid=None,High=None,Low=None,OrderInfo=None):
        #在策略逻辑执行之前判断当前价位针对于持仓单是否会触发止盈和止损
        for item in OrderInfo:
            if item['type'] == OrderType.BUY.value and item['stoploss'] is not None:
                if Low <= item['stoploss']:
                    #多单止损出场  修改数据库记录
                    self.__mongohandler.modify_order(id=item['id'])

    def GetNewData(self, data=None):
        """

        :param data:
        :return:
        """
        self.SendBuyOrder(dataslice=data)
        self.SendSellOrder(dataslice=data)
        self.ModifyOrder(ticket=None, dataslice=data)
        self.CloseOrder(ticket=None, dataslice=data)

    def SendOrder(self, event):
        self.__mongohandler.save_orderinfo(event.dict)

    def CloseOrder(self, ticket, dataslice=None):
        res = False
        orderinfo = {}
        if res == True:
            self.SendEvent(type=EVENT_CLOSEORDER, orderinfo=orderinfo)

    def ModifyOrder(self, ticket, dataslice=None):
        res = False
        orderinfo = {}
        if res == True:
            self.SendEvent(type=EVENT_MODIFYORDER, orderinfo=orderinfo)

    def SendEvent(self, type=None, orderinfo=None):
        OrderEvent = Event(type=type)
        OrderEvent.dict = orderinfo
        self.__eventEngine.SendEvent(OrderEvent)
