import datetime


def print_with_timestamp(*args, **kwargs):
    """
    用于在控制台打印日志，并添加时间戳
    :param args:
    :param kwargs:
    :return:
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(current_time, *args, **kwargs)