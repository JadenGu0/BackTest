# encoding=utf8
from EventEngine.EventEngine import Event
import ConfigParser
import pandas as pd
import logging

class DataHandle(object):
    """
    数据预处理类，用于讲数据按照开始和结束时间切片并返回
    """
    try:
        conf = ConfigParser.ConfigParser()
        conf.read('D:\Github\BackTest\config\\pattern.config')
        data = pd.read_csv(conf.get('common', 'data_path'))
    except ConfigParser.NoSectionError,e:
        logging.error(e)
        raise ConfigParser.NoSectionError

    def __init__(self):
        try:
            self.start = self.conf.get('common', 'start')
            self.end = self.conf.get('common', 'end')
        except ConfigParser.NoSectionError, e:
            logging.error(e)
            raise

    def SplitData(self):
        try:
            data = self.data[self.data['Time (UTC)'] >= self.start]
            data = data[data['Time (UTC)'] <= self.end].values
            return data
        except ValueError,e:
            logging.error(e)
            raise


class DataSliceHandle(object):
    """
    用来处理取到的数据切片
    """
    try:
        conf = ConfigParser.ConfigParser()
        conf.read('D:\Github\BackTest\config\\pattern.config')
    except ConfigParser.NoSectionError,e:
        logging.error(e)
        raise ConfigParser.NoSectionError

    def __init__(self, eventEngine, data=None):
        """
        构造函数，将数据切片中的数据存入不同的变量中并制定事件处理引擎
        :param eventEngine:
        :param type:
        :param data:
        :param magic:
        """
        try:
            self.__eventEngine = eventEngine
            self.__time = data[0]
            self.__open = data[1]
            self.__high = data[2]
            self.__low = data[3]
            self.__close = data[4]
            self.__volume = data[5]
            self.__magic = self.conf.get('common', 'magic')
        except (ConfigParser.NoSectionError,IOError), e:
            logging.error(e)
            raise

    def SendDataEvent(self, type):
        """
        将有新数据产生这一时间发送至事件处理引擎
        :return:
        """
        DataEvent = Event(type=type)
        data = {}
        data['time'] = self.__time
        data['open'] = self.__open
        data['high'] = self.__high
        data['low'] = self.__low
        data['close'] = self.__close
        data['volume'] = self.__volume
        DataEvent.dict['data'] = data
        DataEvent.dict['magic'] = self.__magic
        self.__eventEngine.SendEvent(DataEvent)
