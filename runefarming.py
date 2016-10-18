import sys
import os
import argparse
import logging
import time
import pyautogui

import functions_opencv
import functions_screenshot
import functions_actions
import functions_general
import functions_calibration
import functions_change_fodders

from ConfigParser import SafeConfigParser

def initConfigs():
    
    #Loading all configs
    #We read the config file
    configFile = 'runefarming.ini'
    config = SafeConfigParser()
    config.read(configFile)
    
    calibrationFile = 'calibration.ini'
    calibrationConfig = SafeConfigParser()
    calibrationConfig.read(calibrationFile)
    
    allConfigs = {}
    
    allConfigs['runefarmingFoddersFiles'] = 'runefarming_fodders.ini'
    allConfigs['memoryFiles'] = 'memory.ini'
    allConfigs['calibrationFiles'] = calibrationFile
 
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
	
    if getattr(sys, 'frozen', False):
	    # frozen
	    myPath = os.path.dirname(sys.executable)
    else:
        # unfrozen
        myPath = os.path.dirname(os.path.realpath(__file__))
	
    directories = {}
    directories['basepicsdir'] = os.path.join(myPath,config.get('dir', 'basepics'))
    directories['debugdir'] = os.path.join(myPath,config.get('dir', 'debug'))
    directories['picsdir'] = os.path.join(myPath,config.get('dir', 'savedpics'))

    allConfigs['directories'] = directories

    calibration = {}
    calibration['fodder_right'] = functions_general.fromStringToTuple(calibrationConfig.get('calibration', 'fodder_right'))
    calibration['fodder_bottom'] = functions_general.fromStringToTuple(calibrationConfig.get('calibration', 'fodder_bottom'))
    calibration['fodder_left'] = functions_general.fromStringToTuple(calibrationConfig.get('calibration', 'fodder_left'))
    calibration['level_top_left'] = functions_general.fromStringToTuple(calibrationConfig.get('calibration', 'level_top_left'))
    calibration['level_bottom_right'] = functions_general.fromStringToTuple(calibrationConfig.get('calibration', 'level_bottom_right'))
    calibration['scroll_left_first'] = functions_general.fromStringToTuple(calibrationConfig.get('calibration', 'scroll_left_first'))
    calibration['scroll_left_last'] = functions_general.fromStringToTuple(calibrationConfig.get('calibration', 'scroll_left_last'))
    calibration['numoffoddersinlist'] = int(calibrationConfig.get('calibration', 'numoffoddersinlist'))
    calibration['monster_icon_width'] = int(calibrationConfig.get('calibration', 'monster_icon_width'))
    calibration['error_correction'] = int(config.get('error_correction','monster_scroll'))
    for i in xrange(1,int(calibration['numoffoddersinlist'])+1):
        calibration['fodder_'+str(i)+'_center'] = functions_general.fromStringToTuple(calibrationConfig.get('calibration', 'fodder_'+str(i)+'_center'))

    allConfigs['calibration'] = calibration

    resize = {}
    resize['resize_or_not'] = config.getboolean('resize','resize_or_not')
    resize['rapport'] = config.getfloat('resize','rapport')

    allConfigs['resize'] = resize
    
    position = {}
    position['system'] = str(config.get('position','system'))
    position['window_name'] = str(config.get('position','window_name'))
    position['window_pos_x'] = int(config.get('position','window_pos_x'))
    position['window_pos_y'] = int(config.get('position','window_pos_y'))
    position['window_width'] = int(config.get('position','window_width'))
    
    allConfigs['position'] = position

    return tolerance, wait_times, directories, calibration, allConfigs

def rune_upgrade(tolerance,directories,calibration,number_of_time,allConfigs,wait_times):
    numOfTime = 0
    endLoop = False
    #Looping
    while not endLoop:
        numOfTime += 1
            
        if number_of_time > 0 and numOfTime == number_of_time + 1:
            break
        
        waiting_for = ['power_up.png','power_up_finished.png']
        running_result = functions_opencv.waitForImg(waiting_for, tolerance, wait_times['image_wait'], wait_times['max_run_wait_seconds'],directories,allConfigs)
        
        if running_result['res'] and running_result['name'] == 'power_up.png':
            print ('10x upgrade number: %d/%d' % (numOfTime,int(number_of_time)))
            functions_opencv.clickAndReturnMouse(running_result)
            functions_general.randomWait( 2,0 )
            continue
        if running_result['res'] and running_result['name'] == 'power_up_finished.png':
            return
    return

