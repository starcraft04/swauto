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

def running(stage_type,noChangeFodders,numOfRecharge,number_of_time, tolerance, wait_times, directories,allConfigs):
    #Init
    numOf = {}
    numOf['victory'] = 0
    numOf['defeat'] = 0
    numOf['recharge'] = numOfRecharge
    numOf['Time'] = 0
    allElapsedTimes = []
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
                wait_time = wait_times['networkdelayed']
                random_wait = wait_times['random']
                screenshot = functions_screenshot.screenshotOpencv(allConfigs)
                network_delayed_yes = functions_opencv.checkPicture(screenshot,'network_delayed_yes.png', tolerance ,directories,allConfigs)
                functions_opencv.clickAndReturnMouse(network_delayed_yes)
                #Wait a little bit for the network to stabilise
                functions_general.randomWait( wait_time,random_wait ) 
                continue
            
            #START BATTLE
            elif running_result['res'] and running_result['name'] == 'start_battle.png':
                wait_time = wait_times['startbattle']
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
                random_wait = wait_times['random']
                functions_opencv.clickAndReturnMouse(running_result)
                functions_general.randomWait( wait_time,random_wait )
                continue

            #VICTORY or STAGE CLEAR
            elif running_result['res'] and (running_result['name'] == 'victory.png' or running_result['name'] == 'stage_clear.png'):
                victory_found = True
                numOf['victory'] += 1
                wait_time = wait_times['victory']
                random_wait = wait_times['random']
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
                elapsedTime = (time.time() - startTime)
                allElapsedTimes.append(elapsedTime)
                average = sum(allElapsedTimes) / float(len(allElapsedTimes))
                elapsedTime_m, elapsedTime_s = divmod(elapsedTime, 60)
                average_m, average_s = divmod(average, 60)
                print 'Time for this run: {:02.0f} minute(s) {:07.4f} seconds'.format(elapsedTime_m, elapsedTime_s)
                print 'Average time for all runs: {:02.0f} minute(s) {:07.4f} seconds'.format(average_m, average_s)
                print ('Victory: %d - Defeat: %d - Recharges left: %d' % (numOf['victory'],numOf['defeat'],numOf['recharge']))
                gift = False
                wait_time = wait_times['giftcairosxp']
                random_wait = wait_times['random']
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
                wait_time = wait_times['notenoughenergy']
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
    print('running')
    
if __name__ == "__main__":
    main()
