# encoding=utf8
from DataHandler.MongoHandler import MongoHandler
from Enums.OrderType import OrderType
from Enums.OrderStatus import OrderStatus
import ConfigParser
import logging
import sys

class BaseStrategy(object):
    def __init__(self):
        self.__conf = ConfigParser.ConfigParser()
        self.__conf.read('D:\Github\BackTest\config\\a.config')
        self.magic = self.__conf.get('common', 'magic')
        self.__mongohandler = MongoHandler(self.magic)
        self.spread = float(self.__conf.get('common', 'spread'))
        self.data_path = self.__conf.get('common', 'data_path')
        self.mount = int(self.__conf.get('account', 'mount'))

        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.INFO)
        fh = logging.FileHandler(self.__conf.get('common','log_path'),mode='w')
        fh.setLevel(logging.WARNING)
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        self.__logger.addHandler(fh)
        self.__logger.addHandler(ch)


    def OrderProcess(self, DataSlice=None, OrderInfo=None):
        # 在策略逻辑执行之前判断当前价位针对于持仓单是否会触发止盈和止损
        mount = self.MountCalculate()
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
                if DataSlice['high'] >= item['stoploss'] - self.spread:
                    # 空单止损出场 修改数据库记录
                    # 注意 空单止损是提前点差出场的
                    value = round(
                        (item['openprice'] - round(item['stoploss'] - self.spread, 5)) * item['lot'] * 1000 * 100, 2)
                    new_mount = mount + value
                    mount = new_mount
                    res = dict(id=item['_id'],
                               modifyinfo=dict(mount=new_mount, value=value, status=OrderStatus.CLOSED.value,
                                               closetime=DataSlice['time'],
                                               closeprice=round(item['stoploss'], 5)))
                    self.ModifyOrder(res)
            if item['type'] == OrderType.SELL.value and 'takeprofit' in item:
                if DataSlice['low'] <= item['takeprofit'] - self.spread:
                    # 多单止盈出场 修改数据库记录
                    # 注意 空单止盈是过点差止盈
                    value = round(
                        (item['openprice'] - round(item['takeprofit'] - self.spread, 5)) * item['lot'] * 1000 * 100, 2)
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
        self.__logger.info('TIME:%s - new order open with lot:%f at %f' %(orderinfo['opentime'],orderinfo['lot'],orderinfo['openprice']))
        self.__mongohandler.save_orderinfo(orderinfo)

    # def CloseOrder(self, ticket, dataslice=None):
    #     res = False
    #     orderinfo = {}
    #     if res == True:
    #         self.SendEvent(type=EVENT_CLOSEORDER, orderinfo=orderinfo)

    def ModifyOrder(self, modifyinfo=None):
        self.__logger.info('TIME:%s - order modify')
        self.__mongohandler.modify_order(modifyinfo)

        # def SendOrderEvent(self, type=None, orderinfo=None):
        #     OrderEvent = Event(type=type)
        #     OrderEvent.dict = orderinfo
        #     self.__eventEngine.SendEvent(OrderEvent)

    def Holdingorder_Statistic(self, Ask=None, Bid=None):
        return self.__mongohandler.holdingorder_statistic(Ask=Ask, Bid=Bid)

    def All_HoldingOrderinfo(self):
        return self.__mongohandler.all_holdingorder()

    def TimeInfo(self, Time=None, High=None, Low=None):
        # 用来计算每个时刻的净值，余额，最大净值和最小净值
        holdingorder_info = self.All_HoldingOrderinfo()
        mount = self.MountCalculate()
        high_mount = 0
        low_mount = 0
        order_info = self.__mongohandler.search(opentime=Time)
        buy_lot = 0
        sell_lot = 0
        if order_info is not None:
            for item in order_info:
                if item['type'] == OrderType.SELL.value:
                    sell_lot = sell_lot + item['lot']
                if item['type'] == OrderType.BUY.value:
                    buy_lot = buy_lot + item['lot']
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
        res = dict(
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

    def MountCalculate(self):
        # 计算当前账户净值
        pipline = [{'$group': {'_id': '$value', 'count': {'$sum': 1}}}]
        arrge_res = self.__mongohandler.arrgegate(pipline)
        mount = self.mount
        if arrge_res is not None:
            for item in arrge_res:
                if item['_id'] is not None:
                    mount = mount + item['count'] * item['_id']
        return mount
