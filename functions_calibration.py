import sys
import logging

import pyautogui
import functions_opencv
import functions_screenshot
from ConfigParser import SafeConfigParser

def coordsRelToPoint(origin,point):

    result = (int(origin[0]) - int(point[0]) , int(origin[1]) - int(point[1]))

    return result

def calibrate(configFile,tolerance,directories,allConfigs):
    #We read the config file
    config = SafeConfigParser()
    config.read(configFile)

    #We check if there is a section in the config file that already exists
    if not config.has_section('calibration'):
        config.add_section('calibration')
    else:
        config.remove_section('calibration')
        config.add_section('calibration')

    foundStartBattle = False
    while not foundStartBattle:
        print ('Go to a stage with the screen where you have to select monsters')
        raw_input("Press Enter to continue...")
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        start_battle = functions_opencv.checkPicture(screenshot, 'start_battle.png', tolerance,directories,allConfigs)
        if start_battle['res']:
            foundStartBattle = True
            start_battle = (start_battle['points'][0]['center'][0],start_battle['points'][0]['center'][1])
            config.set('calibration', 'start_battle', str(start_battle))
            print ('Start battle center is at (%d,%d)' % (start_battle[0],start_battle[1]))
    
    print ('8) Position the cursor to the most left side of the first monster in your select monster list')
    raw_input("Press Enter to continue...")
    scroll_left_first = pyautogui.position()
    scroll_left_first = coordsRelToPoint(start_battle,scroll_left_first)
    config.set('calibration', 'scroll_left_first', str(scroll_left_first))
    
    print ('9) Position the cursor to the most left side of the last monster in your select monster list')
    raw_input("Press Enter to continue...")
    scroll_left_last = pyautogui.position()
    scroll_left_last = coordsRelToPoint(start_battle,scroll_left_last)
    config.set('calibration', 'scroll_left_last', str(scroll_left_last))

    print ('--- Now we will measure the width of one icon in the monster list')
    print ('10) Position the cursor to the most left side of a monster in your select monster list')
    raw_input("Press Enter to continue...")
    monster_icon_left = pyautogui.position()
    
    print ('11) Position the cursor to the most right side of the same monster in your select monster list')
    raw_input("Press Enter to continue...")
    monster_icon_right = pyautogui.position()
    config.set('calibration', 'monster_icon_width', str(monster_icon_right[0] - monster_icon_left[0]))

    numOfFoddersInList = raw_input('12) Enter the number of fodders you have in the list:') 
    config.set('calibration', 'numOfFoddersInList', str(numOfFoddersInList))
    
    for i in xrange(1,int(numOfFoddersInList)+1):
        print ('***Position the cursor to the center of monster %d in your select monster list' % i)
        raw_input("Press Enter to continue...")
        fodder_center = pyautogui.position()
        fodder_center = coordsRelToPoint(start_battle,fodder_center)
        config.set('calibration', 'fodder_'+str(i)+'_center', str(fodder_center))

    #We finish by writing everything in the config file
    with open(configFile, 'wb') as f:
        config.write(f)
    return

def main():
    print ('function calibration')
    
if __name__ == "__main__":
    main()
