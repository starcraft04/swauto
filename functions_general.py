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
    
    calibrationFile = os.path.join('config','calibration.ini')
    calibrationConfig = SafeConfigParser()
    calibrationConfig.read(calibrationFile)
    
    allConfigs = {}
    
    allConfigs['runefarmingFoddersFiles'] = os.path.join('config','runefarming_fodders.ini')
    allConfigs['calibrationFiles'] = calibrationFile
    allConfigs['logFiles'] = logFile
 
    tolerance = dict(config.items('tolerance'))

    allConfigs['tolerance'] = tolerance

    wait_times = {}
    wait_times['image_wait'] = int(config.get('wait','image'))
    wait_times['max_wait_seconds'] = int(config.get('wait','max_wait_seconds'))
    wait_times['max_run_wait_seconds'] = int(config.get('wait','max_run_wait_seconds'))
    wait_times['screen_victory_wait'] = int(config.get('wait','victory'))
    wait_times['screen_networkDelayed_wait'] = int(config.get('wait','networkDelayed'))
    wait_times['screen_autorun_wait'] = int(config.get('wait','autorun'))
    wait_times['screen_revive_wait'] = int(config.get('wait','revive'))
    wait_times['screen_defeated_wait'] = int(config.get('wait','defeated'))
    wait_times['screen_replay_wait'] = int(config.get('wait','replay'))
    wait_times['screen_startBattle_wait'] = int(config.get('wait','startBattle'))
    wait_times['screen_notEnoughEnergy_wait'] = int(config.get('wait','notEnoughEnergy'))
    wait_times['screen_giftTOAHOH_wait'] = int(config.get('wait','giftTOAHOH'))
    wait_times['screen_giftCAIROSXP_wait'] = int(config.get('wait','giftCAIROSXP'))
    wait_times['screen_chest_wait'] = int(config.get('wait','chest'))
    wait_times['screen_nextstage_wait'] = int(config.get('wait','nextstage'))
    wait_times['screen_wait_random'] = int(config.get('wait','random'))
    wait_times['screen_not_enough_energy_buy_yes_wait'] = int(config.get('wait','not_enough_energy_buy_yes'))
    wait_times['screen_max_level_wait'] = int(config.get('wait','max_level'))
    wait_times['room_in_inventory'] = int(config.get('wait','room_in_inventory'))
    wait_times['long_press_time'] = int(config.get('wait','long_press_time'))
    wait_times['max_monster_info_screen'] = int(config.get('wait','max_monster_info_screen'))
    wait_times['get_monster_info_max_num_times'] = int(config.get('wait','get_monster_info_max_num_times')) 

    allConfigs['wait_times'] = wait_times
	
    directories = {}
    directories['basepicsdir'] = os.path.join(myPath,config.get('dir', 'basepics'))
    directories['debugdir'] = os.path.join(myPath,config.get('dir', 'debug'))
    directories['picsdir'] = os.path.join(myPath,config.get('dir', 'savedpics'))

    allConfigs['directories'] = directories

    calibration = {}
    calibration['fodder_right'] = fromStringToTuple(calibrationConfig.get('calibration', 'fodder_right'))
    calibration['fodder_bottom'] = fromStringToTuple(calibrationConfig.get('calibration', 'fodder_bottom'))
    calibration['fodder_left'] = fromStringToTuple(calibrationConfig.get('calibration', 'fodder_left'))
    calibration['level_top_left'] = fromStringToTuple(calibrationConfig.get('calibration', 'level_top_left'))
    calibration['level_bottom_right'] = fromStringToTuple(calibrationConfig.get('calibration', 'level_bottom_right'))
    calibration['scroll_left_first'] = fromStringToTuple(calibrationConfig.get('calibration', 'scroll_left_first'))
    calibration['scroll_left_last'] = fromStringToTuple(calibrationConfig.get('calibration', 'scroll_left_last'))
    calibration['numoffoddersinlist'] = int(calibrationConfig.get('calibration', 'numoffoddersinlist'))
    calibration['monster_icon_width'] = int(calibrationConfig.get('calibration', 'monster_icon_width'))
    calibration['error_correction'] = int(config.get('error_correction','monster_scroll'))
    for i in xrange(1,int(calibration['numoffoddersinlist'])+1):
        calibration['fodder_'+str(i)+'_center'] = fromStringToTuple(calibrationConfig.get('calibration', 'fodder_'+str(i)+'_center'))

    allConfigs['calibration'] = calibration

    resize = {}
    resize['resize_or_not'] = config.getboolean('resize','resize_or_not')
    resize['rapport'] = config.getfloat('resize','rapport')

    allConfigs['resize'] = resize
    
    position = {}
    position['system'] = str(config.get('position','system'))
    position['window'] = str(config.get('position','window'))
    position['window_name_1'] = str(config.get('position','window_name_1'))
    position['window_pos_x_1'] = int(config.get('position','window_pos_x_1'))
    position['window_pos_y_1'] = int(config.get('position','window_pos_y_1'))
    position['window_width_1'] = int(config.get('position','window_width_1'))
    position['window_height_1'] = int(config.get('position','window_height_1'))
    position['window_name_2'] = str(config.get('position','window_name_2'))
    position['window_pos_x_2'] = int(config.get('position','window_pos_x_2'))
    position['window_pos_y_2'] = int(config.get('position','window_pos_y_2'))
    position['window_width_2'] = int(config.get('position','window_width_2'))
    position['window_height_2'] = int(config.get('position','window_height_2'))
    position['window_start_x'] = int(config.get('position','window_start_x'))
    position['window_start_y'] = int(config.get('position','window_start_y'))
    position['window_end_x'] = int(config.get('position','window_end_x'))
    position['window_end_y'] = int(config.get('position','window_end_y'))
    position['pos_resize'] = str(config.get('position','pos_resize'))
    position['crop_window'] = str(config.get('position','crop_window'))
    
    allConfigs['position'] = position

    return tolerance, wait_times, directories, calibration, allConfigs

def main():
    print('function general')
    
if __name__ == "__main__":
    main()
