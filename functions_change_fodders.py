import pyautogui
import logging
import sys
import time
import cv2
import numpy as np
import copy
import os
from random import randint

import functions_opencv
import functions_screenshot
import functions_general
from ConfigParser import SafeConfigParser

def getMonsterInfo(tolerance,directories,coords,allConfigs):
    logging.info ('Clicking for %d seconds at coords: %s', allConfigs['wait_times']['long_press_time'], str(coords))
    max_num_times = allConfigs['wait_times']['get_monster_info_max_num_times']
    info_screen_found = False
    for i in xrange(0,int(max_num_times)):
        #Long press to get monster info
        functions_opencv.clickLongPress(coords,allConfigs['wait_times']['long_press_time'])
        waiting_for = ['close_monster_info.png']
        close_button = functions_opencv.waitForImg(waiting_for, tolerance, allConfigs['wait_times']['image'], allConfigs['wait_times']['max_monster_info_screen'],directories,allConfigs)
        if close_button['res']:
            info_screen_found = True
            break
    if not info_screen_found:
        print('Something went wrong with the analysis of the monster, stopping here')
        sys.exit(0)
    #Screenshot then take only the relevant part
    functions_general.randomWait( 1,0 )
    screenshot = functions_screenshot.screenshotOpencv(allConfigs)
    monster_info_location = functions_opencv.checkPicture(screenshot,'monster_info_location.png', tolerance ,directories,allConfigs)
    crop_info = (monster_info_location['points'][0]['top_left'],monster_info_location['points'][0]['bottom_right'])
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
    stars['grey'] = ['1','1','1','1','0','0']
    
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
                    maxFound = functions_opencv.checkPicture(screenshot_with_info,str(i)+'_stars_max.png', tolerance,directories,allConfigs,saveFound = False)
                    if maxFound['res']:
                        monster['max'] = True
                        logging.info ('-----------------> monster with %s %s stars is maxed', i, starColor)
                    else:
                        logging.info ('-----------------> monster with %s %s stars is not maxed', i, starColor)
    if monster['numOfStars'] == '':
        filename = time.strftime("%Y%m%d-%H%M%S")+'_monsterGetInfo_DEBUG.png'
        print('Couldn\'t find an image matching this monster\'s stars, saving to file %s then exit' % filename)
        cv2.imwrite(os.path.join(allConfigs['directories']['debugdir'] , filename), screenshot_with_info)
        sys.exit(0)
                        
    #Click x to leave window
    close_button_still_there = True
    while close_button_still_there:
        functions_opencv.clickAndReturnMouse(close_button)
        functions_general.randomWait( 1,0 )
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        close_button = functions_opencv.checkPicture(screenshot,'close_monster_info.png', tolerance,directories,allConfigs)
        if not close_button['res']:
            close_button_still_there = False
            break
    return monster

def swapMonsters(tolerance,directories,fodder_full,allConfigs):
    #Loading all configs
    #We read the config file
    configFile = allConfigs['runefarmingFoddersFiles']
    config = SafeConfigParser()
    config.read(configFile)

    max_num_of_fodders = {}
    max_num_of_fodders['max_num_of_scrolls'] = int(config.get('max_num_of_fodders_to_upgrade', 'max_num_of_scrolls'))
    max_num_of_fodders['scroll_init'] = int(config.get('max_num_of_fodders_to_upgrade', 'scroll_init'))
    max_num_of_fodders['6_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '6_stars'))
    max_num_of_fodders['5_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '5_stars'))
    max_num_of_fodders['4_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '4_stars'))
    max_num_of_fodders['3_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '3_stars'))
    max_num_of_fodders['2_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '2_stars'))
    max_num_of_fodders['1_stars'] = int(config.get('max_num_of_fodders_to_upgrade', '1_stars'))
    
    screenshot = functions_screenshot.screenshotOpencv(allConfigs)
    fodders_location_all_4_multi = functions_opencv.checkPicture(screenshot,'fodders_location.png', tolerance ,directories,allConfigs, multiple = True)
    fodders_location_all_4 = functions_opencv.find_min_max(fodders_location_all_4_multi,'x','min')
    halfHeight = (fodders_location_all_4['points'][0]['bottom_right'][1]-fodders_location_all_4['points'][0]['top_left'][1])/4
    halfWidth = (fodders_location_all_4['points'][0]['bottom_right'][0]-fodders_location_all_4['points'][0]['top_left'][0])/4

    fodder_right = (fodders_location_all_4['points'][0]['center'][0]+halfWidth,fodders_location_all_4['points'][0]['center'][1])
    fodder_bottom = (fodders_location_all_4['points'][0]['center'][0],fodders_location_all_4['points'][0]['center'][1]+halfHeight)
    fodder_left = (fodders_location_all_4['points'][0]['center'][0]-halfWidth,fodders_location_all_4['points'][0]['center'][1])
    
    if fodder_full < 3:
        monsters = {}
        #We remove the monsters that are max
        logging.info('-----------------> Analysing right monster...')   
        monsters['right'] = getMonsterInfo(tolerance,directories,fodder_right,allConfigs)
        logging.info('-----------------> Analysing left monster...')
        monsters['left'] = getMonsterInfo(tolerance,directories,fodder_left,allConfigs)
        logging.info('-----------------> Analysing bottom monster...')
        monsters['bottom'] = getMonsterInfo(tolerance,directories,fodder_bottom,allConfigs)


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

    else:
        numOfMaxMonsters = 3
        functions_opencv.clickAndReturnMouseCoords(fodder_right)
        functions_opencv.clickAndReturnMouseCoords(fodder_left)
        functions_opencv.clickAndReturnMouseCoords(fodder_bottom)

    logging.info('Passing already maxed monsters by scrolling %d times',max_num_of_fodders['scroll_init'])
    functions_opencv.scrollMonsterBarRightToLeft(max_num_of_fodders['scroll_init'],allConfigs,direction = 'left')
    
    logging.info('Looking for new monsters to be used and scroll maximum %d times',max_num_of_fodders['max_num_of_scrolls'])
    for s in xrange(0,max_num_of_fodders['max_num_of_scrolls']):
        i = 1
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        monster_list = functions_opencv.checkPicture(screenshot,'monster_select.png', allConfigs['tolerance'] ,allConfigs['directories'],allConfigs, multiple = True)
        #Now we check the different monsters in the list to verify if we can take them or not
        
        for monster in monster_list['points']:
            logging.info('-----------------> Analysing monster %d in the list',i)
            if numOfMaxMonsters == 0:
                break
            fodder = getMonsterInfo(tolerance,directories,monster['center'],allConfigs)
            fodder_num_of_stars = fodder['numOfStars']

            if not fodder['max'] and max_num_of_fodders[fodder_num_of_stars+'_stars'] > 0:
                functions_opencv.clickAndReturnMouseCoords(fodder['center'])
                max_num_of_fodders[fodder_num_of_stars+'_stars'] -= 1
                numOfMaxMonsters -= 1
            logging.info('From INI file: replace %d monsters with %d stars',int(max_num_of_fodders[fodder_num_of_stars+'_stars']),int(fodder_num_of_stars))
            i = i + 1
        if numOfMaxMonsters == 0:
            break
        else:
            functions_opencv.scrollMonsterBarRightToLeft(1,allConfigs,direction = 'left')
            max_num_of_fodders['scroll_init'] += 1

    if numOfMaxMonsters > 0:
        print('numOfMaxMonsters remaining: %d and fodder_full: %d' % (numOfMaxMonsters,fodder_full))
        sys.exit(0)

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

def main():
    print ('function change fodders')
        
if __name__ == "__main__":
    main()
