import parsedatetime
from datetime import datetime

def parse_dt(datetime_str, sourceTime=None):
    '''
    Convert given human readable string into date time object
    Returns datetime object or None
    '''
    cal=parsedatetime.Calendar()
    if sourceTime is None:
        time_struct, parse_status = cal.parse(datetime_str)
    else:
        time_struct, parse_status = cal.parse(datetime_str, sourceTime=sourceTime)

    if parse_status == 0:
        print("Datetime " + datetime_str + " not parsed")
        return(None)

    return(datetime(*time_struct[:6]))


def parse_d(datetime_str, sourceTime=None):
    '''
    Convert given human readable string into date object
    Returns dateobject or None
    '''
    cal = parsedatetime.Calendar()
    if sourceTime is None:
        time_struct, parse_status = cal.parse(datetime_str)
    else:
        time_struct, parse_status = cal.parse(datetime_str, sourceTime=sourceTime)

    if parse_status == 0:
        print("Datetime " + datetime_str + " not parsed")
        return (None)

    return (datetime(*time_struct[:3]))


def get_epoch(date):
    '''
    Given datetime object, return POSIX timestamp in milliseconds (int)
    '''
    return int((date.timestamp()*1000)/1000)
    

