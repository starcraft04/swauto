import sys
import os
import logging
import time


import functions_opencv
import functions_general


def rune_upgrade(tolerance,directories,number_of_time,allConfigs,wait_times):
    numOfTime = 0
    endLoop = False
    #Looping
    while not endLoop:
        numOfTime += 1
            
        if number_of_time > 0 and numOfTime == number_of_time + 1:
            break
        
        waiting_for = ['power_up.png','power_up_finished.png']
        running_result = functions_opencv.waitForImg(waiting_for, tolerance, wait_times['image'], wait_times['max_run_wait_seconds'],directories,allConfigs)
        
        if running_result['res'] and running_result['name'] == 'power_up.png':
            print ('10x upgrade number: %d/%d' % (numOfTime,int(number_of_time)))
            functions_opencv.clickAndReturnMouse(running_result)
            functions_general.randomWait( 2,0 )
            continue
        if running_result['res'] and running_result['name'] == 'power_up_finished.png':
            return
    return

def main():
    print('rune upgrade')
    
if __name__ == "__main__":
    main()
