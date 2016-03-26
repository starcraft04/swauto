import sys
import os
import time
import logging
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.dropdown import DropDown

from ConfigParser import SafeConfigParser 
import runefarming
import functions_general

class StartScreen(GridLayout):
    def __init__(self, **kwargs):
        super(StartScreen, self).__init__(**kwargs)

        #Loading all configs
        #We read the config file
        self.configFile = 'runefarming.ini'
        self.config = SafeConfigParser()
        self.config.read(self.configFile)

        self.runeFarmingFoddersFile = 'runefarming_fodders.ini'
        self.runeFarmingFodders = SafeConfigParser()
        self.runeFarmingFodders.read(self.runeFarmingFoddersFile)

        self.memoryFile = 'memory.ini'
        self.memory = SafeConfigParser()
        self.memory.read(self.memoryFile)
        
        self.fodder_info = dict(self.runeFarmingFodders.items('max_num_of_fodders_to_upgrade'))
        self.loadAllConfigs()
        
        self.memory_xp = {}
        self.memory_xp['recharges'] = self.memory.get('xp','recharges')
        self.memory_xp['numOfRuns'] = self.memory.get('xp','numOfRuns')
        self.memory_xp['stage_type'] = self.memory.get('xp','stage_type')
        self.memory_xp['stage_name'] = self.memory.get('xp','stage_name')
        self.memory_xp['position'] = self.memory.getboolean('xp','position')
        self.memory_xp['no_change_fodders'] = self.memory.getboolean('xp','no_change_fodders')
        self.memory_xp['troubleshoot'] = self.memory.getboolean('xp','troubleshoot')
        self.memory_xp['logToConsole'] = self.memory.getboolean('xp','logToConsole')
        self.memory_xp['no_logging'] = self.memory.getboolean('xp','no_logging')

        self.cols = 4
        
        self.add_widget(Label(text='Total number of fodders'))
        self.max_num_of_fodders = TextInput(text=self.fodder_info['max_num_of_fodders'],multiline=False)
        self.add_widget(self.max_num_of_fodders)

        self.add_widget(Label(text='Start with a number of full scrolls'))
        self.scroll_init = TextInput(text=self.fodder_info['scroll_init'],multiline=False)
        self.add_widget(self.scroll_init)

        self.add_widget(Label(text='Number of 6 stars to upgrade'))
        self.stars6 = TextInput(text=self.fodder_info['6_stars'],multiline=False)
        self.add_widget(self.stars6)

        self.add_widget(Label(text='Number of 5 stars to upgrade'))
        self.stars5 = TextInput(text=self.fodder_info['5_stars'],multiline=False)
        self.add_widget(self.stars5)

        self.add_widget(Label(text='Number of 4 stars to upgrade'))
        self.stars4 = TextInput(text=self.fodder_info['4_stars'],multiline=False)
        self.add_widget(self.stars4)

        self.add_widget(Label(text='Number of 3 stars to upgrade'))
        self.stars3 = TextInput(text=self.fodder_info['3_stars'],multiline=False)
        self.add_widget(self.stars3)

        self.add_widget(Label(text='Number of 2 stars to upgrade'))
        self.stars2 = TextInput(text=self.fodder_info['2_stars'],multiline=False)
        self.add_widget(self.stars2)

        self.add_widget(Label(text='Number of 1 stars to upgrade'))
        self.stars1 = TextInput(text=self.fodder_info['1_stars'],multiline=False)
        self.add_widget(self.stars1)
        
        self.add_widget(Label(text='Max number of recharges allowed'))
        self.recharges = TextInput(text=self.memory_xp['recharges'],multiline=False)
        self.add_widget(self.recharges)
        
        self.add_widget(Label(text='Max number of runs allowed'))
        self.numOfRuns = TextInput(text=self.memory_xp['numOfRuns'],multiline=False)
        self.add_widget(self.numOfRuns)
        
        stageTypes_dropdown = DropDown()
        stageTypes = ['cairos', 'xp', 'toa','hoh']
        for stageType in stageTypes:
            # when adding widgets, we need to specify the height manually (disabling
            # the size_hint_y) so the dropdown can calculate the area it needs.
            btn = Button(text='%s' % stageType, size_hint_y=None, height=30)

            # for each button, attach a callback that will call the select() method
            # on the dropdown. We'll pass the text of the button as the data of the
            # selection.
            btn.bind(on_release=lambda btn: stageTypes_dropdown.select(btn.text))

            # then add the button inside the dropdown
            stageTypes_dropdown.add_widget(btn)

        # create a big main button
        self.stageType_mainbutton = Button(text='Stage type', size_hint=(1, 1)) 

        # show the dropdown menu when the main button is released
        # note: all the bind() calls pass the instance of the caller (here, the
        # mainbutton instance) as the first argument of the callback (here,
        # dropdown.open.).
        self.stageType_mainbutton.bind(on_release=stageTypes_dropdown.open)
        #dd_btn.bind(on_release=dropdown.open)

        # one last thing, listen for the selection in the dropdown list and
        # assign the data to the button text.
        stageTypes_dropdown.bind(on_select=lambda instance, x: setattr(self.stageType_mainbutton, 'text', x))
        #dropdown.bind(on_select=lambda instance, x: setattr(dd_btn, 'text', x))

        self.add_widget(self.stageType_mainbutton)
        
        self.add_widget(Label(text='Stage name'))
        self.stage_name = TextInput(text=self.memory_xp['stage_name'],multiline=False)
        self.add_widget(self.stage_name)
        
        if self.memory_xp['position']:
            state = 'down'
        else:
            state = 'normal'
        self.position = ToggleButton(text='Change window position', state=state)
        self.add_widget(self.position)

        if self.memory_xp['no_change_fodders']:
            state = 'down'
        else:
            state = 'normal'
        self.no_change_fodders = ToggleButton(text='Do not change fodders', state=state)
        self.add_widget(self.no_change_fodders)
        
        if self.memory_xp['no_logging']:
            state = 'down'
        else:
            state = 'normal'
        self.no_logging = ToggleButton(text='No logging', state=state, group='troubleshoot')
        self.add_widget(self.no_logging)
        
        if self.memory_xp['troubleshoot']:
            state = 'down'
        else:
            state = 'normal'
        self.troubleshoot = ToggleButton(text='Logging to file', state=state, group='troubleshoot')
        self.add_widget(self.troubleshoot)
        
        if self.memory_xp['logToConsole']:
            state = 'down'
        else:
            state = 'normal'
        self.logToConsole = ToggleButton(text='Logging to console', state=state, group='troubleshoot')
        self.add_widget(self.logToConsole)

        logLevels_dropdown = DropDown()
        logLevels = ['INFO', 'DEBUG']
        for logLevel in logLevels:
            # when adding widgets, we need to specify the height manually (disabling
            # the size_hint_y) so the dropdown can calculate the area it needs.
            btn = Button(text='%s' % logLevel, size_hint_y=None, height=30)

            # for each button, attach a callback that will call the select() method
            # on the dropdown. We'll pass the text of the button as the data of the
            # selection.
            btn.bind(on_release=lambda btn: logLevels_dropdown.select(btn.text))

            # then add the button inside the dropdown
            logLevels_dropdown.add_widget(btn)

        # create a big main button
        self.logLevel_mainbutton = Button(text='Logging level', size_hint=(1, 1)) 

        # show the dropdown menu when the main button is released
        # note: all the bind() calls pass the instance of the caller (here, the
        # mainbutton instance) as the first argument of the callback (here,
        # dropdown.open.).
        self.logLevel_mainbutton.bind(on_release=logLevels_dropdown.open)
        #dd_btn.bind(on_release=dropdown.open)

        # one last thing, listen for the selection in the dropdown list and
        # assign the data to the button text.
        logLevels_dropdown.bind(on_select=lambda instance, x: setattr(self.logLevel_mainbutton, 'text', x))
        #dropdown.bind(on_select=lambda instance, x: setattr(dd_btn, 'text', x))

        self.add_widget(self.logLevel_mainbutton)
        
        self.go = Button(text="Go")
        self.go.bind(on_press=self.update)
        self.add_widget(self.go)

    def update(self,instance):
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', 'max_num_of_fodders', self.max_num_of_fodders.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', 'scroll_init', self.scroll_init.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '6_stars', self.stars6.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '5_stars', self.stars5.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '4_stars', self.stars4.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '3_stars', self.stars3.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '2_stars', self.stars2.text)
        self.runeFarmingFodders.set('max_num_of_fodders_to_upgrade', '1_stars', self.stars1.text)

        self.memory.set('xp', 'recharges', self.recharges.text)
        self.memory.set('xp', 'numOfRuns', self.numOfRuns.text)
        self.memory.set('xp', 'stage_name', self.stage_name.text)
        if self.position.state == 'down':
            position_state = 'True'
            self.moveWindow()
        else:
            position_state = 'False'
        self.memory.set('xp', 'position', position_state)
        if self.no_change_fodders.state == 'down':
            no_change_fodders_state = True
        else:
            no_change_fodders_state = False
        self.memory.set('xp', 'no_change_fodders', str(no_change_fodders_state))
        if self.troubleshoot.state == 'down':
            troubleshoot_state = 'True'
        else:
            troubleshoot_state = 'False'
        self.memory.set('xp', 'troubleshoot', troubleshoot_state)
        if self.logToConsole.state == 'down':
            logToConsole_state = 'True'
        else:
            logToConsole_state = 'False'
        self.memory.set('xp', 'logToConsole', logToConsole_state)
        if self.no_logging.state == 'down':
            no_logging_state = 'True'
        else:
            no_logging_state = 'False'
        self.memory.set('xp', 'no_logging', no_logging_state)

        if not no_logging_state:
            if logToConsole_state:
                logging.basicConfig(level=self.logLevel_mainbutton.text,\
                                format='%(asctime)s:%(levelname)s:%(message)s')
            elif troubleshoot_state:
                logging.basicConfig(filename='runefarming.log',\
                                level=self.logLevel_mainbutton.text,\
                                format='%(asctime)s:%(levelname)s:%(message)s')
        else:
            print('No logging requested')
            logger = logging.getLogger()
            logger.disabled = True
                                
        self.stage_type = self.stageType_mainbutton.text
        self.stage_name = self.stage_name.text
        self.no_change_fodders = self.no_change_fodders.text
        self.recharge = int(self.recharges.text)
        self.number_of_time = int(self.numOfRuns.text)

        #We finish by writing everything in the config file
        with open(self.runeFarmingFoddersFile, 'wb') as f:
            self.runeFarmingFodders.write(f)

        #We finish by writing everything in the config file
        with open(self.memoryFile, 'wb') as f:
            self.memory.write(f)

        runefarming.running(self.stage_type,self.stage_name,self.no_change_fodders,self.recharge,self.number_of_time, self.tolerance, self.wait_times, self.directories,self.calibration,self.allConfigs)

        return

    def moveWindow(self):
        #Before Starting, make sure to use wmctrl -r Vysor -e 1,0,0,800,-1
        #The window size should be 800 x 450
        #This is to ensure we have always the same siz and that pixels won't be off
        #We read the config file
        window_pos_x = int(self.config.get('position','window_pos_x'))
        window_pos_y = int(self.config.get('position','window_pos_y'))
        window_width = int(self.config.get('position','window_width'))
        os.system('wmctrl -r Vysor -e 1,'+str(window_pos_x)+','+str(window_pos_y)+','+str(window_width)+',-1')
        #Now we make sure the window is active and in front on the desktop
        os.system('wmctrl -a Vysor')
        time.sleep(1)
        
    def loadAllConfigs(self):
        self.allConfigs = {}
        
        self.allConfigs['runefarmingFoddersFiles'] = 'runefarming_fodders.ini'
     
        self.tolerance = dict(self.config.items('tolerance'))

        self.allConfigs['tolerance'] = self.tolerance

        self.wait_times = {}
        self.wait_times['image_wait'] = int(self.config.get('wait','image'))
        self.wait_times['max_wait_seconds'] = int(self.config.get('wait','max_wait_seconds'))
        self.wait_times['max_run_wait_seconds'] = int(self.config.get('wait','max_run_wait_seconds'))
        self.wait_times['screen_victory_wait'] = int(self.config.get('wait','victory'))
        self.wait_times['screen_networkDelayed_wait'] = int(self.config.get('wait','networkDelayed'))
        self.wait_times['screen_autorun_wait'] = int(self.config.get('wait','autorun'))
        self.wait_times['screen_revive_wait'] = int(self.config.get('wait','revive'))
        self.wait_times['screen_defeated_wait'] = int(self.config.get('wait','defeated'))
        self.wait_times['screen_replay_wait'] = int(self.config.get('wait','replay'))
        self.wait_times['screen_startBattle_wait'] = int(self.config.get('wait','startBattle'))
        self.wait_times['screen_notEnoughEnergy_wait'] = int(self.config.get('wait','notEnoughEnergy'))
        self.wait_times['screen_giftTOAHOH_wait'] = int(self.config.get('wait','giftTOAHOH'))
        self.wait_times['screen_giftCAIROSXP_wait'] = int(self.config.get('wait','giftCAIROSXP'))
        self.wait_times['screen_chest_wait'] = int(self.config.get('wait','chest'))
        self.wait_times['screen_wait_random'] = int(self.config.get('wait','random'))
        self.wait_times['screen_not_enough_energy_buy_yes_wait'] = int(self.config.get('wait','not_enough_energy_buy_yes'))
        self.wait_times['screen_max_level_wait'] = int(self.config.get('wait','max_level'))
        self.wait_times['room_in_inventory'] = int(self.config.get('wait','room_in_inventory'))
        
        self.allConfigs['wait_times'] = self.wait_times
        
        myPath = os.path.dirname(os.path.abspath(__file__))
        self.directories = {}
        self.directories['basepicsdir'] = os.path.join(myPath,self.config.get('dir', 'basepics'))
        self.directories['debugdir'] = os.path.join(myPath,self.config.get('dir', 'debug'))
        self.directories['picsdir'] = os.path.join(myPath,self.config.get('dir', 'savedpics'))

        self.allConfigs['directories'] = self.directories

        self.calibration = {}
        self.calibration['fodder_right'] = functions_general.fromStringToTuple(self.config.get('calibration', 'fodder_right'))
        self.calibration['fodder_bottom'] = functions_general.fromStringToTuple(self.config.get('calibration', 'fodder_bottom'))
        self.calibration['fodder_left'] = functions_general.fromStringToTuple(self.config.get('calibration', 'fodder_left'))
        self.calibration['level_top_left'] = functions_general.fromStringToTuple(self.config.get('calibration', 'level_top_left'))
        self.calibration['level_bottom_right'] = functions_general.fromStringToTuple(self.config.get('calibration', 'level_bottom_right'))
        self.calibration['level_close'] = functions_general.fromStringToTuple(self.config.get('calibration', 'level_close'))
        self.calibration['scroll_left_first'] = functions_general.fromStringToTuple(self.config.get('calibration', 'scroll_left_first'))
        self.calibration['scroll_left_last'] = functions_general.fromStringToTuple(self.config.get('calibration', 'scroll_left_last'))
        self.calibration['numoffoddersinlist'] = int(self.config.get('calibration', 'numoffoddersinlist'))
        self.calibration['monster_icon_width'] = int(self.config.get('calibration', 'monster_icon_width'))
        for i in xrange(1,int(self.calibration['numoffoddersinlist'])+1):
            self.calibration['fodder_'+str(i)+'_center'] = functions_general.fromStringToTuple(self.config.get('calibration', 'fodder_'+str(i)+'_center'))

        self.allConfigs['calibration'] = self.calibration

        self.resize = {}
        self.resize['resize_or_not'] = self.config.getboolean('resize','resize_or_not')
        self.resize['rapport'] = self.config.getfloat('resize','rapport')

        self.allConfigs['resize'] = self.resize
        
class MyApp(App):
    def build(self):
        return StartScreen()


if __name__ == '__main__':
     
    MyApp().run()
