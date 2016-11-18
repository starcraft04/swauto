import time
import logging
import sys
import os
from random import randint
from ConfigParser import SafeConfigParser
import win32gui
import re
import ctypes
import functions_screenshot
import functions_opencv

def randomWait(wait_time, random_wait):
    wait_time = wait_time + randint(0,random_wait)
    time.sleep(wait_time)
    
def fromStringToTuple(string):
    string = string.replace(' ', '')
    string = string.replace('(', '')
    string = string.replace(')', '')
    string = string.split(',')
    coords = (int(string[0]),int(string[1]))
    return coords

def dictStringToInt(d):
    for key, value in d.iteritems():
        try:
            d[key] = int(value)
        except ValueError:
            d[key] = str(value)
    return d

def initConfigs():
    
    #Getting the path to the program
    if getattr(sys, 'frozen', False):
	    # frozen
	    myPath = os.path.dirname(sys.executable)
    else:
        # unfrozen
        myPath = os.path.dirname(os.path.realpath(__file__))
        
    #Let's check we have the empty directory debug in case we need it
    try:
        os.makedirs('debug')
    except OSError:
        if os.path.exists('debug'):
            # We are nearly safe
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise
    #Now we check the log file exists
    logFile = os.path.join('debug','runefarming.log')
    file = open(logFile, 'w')
    
    #Loading all configs
    #We read the config file
    configFile = os.path.join('config','runefarming.ini')
    config = SafeConfigParser()
    config.read(configFile)
    
    allConfigs = {}
    
    allConfigs['runefarmingFoddersFiles'] = os.path.join('config','runefarming_fodders.ini')
    allConfigs['logFiles'] = logFile
 
    tolerance = dict(config.items('tolerance'))

    allConfigs['tolerance'] = tolerance

    wait_times_string = dict(config.items('wait'))
    wait_times = dictStringToInt(wait_times_string)
    
    allConfigs['wait_times'] = wait_times
	
    directories = {}
    directories['basepicsdir'] = os.path.join(myPath,config.get('dir', 'basepics'))
    directories['debugdir'] = os.path.join(myPath,config.get('dir', 'debug'))
    directories['picsdir'] = os.path.join(myPath,config.get('dir', 'savedpics'))

    allConfigs['directories'] = directories

    resize = {}
    resize['resize_or_not'] = config.getboolean('resize','resize_or_not')
    resize['rapport'] = config.getfloat('resize','rapport')

    allConfigs['resize'] = resize
    
    position_string = dict(config.items('position'))
    position = dictStringToInt(position_string)
    
    allConfigs['position'] = position
    
    error_correction = {}
    error_correction['monster_scroll'] = int(config.get('error_correction','monster_scroll'))
    
    allConfigs['error_correction'] = error_correction

    return tolerance, wait_times, directories, allConfigs

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

    def move_window(self,x,y,w,h,allConfigs,i):
        """put the window in the foreground"""
        win32gui.MoveWindow(self._handle, x,y,w,h, True)
        
    def get_original_window_size(self,allConfigs):
        rect = win32gui.GetWindowRect(self._handle)
        x = rect[0]
        y = rect[1]
        orig_width = rect[2] - x
        orig_height = rect[3] - y
        return x,y,orig_width, orig_height
           
def windowResizeAndPosition(workspace,allConfigs):        
    i = str(allConfigs['position']['window'])
    w = WindowMgr()
    w.find_window_wildcard(".*"+allConfigs['position']['window_name_'+i]+".*")
    w.set_foreground()
    w.move_window(allConfigs['position']['window_pos_x_'+i], allConfigs['position']['window_pos_y_'+i], allConfigs['position']['window_width_'+i], allConfigs['position']['window_height_'+i],allConfigs,i)

def calibrate(tolerance, directories,allConfigs):
    testFile = allConfigs['position']['testfile']
    iteration = allConfigs['position']['calibration_num_of_iteration']
    print ('Go to a scenario where you have to select your monsters')
    print ('As soon as enter is pressed, you will go through several screens and try to note down the image where most of your monsters are selected')
    raw_input("Press Enter to continue...")
    i = str(allConfigs['position']['window'])
    w = WindowMgr()
    w.find_window_wildcard(".*"+allConfigs['position']['window_name_'+i]+".*")
    w.set_foreground()
    orig_x,orig_y,orig_width, orig_height = w.get_original_window_size(allConfigs)
    new_width = allConfigs['position']['window_width_'+i]
    rapport = float(new_width)/float(orig_width)
    new_height = int(rapport*orig_height)
    print "Orig width: %d - Orig height: %d" % (orig_width,orig_height)
    print "New width: %d - New height: %d" % (new_width,new_height)
    for test_height in range(new_height-iteration,new_height+iteration):
        print "Testing with height of %d" % (test_height)
        print "Select window called showFound and hit enter"
        w.move_window(allConfigs['position']['window_pos_x_'+i], allConfigs['position']['window_pos_y_'+i], new_width, test_height,allConfigs,i)
        imageTest(testFile,tolerance, directories,allConfigs)
    
    best_height = raw_input('Which height gave the best result:')
    
    #We read the config file
    configFile = os.path.join('config','runefarming.ini')
    config = SafeConfigParser()
    config.read(configFile)
    
    config.set('position', 'window_height_'+i, str(best_height))
    
    #We finish by writing everything in the config file
    with open(configFile, 'wb') as f:
        config.write(f)
    
def imageTest(testFile,tolerance, directories,allConfigs):
    screenshot = functions_screenshot.screenshotOpencv(allConfigs)
    result = functions_opencv.checkPicture(screenshot,testFile, tolerance, directories,allConfigs, multiple = True, showFound = True)
    if not result['res']:
        if testFile[:-4] in tolerance:
            tolerance = float(tolerance[testFile[0][:-4]])
        else:
            tolerance = float(tolerance['global'])
        print ('Tolerance for file %s is: %f' % (testFile,tolerance))
        print ('Best tolerance found is: %f' % (result['best_val']))

def main():
    print('function general')
    
if __name__ == "__main__":
    main()
