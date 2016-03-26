import sys
import logging

import pyautogui
import functions_opencv
import functions_screenshot
from ConfigParser import SafeConfigParser

def coordsRelToPoint(origin,point):
    result = (origin[0] - point[0] , origin[1] - point[1])
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
        screenshot = functions_screenshot.screenshotOpencv()
        start_battle = functions_opencv.checkPicture(screenshot, 'start_battle.png', tolerance,directories,allConfigs)
        if start_battle['res']:
            foundStartBattle = True
            start_battle = (start_battle['points'][0]['center'][0],start_battle['points'][0]['center'][1])
            config.set('calibration', 'start_battle', str(start_battle))
            print ('Start battle center is at (%d,%d)' % (start_battle[0],start_battle[1]))
    
    print ('1) Position the cursor to the center of the right fodder')
    raw_input("Press Enter to continue...")
    fodder_right = pyautogui.position()
    fodder_right = coordsRelToPoint(start_battle,fodder_right)
    config.set('calibration', 'fodder_right', str(fodder_right))
    print ('2) Position the cursor to the center of the bottom fodder')
    raw_input("Press Enter to continue...")
    fodder_bottom = pyautogui.position()
    fodder_bottom = coordsRelToPoint(start_battle,fodder_bottom)
    config.set('calibration', 'fodder_bottom', str(fodder_bottom))
    print ('3) Position the cursor to the center of the left fodder')
    raw_input("Press Enter to continue...")
    fodder_left = pyautogui.position()
    fodder_left = coordsRelToPoint(start_battle,fodder_left)
    config.set('calibration', 'fodder_left', str(fodder_left))
    print ('4) Click for 2 seconds on your farmer monster')
    raw_input("Press Enter to continue...")
    print ('5) Position the cursor to the top left of the level and stars square')
    raw_input("Press Enter to continue...")
    level_top_left = pyautogui.position()
    level_top_left = coordsRelToPoint(start_battle,level_top_left)
    config.set('calibration', 'level_top_left', str(level_top_left))
    print ('6) Position the cursor to the bottom right of the level and stars square')
    raw_input("Press Enter to continue...")
    level_bottom_right = pyautogui.position()
    level_bottom_right = coordsRelToPoint(start_battle,level_bottom_right)
    config.set('calibration', 'level_bottom_right', str(level_bottom_right))
    
    print ('7) Position the cursor to the center of the x to close the window')
    raw_input("Press Enter to continue...")
    level_close = pyautogui.position()
    level_close = coordsRelToPoint(start_battle,level_close)
    config.set('calibration', 'level_close', str(level_close))
    
    print ('Now close the window')
    raw_input("Press Enter to continue...")
    
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
