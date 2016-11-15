import time
import logging
import sys
import os
from random import randint
from ConfigParser import SafeConfigParser

def randomWait(wait_time, random_wait):
    wait_time = wait_time + randint(0,random_wait)
    time.sleep(wait_time)
    
def fromStringToTuple(string):
    string = string.replace(' ', '')
    string = string.replace('(', '')
    string = string.replace(')', '')
    string = string.split(',')
    coords = (int(string[0]),int(string[1]))
    return coords

def dictStringToInt(d):
    for key, value in d.iteritems():
        try:
            d[key] = int(value)
        except ValueError:
            d[key] = str(value)
    return d

def initConfigs():
    
    #Getting the path to the program
    if getattr(sys, 'frozen', False):
	    # frozen
	    myPath = os.path.dirname(sys.executable)
    else:
        # unfrozen
        myPath = os.path.dirname(os.path.realpath(__file__))
        
    #Let's check we have the empty directory debug in case we need it
    try:
        os.makedirs('debug')
    except OSError:
        if os.path.exists('debug'):
            # We are nearly safe
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise
    #Now we check the log file exists
    logFile = os.path.join('debug','runefarming.log')
    file = open(logFile, 'w')
    
    #Loading all configs
    #We read the config file
    configFile = os.path.join('config','runefarming.ini')
    config = SafeConfigParser()
    config.read(configFile)
    
    allConfigs = {}
    
    allConfigs['runefarmingFoddersFiles'] = os.path.join('config','runefarming_fodders.ini')
    allConfigs['logFiles'] = logFile
 
    tolerance = dict(config.items('tolerance'))

    allConfigs['tolerance'] = tolerance

    wait_times_string = dict(config.items('wait'))
    wait_times = dictStringToInt(wait_times_string)
    
    allConfigs['wait_times'] = wait_times
	
    directories = {}
    directories['basepicsdir'] = os.path.join(myPath,config.get('dir', 'basepics'))
    directories['debugdir'] = os.path.join(myPath,config.get('dir', 'debug'))
    directories['picsdir'] = os.path.join(myPath,config.get('dir', 'savedpics'))

    allConfigs['directories'] = directories

    resize = {}
    resize['resize_or_not'] = config.getboolean('resize','resize_or_not')
    resize['rapport'] = config.getfloat('resize','rapport')

    allConfigs['resize'] = resize
    
    position_string = dict(config.items('position'))
    position = dictStringToInt(position_string)
    
    allConfigs['position'] = position
    
    error_correction = {}
    error_correction['monster_scroll'] = int(config.get('error_correction','monster_scroll'))
    allConfigs['error_correction'] = error_correction

    return tolerance, wait_times, directories, allConfigs

def main():
    print('function general')
    
if __name__ == "__main__":
    main()
