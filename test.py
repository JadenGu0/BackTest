# encoding=utf8
from EventEngine.EventType import EVENT_NEWDATA, EVENT_NEWORDER
from EventEngine.EventEngine import EventEngine
from Strategy.Strategy import BaseStrategy
from DataHandler.DataHandle import DataSliceHandle, DataHandle
import pandas as pd
from config.config import DATA_ROOT_PATH
from Strategy.Indicators import BarInfo,Ma
from Enums.OrderType import OrderType
from Enums.OrderStatus import OrderStatus
MAGIC='1232525'
SPREAD = 0.00030


class MyStrategy(BaseStrategy):
    def __init__(self,  magic=None):
        BaseStrategy.__init__(self,  magic)

    def GetNewData(self, event):
        Bid = event.dict['data']['open']
        print event.dict['data']['time']
        Ask = Bid + SPREAD
        orderinfo = self.mongohandler.allorder_info()
        self.OrderPreProcess(Ask=Ask, Bid=Bid, DataSlice=event.dict['data'], OrderInfo=orderinfo)
        orderstatistic = self.mongohandler.holdingorder_statistic(Ask=Ask, Bid=Bid)
        ma_now_long=Ma(period=10,shift=1,time=event.dict['data']['time']).get_Ma()
        ma_last_long=Ma(period=10,shift=2,time=event.dict['data']['time']).get_Ma()
        ma_now_short=Ma(period=5,shift=1,time=event.dict['data']['time']).get_Ma()
        ma_last_short=Ma(period=5,shift=2,time=event.dict['data']['time']).get_Ma()
        if ma_last_long<ma_last_short and ma_now_long>ma_now_short:
            res=dict(
                status=OrderStatus.HOLDING.value,
                type=OrderType.SELL.value,
                opentime=event.dict['data']['time'],
                magic=MAGIC,
                lot=0.01,
                openprice=Bid,
                takeprofit=round((Bid-0.00300),5),
                stoploss=round((Bid+0.00300),5),
            )
            self.SendOrder(res)



def test():
    # 事件处理引擎实例
    eventEngine = EventEngine()
    # mystrategy类的实例
    data_1 = MyStrategy(magic=MAGIC)
    # 制定EVENT_NEWDATA类型时间由data_1.GetNewData函数处理
    eventEngine.AddEventListener(type_=EVENT_NEWDATA, handler=data_1.GetNewData)
    # 启动引擎
    eventEngine.Start()
    # 获取数据

    data = DataHandle(data=pd.read_csv('.\HistoryData\EURUSD_1H.csv'), start='2017.01.01',
                      end='2017.01.30').SplitData()
    for i in data:
        # 获取迭代产生的每一个数据切片
        new_data = DataSliceHandle(magic=MAGIC, eventEngine=eventEngine, data=i)
        # 调用实例的发送事件接口，并指定事件类型
        new_data.SendDataEvent(type=EVENT_NEWDATA)


    # eventEngine.Stop()


if __name__ == '__main__':
    test()
