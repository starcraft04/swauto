import time
import logging
import sys

import functions_opencv
import functions_general
import functions_screenshot
import functions_change_fodders

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
    waiting_for = ['sstones.png','uscroll.png','mscroll.png','rainbowmon.png','rune_sell.png','fodder.png','symbol01.png','symbol02.png','symbol03.png','symbol04.png','symbol05.png','symbol06.png']
    gift = functions_opencv.waitForImg(waiting_for, tolerance, wait_times['image_wait'], wait_times['max_wait_seconds'],directories,allConfigs)

    if gift['res'] and gift['name'] == 'rune_sell.png':
        logging.info('We got a rune')
        #CAIROS case
        if (stage_type == 'cairos'):
            crop_square = (gift['points'][0]['center'][0] - 90,gift['points'][0]['center'][1] - 240,gift['points'][0]['center'][0] + 220,gift['points'][0]['center'][1] + 45)
            functions_screenshot.takeScreenshotCoords(time.strftime("%Y%m%d-%H%M%S")+'_rune.png',directories,crop_square,allConfigs)
            screenshot = functions_screenshot.screenshotOpencv(allConfigs)
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
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs)
        functions_opencv.clickAndReturnMouse(ok)
        functions_general.randomWait( wait_time,random_wait )
        return 'uscroll'
        
    elif gift['res'] and gift['name'] == 'mscroll.png':
        logging.info('We got a mystical scroll')
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs)
        functions_opencv.clickAndReturnMouse(ok)
        functions_general.randomWait( wait_time,random_wait )
        return 'mscroll'
        
    elif gift['res'] and gift['name'] == 'rainbowmon.png':
        logging.info('We got a Rainbowmon')
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs)
        functions_opencv.clickAndReturnMouse(ok)
        functions_general.randomWait( wait_time,random_wait )
        return 'rainbowmon'
        
    elif gift['res'] and gift['name'] == 'sstones.png':
        logging.info('We got a Summoning stone')
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs)
        functions_opencv.clickAndReturnMouse(ok)
        functions_general.randomWait( wait_time,random_wait )
        return 'sstones'

    elif gift['res'] and (gift['name'] == 'fodder.png' or \
                          gift['name'] == 'fodder2.png'):
        logging.info('We got a fodder monster')
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs)
        functions_opencv.clickAndReturnMouse(ok)
        functions_general.randomWait( wait_time,random_wait )
        return 'monster'
    elif gift['res'] and (gift['name'] == 'symbol01.png' or \
                          gift['name'] == 'symbol02.png' or \
                          gift['name'] == 'symbol03.png' or \
                          gift['name'] == 'symbol04.png' or \
                          gift['name'] == 'symbol05.png' or \
                          gift['name'] == 'symbol06.png' or \
                          gift['name'] == 'symbol07.png' or \
                          gift['name'] == 'symbol08.png'):
        logging.info('We got a symbol')
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        ok = functions_opencv.checkPicture(screenshot,'ok.png', tolerance, directories,allConfigs)
        functions_opencv.clickAndReturnMouse(ok)
        functions_general.randomWait( wait_time,random_wait )
        return 'unknown'        
    else:
        logging.info('Waiting exceeded %d',wait_times['max_wait_seconds'])
        logging.info('I don t know what I got, saved as unkown')
        functions_screenshot.takeScreenshot('unknown_'+time.strftime("%Y%m%d-%H%M%S")+'.png',directories,allConfigs)
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
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
