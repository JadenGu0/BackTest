# encoding=utf8
from pymongo import MongoClient
from Enums.OrderStatus import OrderStatus
from Enums.OrderType import OrderType


class MongoHandler(object):
    def __init__(self, magic):
        self.__magic = magic
        self.__client = MongoClient('localhost', 27017)
        self.__db = self.__client[self.__magic]
        self.__collection_order = self.__db['OrderIndo']
        self.__collection_time = self.__db['Time']

    def save_orderinfo(self, info=None):
        """
        将订单信息写入数据库
        :param info:
        :return:
        """
        res = self.__collection_order.insert_one(info)

    def save_timeinfo(self, info=None):
        """
        将时间序列信息写入数据库
        :param info:
        :return:
        """
        res = self.__collection_time.insert_one(info)

    def allorder_info(self):
        """
        返回所有持仓单订单信息，包含订单的每一个字段
        :param Ask:
        :param Bid:
        :return:
        """
        res={}
        res['buy_order']=[i for i in self.__collection_order.find({'status':OrderStatus.HOLDING.value,'type':OrderType.BUY.value})]
        res['sell_order']=[i for i in self.__collection_order.find({'status':OrderStatus.HOLDING.value,'type':OrderType.SELL.value})]
        return res

    def holdingorder_statistic(self, Ask=None, Bid=None):
        """
        返回所有持仓单订单统计信息，包括多\空单持仓量，持仓浮亏，以及最后一单开单价
        :param Ask:
        :param Bid:
        :return:
        """
        res = {}
        buy_order = self.__collection_order.find({'status': OrderStatus.HOLDING.value, 'type': OrderType.BUY.value})
        sell_order = self.__collection_order.find({'status': OrderStatus.HOLDING.value, 'type': OrderType.SELL.value})
        res['buy_number'] = buy_order.count()
        res['sell_number'] = sell_order.count()

        buy_mount = 0
        sell_mount = 0
        buy_lot = 0
        sell_lot = 0
        if buy_order.count() != 0:
            last_buy_openprice = \
                self.__collection_order.find_one({'status': OrderStatus.HOLDING.value, 'type': OrderType.BUY.value})[
                    'openprice']
            for i in buy_order:
                buy_mount = buy_mount + round((Ask - i['openprice']) * 1000 * i['lot'], 2)
                buy_lot = buy_lot + i['lot']
                if last_buy_openprice > i['openprice']:
                    last_buy_openprice = i['openprice']
            res['buy_mount'] = buy_mount
            res['buy_lot'] = buy_lot
            res['last_buy_openprice'] = last_buy_openprice

        if sell_order.count() != 0:
            last_sell_openprice = \
                self.__collection_order.find_one({'status': OrderStatus.HOLDING.value, 'type': OrderType.SELL.value})[
                    'openprice']
            for i in sell_order:
                sell_mount = sell_mount + round((i['openprice'] - Bid) * 1000 * i['lot'], 2)
                sell_lot = sell_lot + i['lot']
                if last_sell_openprice < i['openprice']:
                    last_sell_openprice = i['openprice']
            res['sell_mount'] = sell_mount
            res['sell_lot'] = sell_lot
            res['last_sell_openprice'] = last_sell_openprice
        return res

    def get_orderdetail(self, ticket=None):
        pass

    def modify_order(self,modifyinfo=None):
        print  modifyinfo
        for k,v in modifyinfo['modifyinfo'].items():
            self.__collection_order.update(
                {'_id':modifyinfo['id']},
                 {'$set':{k:v}}
            )






