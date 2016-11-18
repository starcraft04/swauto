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
import functions_change_fodders
import rune_upgrade
import running
import win32gui
import re
import ctypes

def main():
    parser = argparse.ArgumentParser(description='This program will automate the farming')

    parser.add_argument('-nf','--no_change_fodders', help='This will tell the program not to change fodders and stop when all fodders are full', required=False, action='store_true')
    parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level")
    parser.add_argument('-r','--recharge', default='0' , help='This is the number of recharges you want', required=False)
    parser.add_argument('-n','--number_of_time', default='0' , help='This is the number of times you want the stage to be run', required=False)
    parser.add_argument('-t','--stage_type', choices=['cairos','essence','xp', 'toa','hoh'], help='This is the stage that you want to automate.', required=False)
    parser.add_argument('-tst','--test', nargs=1, help='Just give the name of the picture to be tested through the screenshot', required=False)
    parser.add_argument('-lc','--log_console', help='This will log to console', required=False, action='store_true')
    parser.add_argument('-w','--windows', help='This will, under Windows environment, give you all the windows that are present for you to configure the ini file', required=False, action='store_true')
    parser.add_argument('-sm','--swap_monsters', nargs=1, help='This will swap the monsters that are max, you have to enter the number of fodders that are full for consistency test', required=False)
    parser.add_argument('-ru','--rune_upgrade', nargs=1, help='This will upgrade the runes n times', required=False)
    parser.add_argument('-ws','--workspace', help='This will show you the workspace by showing you a printscreen of the area', required=False, action='store_true')
    parser.add_argument('-c','--calibration', help='This will, under Windows environment, help you to calibrate the screen to the right size', required=False, action='store_true')
    tolerance, wait_times, directories, allConfigs = functions_general.initConfigs()

    args = parser.parse_args()
    logginFormat = '%(asctime)s [%(levelname)s][%(funcName)s]: %(message)s'

    if args.logLevel:
        if args.log_console:
            logging.basicConfig(level=args.logLevel,
                            datefmt='%Y/%m/%d %H:%M:%S',
                            format=logginFormat)
        else:
            logging.basicConfig(filename=allConfigs['logFiles'],
                            level=args.logLevel,
                            datefmt='%y%m%d %H:%M:%S',
                            format=logginFormat)
            
    if args.calibration:
        functions_general.calibrate(tolerance, directories,allConfigs)
        sys.exit(0)

    if args.windows:
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible

        titles = []
        
        def foreach_window(hwnd, lParam):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                titles.append(buff.value)
            return True
        
        EnumWindows(EnumWindowsProc(foreach_window), 0)
        
        print("Here are all the windows I found")
        print(titles)
        sys.exit(0)
        
    if allConfigs['position']['pos_resize'] == 'yes':
        #Before Starting, make sure to use wmctrl -r Vysor -e 1,0,0,800,-1
        #The window size should be 800 x 450
        #This is to ensure we have always the same siz and that pixels won't be off
        #We read the config file
        if allConfigs['position']['system'] == 'linux':
            os.system('wmctrl -r '+allConfigs['position']['window_name_1']+' -e 1,'+str(allConfigs['position']['window_pos_x_1'])+','+str(allConfigs['position']['window_pos_y_1'])+','+str(allConfigs['position']['window_width_1'])+',-1')
            #Now we make sure the window is active and in front on the desktop
            os.system('wmctrl -a '+allConfigs['position']['window_name'])
        if allConfigs['position']['system'] == 'windows':
            functions_general.windowResizeAndPosition(args.workspace,allConfigs)
 
        time.sleep(1)

    if args.workspace:
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        cv2.imshow('showFound',screenshot)
        cv2.waitKey(0)
        sys.exit(0)

    if args.test:
        functions_general.imageTest(args.test[0],tolerance, directories,allConfigs)
        sys.exit(0)
        
    if args.swap_monsters:
        functions_change_fodders.swapMonsters(tolerance,directories,int(args.swap_monsters[0]),allConfigs)
        sys.exit(0)    

    if args.rune_upgrade:
        rune_upgrade.rune_upgrade(tolerance,directories,int(args.rune_upgrade[0]),allConfigs, wait_times)
        sys.exit(0)

    if args.stage_type:
        running.running(args.stage_type,args.no_change_fodders,int(args.recharge),int(args.number_of_time),tolerance, wait_times, directories,allConfigs)
    else:
        print ('You must select a stage type and a stage name, help for more info')

if __name__ == "__main__":
    main()

