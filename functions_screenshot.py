import time
import os
import sys
import pyautogui
import logging
import cv2
import numpy as np

def screenshotOpencvFull():
    #This function is taking a screenshot with pyautogui which gets a Pillow image
    #Then it makes sure it is transformed in an opencv format
    img = pyautogui.screenshot()
    open_cv_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return open_cv_image
    
def screenshotOpencv(allConfigs):
    #This function is taking a screenshot with pyautogui which gets a Pillow image
    #Then it makes sure it is transformed in an opencv format
    position = allConfigs['position']
    im = pyautogui.screenshot()
    if position['crop_window'] == 'yes':
        im = im.crop((position['window_start_x'],position['window_start_y'], position['window_end_x'], position['window_end_y']))
    open_cv_image = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
    return open_cv_image
    
def takeScreenshot(filename,directories,allConfigs):
    im = pyautogui.screenshot()
    im.save(os.path.join(directories['picsdir'],filename))

def takeScreenshotCoords(filename,directories,coords,allConfigs):
    im = pyautogui.screenshot()
    im2 = im.crop((coords[0],coords[1], coords[2], coords[3]))
    im2.save(os.path.join(directories['picsdir'],filename))
    
def takeScreenshotCoordsFreeze(filename,directories,coords,allConfigs):
    im = pyautogui.screenshot()
    im2 = im.crop((coords[0],coords[1], coords[2], coords[3]))
    im2.save(os.path.join(directories['basepicsdir'],filename))
    
def main():
    print('Functions')
    
if __name__ == "__main__":
    main()