def arena(tolerance,directories,calibration,allConfigs,wait_times):
    for i in xrange (0,3):
        print 'scroll:%i' % i
        screenshot = functions_screenshot.screenshotOpencv()
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
                    running_result = functions_opencv.waitForImg(waiting_for, tolerance, wait_times['image_wait'], wait_times['max_run_wait_seconds'],directories,allConfigs)

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

def running(stage_type,stage_name,no_change_fodders,recharge,number_of_time, tolerance, wait_times, directories,calibration,allConfigs):
    #Init
    numOf = {}
       
    printNumOf = {}
    printNumOf['runes'] = 0
    printNumOf['uscroll'] = 0
    printNumOf['mscroll'] = 0
    printNumOf['rainbowmon'] = 0
    printNumOf['sstones'] = 0
    printNumOf['monster'] = 0
    printNumOf['victory'] = 0
    printNumOf['defeat'] = 0
    printNumOf['unknown'] = 0    
    printNumOf['recharge'] = int(recharge)
    
    numOfTime = 0
    endLoop = False
    #Looping
    while not endLoop:
        numOfTime += 1
            
        if number_of_time > 0 and numOfTime == number_of_time + 1:
            break

        victory_found = False
        defeated_found = False
        
        numOf['fodder_full'] = 0
        numOf['runes'] = 0
        numOf['uscroll'] = 0
        numOf['mscroll'] = 0
        numOf['rainbowmon'] = 0
        numOf['sstones'] = 0
        numOf['monster'] = 0
        numOf['victory'] = 0
        numOf['defeat'] = 0
        numOf['unknown'] = 0
        running = True
        
        if number_of_time > 0:
            print ('Run number: %d/%d' % (numOfTime,int(number_of_time)))
        else:
            print ('Run number: %d' % (numOfTime))
        
        while running:
            if stage_type == 'toa':
                waiting_for = ['start_battle.png','autorun.png','not_enough_energy.png','chest.png','next_stage.png','replay.png','defeated.png','revive.png','network_connection_delayed.png','network_delayed.png','unstable.png','victory.png','stage_clear.png']
            else:
                waiting_for = ['start_battle.png','autorun.png','not_enough_energy.png','chest.png','replay.png','defeated.png','revive.png','network_connection_delayed.png','network_delayed.png','unstable.png','victory.png','stage_clear.png']
            running_result = functions_opencv.waitForImg(waiting_for, tolerance, wait_times['image_wait'], wait_times['max_run_wait_seconds'],directories,allConfigs)

            #Check first if we had an issue crash or network delayed
            #NETWORK DELAYED
            if running_result['res'] and (running_result['name'] == 'network_delayed.png' or running_result['name'] == 'unstable.png' or running_result['name'] == 'network_connection_delayed.png'):
                functions_actions.actionNetworkDelayed(tolerance, wait_times,directories,allConfigs)
                continue
            
            #START BATTLE
            elif running_result['res'] and running_result['name'] == 'start_battle.png':
                functions_actions.actionStartBattle(running_result, tolerance, wait_times,directories,calibration,numOf['fodder_full'],no_change_fodders,allConfigs)
                #ROOM IN INVENTORY
                screenshot = functions_screenshot.screenshotOpencv()
                result = functions_opencv.checkPicture(screenshot,'room_in_inventory.png', tolerance, directories,allConfigs)
                if result['res']:
                    room_in_inventory = functions_actions.actionRoomInInventory(tolerance, wait_times,directories,stage_type,allConfigs)
                    #In case we do cairos, we have to stop if we don't have place in the inventory
                    #But if we do another stage, we can ignore this because we sell the rune anywway
                    if not room_in_inventory:
                        logging.info('No place left in the inventory to get new runes, stopping here')
                        sys.exit(0)
                if victory_found or defeated_found:
                    running = False

                
            #Revive - coming from Hall of
            elif running_result['res'] and running_result['name'] == 'revive.png':
                functions_actions.actionRevive(tolerance, wait_times,directories,allConfigs)

            #Next stage - coming from ToA
            elif running_result['res'] and running_result['name'] == 'next_stage.png':
                functions_actions.actionNextStage(running_result,tolerance, wait_times,directories,allConfigs) 
                                   
            #Defeated
            elif running_result['res'] and running_result['name'] == 'defeated.png':
                defeated_found = True
                numOf['defeat'] += 1
                printNumOf['defeat'] += 1
                functions_actions.actionDefeated(running_result, tolerance, wait_times,directories,allConfigs)
                #Printing some statistics
                print ('Victory: %d - Defeat: %d - Recharges left: %d' % (printNumOf['victory'],printNumOf['defeat'],printNumOf['recharge']))

                if stage_type == 'toa':
                    logging.info('Stage is TOA and defeated so ending here')
                    return
                    
            #AUTORUN
            elif running_result['res'] and running_result['name'] == 'autorun.png':
                functions_actions.actionAutorun(running_result, tolerance, wait_times,directories,allConfigs)
                continue

            #VICTORY
            elif running_result['res'] and running_result['name'] == 'victory.png':
                victory_found = True
                numOf['victory'] += 1
                printNumOf['victory'] += 1
                numOf['fodder_full'] = functions_actions.actionVictory(running_result, tolerance, stage_type, stage_name, wait_times,directories,allConfigs)
                #Printing some statistics
                print ('Victory: %d - Defeat: %d - Recharges left: %d' % (printNumOf['victory'],printNumOf['defeat'],printNumOf['recharge']))
                continue

            #STAGE CLEAR
            elif running_result['res'] and running_result['name'] == 'stage_clear.png':
                victory_found = True
                numOf['victory'] += 1
                printNumOf['victory'] += 1
                #Printing some statistics
                print ('Victory: %d - Defeat: %d - Recharges left: %d' % (printNumOf['victory'],printNumOf['defeat'],printNumOf['recharge']))

                numOf['fodder_full'] = functions_actions.actionVictory(running_result, tolerance, stage_type, stage_name, wait_times,directories,allConfigs)
                continue
                
            #CHEST
            elif running_result['res'] and running_result['name'] == 'chest.png':
                functions_actions.actionChest(running_result, tolerance, stage_type, stage_name, wait_times,directories,allConfigs)
                if stage_type == 'cairos' or stage_type == 'xp':
                    gift = functions_actions.actionGiftCAIROSXP(running_result, tolerance, stage_type, stage_name, wait_times,directories,allConfigs)
                    numOf[gift] += 1
                elif stage_type == 'toa' or stage_type == 'hoh' or stage_type == 'essence':
                    functions_actions.actionGiftTOAHOH(tolerance, stage_type, stage_name, wait_times,directories,allConfigs)

                #Printing stats and updating the CSV
                printNumOf['runes'] += numOf['runes']
                printNumOf['uscroll'] += numOf['uscroll']
                printNumOf['mscroll'] += numOf['mscroll']
                printNumOf['rainbowmon'] += numOf['rainbowmon']
                printNumOf['sstones'] += numOf['sstones']
                printNumOf['monster'] += numOf['monster']
                printNumOf['unknown'] += numOf['unknown'] 
                
                if stage_type == 'cairos' or stage_type == 'xp':
                    print ('Runes: %d - Mystical scroll: %d - Unknown scroll: %d - Rainbowmon: %d - S Stones: %d - Monster: %d - Unknown: %d' % (printNumOf['runes'],printNumOf['mscroll'],printNumOf['uscroll'],printNumOf['rainbowmon'],printNumOf['sstones'],printNumOf['monster'],printNumOf['unknown']))

                print ('')

                #Updating CSV                                    
                functions_general.updateCsv('runefarming_stats.csv', stage_type, stage_name, numOf)
                continue

            #REPLAY
            elif running_result['res'] and running_result['name'] == 'replay.png':
                if int(numOfTime) == int(number_of_time):
                    break
                functions_actions.actionReplay(running_result, tolerance, numOf['fodder_full'],no_change_fodders, wait_times,directories,allConfigs)
                continue
                
            #NOT ENOUGH ENERGY
            elif running_result['res'] and running_result['name'] == 'not_enough_energy.png':
                printNumOf['recharge'] = functions_actions.actionNotEnoughEnergy(tolerance, printNumOf['recharge'], wait_times,directories,allConfigs)
                continue

            logging.info('**********************************')

