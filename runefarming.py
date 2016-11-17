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

def main():
    parser = argparse.ArgumentParser(description='This program will automate the farming')

    parser.add_argument('-nf','--no_change_fodders', help='This will tell the program not to change fodders and stop when all fodders are full', required=False, action='store_true')
    parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level")
    parser.add_argument('-r','--recharge', default='0' , help='This is the number of recharges you want', required=False)
    parser.add_argument('-n','--number_of_time', default='0' , help='This is the number of times you want the stage to be run', required=False)
    parser.add_argument('-t','--stage_type', choices=['cairos','essence','xp', 'toa','hoh'], help='This is the stage that you want to automate.', required=False)
    parser.add_argument('-tst','--test', nargs=1, help='Just give the name of the picture to be tested through the screenshot', required=False)
    parser.add_argument('-lc','--log_console', help='This will log to console', required=False, action='store_true')
    parser.add_argument('-sm','--swap_monsters', nargs=1, help='This will swap the monsters that are max, you have to enter the number of fodders that are full for consistency test', required=False)
    parser.add_argument('-ru','--rune_upgrade', nargs=1, help='This will upgrade the runes n times', required=False)
    parser.add_argument('-ws','--workspace', help='This will show you the workspace by showing you a printscreen of the area', required=False, action='store_true')

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
            import win32gui
            import re
            import ctypes

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
            if args.workspace:
                print("Here are all the windows I found")
                print(titles)
            
            class WindowMgr:
                """Encapsulates some calls to the winapi for window management"""
                def __init__ (self):
                    """Constructor"""
                    self._handle = None

                def find_window(self, class_name, window_name = None):
                    """find a window by its class_name"""
                    self._handle = win32gui.FindWindow(class_name, window_name)

                def _window_enum_callback(self, hwnd, wildcard):
                    '''Pass to win32gui.EnumWindows() to check all the opened windows'''
                    if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) != None:
                        self._handle = hwnd

                def find_window_wildcard(self, wildcard):
                    self._handle = None
                    win32gui.EnumWindows(self._window_enum_callback, wildcard)

                def set_foreground(self):
                    """put the window in the foreground"""
                    win32gui.SetForegroundWindow(self._handle)

                def move_window(self,allConfigs,i):
                    """put the window in the foreground"""
                    rect = win32gui.GetWindowRect(self._handle)
                    x = rect[0]
                    y = rect[1]
                    orig_width = rect[2] - x
                    orig_height = rect[3] - y
                    new_width = allConfigs['position']['window_width_'+i]
                    if allConfigs['position']['calculated_height'] == 'yes':
                        rapport = float(new_width)/float(orig_width)
                        new_height = int(rapport*orig_height)
                    else:
                        new_height = allConfigs['position']['window_height_'+i]
                    logging.info("Orig width: %d - Orig height: %d",orig_width,orig_height)
                    logging.info("New width: %d - New height: %d",new_width,new_height)
                    win32gui.MoveWindow(self._handle, allConfigs['position']['window_pos_x_'+i], allConfigs['position']['window_pos_y_'+i], new_width, new_height, True)

            i = str(allConfigs['position']['window'])
            w = WindowMgr()
            w.find_window_wildcard(".*"+allConfigs['position']['window_name_'+i]+".*")
            w.set_foreground()
            w.move_window(allConfigs,i)

        time.sleep(1)

    if args.workspace:
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        cv2.imshow('showFound',screenshot)
        cv2.waitKey(0)
        sys.exit(0) 

    if args.test:
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        result = functions_opencv.checkPicture(screenshot,args.test[0], tolerance, directories,allConfigs, multiple = True, showFound = True)
        if not result['res']:
            if args.test[0][:-4] in tolerance:
                tolerance = float(tolerance[args.test[0][:-4]])
            else:
                tolerance = float(tolerance['global'])
            print ('Tolerance for file %s is: %f' % (args.test[0],tolerance))
            print ('Best tolerance found is: %f' % (result['best_val']))
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

