import datetime


def get_current_datetime_str():
    dt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    return dt
