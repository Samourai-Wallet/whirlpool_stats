'''
Copyright (c) 2019 Katana Cryptographic Ltd. All Rights Reserved.

A set of functions to manipulate datetimes and timestamps
'''
import calendar
from datetime import datetime


def to_utcdate(timestamp): 
  '''
  Converts a unix timestamp to an utc datetime
  Returns the utc datetime
  Parameters:
    timestamp = unix timestamp        
  '''
  return datetime.utcfromtimestamp(timestamp)


def to_timestamp(date): 
  '''
  Converts an utc datetime to a unix timestamp
  Returns the unix timestamp
  Parameters:
    date = utc datetime        
  '''
  return calendar.timegm(date.timetuple())


def get_timestamp_of_day(timestamp):
  '''
  Computes the timestamp corresponding to the same day 
  as the given parameter but at 0h00
  Returns the computed timestamp
  Parameters:
    timestamp = unix timestamp        
  '''
  tmp = to_utcdate(timestamp)
  return to_timestamp(datetime(tmp.year, tmp.month, tmp.day, 0, 0, 0, 0))


def get_datetime_of_day(timestamp):
  '''
  Computes the datetime corresponding to the same day 
  as the given parameter but at 0h00
  Returns the computed datetime
  Parameters:
    timestamp = unix timestamp        
  '''
  tmp = to_utcdate(timestamp)
  return datetime(tmp.year, tmp.month, tmp.day, 0, 0, 0, 0)

