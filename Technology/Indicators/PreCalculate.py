# encoding=utf8
import ConfigParser
import pandas as pd
import datetime
import logging
from Error.error import PeriodError, StartEndError, ParameterError


class PreCalculate(object):
    try:
        conf = ConfigParser.ConfigParser()
        conf.read('D:\Github\BackTest\config\\pattern.config')
        data = pd.read_csv(conf.get('common', 'data_path'))
        period = [5, 15, 30, 60, 240, 1440, 10080, 43200]
    except (ConfigParser.NoSectionError, IOError), e:
        logging.error(e)
        raise

    def __init__(self, delta=None):
        # 用于在策略执行前计算策略需要用到的指标数据并全部写入csv临时文件，目的是为了提高回测过程中的效率
        # delta的作用是为了补偿策略计算用到的前值数据
        try:
            self.__delta = delta
            self.start = self.conf.get('common', 'start')
            self.end = self.conf.get('common', 'end')
            self.__data_period = int(self.conf.get('common', 'period'))
            self.__point = int(self.conf.get('common', 'point'))
            self.__data_split()
            self.__config_check()
        except ConfigParser.NoSectionError, e:
            logging.error(e)
            raise ConfigParser.NoSectionError

    def __config_check(self):
        if self.end <= self.start:
            raise StartEndError
        if self.__data_period not in self.period:
            raise PeriodError

    def __data_split(self):
        try:
            start_time = datetime.datetime.strptime(self.start, '%Y.%m.%d')
            delta_time = datetime.timedelta(hours=-(self.__delta / (60 / self.__data_period)))
            start_time = (start_time + delta_time).strftime('%Y.%m.%d')
            data = self.data[self.data['Time (UTC)'] >= start_time]
            data = data[data['Time (UTC)'] <= self.end]
            data.to_csv(self.conf.get('common', 'test_data_path'))
            logging.info("Date Split Done")
        except (ValueError, IOError), e:
            logging.error(e)
            raise

    def ma_calculate(self, period=None, shift=None):
        try:
            if period < 0 or shift < 0:
                raise ParameterError
            data = pd.read_csv(self.conf.get('common', 'test_data_path'))
            MA = pd.Series(data.rolling(period).mean()['Close'].shift(shift),
                           name='MA-' + str(period) + '-Shift-' + str(shift))
            data = data.join(MA)
            data.to_csv(self.conf.get('common', 'test_data_path'), index=None, float_format='%.5f')
            logging.info('Ma Calculate(Period=%d,Shift=%d) Done' % (period, shift))
        except (ConfigParser.NoSectionError, IOError, ParameterError), e:
            logging.error(e)
            raise

    def high_calculate(self, period=None, shift=None):
        try:
            if period < 0 or shift < 0:
                raise ParameterError
            data = pd.read_csv(self.conf.get('common', 'test_data_path'))
            HIGH = pd.Series(data.rolling(period).max()['High'].shift(shift),
                             name='High-' + str(period) + '-Shift-' + str(shift))
            data = data.join(HIGH)
            data.to_csv(self.conf.get('common', 'test_data_path'), index=None, float_format='%.5f')
            logging.info('High Calculate(Period=%d,Shift=%d) Done' % (period, shift))
        except (ConfigParser.NoSectionError, IOError, ParameterError), e:
            logging.error(e)
            raise

    def low_calculate(self, period=None, shift=None):
        try:
            if period < 0 or shift < 0:
                raise ParameterError
            data = pd.read_csv(self.conf.get('common', 'test_data_path'))
            LOW = pd.Series(data.rolling(period).min()['Low'].shift(shift),
                            name='Low-' + str(period) + '-Shift-' + str(shift))
            data = data.join(LOW)
            data.to_csv(self.conf.get('common', 'test_data_path'), index=None, float_format='%.5f')
            logging.info('Low Calculate(Period=%d,Shift=%d) Done' % (period, shift))
        except (ConfigParser.NoSectionError, IOError, ParameterError), e:
            logging.error(e)
            raise
