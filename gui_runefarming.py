import sys
import os
import time
import logging
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner

from ConfigParser import SafeConfigParser 
import runefarming
import functions_general
import functions_opencv
import functions_screenshot
import functions_calibration

class StartScreen(GridLayout):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)

        self.loadAllConfigs()
        
        self.cols = 1
        self.row_default_height=40
        self.font_size_label = '14sp'
               
        #Stage types
        self.stageTypeLabel = Label(text='Stage type', font_size=self.font_size_label)
        self.stageType = Spinner(
            # default value shown
            text=self.allConfigs['memory']['stage_type'],
            # available values
            values=('cairos', 'xp', 'toa', 'hoh','essence'),
            # just for positioning in our example
            size=(100, 40), 
            font_size=self.font_size_label
            )
        #End
        
        #Stage name
        self.stageNameLabel = Label(text='Stage name', font_size=self.font_size_label)
        self.stageName = TextInput(text=self.allConfigs['memory']['stage_name'],multiline=False,font_size=self.font_size_label)
        #End

        #Logging
        self.appLoggingLabel = Label(text='Logging', font_size=self.font_size_label)
        self.appLogging = Spinner(
            # default value shown
            text='no',
            # available values
            values=('no', 'INFO', 'DEBUG'),
            # just for positioning in our example
            size=(100, 40), 
            font_size=self.font_size_label
            )
        #End
        
        #Window position
        self.windowPositionLabel = Label(text='Resize window\n(Works only in linux)',font_size=self.font_size_label)
        self.windowPosition = Spinner(
            # default value shown
            text='no',
            # available values
            values=('no', 'yes'),
            # just for positioning in our example
            size=(100, 44), 
            font_size=self.font_size_label
            )
        #End
        
        #Number of runs
        self.numOfRunsLabel = Label(text='Max number of runs\n0 for infinity', font_size=self.font_size_label)
        self.numOfRuns = TextInput(text=self.allConfigs['memory']['numofruns'],multiline=False,font_size=self.font_size_label)
        #End

        #Number of recharges
        self.numOfRechargesLabel = Label(text='Max number of\nrecharges', font_size=self.font_size_label)
        self.numOfRecharges = TextInput(text=self.allConfigs['memory']['recharges'],multiline=False,font_size=self.font_size_label)
        #End
        
        #Change fodders
        self.changeFoddersLabel = Label(text='Change fodders',font_size=self.font_size_label)
        self.changeFodders = Spinner(
            # default value shown
            text=self.allConfigs['memory']['change_fodders'],
            # available values
            values=('no', 'yes'),
            # just for positioning in our example
            size=(100, 44), 
            font_size=self.font_size_label
            )
        #End

        
        #Text for XP only
        self.textForXPOnlyLabel = Label(text='Below is only for XP type', font_size=self.font_size_label)
        #End
        
        #Total number of fodders in the list
        self.totalNumOfFoddersLabel = Label(text='Total number of fodders in the list', font_size=self.font_size_label)
        self.totalNumOfFodders = TextInput(text=self.allConfigs['fodder_info']['max_num_of_fodders'],multiline=False,font_size=self.font_size_label)
        #End
        
        #Number of initial scrolls
        self.scrollInitLabel = Label(text='Number of initial scrolls', font_size=self.font_size_label)
        self.scrollInit = TextInput(text=self.allConfigs['fodder_info']['scroll_init'],multiline=False,font_size=self.font_size_label)
        #End
        
        #Number of 6 stars to upgrade
        self.stars6Label = Label(text='Number of 6 stars to upgrade', font_size=self.font_size_label)
        self.stars6 = TextInput(text=self.allConfigs['fodder_info']['6_stars'],multiline=False,font_size=self.font_size_label)
        #End
        
        #Number of 5 stars to upgrade
        self.stars5Label = Label(text='Number of 5 stars to upgrade', font_size=self.font_size_label)
        self.stars5 = TextInput(text=self.allConfigs['fodder_info']['5_stars'],multiline=False,font_size=self.font_size_label)
        #End
        
        #Number of 4 stars to upgrade
        self.stars4Label = Label(text='Number of 4 stars to upgrade', font_size=self.font_size_label)
        self.stars4 = TextInput(text=self.allConfigs['fodder_info']['4_stars'],multiline=False,font_size=self.font_size_label)
        #End
        
        #Number of 3 stars to upgrade
        self.stars3Label = Label(text='Number of 3 stars to upgrade', font_size=self.font_size_label)
        self.stars3 = TextInput(text=self.allConfigs['fodder_info']['3_stars'],multiline=False,font_size=self.font_size_label)
        #End
        
        #Number of 2 stars to upgrade
        self.stars2Label = Label(text='Number of 2 stars to upgrades', font_size=self.font_size_label)
        self.stars2 = TextInput(text=self.allConfigs['fodder_info']['2_stars'],multiline=False,font_size=self.font_size_label)
        #End
        
        #Number of 1 stars to upgrade
        self.stars1Label = Label(text='Number of 1 stars to upgrade', font_size=self.font_size_label)
        self.stars1 = TextInput(text=self.allConfigs['fodder_info']['1_stars'],multiline=False,font_size=self.font_size_label)
        #End
        
        #Go button
        self.go = Button(text="Go")
        self.go.bind(on_press=self.update)
        #End

        box1 = BoxLayout(orientation='horizontal')
        box2 = BoxLayout(orientation='horizontal')
        box3 = BoxLayout(orientation='horizontal')
        box4 = BoxLayout(orientation='horizontal')
        box45 = BoxLayout(orientation='horizontal')
        box5 = BoxLayout(orientation='horizontal')
        box6 = BoxLayout(orientation='horizontal')
        box7 = BoxLayout(orientation='horizontal')
        box8 = BoxLayout(orientation='horizontal')

        boxGo = BoxLayout(orientation='horizontal')

        box1.add_widget(self.stageTypeLabel)
        box1.add_widget(self.stageType)        
        box1.add_widget(self.stageNameLabel)
        box1.add_widget(self.stageName)        
        self.add_widget(box1)
        
        box2.add_widget(self.appLoggingLabel)
        box2.add_widget(self.appLogging)        
        box2.add_widget(self.windowPositionLabel)
        box2.add_widget(self.windowPosition)        
        self.add_widget(box2)
        
        box3.add_widget(self.numOfRunsLabel)
        box3.add_widget(self.numOfRuns)        
        box3.add_widget(self.numOfRechargesLabel)
        box3.add_widget(self.numOfRecharges)        
        self.add_widget(box3)

        box4.add_widget(self.textForXPOnlyLabel)       
        self.add_widget(box4)
        
        box45.add_widget(self.changeFoddersLabel)
        box45.add_widget(self.changeFodders)
        self.add_widget(box45)
        
        box5.add_widget(self.totalNumOfFoddersLabel)
        box5.add_widget(self.totalNumOfFodders)
        box5.add_widget(self.scrollInitLabel)
        box5.add_widget(self.scrollInit)
        self.add_widget(box5)
        
        box6.add_widget(self.stars1Label)
        box6.add_widget(self.stars1)
        box6.add_widget(self.stars2Label)
        box6.add_widget(self.stars2)
        self.add_widget(box6)
        
        box7.add_widget(self.stars3Label)
        box7.add_widget(self.stars3)
        box7.add_widget(self.stars4Label)
        box7.add_widget(self.stars4)
        self.add_widget(box7)
        
        box8.add_widget(self.stars5Label)
        box8.add_widget(self.stars5)
        box8.add_widget(self.stars6Label)
        box8.add_widget(self.stars6)
        self.add_widget(box8)
        
        boxGo.add_widget(self.go)      
        self.add_widget(boxGo)

        #Tools
        self.textForToolsLabel = Label(text='Tools', font_size=self.font_size_label)
        #End
        box9 = BoxLayout(orientation='horizontal')
        box9.add_widget(self.textForToolsLabel)
        self.add_widget(box9)

        #Calibrate button
        self.calibration = Button(text="Launch calibration")
        self.calibration.bind(on_press=self.launchCalibration)
        #End
        
        box10 = BoxLayout(orientation='horizontal')
        box10.add_widget(self.calibration)      
        self.add_widget(box10)

        #Look for image
        self.imageNameLabel = Label(text='Image name', font_size=self.font_size_label)
        self.imageName = TextInput(text=self.allConfigs['memory']['image_name'],multiline=False,font_size=self.font_size_label)
        #End
        
        box11 = BoxLayout(orientation='horizontal')
        box11.add_widget(self.imageNameLabel)  
        box11.add_widget(self.imageName)        
        self.add_widget(box11)
        
        #Look for image button
        self.lookForImage = Button(text="Launch look for image tool")
        self.lookForImage.bind(on_press=self.launchLookForImage)
        #End
        
        box12 = BoxLayout(orientation='horizontal')
        box12.add_widget(self.lookForImage)      
        self.add_widget(box12)

    def launchCalibration(self,instance):
        self.saveAllConfigs()
        functions_calibration.calibrate(self.allConfigs['runefarmingFoddersFiles'],self.tolerance,self.directories,self.allConfigs)
        return
        
    def launchLookForImage(self,instance):
        self.saveAllConfigs()
        screenshot = functions_screenshot.screenshotOpencv()
        result = functions_opencv.checkPicture(screenshot,self.imageName.text, self.tolerance, self.directories,self.allConfigs, multiple = True, showFound = True)
        if not result['res']:
            if self.imageName.text[:-4] in self.tolerance:
                myTolerance = float(self.tolerance[self.imageName.text[:-4]])
            else:
                myTolerance = float(self.tolerance['global'])
            print ('Tolerance for file %s is: %f' % (self.imageName.text,myTolerance))
            print ('Best tolerance found is: %f' % (result['best_val']))
        return
        
    def update(self,instance):
        self.saveAllConfigs()
        if self.changeFodders.text == 'yes':
            no_change_fodders = False
        else:
            no_change_fodders = True
        
        runefarming.running(self.stageType.text,self.stageName.text,no_change_fodders,int(self.numOfRecharges.text),int(self.numOfRuns.text), self.tolerance, self.wait_times, self.directories,self.calibration,self.allConfigs)
        return
        
    def moveWindow(self):
        #Before Starting, make sure to use wmctrl -r Vysor -e 1,0,0,800,-1
        #The window size should be 800 x 450
        #This is to ensure we have always the same siz and that pixels won't be off
        os.system('wmctrl -r Vysor -e 1,'+str(self.allConfigs['position']['window_pos_x'])+','+str(self.allConfigs['position']['window_pos_y'])+','+str(self.allConfigs['position']['window_width'])+',-1')
        #Now we make sure the window is active and in front on the desktop
        os.system('wmctrl -a Vysor')
        time.sleep(1)
        
    def loadAllConfigs(self):
        self.tolerance, self.wait_times, self.directories, self.calibration, self.allConfigs = runefarming.initConfigs()
        
        self.runeFarmingFodders = SafeConfigParser()
        self.runeFarmingFodders.read(self.allConfigs['runefarmingFoddersFiles'])
        
        self.allConfigs['fodder_info'] = dict(self.runeFarmingFodders.items('max_num_of_fodders_to_upgrade'))

        self.memory = SafeConfigParser()
        self.memory.read(self.allConfigs['memoryFiles'])
        
        self.allConfigs['memory'] = {}
        self.allConfigs['memory']['recharges'] = self.memory.get('xp','recharges')
        self.allConfigs['memory']['numofruns'] = self.memory.get('xp','numofruns')
        self.allConfigs['memory']['stage_type'] = self.memory.get('xp','stage_type')
        self.allConfigs['memory']['stage_name'] = self.memory.get('xp','stage_name')
        self.allConfigs['memory']['position'] = self.memory.get('xp','position')
        self.allConfigs['memory']['change_fodders'] = self.memory.get('xp','change_fodders')
        self.allConfigs['memory']['logging'] = self.memory.get('xp','logging')
        self.allConfigs['memory']['image_name'] = self.memory.get('xp','image_name')
    
    def saveAllConfigs(self):
        self.memory.set('xp', 'stage_type', self.stageType.text)
        self.memory.set('xp', 'stage_name', self.stageName.text)
        self.memory.set('xp', 'numofruns', self.numOfRuns.text)
        self.memory.set('xp', 'recharges', self.numOfRecharges.text)
        
        self.memory.set('xp', 'position', self.windowPosition.text)
        self.memory.set('xp', 'logging', self.appLogging.text)
        self.memory.set('xp', 'image_name', self.imageName.text)
        self.memory.set('xp', 'change_fodders', self.changeFodders.text)

        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', 'max_num_of_fodders', self.totalNumOfFodders.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', 'scroll_init', self.scrollInit.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '6_stars', self.stars6.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '5_stars', self.stars5.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '4_stars', self.stars4.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '3_stars', self.stars3.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '2_stars', self.stars2.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '1_stars', self.stars1.text)

        #We finish by writing everything in the config file
        with open(self.allConfigs['runefarmingFoddersFiles'], 'wb') as f:
            self.runeFarmingFodders.write(f)

        #We finish by writing everything in the config file
        with open(self.allConfigs['memoryFiles'], 'wb') as f:
            self.memory.write(f)

        if self.appLogging.text != 'no':
            # set up logging to file - see previous section for more details
            logging.basicConfig(level=self.appLogging.text,\
                                format='%(asctime)s:%(levelname)s:%(message)s')
        else:
            logger = logging.getLogger()
            logger.disabled = True
        return

class MyApp(App):
    def build(self):
        return StartScreen()


if __name__ == '__main__':
     
    MyApp().run()
