import time
import os
import logging
import cv2
import numpy as np
import pyautogui
import functions_screenshot
import sys
from ConfigParser import SafeConfigParser 


def scrollMonsterBarRightToLeft(numOfTimes,calibration,direction = 'left'):
    for i in xrange(0,numOfTimes):
        if direction == 'left':
            pyautogui.moveTo(calibration['scroll_left_last'][0],calibration['scroll_left_last'][1])
            pyautogui.dragTo(calibration['scroll_left_first'][0],calibration['scroll_left_first'][1],1)
        else:
            pyautogui.moveTo(calibration['scroll_left_first'][0],calibration['scroll_left_first'][1])
            pyautogui.dragTo(calibration['scroll_left_last'][0],calibration['scroll_left_last'][1],1)
    return    

def scrollMaxRight(calibration):
    numOfTimes = (100 // calibration['numoffoddersinlist']) + 1
    scrollMonsterBarRightToLeft(numOfTimes,calibration,direction = 'left')
    return

def clickAndReturnMouse(img):
    orig_x,orig_y = pyautogui.position()
    pyautogui.moveTo(img['points'][0]['center'][0],img['points'][0]['center'][1])
    pyautogui.click()
    logging.info('CLICK')
    pyautogui.moveTo(orig_x, orig_y)
    return

def clickAndReturnMouseCoords(coords):
    orig_x,orig_y = pyautogui.position()
    pyautogui.moveTo(coords[0],coords[1])
    pyautogui.click()
    logging.info('CLICK')
    pyautogui.moveTo(orig_x, orig_y)
    return
  
def clickLongPress(coords,press_time):
    pyautogui.moveTo(coords[0], coords[1])
    pyautogui.mouseDown()
    time.sleep(press_time)
    pyautogui.mouseUp()
    return

def cropToCoords(img, coords):
    (ulx,uly) = coords[0]
    (brx,bry) = coords[1]
    return img[uly:bry, ulx:brx]

def getMultiFullInfo(all_matches,w,h):
    #This function will rearrange the data and calculate the tuple
    #   for the square and the center and the tolerance for each point
    result = []
    for match in all_matches:
        tlx = match[0]
        tly = match[1]
        top_left = (tlx,tly)
        brx = match[0] + w
        bry = match[1] + h 
        bottom_right = (brx,bry)     
        centerx = match[0] + w/2
        centery = match[1] + h/2
        center = [centerx,centery]
        result.append({'top_left':top_left,'bottom_right':bottom_right,'center':center,'tolerance':match[2]})
    return result

def getMulti(res, tolerance,w,h):
    #We get an opencv image in the form of a numpy array and we need to
    #   find all the occurances in there knowing that 2 squares cannot intersect
    #This will give us exactly the matches that are unique
    
    #First we need to get all the points where value is >= tolerance
    #This wil get sometimes some squares that vary only from some pixels and that are overlapping
    all_matches_full = np.where (res >= tolerance)

    #Now we need to arrange it in x,y coordinates
    all_matches_coords = []
    for pt in zip(*all_matches_full[::-1]):
        all_matches_coords.append([pt[0],pt[1],res[pt[1]][pt[0]]])
    #Let's sort the new array
    all_matches_coords = sorted(all_matches_coords)
    
    #This function will be called only when there is at least one match so if matchtemplate returns something
    #This means we have found at least one record so we can prepare the analysis and loop through each records 
    all_matches = [[all_matches_coords[0][0],all_matches_coords[0][1],all_matches_coords[0][2]]]
    i=1
    for pt in all_matches_coords:
        found_in_existing = False
        for match in all_matches:
            #This is the test to make sure that the square we analyse doesn't overlap with one of the squares already found
            if pt[0] >= (match[0]-w) and pt[0] <= (match[0]+w) and pt[1] >= (match[1]-h) and pt[1] <= (match[1]+h):
                found_in_existing = True
                if pt[2] > match[2]:
                    match[0] = pt[0]
                    match[1] = pt[1]
                    match[2] = res[pt[1]][pt[0]]
        if not found_in_existing:
            all_matches.append([pt[0],pt[1],res[pt[1]][pt[0]]])
        i += 1

    #Before returning the result, we will arrange it with data easily accessible
    all_matches = getMultiFullInfo(all_matches,w,h) 
    return all_matches

def extractAlpha(img, hardedge = True):
    if img.shape[2]>3:
        logging.debug('Mask detected')
        channels = cv2.split(img)
        mask = np.array(channels[3])
        if hardedge:
            for idx in xrange(len(mask[0])):
                if mask[0][idx] <=128:
                    mask[0][idx] = 0
                else:
                    mask[0][idx] = 255

        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        return {'res':True,'image':img,'mask':mask}
    else:
        return {'res':False,'image':img}

def findPicture(screenshot,template, tolerance,allConfigs, multiple = False):
    #This function will work with color images 3 channels minimum
    #The template can have an alpha channel and we will extract it to have the mask

    logging.debug('Tolerance to check is %f' , tolerance)

    logging.debug('*************Start of checkPicture')

    h = template.shape[0]
    w = template.shape[1]
    
    #We will now extract the alpha channel
    tmpl = extractAlpha(template)
        
    # the method used for comparison, can be ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR','cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']
    meth = 'cv2.TM_CCORR_NORMED'
    method = eval(meth)

    # Apply template Matching
    if tmpl['res']:
        res = cv2.matchTemplate(screenshot,tmpl['image'],method, mask = tmpl['mask'])
    else:
        res = cv2.matchTemplate(screenshot,tmpl['image'],method)
        
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
        best_val = 1 - min_val
    else:
        top_left = max_loc
        best_val = max_val
    #We need to ensure we found at least one match otherwise we return false
    if best_val >= tolerance:
        if multiple:
            #We need to find all the time the image is found
            all_matches = getMulti(res, float(tolerance),int(w),int(h))
        else:
            bottom_right = (top_left[0] + w, top_left[1] + h)
            center = (top_left[0] + (w/2), top_left[1] + (h/2))
            all_matches = [{'top_left':top_left,'bottom_right':bottom_right,'center':center,'tolerance':best_val}]

        #point will be in the form: [{'tolerance': 0.9889718890190125, 'center': (470, 193), 'bottom_right': (597, 215), 'top_left': (343, 172)}]
        
        logging.debug('The points found will be:')
        logging.debug(all_matches)
        logging.debug('*************End of checkPicture')
        return {'res': True,'points':all_matches}
    else:
        logging.debug('Could not find a value above tolerance')
        logging.debug('*************End of checkPicture')
        return {'res': False,'best_val':best_val}

def checkPicture(screenshot, templateFile, tolerance_list ,directories,allConfigs,multiple = False, showFound = False, saveFound = False):
    #This is an intermediary function so that the actual function doesn't include too much specific arguments

    if templateFile[:-4] in tolerance_list:
        tolerance = float(tolerance_list[templateFile[:-4]])
    else:
        tolerance = float(tolerance_list['global'])

    font = cv2.FONT_HERSHEY_PLAIN
    
    template = cv2.imread(os.path.join(directories['basepicsdir'],templateFile),-1)
    h = template.shape[0]
    w = template.shape[1] 

    resize_or_not = allConfigs['resize']['resize_or_not']
    resize_rapport = allConfigs['resize']['rapport']
    if resize_or_not:
        logging.info('Resizing the template image with a rapport of %f',resize_rapport)       
        dim = (int(w*resize_rapport), int(h*resize_rapport))
        template = cv2.resize(template, dim, interpolation = cv2.INTER_AREA)

        
    
    #The value -1 means we keep the file as is meaning with color and alpha channel if any
    #   btw, 0 means grayscale and 1 is color
    
    #Now we search in the picture
    result = findPicture(screenshot,template, tolerance,allConfigs, multiple)
    #If it didn't get any result, we log the best value
    
    if not result['res']:
        logging.debug('Best value found for %s is: %f',templateFile,result['best_val'])
    else:
        logging.info('Image %s found',templateFile)
        if logging.getLogger().getEffectiveLevel() == 10:
            saveFound = True
        if saveFound or showFound:
            screenshot_with_rectangle = screenshot.copy()
            for pt in result['points']:
                cv2.rectangle(screenshot_with_rectangle, pt['top_left'], pt['bottom_right'], 255, 2)
                fileName_top_left = (pt['top_left'][0],pt['top_left'][1]-10)
                cv2.putText(screenshot_with_rectangle,str(pt['tolerance'])[:4],fileName_top_left, font, 1,(255,255,255),2)
            if saveFound:
                #Now we save to the file if needed
                filename = time.strftime("%Y%m%d-%H%M%S") + '_' + templateFile[:-4] + '.jpg'
                cv2.imwrite(os.path.join(directories['debugdir'] , filename), screenshot_with_rectangle)
            if showFound:
                cv2.imshow('showFound',screenshot_with_rectangle)
                cv2.waitKey(0)
                
    result['name']=templateFile
    
    return result

def waitForImg(images, tolerance, frequency, max_wait_seconds, directories,allConfigs):
    max_wait_number = max_wait_seconds // frequency

    logging.debug('*************Start of waitForImg')
    logging.info('WAITING for: %s',images)
    logging.info('Waiting for maximum %d seconds',max_wait_number * frequency)
    waiting = True
    while waiting:
        
        screenshot = functions_screenshot.screenshotOpencv()
        for image in images:
            img = checkPicture(screenshot,image, tolerance ,directories,allConfigs)
            #Image check
            if img['res']:
                logging.debug('waitForImg will return:')
                logging.debug(img)
                logging.debug('*************End of waitForImg')
                return img

        max_wait_number -= frequency
        if max_wait_number <= 0:
            logging.debug('waitForImg took too much time and will return False')
            logging.debug('*************End of waitForImg')
            return {'res':False}
        time.sleep(frequency)
        
def main():
    print('Functions')
    
if __name__ == "__main__":
    main()
    