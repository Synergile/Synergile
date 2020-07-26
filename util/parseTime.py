import re
from .pyutil import isNaN

READABLE_TIME_FORMAT_REG = re.compile('[^-\dymwdhms.]')
YEAR_REG = re.compile('(-?\d+(?:\.\d+))y')
WEEK_REG = re.compile('(-?\d+(?:\.\d+))w')
DAY_REG = re.compile('(-?\d+(?:\.\d+))d')
HOUR_REG = re.compile('(-?\d+(?:\.\d+))h')
MIN_REG = re.compile('(-?\d+(?:\.\d+))m(?!s)')
SEC_REG = re.compile('(-?\d+(?:\.\d+))s')
MS_REG = re.compile('(-?\d+(?:\.\d+))ms')

def parseTime(timeToParse):
    if(isNaN(timeToParse)):
        timeString = timeToParse
        if(READABLE_TIME_FORMAT_REG.search(timeString)):
            raise TypeError('invalid time formatting')
        else:
        match = None
        years = 0
        weeks = 0
        days = 0
        hours = 0
        minutes = 0
        seconds = 0
        milliseconds = 0
        match = YEAR_REG.match(timeString)
        if(match is not None):
            years = double(match)
        match = None
        match = WEEK_REG.match(timeString)
        if(match is not None):
            weeks = double(match)
        match = None
        match = DAY_REG.match(timeString)
        if(match is not None):
            days = double(match)
        match = None
        match = HOUR_REG.match(timeString)
        if(match is not None):
            hours = double(match)
        match = None
        match = MIN_REG.match(timeString)
        if(match is not None):
            minutes = double(match)
        match = None
        match = SEC_REG.match(timeString)
        if(match is not None):
            seconds = double(match)
        match = None
        match = MS_REG.match(timeString)
        if(match is not None):
            milliseconds = double(match)
        days += 365*years
        days += 7*weeks
        hours += 24*days
        minutes += hours*60
        seconds += minutes*60
        milliseconds += seconds*1000
        timeValue = double(milliseconds)/1000
    else:
        timeValue = timeToParse
    return timeValue