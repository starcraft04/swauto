import pyautogui
import logging
import sys
import time
import cv2
import numpy as np

import functions_opencv
import functions_screenshot
import functions_calibration
import functions_general
from ConfigParser import SafeConfigParser

def getMonsterInfo(tolerance,directories,calibration,coords,allConfigs):
    logging.info ('Clicking for %d seconds at coords: %s', allConfigs['wait_times']['long_press_time'], str(coords))
    max_num_times = allConfigs['wait_times']['get_monster_info_max_num_times']
    info_screen_found = False
    for i in xrange(0,int(max_num_times)):
        #Long press to get monster info
        functions_opencv.clickLongPress(coords,allConfigs['wait_times']['long_press_time'])
        waiting_for = ['close_monster_info.png']
        close_button = functions_opencv.waitForImg(waiting_for, tolerance, allConfigs['wait_times']['image_wait'], allConfigs['wait_times']['max_monster_info_screen'],directories,allConfigs)
        if close_button['res']:
            info_screen_found = True
            break
    if not info_screen_found:
        print('Something went wrong with the analysis of the monster, stopping here')
        sys.exit(0)
    #Screenshot then take only the relevant part
    screenshot = functions_screenshot.screenshotOpencv()
    crop_info = (calibration['level_top_left'],calibration['level_bottom_right'])
    screenshot_with_info = functions_opencv.cropToCoords(screenshot,crop_info)

    #Preparing the monster
    monster = {}
    monster['center'] = coords
    monster['max'] = False
    monster['numOfStars'] = ''
    monster['starColor'] = ''

    stars = {}
    stars['yellow'] = ['1','1','1','1','1','1']
    stars['pink'] = ['1','1','1','1','1','1']
    stars['grey'] = ['1','1','1','0','0','0']
    
    for starColor,starValue in stars.iteritems():
        if monster['numOfStars'] != '':
            break            
        for i in xrange(6,0,-1):
            if monster['numOfStars'] != '':
                break
            if starValue[i-1] != '0':
                starFound = functions_opencv.checkPicture(screenshot_with_info,str(i)+'_stars_'+starColor+'.png', tolerance,directories,allConfigs)
                if starFound['res']:
                    monster['numOfStars'] = str(i)
                    monster['starColor'] = starColor
                    maxFound = functions_opencv.checkPicture(screenshot_with_info,str(i)+'_stars_max.png', tolerance,directories,allConfigs)
                    if maxFound['res']:
                        monster['max'] = True
                        logging.info ('monster with %s %s stars is maxed', i, starColor)
                    else:
                        logging.info ('monster with %s %s stars is not maxed', i, starColor)

    #Click x to leave window
    functions_opencv.clickAndReturnMouse(close_button)
    return monster

def initCoordsRelToStartBattle(tolerance,directories,calibration,allConfigs):
    #Find the start_battle
    screenshot = functions_screenshot.screenshotOpencv()
    start_battle = functions_opencv.checkPicture(screenshot,'start_battle.png', tolerance,directories,allConfigs)
    if start_battle['res']:
        start_battle_center = (int(start_battle['points'][0]['center'][0]),int(start_battle['points'][0]['center'][1]))

        new_calibration = calibration.copy()
        
        new_calibration['fodder_right'] = functions_calibration.coordsRelToPoint(start_battle_center,calibration['fodder_right'])
        new_calibration['fodder_bottom'] = functions_calibration.coordsRelToPoint(start_battle_center,calibration['fodder_bottom'])
        new_calibration['fodder_left'] = functions_calibration.coordsRelToPoint(start_battle_center,calibration['fodder_left'])
        new_calibration['level_top_left'] = functions_calibration.coordsRelToPoint(start_battle_center,calibration['level_top_left'])
        new_calibration['level_bottom_right'] = functions_calibration.coordsRelToPoint(start_battle_center,calibration['level_bottom_right'])
        new_calibration['scroll_left_first'] = functions_calibration.coordsRelToPoint(start_battle_center,calibration['scroll_left_first'])
        new_calibration['scroll_left_last'] = functions_calibration.coordsRelToPoint(start_battle_center,calibration['scroll_left_last'])
                
        for i in xrange(1,int(calibration['numoffoddersinlist'])+1):
            new_calibration['fodder_'+str(i)+'_center'] = functions_calibration.coordsRelToPoint(start_battle_center,calibration['fodder_'+str(i)+'_center'])

        return new_calibration
    else:
        print('Could not find the start battle, stopping here')
        sys.exit(0)
        return False

