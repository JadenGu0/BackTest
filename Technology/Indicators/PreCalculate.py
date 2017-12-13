# encoding=utf8
import ConfigParser
import pandas as pd
import datetime
import logging


class PreCalculate(object):
    def __init__(self, delta=None):
        #用于在策略执行前计算策略需要用到的指标数据并全部写入csv临时文件，目的是为了提高回测过程中的效率
        #delta的作用是为了补偿策略计算用到的前值数据
        self.__conf = ConfigParser.ConfigParser()
        self.__delta = delta
        self.__conf.read('D:\Github\BackTest\config\\best_marting.config')
        self.__data = pd.read_csv(self.__conf.get('common', 'data_path'))
        self.start = self.__conf.get('common', 'start')
        self.end = self.__conf.get('common', 'end')
        self.__data_period = int(self.__conf.get('common', 'period'))
        self.__point = int(self.__conf.get('common', 'point'))

    def data_split(self):
        start_time = datetime.datetime.strptime(self.start, '%Y.%m.%d')
        delta_time = datetime.timedelta(hours=-(self.__delta / (60 / self.__data_period)))
        start_time = (start_time + delta_time).strftime('%Y.%m.%d')
        data = self.__data[self.__data['Time (UTC)'] >= start_time]
        data = data[data['Time (UTC)'] <= self.end]
        data.to_csv(self.__conf.get('common', 'test_data_path'))
        print 'data split finish'

    def ma_calculate(self, period=None, shift=None):
        data = pd.read_csv(self.__conf.get('common', 'test_data_path'))
        MA = pd.Series(data.rolling(period).mean()['Close'].shift(shift),
                       name='MA-' + str(period) + '-Shift-' + str(shift))
        data = data.join(MA)
        data.to_csv(self.__conf.get('common', 'test_data_path'), index=None, float_format='%.5f')
        print 'ma calculate finish'

    def high_calculate(self, period=None, shift=None):
        data = pd.read_csv(self.__conf.get('common', 'test_data_path'))
        HIGH = pd.Series(data.rolling(period).max()['High'].shift(shift),
                         name='High-' + str(period) + '-Shift-' + str(shift))
        data = data.join(HIGH)
        data.to_csv(self.__conf.get('common', 'test_data_path'), index=None, float_format='%.5f')
        print 'high calculate finish'

    def low_calculate(self, period=None, shift=None):
        data = pd.read_csv(self.__conf.get('common', 'test_data_path'))
        LOW = pd.Series(data.rolling(period).min()['Low'].shift(shift),
                        name='Low-' + str(period) + '-Shift-' + str(shift))
        data = data.join(LOW)
        data.to_csv(self.__conf.get('common', 'test_data_path'), index=None, float_format='%.5f')
        print 'low calculate finish'

if __name__ == '__main__':
    test = PreCalculate(delta=120)
    test.data_split()
    test.ma_calculate(period=10, shift=1)
    test.high_calculate(period=10, shift=1)