def main():
    parser = argparse.ArgumentParser(description='This program will automate the farming')

    parser.add_argument('-p','--position', help='This will tell the program not to reposition the window according to the config file x y and width', required=False, action='store_true')
    parser.add_argument('-nf','--no_change_fodders', help='This will tell the program not to change fodders and stop when all fodders are full', required=False, action='store_true')
    parser.add_argument("-l", "--log", dest="logLevel", choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Set the logging level")
    parser.add_argument('-r','--recharge', default='0' , help='This is the number of recharges you want', required=False)
    parser.add_argument('-n','--number_of_time', default='0' , help='This is the number of times you want the stage to be run', required=False)
    parser.add_argument('-t','--stage_type', choices=['cairos','essence','xp', 'toa','hoh'], help='This is the stage that you want to automate.', required=False)
    parser.add_argument('-s','--stage_name', help='This is the stage that you want to automate. Can be any name and is there more for logging purpose', required=False)
    parser.add_argument('-tst','--test', nargs=1, help='Just give the name of the picture to be tested through the screenshot', required=False)
    parser.add_argument('-c','--calibration', help='This will do the calibration for the fodders', required=False, action='store_true')
    parser.add_argument('-lc','--log_console', help='This will log to console', required=False, action='store_true')
    parser.add_argument('-sm','--swap_monsters', nargs=1, help='This will swap the monsters that are max, you have to enter the number of fodders that are full for consistency test', required=False)
    parser.add_argument('-ru','--rune_upgrade', nargs=1, help='This will upgrade the runes n times', required=False)
    parser.add_argument('-a','--arena', help='This will automate the arenas', required=False, action='store_true')

    tolerance, wait_times, directories, calibration, allConfigs = initConfigs()

    args = parser.parse_args()
    logginFormat = '%(asctime)s [%(levelname)s][%(funcName)s]: %(message)s'

    if args.logLevel:
        if args.log_console:
            logging.basicConfig(level=args.logLevel,
                            datefmt='%Y/%m/%d %H:%M:%S',
                            format=logginFormat)
        else:
            logging.basicConfig(filename='runefarming.log',
                            level=args.logLevel,
                            datefmt='%y%m%d %H:%M:%S',
                            format=logginFormat)


    if args.position:
        #Before Starting, make sure to use wmctrl -r Vysor -e 1,0,0,800,-1
        #The window size should be 800 x 450
        #This is to ensure we have always the same siz and that pixels won't be off
        #We read the config file
        if allConfigs['position']['system'] == "linux":
            os.system('wmctrl -r '+allConfigs['position']['window_name']+' -e 1,'+str(allConfigs['position']['window_pos_x'])+','+str(allConfigs['position']['window_pos_y'])+','+str(allConfigs['position']['window_width'])+',-1')
            #Now we make sure the window is active and in front on the desktop
            os.system('wmctrl -a '+allConfigs['position']['window_name'])
        if allConfigs['position']['system'] == "windows":
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

                def move_window(self):
                    """put the window in the foreground"""
                    win32gui.MoveWindow(self._handle, 0, 0, 800, 500, True)

            w = WindowMgr()
            w.find_window_wildcard(".*"+allConfigs['position']['window_name']+".*")
            w.set_foreground()
            w.move_window()

        time.sleep(1)

    if args.test:
        screenshot = functions_screenshot.screenshotOpencv()
        result = functions_opencv.checkPicture(screenshot,args.test[0], tolerance, directories,allConfigs, multiple = True, showFound = True)
        if not result['res']:
            if args.test[0][:-4] in tolerance:
                tolerance = float(tolerance[args.test[0][:-4]])
            else:
                tolerance = float(tolerance['global'])
            print ('Tolerance for file %s is: %f' % (args.test[0],tolerance))
            print ('Best tolerance found is: %f' % (result['best_val']))
        sys.exit(0)

    if args.calibration:
        functions_calibration.calibrate(allConfigs['calibrationFiles'],tolerance,directories,allConfigs)
        sys.exit(0)
        
    if args.swap_monsters:
        functions_change_fodders.swapMonsters(tolerance,directories,calibration,int(args.swap_monsters[0]),allConfigs)
        sys.exit(0)    

    if args.rune_upgrade:
        rune_upgrade(tolerance,directories,calibration,int(args.rune_upgrade[0]),allConfigs, wait_times)
        sys.exit(0)
        
    if args.arena:
        arena(tolerance,directories,calibration,allConfigs, wait_times)
        sys.exit(0)    

    if args.stage_name and args.stage_type:
        running(args.stage_type,args.stage_name,args.no_change_fodders,args.recharge,int(args.number_of_time),tolerance, wait_times, directories,calibration,allConfigs)
    else:
        print ('You must select a stage type and a stage name, help for more info')

if __name__ == "__main__":
    main()

