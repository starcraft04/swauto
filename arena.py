import sys
import os
import argparse
import logging
import time
import pyautogui
import cv2

import functions_opencv
import functions_screenshot
import functions_general

def arena(tolerance,directories,allConfigs,wait_times):
    for i in xrange (0,3):
        print 'scroll:%i' % i
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        away = functions_opencv.checkPicture(screenshot,'arena_away.png', tolerance ,directories,allConfigs,multiple = True, showFound = False)
        battle = functions_opencv.checkPicture(screenshot,'arena_battle.png', tolerance ,directories,allConfigs,multiple = True, showFound = False)
        win = functions_opencv.checkPicture(screenshot,'arena_win.png', tolerance ,directories,allConfigs,multiple = True, showFound = False)
        all_squares = []
        if away['res']:
            all_squares.append(away)
        if battle['res']:
            all_squares.append(battle)
        if win['res']:
            all_squares.append(win)

        max_point = functions_opencv.find_min_max(all_squares,'y','max')
        min_point = functions_opencv.find_min_max(all_squares,'y','min')
        
        if battle['res']:
            for b in battle['points']:
                print b
                functions_general.randomWait( 2,0 )
                functions_opencv.clickAndReturnMouse_point(b)
                
                running = True
                while running:
                    functions_general.randomWait( 3,0 )
                    waiting_for = ['start_battle.png','arena_place.png','autorun.png','defeated.png','network_delayed.png','victory.png','arena_center.png','arena_center_finished.png']
                    running_result = functions_opencv.waitForImg(waiting_for, tolerance, wait_times['image'], wait_times['max_run_wait_seconds'],directories,allConfigs)

                    if running_result['name'] == 'arena_place.png':
                        break
                    if running_result['res']:
                        functions_opencv.clickAndReturnMouse(running_result)
                        
        orig_x,orig_y = pyautogui.position()                
        pyautogui.moveTo(max_point['center'][0],max_point['center'][1])
        pyautogui.dragTo(min_point['center'][0],min_point['center'][1],1)
        pyautogui.moveTo(orig_x, orig_y)
        functions_general.randomWait( 3,0 )
    return         

def main():
    print('arena')
    
if __name__ == "__main__":
    main()

