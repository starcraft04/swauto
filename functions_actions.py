import time
import logging
import sys

import functions_opencv
import functions_general
import functions_screenshot
import functions_change_fodders

def actionNetworkDelayed(tolerance, wait_times,directories,allConfigs):
    wait_time = wait_times['screen_networkDelayed_wait']
    random_wait = wait_times['screen_wait_random']
    screenshot = functions_screenshot.screenshotOpencv()
    network_delayed_yes = functions_opencv.checkPicture(screenshot,'network_delayed_yes.png', tolerance ,directories,allConfigs)
    functions_opencv.clickAndReturnMouse(network_delayed_yes)
    #Wait a little bit for the network to stabilise
    functions_general.randomWait( wait_time,random_wait ) 
    return

def actionAutorun(running_result, tolerance, wait_times,directories,allConfigs):
    wait_time = wait_times['screen_autorun_wait']
    random_wait = wait_times['screen_wait_random']
    functions_opencv.clickAndReturnMouse(running_result)
    functions_general.randomWait( wait_time,random_wait )
    return

def actionRevive(tolerance, wait_times,directories,allConfigs):
    wait_time = wait_times['screen_revive_wait']
    random_wait = wait_times['screen_wait_random']
    screenshot = functions_screenshot.screenshotOpencv()
    revive_no = functions_opencv.checkPicture(screenshot,'revive_no.png', tolerance ,directories,allConfigs)
    functions_opencv.clickAndReturnMouse(revive_no)
    functions_general.randomWait( wait_time,random_wait )
    return

def actionDefeated(running_result, tolerance, wait_times,directories,allConfigs):
    wait_time = wait_times['screen_defeated_wait']
    random_wait = wait_times['screen_wait_random']
    functions_opencv.clickAndReturnMouse(running_result)
    functions_general.randomWait( wait_time,random_wait )
    return

def actionNextStage(running_result, tolerance, wait_times,directories,allConfigs):
    wait_time = wait_times['screen_defeated_wait']
    random_wait = wait_times['screen_wait_random']
    functions_opencv.clickAndReturnMouse(running_result)
    functions_general.randomWait( wait_time,random_wait )
    return
   
def actionVictory(running_result, tolerance, stage_type, stage_name, wait_times,directories,allConfigs):
    wait_time = wait_times['screen_victory_wait']
    random_wait = wait_times['screen_wait_random']
    max_level_wait = wait_times['screen_max_level_wait']
    fodder_full = 0
    if stage_type == 'xp':
        #Waiting for the max level to appear
        functions_general.randomWait( max_level_wait,random_wait )
        screenshot = functions_screenshot.screenshotOpencv()
        max_level = functions_opencv.checkPicture(screenshot,'max_level.png', tolerance, directories,allConfigs, multiple = True)
        if max_level['res']:
            fodder_full = len(max_level['points']) - 1
        logging.info('-----------------> Number of monsters full: %d',fodder_full)
    functions_opencv.clickAndReturnMouse(running_result)
    functions_general.randomWait( wait_time,random_wait )
    return fodder_full

def actionReplay(running_result, tolerance, numOfFodderFull,noChangeFodders, wait_times,directories,allConfigs):
    wait_time = wait_times['screen_replay_wait']
    random_wait = wait_times['screen_wait_random']
    if noChangeFodders and numOfFodderFull > 0:
        logging.info('Number of fodders full: %s - Change fodders: %s',str(numOfFodderFull),str(not noChangeFodders))
        sys.exit(0)
    else:
        functions_opencv.clickAndReturnMouse(running_result)
        functions_general.randomWait( wait_time,random_wait )
        return
    
def actionStartBattle(running_result, tolerance, wait_times,directories,calibration,numOfFodderFull,noChangeFodders,allConfigs):
    wait_time = wait_times['screen_startBattle_wait']
    random_wait = wait_times['screen_wait_random']
    if noChangeFodders and numOfFodderFull > 0:
        logging.info('Number of fodders full: %s - Change fodders: %s',str(numOfFodderFull-1),str(not noChangeFodders))
        sys.exit(0)
    if numOfFodderFull > 0:
        logging.info('-----------------> Changing %d fodders because they are max',numOfFodderFull)
        result = functions_change_fodders.swapMonsters(tolerance,directories,calibration,numOfFodderFull,allConfigs)
    functions_general.randomWait( 1,1 )
    functions_opencv.clickAndReturnMouse(running_result)
    functions_general.randomWait( wait_time,random_wait )
    return 

