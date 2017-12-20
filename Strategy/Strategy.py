# encoding=utf8
from DataHandler.MongoHandler import MongoHandler
from Enums.OrderType import OrderType
from Enums.OrderStatus import OrderStatus
import ConfigParser
import logging


class BaseStrategy(object):
    conf = ConfigParser.ConfigParser()
    conf.read('D:\Github\BackTest\config\\pattern.config')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(conf.get('common', 'log_path'), mode='w')
    fh.setLevel(logging.WARNING)
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    def __init__(self):
        self.magic = self.conf.get('common', 'magic')
        self.__mongohandler = MongoHandler(self.magic)
        self.spread = float(self.conf.get('common', 'spread'))
        self.data_path = self.conf.get('common', 'data_path')
        self.mount = int(self.conf.get('account', 'mount'))

    def ValueProcess(self,ClosePrice=None,Openprice=None,Lot=None,Type=None):
        mount = self.MountCalculate()
        if Type == OrderType.BUY.value:
            value = round(
                (ClosePrice-Openprice-self.spread)*Lot*1000*100,2
            )
        else:
            value = round(
                (Openprice-ClosePrice-self.spread)*Lot*1000*100,2
            )
        mount = mount+value
        return mount,value
    def OrderProcess(self, DataSlice=None, OrderInfo=None):
        # 在策略逻辑执行之前判断当前价位针对于持仓单是否会触发止盈和止损
        mount = self.MountCalculate()
        for item in OrderInfo['buy_order']:
            if item['type'] == OrderType.BUY.value and 'stoploss' in item:
                if DataSlice['low'] <= item['stoploss']:
                    # 多单止损出场  修改数据库记录
                    new_mount,value = self.ValueProcess(ClosePrice=item['stoploss'],Openprice=item['openprice'],Lot=item['lot'],Type=OrderType.BUY.value)
                    res = dict(id=item['_id'],
                               modifyinfo=dict(mount=new_mount, value=value, status=OrderStatus.CLOSED.value,
                                               closetime=DataSlice['time'],
                                               closeprice=round(item['stoploss'], 5)))

                    self.ModifyOrder(res)
            if item['type'] == OrderType.BUY.value and 'takeprofit' in item:
                if DataSlice['high'] >= item['takeprofit']:
                    # 多单止盈出场 修改数据库记录
                    new_mount,value = self.ValueProcess(ClosePrice=item['takeprofit'],Openprice=item['openprice'],Lot=item['lot'],Type=OrderType.BUY.value)
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
                    new_mount,value = self.ValueProcess(ClosePrice=item['stoploss'],Openprice=item['openprice'],Lot=item['lot'],Type=OrderType.SELL.value)
                    res = dict(id=item['_id'],
                               modifyinfo=dict(mount=new_mount, value=value, status=OrderStatus.CLOSED.value,
                                               closetime=DataSlice['time'],
                                               closeprice=round(item['stoploss'], 5)))
                    self.ModifyOrder(res)
            if item['type'] == OrderType.SELL.value and 'takeprofit' in item:
                if DataSlice['low'] <= item['takeprofit'] - self.spread:
                    # 空单止盈出场 修改数据库记录
                    # 注意 空单止盈是过点差止盈
                    new_mount,value = self.ValueProcess(ClosePrice=item['takeprofit'],Openprice=item['openprice'],Lot=item['lot'],Type=OrderType.SELL.value)
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
        self.logger.warning('TIME:%s - new order open with lot:%f at %f' % (
        orderinfo['opentime'], orderinfo['lot'], orderinfo['openprice']))
        self.__mongohandler.save_orderinfo(orderinfo)

    def CloseOrder(self, info=None):
        self.logger.warning('TIME:%s - order closed at:%f' % (info['modifyinfo']['closetime'], info['modifyinfo']['closeprice']))
        order_info = self.__mongohandler.get_orderdetail(id=info['id'],info=['lot','openprice'])
        close_time = info['modifyinfo']['closetime']
        close_price = info['modifyinfo']['closeprice']
        lot=order_info['lot']
        open_price=order_info['openprice']
        order_type=info['modifyinfo']['type']
        if order_type == OrderType.BUY.value:
            new_mount, value = self.ValueProcess(ClosePrice=close_price, Openprice=open_price,
                                                 Lot=lot, Type=OrderType.BUY.value)
            res = dict(id=info['id'],
                       modifyinfo=dict(mount=new_mount, value=value, status=OrderStatus.CLOSED.value,
                                       closetime=close_time,
                                       closeprice=round(close_price, 5)))

            self.ModifyOrder(res)
        if order_type == OrderType.SELL.value:
            new_mount, value = self.ValueProcess(ClosePrice=close_price, Openprice=open_price,
                                                 Lot=lot, Type=OrderType.SELL.value)
            res = dict(id=info['id'],
                       modifyinfo=dict(mount=new_mount, value=value, status=OrderStatus.CLOSED.value,
                                       closetime=close_time,
                                       closeprice=round(close_price, 5)))
            self.ModifyOrder(res)





    def ModifyOrder(self, modifyinfo=None):
        self.logger.info('TIME:%s - order modify')
        self.__mongohandler.modify_order(modifyinfo)

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
        pipline = [
            {'$group': {
                '_id': '$status',
                'last_mount': {
                    '$last': '$mount'
                }
            }}
        ]
        res = self.__mongohandler.arrgegate(pipline)
        mount = self.mount
        for i in res:
            if i['last_mount'] is not None:
                mount = float(i['last_mount'])
            else:
                mount = self.mount
        return mount
