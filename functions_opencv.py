import time
import os
import logging
import cv2
import numpy as np
import pyautogui
import functions_screenshot
import sys
from ConfigParser import SafeConfigParser 
import functions_general

def find_min_max(all_squares,axe,minormax):
    if axe == 'x':
        coord = 0
    else:
        coord = 1
    best_result = {}
    best_result['res'] = all_squares['res']
    best_result['points'] = []
    best_result['points'].append(all_squares['points'][0])
    best_result['name'] = all_squares['name']
    
    for point in all_squares['points']:
        if minormax == 'max':
            if point['center'][coord] > best_result['points'][0]['center'][coord]:
                best_result['points'][0] = point
        else:
            if point['center'][coord] < best_result['points'][0]['center'][coord]:
                best_result['points'][0] = point

    return best_result

def scrollMonsterBarRightToLeft(numOfTimes,allConfigs,direction = 'left'):
    for i in xrange(0,numOfTimes):
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        monster_select = checkPicture(screenshot,'monster_select.png', allConfigs['tolerance'] ,allConfigs['directories'],allConfigs, multiple = True)

        most_left_monster = find_min_max(monster_select,'x','min')
        most_right_monster = find_min_max(monster_select,'x','max')

        if direction == 'left':
            pyautogui.moveTo(most_right_monster['points'][0]['top_left'][0],most_right_monster['points'][0]['bottom_right'][1])
            pyautogui.mouseDown()
            pyautogui.moveTo(most_left_monster['points'][0]['top_left'][0]+int(allConfigs['error_correction']['monster_scroll']),most_left_monster['points'][0]['bottom_right'][1],allConfigs['wait_times']['scroll_speed'])
            pyautogui.mouseUp()
            functions_general.randomWait( allConfigs['wait_times']['between_scrolls'],0 )
        else:
            pyautogui.moveTo(most_left_monster['points'][0]['top_left'][0],most_left_monster['points'][0]['bottom_right'][1])
            pyautogui.mouseDown()
            pyautogui.moveTo(most_right_monster['points'][0]['top_left'][0]+int(allConfigs['error_correction']['monster_scroll']),most_right_monster['points'][0]['bottom_right'][1],allConfigs['wait_times']['scroll_speed'])
            pyautogui.mouseUp()
            functions_general.randomWait( allConfigs['wait_times']['between_scrolls'],0 )
    return    

def clickAndReturnMouse(img):
    orig_x,orig_y = pyautogui.position()
    pyautogui.moveTo(img['points'][0]['center'][0],img['points'][0]['center'][1])
    pyautogui.click()
    logging.info('CLICK')
    pyautogui.moveTo(orig_x, orig_y)
    return

def clickAndReturnMouse_point(point):
    orig_x,orig_y = pyautogui.position()
    pyautogui.moveTo(point['center'][0],point['center'][1])
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

    logging.debug('*************Start of findPicture')

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
        return {'res': True,'best_val':best_val,'points':all_matches}
    else:
        bottom_right = (top_left[0] + w, top_left[1] + h)
        center = (top_left[0] + (w/2), top_left[1] + (h/2))
        all_matches = [{'top_left':top_left,'bottom_right':bottom_right,'center':center,'tolerance':best_val}]

        logging.debug('Could not find a value above tolerance')
        logging.debug('*************End of findPicture')
        return {'res': False,'best_val':best_val,'points':all_matches}

def findAllPictureFiles(base_filename,directory):
    allPictureFiles = []
    onlyfiles = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    for myfile in onlyfiles:
        if myfile.startswith(base_filename):
            if not myfile[len(base_filename):].startswith('_'):
                allPictureFiles.append(myfile)
    return allPictureFiles

def twoSquaresDoOverlap(squareA,squareB):
    #The two squares must have coordinates in the form of named list with name top_left and bottom_right
    overlap = True
    if squareA['top_left'][1] > squareB['bottom_right'][1] or \
            squareA['top_left'][0] > squareB['bottom_right'][0] or \
            squareA['bottom_right'][0] < squareB['top_left'][0] or \
            squareA['bottom_right'][1] < squareB['top_left'][1]:
        overlap = False
            
    return overlap
    