def actionRoomInInventory(tolerance, wait_times,directories,stage_type,allConfigs):
    wait_time = wait_times['room_in_inventory']
    random_wait = wait_times['screen_wait_random']
    screenshot = functions_screenshot.screenshotOpencv()
    if stage_type == 'cairos':
        room_in_inventory_no = functions_opencv.checkPicture(screenshot,'room_in_inventory_no.png', tolerance ,directories,allConfigs)
        functions_opencv.clickAndReturnMouse(room_in_inventory_no)
        #Wait a little bit for the network to stabilise
        functions_general.randomWait( wait_time,random_wait )
        return False
    else:
        room_in_inventory_yes = functions_opencv.checkPicture(screenshot,'room_in_inventory_yes.png', tolerance ,directories,allConfigs)
        functions_opencv.clickAndReturnMouse(room_in_inventory_yes)
        #Wait a little bit for the network to stabilise
        functions_general.randomWait( wait_time,random_wait )
        return True
         
def actionNotEnoughEnergy(tolerance, numOfRecharge, wait_times,directories,allConfigs):
    wait_time = wait_times['screen_notEnoughEnergy_wait']
    random_wait = wait_times['screen_wait_random']
    not_enough_energy_buy_yes_time = wait_times['screen_not_enough_energy_buy_yes_wait']
    logging.info('Not enough energy')
    if (numOfRecharge > 0):
        logging.info('Number of recharges > 0 so we buy new energy')
        numOfRecharge -= 1
        not_enough_energy_yes = functions_opencv.waitForImg(['not_enough_energy_yes.png'], tolerance, wait_times['image_wait'], wait_times['max_wait_seconds'],directories,allConfigs)
        functions_opencv.clickAndReturnMouse(not_enough_energy_yes)
        not_enough_energy_buy = functions_opencv.waitForImg(['not_enough_energy_buy.png'], tolerance, wait_times['image_wait'], wait_times['max_wait_seconds'],directories,allConfigs)
        functions_opencv.clickAndReturnMouse(not_enough_energy_buy)
        not_enough_energy_buy_yes = functions_opencv.waitForImg(['not_enough_energy_buy_yes.png'], tolerance, wait_times['image_wait'], wait_times['max_wait_seconds'],directories,allConfigs)
        functions_opencv.clickAndReturnMouse(not_enough_energy_buy_yes)
        #We need to wait a little bit because the next screen can come up pretty slowly
        functions_general.randomWait( not_enough_energy_buy_yes_time,random_wait )
        not_enough_energy_bought_ok = functions_opencv.waitForImg(['not_enough_energy_bought_ok.png'], tolerance, wait_times['image_wait'], wait_times['max_wait_seconds'],directories,allConfigs)
        functions_opencv.clickAndReturnMouse(not_enough_energy_bought_ok)
        not_enough_energy_close = functions_opencv.waitForImg(['not_enough_energy_close.png'], tolerance, wait_times['image_wait'], wait_times['max_wait_seconds'],directories,allConfigs)
        functions_opencv.clickAndReturnMouse(not_enough_energy_close)
    else:
        logging.info('No energy left and no recharges left so leaving the loop')
        sys.exit(0)
        
    functions_general.randomWait( wait_time,random_wait )    
    return numOfRecharge
    
def actionChest(running_result, tolerance, stage_type, stage_name, wait_times,directories,allConfigs):
    wait_time = wait_times['screen_chest_wait']
    random_wait = wait_times['screen_wait_random']
    functions_opencv.clickAndReturnMouse(running_result)
    #We need an extra wait because the chest takes a long time to open
    functions_general.randomWait( wait_time,random_wait )                    
    return


def actionGiftTOAHOH(tolerance, stage_type, stage_name, wait_times,directories,allConfigs):
    wait_time = wait_times['screen_giftTOAHOH_wait']
    random_wait = wait_times['screen_wait_random']
    #Searching for OK button
    button_ok = functions_opencv.waitForImg(['ok.png'], tolerance, wait_times['image_wait'], wait_times['max_wait_seconds'],directories,allConfigs)
    crop_square = (button_ok['points'][0]['center'][0] - 160,button_ok['points'][0]['center'][1] - 220,button_ok['points'][0]['center'][0] + 155,button_ok['points'][0]['center'][1] + 35)
    if stage_type == 'toa' or stage_type == 'hoh':
        image_name = stage_type+'_'+stage_name+'.png'
    elif stage_type == 'essence':
        image_name = time.strftime("%Y%m%d-%H%M%S")+'_' + stage_type+'_'+stage_name+'.png'
    functions_screenshot.takeScreenshotCoords(image_name,directories,crop_square,allConfigs)
    functions_opencv.clickAndReturnMouse(button_ok)
    functions_general.randomWait( wait_time,random_wait )
    return

