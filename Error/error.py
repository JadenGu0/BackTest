# encoding=utf8
class StartEndError(Exception):
    def __init__(self, err="起止时间错误"):
        Exception.__init__(self, err)


class PeriodError(Exception):
    def __init__(self, err="周期选取错误"):
        Exception.__init__(self, err)


class LotError(Exception):
    def __init__(self, err='下单手数错误'):
        Exception.__init__(self, err)


class OrderSendError(Exception):
    def __init__(self, err='下单参数错误'):
        Exception.__init__(self, err)


class OrderModifyError(Exception):
    def __init__(self, err='修改订单错误'):
        Exception.__init__(self, err)


class ParameterError(Exception):
    def __init__(self, err='参数错误'):
        Exception.__init__(self, err)


class DataError(Exception):
    def __init__(self, err=None):
        Exception.__init__(self, err)


class EventError(Exception):
    def __init__(self, err=None):
        Exception.__init__(self, err)


class TechError(Exception):
    def __init__(self, err=None):
        Exception.__init__(self, err)

