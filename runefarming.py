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
import arena

def running(stage_type,noChangeFodders,numOfRecharge,number_of_time, tolerance, wait_times, directories,allConfigs):
    #Init
    numOf = {}
    numOf['victory'] = 0
    numOf['defeat'] = 0
    numOf['recharge'] = numOfRecharge
    numOf['Time'] = 0
    endLoop = False
    #Looping
    while not endLoop:
        numOf['Time'] += 1
        numOf['fodder_full'] = 0
        startTime = time.time()
        if number_of_time > 0 and numOf['Time'] == number_of_time + 1:
            break

        victory_found = False
        defeated_found = False
        running = True
        
        if number_of_time > 0:
            print ('Run number: %d/%d' % (numOf['Time'],int(number_of_time)))
        else:
            print ('Run number: %d' % (numOf['Time']))
        
        while running:

            waiting_for = ['start_battle.png','autorun.png','not_enough_energy.png','next_stage.png','replay.png','defeated.png','revive.png','network_connection_delayed.png','network_delayed.png','unstable.png','victory.png','stage_clear.png']

            running_result = functions_opencv.waitForImg(waiting_for, tolerance, wait_times['image'], wait_times['max_run_wait_seconds'],directories,allConfigs)

            #Check first if we had an issue crash or network delayed
            #NETWORK DELAYED
            if running_result['res'] and (running_result['name'] == 'network_delayed.png' or running_result['name'] == 'unstable.png' or running_result['name'] == 'network_connection_delayed.png'):
                wait_time = wait_times['networkDelayed']
                random_wait = wait_times['random']
                screenshot = functions_screenshot.screenshotOpencv(allConfigs)
                network_delayed_yes = functions_opencv.checkPicture(screenshot,'network_delayed_yes.png', tolerance ,directories,allConfigs)
                functions_opencv.clickAndReturnMouse(network_delayed_yes)
                #Wait a little bit for the network to stabilise
                functions_general.randomWait( wait_time,random_wait ) 
                continue
            
            #START BATTLE
            elif running_result['res'] and running_result['name'] == 'start_battle.png':
                wait_time = wait_times['startBattle']
                random_wait = wait_times['random']
                if noChangeFodders and numOf['fodder_full'] > 0:
                    logging.info('Number of fodders full: %s - Change fodders: %s',str(numOf['fodder_full']-1),str(not noChangeFodders))
                    sys.exit(0)
                if numOf['fodder_full'] > 0:
                    logging.info('-----------------> Changing %d fodders because they are max',numOf['fodder_full'])
                    result = functions_change_fodders.swapMonsters(tolerance,directories,numOf['fodder_full'],allConfigs)

                functions_general.randomWait( 1,1 )
                functions_opencv.clickAndReturnMouse(running_result)
                functions_general.randomWait( wait_time,random_wait )
                #ROOM IN INVENTORY
                screenshot = functions_screenshot.screenshotOpencv(allConfigs)
                result = functions_opencv.checkPicture(screenshot,'room_in_inventory.png', tolerance, directories,allConfigs)
                if result['res']:
                    wait_time = wait_times['room_in_inventory']
                    random_wait = wait_times['random']
                    screenshot = functions_screenshot.screenshotOpencv(allConfigs)
                    if stage_type == 'cairos':
                        room_in_inventory_no = functions_opencv.checkPicture(screenshot,'room_in_inventory_no.png', tolerance ,directories,allConfigs)
                        functions_opencv.clickAndReturnMouse(room_in_inventory_no)
                        #Wait a little bit for the network to stabilise
                        functions_general.randomWait( wait_time,random_wait )
                        room_in_inventory = False
                    else:
                        room_in_inventory_yes = functions_opencv.checkPicture(screenshot,'room_in_inventory_yes.png', tolerance ,directories,allConfigs)
                        functions_opencv.clickAndReturnMouse(room_in_inventory_yes)
                        #Wait a little bit for the network to stabilise
                        functions_general.randomWait( wait_time,random_wait )
                        room_in_inventory = True
                    #In case we do cairos, we have to stop if we don't have place in the inventory
                    #But if we do another stage, we can ignore this because we sell the rune anywway
                    if not room_in_inventory:
                        logging.info('No place left in the inventory to get new runes, stopping here')
                        sys.exit(0)
                        
                if victory_found or defeated_found:
                    running = False

                
            #Revive - coming from Hall of
            elif running_result['res'] and running_result['name'] == 'revive.png':
                wait_time = wait_times['revive']
                random_wait = wait_times['random']
                screenshot = functions_screenshot.screenshotOpencv(allConfigs)
                revive_no = functions_opencv.checkPicture(screenshot,'revive_no.png', tolerance ,directories,allConfigs)
                functions_opencv.clickAndReturnMouse(revive_no)
                functions_general.randomWait( wait_time,random_wait )

            #Next stage - coming from ToA
            elif running_result['res'] and running_result['name'] == 'next_stage.png':
                wait_time = wait_times['defeated']
                random_wait = wait_times['random']
                functions_opencv.clickAndReturnMouse(running_result)
                functions_general.randomWait( wait_time,random_wait ) 
                                   
            #Defeated
            elif running_result['res'] and running_result['name'] == 'defeated.png':
                defeated_found = True
                numOf['defeat'] += 1
                wait_time = wait_times['defeated']
                random_wait = wait_times['random']
                functions_opencv.clickAndReturnMouse(running_result)
                functions_general.randomWait( wait_time,random_wait )
                #Printing some statistics
                print ('Victory: %d - Defeat: %d - Recharges left: %d' % (numOf['victory'],numOf['defeat'],numOf['recharge']))

                if stage_type == 'toa':
                    logging.info('Stage is TOA and defeated so ending here')
                    return
                    
            #AUTORUN
            elif running_result['res'] and running_result['name'] == 'autorun.png':
                wait_time = wait_times['autorun']
                random_wait = wait_times['wait']
                functions_opencv.clickAndReturnMouse(running_result)
                functions_general.randomWait( wait_time,random_wait )
                continue

            #VICTORY or STAGE CLEAR
            elif running_result['res'] and (running_result['name'] == 'victory.png' or running_result['name'] == 'stage_clear.png'):
                victory_found = True
                numOf['victory'] += 1
                elapsedTime = (time.time() - startTime) / 60
                wait_time = wait_times['victory']
                random_wait = wait_times['wait']
                max_level_wait = wait_times['max_level']
                fodder_full = 0
                if stage_type == 'xp':
                    #Waiting for the max level to appear
                    functions_general.randomWait( max_level_wait,random_wait )
                    screenshot = functions_screenshot.screenshotOpencv(allConfigs)
                    max_level = functions_opencv.checkPicture(screenshot,'max_level.png', tolerance, directories,allConfigs, multiple = True)
                    if max_level['res']:
                        fodder_full = len(max_level['points']) - 1
                    logging.info('-----------------> Number of monsters full: %d',fodder_full)
                functions_opencv.clickAndReturnMouse(running_result)
                functions_general.randomWait( wait_time,random_wait )
                numOf['fodder_full'] = fodder_full
                #Printing some statistics
                print ('Time for this run: %f min' % (elapsedTime))
                print ('Victory: %d - Defeat: %d - Recharges left: %d' % (numOf['victory'],numOf['defeat'],numOf['recharge']))
                gift = False
                wait_time = wait_times['giftCAIROSXP']
                random_wait = wait_times['wait']
                while not gift:
                    waiting_for_gift = ['rune_get.png','ok.png','chest.png','victory.png']
                    after_victory_result = functions_opencv.waitForImg(waiting_for_gift, tolerance, wait_times['image'], wait_times['max_wait_seconds'],directories,allConfigs)
                    if after_victory_result['res'] and after_victory_result['name'] == 'chest.png' or after_victory_result['name'] == 'victory.png':
                        functions_opencv.clickAndReturnMouse(after_victory_result)
                    elif after_victory_result['res'] and after_victory_result['name'] == 'rune_get.png':
                        if stage_type == 'cairos':
                            functions_opencv.clickAndReturnMouse(after_victory_result)
                        elif stage_type == 'xp':
                            screenshot = functions_screenshot.screenshotOpencv(allConfigs)
                            rune_sell = functions_opencv.checkPicture(screenshot,'rune_sell.png', tolerance, directories,allConfigs)
                            functions_opencv.clickAndReturnMouse(rune_sell)
                        gift = True
                    elif after_victory_result['res'] and after_victory_result['name'] == 'ok.png':
                        functions_opencv.clickAndReturnMouse(after_victory_result)
                        gift = True

                    functions_general.randomWait( wait_time,random_wait )
                continue

            #REPLAY
            elif running_result['res'] and running_result['name'] == 'replay.png':
                if int(numOf['Time']) == int(number_of_time):
                    break
                wait_time = wait_times['replay']
                random_wait = wait_times['random']
                if noChangeFodders and numOf['fodder_full'] > 0:
                    logging.info('Number of fodders full: %s - Change fodders: %s',str(numOf['fodder_full']),str(not noChangeFodders))
                    sys.exit(0)
                else:
                    functions_opencv.clickAndReturnMouse(running_result)
                    functions_general.randomWait( wait_time,random_wait )
                continue
                
            #NOT ENOUGH ENERGY
            elif running_result['res'] and running_result['name'] == 'not_enough_energy.png':
                wait_time = wait_times['notEnoughEnergy']
                random_wait = wait_times['random']
                not_enough_energy_buy_yes_time = wait_times['not_enough_energy_buy_yes']
                logging.info('Not enough energy')
                if (numOf['recharge'] > 0):
                    logging.info('Number of recharges > 0 so we buy new energy')
                    numOf['recharge'] -= 1
                    not_enough_energy_yes = functions_opencv.waitForImg(['not_enough_energy_yes.png'], tolerance, wait_times['image'], wait_times['max_wait_seconds'],directories,allConfigs)
                    functions_opencv.clickAndReturnMouse(not_enough_energy_yes)
                    functions_general.randomWait( wait_time,random_wait )
                    not_enough_energy_buy = functions_opencv.waitForImg(['not_enough_energy_buy.png'], tolerance, wait_times['image'], wait_times['max_wait_seconds'],directories,allConfigs)
                    functions_opencv.clickAndReturnMouse(not_enough_energy_buy)
                    functions_general.randomWait( wait_time,random_wait )
                    not_enough_energy_buy_yes = functions_opencv.waitForImg(['not_enough_energy_buy_yes.png'], tolerance, wait_times['image'], wait_times['max_wait_seconds'],directories,allConfigs)
                    functions_opencv.clickAndReturnMouse(not_enough_energy_buy_yes)
                    #We need to wait a little bit because the next screen can come up pretty slowly
                    functions_general.randomWait( not_enough_energy_buy_yes_time,random_wait )
                    not_enough_energy_bought_ok = functions_opencv.waitForImg(['not_enough_energy_bought_ok.png'], tolerance, wait_times['image'], wait_times['max_wait_seconds'],directories,allConfigs)
                    functions_opencv.clickAndReturnMouse(not_enough_energy_bought_ok)
                    functions_general.randomWait( wait_time,random_wait )
                    not_enough_energy_close = functions_opencv.waitForImg(['not_enough_energy_close.png'], tolerance, wait_times['image'], wait_times['max_wait_seconds'],directories,allConfigs)
                    functions_opencv.clickAndReturnMouse(not_enough_energy_close)
                    functions_general.randomWait( wait_time,random_wait )
                else:
                    logging.info('No energy left and no recharges left so leaving the loop')
                    sys.exit(0)
        
                functions_general.randomWait( wait_time,random_wait )    
                continue

            logging.info('**********************************')

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
    parser.add_argument('-a','--arena', help='This will automate the arenas', required=False, action='store_true')
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
                    win32gui.MoveWindow(self._handle, allConfigs['position']['window_pos_x_'+i], allConfigs['position']['window_pos_y_'+i], allConfigs['position']['window_width_'+i], allConfigs['position']['window_height_'+i], True)

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
        
    if args.arena:
        arena.arena(tolerance,directories,allConfigs, wait_times)
        sys.exit(0)    

    if args.stage_type:
        running(args.stage_type,args.no_change_fodders,int(args.recharge),int(args.number_of_time),tolerance, wait_times, directories,allConfigs)
    else:
        print ('You must select a stage type and a stage name, help for more info')

if __name__ == "__main__":
    main()