def swapMonsters(tolerance,directories,calibration,fodder_full,allConfigs):
    #Loading all configs
    #We read the config file
    configFile = allConfigs['runefarmingFoddersFiles']
    config = SafeConfigParser()
    config.read(configFile)

    #We need to get absolute positions and not relative to start battle
    calibration_from_start = initCoordsRelToStartBattle(tolerance,directories,calibration,allConfigs)

    max_num_of_fodders = {}
    max_num_of_fodders['max_num_of_fodders'] = int(config.get('max_num_of_fodders_to_upgrade', 'max_num_of_fodders'))
    max_num_of_fodders['scroll_init'] = int(config.get('max_num_of_fodders_to_upgrade', 'scroll_init'))
    max_num_of_fodders['6_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '6_stars'))
    max_num_of_fodders['5_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '5_stars'))
    max_num_of_fodders['4_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '4_stars'))
    max_num_of_fodders['3_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '3_stars'))
    max_num_of_fodders['2_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '2_stars'))
    max_num_of_fodders['1_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '1_stars'))

    #We remove the monsters that are max
    monsters = {}
    logging.info('Analysing right monster...')
    
    monsters['right'] = getMonsterInfo(tolerance,directories,calibration_from_start,calibration_from_start['fodder_right'],allConfigs)
    monsters['left'] = getMonsterInfo(tolerance,directories,calibration_from_start,calibration_from_start['fodder_left'],allConfigs)
    logging.info('Analysing left monster...')
    monsters['bottom'] = getMonsterInfo(tolerance,directories,calibration_from_start,calibration_from_start['fodder_bottom'],allConfigs)
    logging.info('Analysing bottom monster...')

    numOfMaxMonsters = 0
    for name,monster in monsters.iteritems():
        if monster['max']:
            numOfMaxMonsters += 1
    #Now we need to make sure that we have the same amount of max monsters with the victory screen
    if not (numOfMaxMonsters == fodder_full):
        print('numOfMaxMonsters: %d and fodder_full: %d' % (numOfMaxMonsters,fodder_full))
        print('Not the same so stopping here')
        sys.exit(0)
    else:
        logging.info('Consistency checked, max monsters')
        logging.info('--from victory screen: %d',fodder_full)
        logging.info('--from this screen: %d',numOfMaxMonsters)
        
    #Now we deselect the monsters that are max
    for name,monster in monsters.iteritems():
        if monster['max']:
            functions_opencv.clickAndReturnMouseCoords(monster['center'])

    logging.info('Passing already maxed monsters by scrolling %d times',max_num_of_fodders['scroll_init'])
    functions_opencv.scrollMonsterBarRightToLeft(max_num_of_fodders['scroll_init'],calibration_from_start,direction = 'left')

    num_of_scroll = (max_num_of_fodders['max_num_of_fodders'] // calibration_from_start['numoffoddersinlist']) - max_num_of_fodders['scroll_init']
    
    logging.info('Looking for new monsters to be used and scroll maximum %d times',num_of_scroll)
    for s in xrange(0,num_of_scroll):      
        screenshot = functions_screenshot.screenshotOpencv()
        #Now we check the different monsters in the list to verify if we can take them or not
        for i in xrange(1,int(calibration_from_start['numoffoddersinlist'])+1):
            if numOfMaxMonsters == 0:
                break
            fodder = getMonsterInfo(tolerance,directories,calibration_from_start,calibration_from_start['fodder_'+str(i)+'_center'],allConfigs)
            #Now we need to verify that the monster is not already selected
            has_a_v = checkForV(tolerance,directories,calibration_from_start,screenshot,fodder['center'],allConfigs)
            if has_a_v:
                logging.info('This monster is already selected')
                continue
            fodder_num_of_stars = fodder['numOfStars']
            if not fodder['max'] and max_num_of_fodders[fodder_num_of_stars+'_stars'] > 0:
                functions_opencv.clickAndReturnMouseCoords(fodder['center'])
                max_num_of_fodders[fodder_num_of_stars+'_stars'] -= 1
                numOfMaxMonsters -= 1
            logging.info('From INI file: replace %d monsters with %d stars',int(max_num_of_fodders[fodder_num_of_stars+'_stars']),int(fodder_num_of_stars))
        if numOfMaxMonsters == 0:
            break
        else:
            functions_opencv.scrollMonsterBarRightToLeft(1,calibration_from_start,direction = 'left')
            max_num_of_fodders['scroll_init'] += 1

    config.set('max_num_of_fodders_to_upgrade', 'scroll_init', str(max_num_of_fodders['scroll_init']))
    config.set('max_num_of_fodders_to_upgrade', '6_stars', str(max_num_of_fodders['6_stars']))
    config.set('max_num_of_fodders_to_upgrade', '5_stars', str(max_num_of_fodders['5_stars']))
    config.set('max_num_of_fodders_to_upgrade', '4_stars', str(max_num_of_fodders['4_stars']))
    config.set('max_num_of_fodders_to_upgrade', '3_stars', str(max_num_of_fodders['3_stars']))
    config.set('max_num_of_fodders_to_upgrade', '2_stars', str(max_num_of_fodders['2_stars']))
    config.set('max_num_of_fodders_to_upgrade', '1_stars', str(max_num_of_fodders['1_stars']))

    #We finish by writing everything in the config file
    with open(configFile, 'wb') as f:
        config.write(f)

    return True

def checkForV(tolerance,directories,calibration,screenshot,coords,allConfigs):
    width = int(calibration['monster_icon_width']*0.7)
    heigth = calibration['monster_icon_width']
    square_top_left = (coords[0]-width,coords[1]-heigth)
    square_bottom_right = (coords[0]+width,coords[1])
    crop_info = (square_top_left,square_bottom_right)
    screenshot_with_info = functions_opencv.cropToCoords(screenshot,crop_info)
    has_a_v = functions_opencv.checkPicture(screenshot_with_info,'monsters_list_v.png', tolerance,directories,allConfigs)
    return has_a_v['res']

def main():
    print ('function change fodders')
        
if __name__ == "__main__":
    main()