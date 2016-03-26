import sys
import os
import argparse
import logging
import time

import functions_opencv
import functions_screenshot
import functions_actions
import functions_general
import functions_calibration
import functions_change_fodders

from ConfigParser import SafeConfigParser 

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
    
    #Looping
    for numOfTime in xrange(1,int(number_of_time)+1):
        victory_found = False
        
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
        
        print ('Run number: %d/%d' % (numOfTime,int(number_of_time)))
        
        while running:
            waiting_for = ['start_battle.png','autorun.png','chest.png','replay.png','defeated.png','revive.png','network_delayed.png','not_enough_energy.png','victory.png','stage_clear.png']
            running_result = functions_opencv.waitForImg(waiting_for, tolerance, wait_times['image_wait'], wait_times['max_run_wait_seconds'],directories,allConfigs)

            #Check first if we had an issue crash or network delayed
            #NETWORK DELAYED
            if running_result['res'] and running_result['name'] == 'network_delayed.png':
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
                if victory_found:
                    running = False

                
            #Revive - coming from Hall of
            elif running_result['res'] and running_result['name'] == 'revive.png':
                functions_actions.actionRevive(tolerance, wait_times,directories,allConfigs)
                    
            #Defeated
            elif running_result['res'] and running_result['name'] == 'defeated.png':
                numOf['defeat'] += 1
                printNumOf['defeat'] += numOf['defeat']
                functions_actions.actionDefeated(running_result, tolerance, wait_times,directories,allConfigs)
                #Printing some statistics
                print ('Victory: %d - Defeat: %d - Recharges left: %d' % (printNumOf['victory'],printNumOf['defeat'],printNumOf['recharge']))

                if stage_name == 'toa':
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
                printNumOf['victory'] += numOf['victory']
                numOf['fodder_full'] = functions_actions.actionVictory(running_result, tolerance, stage_type, stage_name, wait_times,directories,allConfigs)
                #Printing some statistics
                print ('Victory: %d - Defeat: %d - Recharges left: %d' % (printNumOf['victory'],printNumOf['defeat'],printNumOf['recharge']))
                continue

            #STAGE CLEAR
            elif running_result['res'] and running_result['name'] == 'stage_clear.png':
                numOf['victory'] += 1
                printNumOf['victory'] += numOf['victory']
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
                elif stage_type == 'toa' or stage_type == 'hoh':
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
    parser.add_argument('-n','--number_of_time', default='1000' , help='This is the number of times you want the stage to be run', required=False)
    parser.add_argument('-t','--stage_type', choices=['cairos', 'xp', 'toa','hoh'], help='This is the stage that you want to automate.', required=False)
    parser.add_argument('-s','--stage_name', help='This is the stage that you want to automate. Can be any name and is there more for logging purpose', required=False)
    parser.add_argument('-tst','--test', nargs=1, help='Just give the name of the picture to be tested through the screenshot', required=False)
    parser.add_argument('-c','--calibration', help='This will do the calibration for the fodders', required=False, action='store_true')
    parser.add_argument('-lc','--log_console', help='This will log to console', required=False, action='store_true')
    parser.add_argument('-sm','--swap_monsters', nargs=1, help='This will swap the monsters that are max, you have to enter the number of fodders that are full for consistency test', required=False)


    args = parser.parse_args()
    
    #Loading all configs
    #We read the config file
    configFile = 'runefarming.ini'
    config = SafeConfigParser()
    config.read(configFile)
    
    allConfigs = {}
    
    allConfigs['runefarmingFoddersFiles'] = 'runefarming_fodders.ini'
 
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
    wait_times['screen_wait_random'] = int(config.get('wait','random'))
    wait_times['screen_not_enough_energy_buy_yes_wait'] = int(config.get('wait','not_enough_energy_buy_yes'))
    wait_times['screen_max_level_wait'] = int(config.get('wait','max_level'))
    wait_times['room_in_inventory'] = int(config.get('wait','room_in_inventory'))
    wait_times['long_press_time'] = int(config.get('wait','long_press_time'))
    wait_times['max_monster_info_screen'] = int(config.get('wait','max_monster_info_screen'))
    wait_times['get_monster_info_max_num_times'] = int(config.get('wait','get_monster_info_max_num_times')) 

    allConfigs['wait_times'] = wait_times
    
    myPath = os.path.dirname(os.path.abspath(__file__))
    directories = {}
    directories['basepicsdir'] = os.path.join(myPath,config.get('dir', 'basepics'))
    directories['debugdir'] = os.path.join(myPath,config.get('dir', 'debug'))
    directories['picsdir'] = os.path.join(myPath,config.get('dir', 'savedpics'))

    allConfigs['directories'] = directories

    calibration = {}
    calibration['fodder_right'] = functions_general.fromStringToTuple(config.get('calibration', 'fodder_right'))
    calibration['fodder_bottom'] = functions_general.fromStringToTuple(config.get('calibration', 'fodder_bottom'))
    calibration['fodder_left'] = functions_general.fromStringToTuple(config.get('calibration', 'fodder_left'))
    calibration['level_top_left'] = functions_general.fromStringToTuple(config.get('calibration', 'level_top_left'))
    calibration['level_bottom_right'] = functions_general.fromStringToTuple(config.get('calibration', 'level_bottom_right'))
    calibration['scroll_left_first'] = functions_general.fromStringToTuple(config.get('calibration', 'scroll_left_first'))
    calibration['scroll_left_last'] = functions_general.fromStringToTuple(config.get('calibration', 'scroll_left_last'))
    calibration['numoffoddersinlist'] = int(config.get('calibration', 'numoffoddersinlist'))
    calibration['monster_icon_width'] = int(config.get('calibration', 'monster_icon_width'))
    for i in xrange(1,int(calibration['numoffoddersinlist'])+1):
        calibration['fodder_'+str(i)+'_center'] = functions_general.fromStringToTuple(config.get('calibration', 'fodder_'+str(i)+'_center'))

    allConfigs['calibration'] = calibration

    resize = {}
    resize['resize_or_not'] = config.getboolean('resize','resize_or_not')
    resize['rapport'] = config.getfloat('resize','rapport')

    allConfigs['resize'] = resize

    if args.logLevel:
        if args.log_console:
            logging.basicConfig(level=args.logLevel,\
                            format='%(asctime)s:%(levelname)s:%(message)s')
        else:
            logging.basicConfig(filename='runefarming.log',\
                            level=args.logLevel,\
                            format='%(asctime)s:%(levelname)s:%(message)s')

    if args.position:
        #Before Starting, make sure to use wmctrl -r Vysor -e 1,0,0,800,-1
        #The window size should be 800 x 450
        #This is to ensure we have always the same siz and that pixels won't be off
        #We read the config file
        window_pos_x = int(config.get('position','window_pos_x'))
        window_pos_y = int(config.get('position','window_pos_y'))
        window_width = int(config.get('position','window_width'))
        os.system('wmctrl -r Vysor -e 1,'+str(window_pos_x)+','+str(window_pos_y)+','+str(window_width)+',-1')
        #Now we make sure the window is active and in front on the desktop
        os.system('wmctrl -a Vysor')
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
        functions_calibration.calibrate(configFile,tolerance,directories,allConfigs)
        sys.exit(0)
    if args.swap_monsters:
        functions_change_fodders.swapMonsters(tolerance,directories,calibration,int(args.swap_monsters[0]),allConfigs)
        sys.exit(0)    

    if args.stage_name and args.stage_type:
        running(args.stage_type,args.stage_name,args.no_change_fodders,args.recharge,args.number_of_time,tolerance, wait_times, directories,calibration,allConfigs)
    else:
        print ('You must select a stage type and a stage name, help for more info')

if __name__ == "__main__":
    main()
