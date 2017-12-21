# encoding=utf8
import ConfigParser
import pandas as pd
import logging
from Error.error import ParameterError

class Indicator(object):
    try:
        conf = ConfigParser.ConfigParser()
        conf.read('D:\Github\BackTest\config\\pattern.config')
        data = pd.read_csv(conf.get('common', 'test_data_path'))
    except (ConfigParser.NoSectionError, IOError), e:
        logging.error(e)
        raise

    def __init__(self, period=None, shift=None, time=None):
        try:
            if period<0 or shift<= 0:
                raise ParameterError
            self.__period = period
            self.__shift = shift
            self.__time = time
            if period is None and shift != 0:
                self.bardata = self.data[self.data['Time (UTC)'] < time][-self.__shift:]
        except ParameterError,e:
            logging.error(e)
            raise

class Ma(Indicator):
    def __init__(self, period=None, shift=None, time=None):
        Indicator.__init__(self, period, shift, time)
        self.__name = 'MA-' + str(period) + '-Shift-' + str(shift)
        self.time = time

    def get_Ma(self):
        return self.data[self.data['Time (UTC)'] == self.time][self.__name].values[0]


class High(Indicator):
    def __init__(self, period=None, shift=None, time=None):
        Indicator.__init__(self, period, shift, time)
        self.__name = 'High-' + str(period) + '-Shift-' + str(shift)
        self.time = time

    def get_High(self):
        return self.data[self.data['Time (UTC)'] == self.time][self.__name].values[0]


class Low(Indicator):
    def __init__(self, period=None, shift=None, time=None):
        Indicator.__init__(self, period, shift, time)
        self.__name = 'Low-' + str(period) + '-Shift-' + str(shift)
        self.time = time

    def get_Low(self):
        return self.data[self.data['Time (UTC)'] == self.time][self.__name].values[0]


class BarInfo(Indicator):
    def __init__(self, period=None, shift=None, time=None):
        Indicator.__init__(self, period, shift, time)

    def get_barinfo(self):
        res = dict(
            open=self.bardata['Open'].values[0],
            high=self.bardata['High'].values[0],
            close=self.bardata['Close'].values[0],
            low=self.bardata['Low'].values[0],
            time=self.bardata['Time (UTC)'].values[0]
        )
        return res