def checkPicture(screenshot, templateFile, tolerance_list ,directories,allConfigs,multiple = False, showFound = False, saveFound = False):
    
    #This is an intermediary function so that the actual function doesn't include too much specific arguments

    if templateFile[:-4] in tolerance_list:
        tolerance = float(tolerance_list[templateFile[:-4]])
    else:
        tolerance = float(tolerance_list['global'])

    font = cv2.FONT_HERSHEY_PLAIN
    
    #Here we will detect all files that have the same base name ex: victory.png, victory02.png, ...
    allTemplateFiles = findAllPictureFiles(templateFile[:-4],directories['basepicsdir'])
    result = {}
    result['res'] = False
    result['best_val'] = 0
    result['points'] = []
    
    for templateFile in allTemplateFiles:
    
        template = cv2.imread(os.path.join(directories['basepicsdir'],templateFile),-1)

        #The value -1 means we keep the file as is meaning with color and alpha channel if any
        #   btw, 0 means grayscale and 1 is color

        #Now we search in the picture
        result_temp = findPicture(screenshot,template, tolerance,allConfigs, multiple)
        
        if result_temp['res'] == True:
            if result['res'] == False:
                result['points'] = []
            result['res'] = result_temp['res']
            result['best_val'] = result_temp['best_val']
            #!!!!! Attention, if the images are close to each other, there could be overlaps !!!!!!
            
            for result_temp_point in result_temp['points']:
                overlap = False
                for result_point in result['points']:
                    overlap = twoSquaresDoOverlap(result_point,result_temp_point)
                    if overlap:
                        break
                if not overlap:
                    result['points'].append(result_temp_point)
            result['name']=templateFile

        else:
            if result['res'] == False:
                result['best_val'] = result_temp['best_val']
                result['points'].extend(result_temp['points'])
                result['name']=templateFile
        
    #If it didn't get any result, we log the best value
    if not result['res']:
        logging.debug('Best value found for %s is: %f',templateFile,result['best_val'])
        color_showFound = (0,0,255)
    else:
        logging.info('Image %s found',templateFile)
        if logging.getLogger().getEffectiveLevel() == 10:
            saveFound = True
        color_showFound = (0,255,0)
            
    if saveFound or showFound:
        screenshot_with_rectangle = screenshot.copy()
        for pt in result['points']:
            cv2.rectangle(screenshot_with_rectangle, pt['top_left'], pt['bottom_right'], color_showFound, 2)
            fileName_top_left = (pt['top_left'][0],pt['top_left'][1]-10)
            cv2.putText(screenshot_with_rectangle,str(pt['tolerance'])[:4],fileName_top_left, font, 1,color_showFound,2)
        if saveFound:
            #Now we save to the file if needed
            filename = time.strftime("%Y%m%d-%H%M%S") + '_' + templateFile[:-4] + '.jpg'
            cv2.imwrite(os.path.join(directories['debugdir'] , filename), screenshot_with_rectangle)
        if showFound:
            cv2.imshow('showFound',screenshot_with_rectangle)
            cv2.waitKey(0)
    
    return result

def waitForImg(images, tolerance, frequency, max_wait_seconds, directories,allConfigs):
    max_wait_number = max_wait_seconds // frequency

    logging.debug('*************Start of waitForImg')
    logging.info('WAITING for: %s',images)
    logging.info('Waiting for maximum %d seconds',max_wait_number * frequency)
    
    functions_screenshot.takeScreenshotCoordsFreeze('freeze_test_init.png',directories,(250,120,550,220),allConfigs)
    time_orig = time.time()
    
    waiting = True
    while waiting:
        
        screenshot = functions_screenshot.screenshotOpencv(allConfigs)
        for image in images:
            img = checkPicture(screenshot,image, tolerance ,directories,allConfigs)
            #Image check
            if img['res']:
                logging.debug('waitForImg will return:')
                logging.debug(img)
                logging.debug('*************End of waitForImg')
                return img

        max_wait_number -= frequency
        time_spent = int(time.time() - time_orig)

        if max_wait_number % 10 == 0:
            screenshot = functions_screenshot.screenshotOpencv(allConfigs)
            #screenshot_cropped = cropToCoords(screenshot, [(100,100),(900,400)])
            freeze_test = checkPicture(screenshot,'freeze_test_init.jpg', tolerance ,directories,allConfigs,multiple = False, showFound = False)
            if freeze_test['res']:
                clickAndReturnMouse(freeze_test)
                print 'Freeze detected'
                time.sleep(5)
            functions_screenshot.takeScreenshotCoordsFreeze('freeze_test_init.png',directories,(250,120,550,220),allConfigs)
            
        if max_wait_number <= 0:
            logging.debug('waitForImg took too much time and will return False')
            logging.debug('*************End of waitForImg')
            return {'res':False}
        time.sleep(frequency)
        
def main():
    print('Functions')
    
if __name__ == "__main__":
    main()
    