def actionGiftCAIROSXP(running_result, tolerance, stage_type, stage_name, wait_times,directories,allConfigs):
    wait_time = wait_times['screen_giftCAIROSXP_wait']
    random_wait = wait_times['screen_wait_random']
    #Searching which gift we got
    waiting_for = ['sstones.png','uscroll.png','mscroll.png','rainbowmon.png','rune_sell.png','fodder.png']
    gift = functions_opencv.waitForImg(waiting_for, tolerance, wait_times['image_wait'], wait_times['max_wait_seconds'],directories,allConfigs)

    if gift['res'] and gift['name'] == 'rune_sell.png':
        logging.info('We got a rune')
        #CAIROS case
        if (stage_type == 'cairos'):
            crop_square = (gift['points'][0]['center'][0] - 90,gift['points'][0]['center'][1] - 240,gift['points'][0]['center'][0] + 220,gift['points'][0]['center'][1] + 45)
            functions_screenshot.takeScreenshotCoords(time.strftime("%Y%m%d-%H%M%S")+'_rune.png',directories,crop_square,allConfigs)
            screenshot = functions_screenshot.screenshotOpencv()
            rune_get = functions_opencv.checkPicture(screenshot,'rune_get.png', tolerance, directories,allConfigs)
            logging.info('Getting the rune')
            functions_opencv.clickAndReturnMouse(rune_get)
            functions_general.randomWait( wait_time,random_wait )
            return 'runes'
        #XP case
        elif (stage_type == 'xp'):
            logging.info('Selling the rune')
            functions_opencv.clickAndReturnMouse(gift)
            functions_general.randomWait( wait_time,random_wait )
            return 'runes'
            
    elif gift['res'] and gift['name'] == 'uscroll.png':
        logging.info('We got an unknown scroll')
        screenshot = functions_screenshot.screenshotOpencv()
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs)
        functions_opencv.clickAndReturnMouse(ok)
        functions_general.randomWait( wait_time,random_wait )
        return 'uscroll'
        
    elif gift['res'] and gift['name'] == 'mscroll.png':
        logging.info('We got a mystical scroll')
        screenshot = functions_screenshot.screenshotOpencv()
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs)
        functions_opencv.clickAndReturnMouse(ok)
        functions_general.randomWait( wait_time,random_wait )
        return 'mscroll'
        
    elif gift['res'] and gift['name'] == 'rainbowmon.png':
        logging.info('We got a Rainbowmon')
        screenshot = functions_screenshot.screenshotOpencv()
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs)
        functions_opencv.clickAndReturnMouse(ok)
        functions_general.randomWait( wait_time,random_wait )
        return 'rainbowmon'
        
    elif gift['res'] and gift['name'] == 'sstones.png':
        logging.info('We got a Summoning stone')
        screenshot = functions_screenshot.screenshotOpencv()
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs)
        functions_opencv.clickAndReturnMouse(ok)
        functions_general.randomWait( wait_time,random_wait )
        return 'sstones'

    elif gift['res'] and gift['name'] == 'fodder.png':
        logging.info('We got a fodder monster')
        screenshot = functions_screenshot.screenshotOpencv()
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs)
        functions_opencv.clickAndReturnMouse(ok)
        functions_general.randomWait( wait_time,random_wait )
        return 'monster'
        
    else:
        logging.info('Waiting exceeded %d',wait_times['max_wait_seconds'])
        logging.info('I don t know what I got, saved as unkown')
        functions_screenshot.takeScreenshot('unknown_'+time.strftime("%Y%m%d-%H%M%S")+'.png',directories,allConfigs)
        screenshot = functions_screenshot.screenshotOpencv()
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs) 
        if ok['res']:                    
            functions_opencv.clickAndReturnMouse(ok)
            functions_general.randomWait( wait_time,random_wait )
            return 'unknown'
        else:
            logging.info('Could not find an OK button so stopping here')
            sys.exit(0)

def main():
    print('function actions')
    
if __name__ == "__main__":
    main()
