#!/usr/bin/python
# -*- coding: utf-8 -*-
### BEGIN LICENSE
#
# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <davy.renaud@laposte.net> wrote this file. As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return Davy Renaud (glyptostroboides)
# ----------------------------------------------------------------------------
#

#    This file is part of bumblebee-ui.
#
#    bumblebee-ui is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    bumblebee-ui is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with bumblebee-ui.  If not, see <http://www.gnu.org/licenses/>.
#
### END LICENSE

####TODO : Maybe i can build a subclass for global file and a subclass for local file : may be also a subclass for configured desktop file
###TODO DesktopFile might be a subclass of ConfigParser so I don't need to refer to config later ?????!!!! : shorted and clean the script, reflect the reality also

import os
import glob
import re
import ConfigParser
import gtk

#TODO: THIS MODULE IS NOT CROSS DISTRIBUTION BUT CAN BE USE FOR DYNAMIC CONFIGURATION
#from gi.repository import Unity, Dbusmenu

#ORIGINAL MODULE
import Config

#FIXME Clean this class and find shorter and cleaner way
class DesktopFileSet:
	"""This class contain list of files in local directory or in global directory and a list of configured files"""
	def __init__(self):
		self.get_local()
		self.get_global()
		self.get_configured_from_cfg()

	def get_desktop_file_set(self, directory):
		return set([re.sub(r'(.*)\.desktop',r'\1',x) for x in glob.glob1( directory, '*.desktop' )])
		
	def get_local (self):
		self.local_set = self.get_desktop_file_set(Config.user_desktop_file_directory)

	def get_global (self):
		self.global_set = self.get_desktop_file_set(Config.global_desktop_file_directory) - self.local_set

	##CAN BE TEST SO THERE IS NO CONFIGURATION FILE BUT THE UPLOAD IS LONGER
	#FIXME The preferred app list should be check dynamically with a special function to parse user file( conf is needed when bumblebee indicator change
#	def get_configured_from_check (self):
#		self.configured_set = set([ app for app in list(self.local_set) if DesktopFile(app).is_configured() ])

	def get_configured_from_cfg (self):
		self.open_cfg()
        	self.configured_set = set(eval(self.ui_config.get('Bumblebee UI','preferred_app')))
	
	def open_cfg (self):
		self.ui_config = ConfigParser.RawConfigParser()
        	self.ui_config.read(Config.ui_config_file_path)
	
	def store_configured (self):
		self.open_cfg()
		self.ui_config.set('Bumblebee UI','preferred_app', str(list(self.configured_set)))
		with open(Config.ui_config_file_path,'w') as file_object: self.ui_config.write(file_object)
	
	def get_apps_info (self):
		for file_name in self.local_set: 
			desktop_file = DesktopFile(file_name, local=True)
			app_info_list = desktop_file.get_app_info()
			app_config = desktop_file.get_app_config()
			if app_config[0]==True : self.configured_set.add(file_name)
			yield app_info_list + [True] + app_config
		self.store_configured()
		for file_name in self.global_set:
			app_info_list = DesktopFile(file_name, local=False).get_app_info()
			yield app_info_list + [True] + 4*[False] + ['default']

		
	def configure_file (self, file_name):
		if file_name in self.local_set:
			DesktopFile(file_name, local=True).add_shortcuts() #False : don't add the tag : created for bumblebee
			print 'Bumblebee Shortcuts added to: ' + file_name
		elif file_name in self.global_set:	
			DesktopFile(file_name, local=False).add_shortcuts() #True : add the tag : created for bumblebee
			self.local_set.add(file_name)
			self.global_set.remove(file_name)
			print 'Bumblebee Shortcuts added to a desktop file created: ' + file_name
		else : print "ERROR : The app name of configured file is not recognized"
		self.configured_set.add(file_name)

	def unconfigure_file (self, file_name):
		if DesktopFile(file_name).unconfigure_file():
			self.local_set.remove(file_name)
			self.global_set.add(file_name)
			print 'Desktop file created for Bumblebee removed: ' + file_name
		else: print 'Desktop file modified for Bumblebee is unconfigured: ' + file_name
		self.configured_set.remove(file_name)

#TODO : Rewrite in order to allow use of the script without user interface		

#MAIN DESKTOP FILE CLASS
class DesktopFile:
###INITIALIZATION OF A DESKTOP FILE OBJECT
	def __init__(self,file_name,local=True):
		"""Function that create a desktop file object that can be parsed"""
		self.file_name_without_extension=file_name
		self.file_name_with_extension=self.file_name_without_extension + ".desktop"
		self.local = local
		if self.local == True : 
			self.file_path = Config.user_desktop_file_directory + self.file_name_with_extension
		elif self.local == False : self.file_path = Config.global_desktop_file_directory + self.file_name_with_extension		
		self.config = ConfigParser.ConfigParser()
		self.config.optionxform = str
		self.config.read(self.file_path)

###FUNCTIONS TO GET THE VALUES INSIDE ALL DESKTOP FILES
	def get_app_info(self):
		"""Function to get values inside a desktop file object : 
		Application Name, File Name, Application Categories List, Application Icon Path"""
		return [self.config.get('Desktop Entry','Name'), self.file_name_without_extension, self.get_category(), self.get_icon_path()]
	
	def get_category(self, app_category=Config.unmatch_categorie[0]):
		"""Function to get the main category if categories are defined in the desktop file"""
		try: 
			for item in reversed(self.config.get('Desktop Entry','Categories').split(';')):
				for matching_item in reversed(Config.categorie_list):
					if item==matching_item[0] : app_category = str(item)
		except ConfigParser.NoOptionError: app_category=Config.uncategorized_categorie[0]
		finally: return app_category
	
	def get_icon_path(self):
		"""Function to get the icon path or the icon name if an icon is defined in the desktop file"""
		try : 
			icon_name=self.config.get('Desktop Entry', 'Icon')
			if os.path.exists(icon_name): return icon_name
			else:
				try : return os.path.splitext(os.path.basename(icon_name))[0]
				except : return Config.default_icon_name	
		except ConfigParser.NoOptionError: 
			return Config.default_icon_name
						
				
	def is_configured(self):
		"""Function to check if the desktop file is configured for Bumblebee or not"""
		try: 
			if (self.config.has_section('BumblebeeDisable Shortcut Group') 
			and self.config.has_section('BumblebeeEnable Shortcut Group')
			and self.config.has_option('Desktop Entry','X-Ayatana-Desktop-Shortcuts')): return True
			else: return False
		except: return False

###FUNCTIONS TO GET VALUE INSIDE LOCAL DESKTOP FILES
	def get_app_config(self):
		"""Function to search for configuration inside a local desktop file object : 
		Configured, (Selected by default : unselected), Mode, 32bits, Compression
		"""
		self.app_exec= self.config.get('Desktop Entry','Exec')
		if self.is_configured(): return [True, True] + self.get_mode()
		else: return [False, False] + [None] + self.get_exec_config(self.app_exec)[1:]
		#else: return [False, False] + [None] + [False] + ['default']
	
	
	def get_mode(self):
		"""Function to get the mode and the exec config in a desktop file"""
		Shortcuts = self.config.get('Desktop Entry', 'X-Ayatana-Desktop-Shortcuts')
		exec_config= self.get_exec_config(self.app_exec)
		if ( 'BumblebeeEnable' in Shortcuts and 'optirun ' in self.app_exec and exec_config[0] == True ):
			return [Config.mode_keys['perf']] + exec_config[1:]
		elif ( 'BumblebeeDisable' in Shortcuts and 'optirun ' in self.app_exec and exec_config[0] == False ) :
			return [Config.mode_keys['eco']] + exec_config[1:]
		elif ( 'BumblebeeDisable' in Shortcuts and not 'optirun ' in self.app_exec ):
			return [Config.mode_keys['option']] + self.get_exec_config(self.config.get('BumblebeeDisable Shortcut Group','Exec'))[1:]
		else: return ['Unrecognized mode'] + exec_config[1:] 
			
	def set_true(arg, next_arg=None): return {arg:True}

	def get_compression(arg, next_arg=None, default=Config.default_compression): 
		if (next_arg in Config.compression_list and next_arg != default): return {arg:next_arg}

	def get_exec_config(self, Exec, i=-1, 
				case={'-32':set_true, '-f':set_true, '-c':get_compression},
				skip=['ecoptirun', 'optirun', '-d', ':0', ':1', ':2'] + Config.compression_list):
		"""Function to search for configuration inside ecoptirun arguments in the desktop file object : 
		Force_eco, 32bits, Compression"""	

		arg_list=re.split(' ',Exec)	
		exec_config={'-f':False, '-32':False, '-c':'default'}
		for arg in arg_list:
			i = i+1
			if arg in case: exec_config.update(case.get(arg)(arg,next_arg=arg_list[i+1]))
			elif arg in skip: continue
			else: break
		return [exec_config['-f']] + [exec_config['-32']] + [exec_config['-c']]

#FUNCTION TO GET THE LIST OF ARGUMENT FOR SUBPROCESS
	def get_exec_list(self):
		return re.split(' ',self.config.get('BumblebeeDisable Shortcut Group','Exec'))
		

###FUNCTIONS TO CONFIGURE THE FILES WITH SHORTCUTS
	def write_config_to_file(self,output_file_name):
		with open(output_file_name,'w') as file_object:
			self.config.write(file_object)
	
	def configure_file(self):
		"""Function to configure the local or global desktop file"""
		if self.local == False:
			try : self.config.set('Desktop Entry', 'Comment', self.config.get('Desktop Entry','Comment') + '(Bumblebee enabled)')
			except ConfigParser.NoOptionError: 
				self.config.set('Desktop Entry', 'Comment', 'This file has been created for Bumblebee (Bumblebee enabled)')		
			self.add_shortcuts()
			os.chmod(Config.user_desktop_file_directory + self.file_name_with_extension,0755)
		elif self.local == True:
			self.add_shortcuts
		
	def add_shortcuts(self):
		"""Function to add shorcut section for bumblebee and add a shortcut to the desktop file object"""
		self.prepend_option('Desktop Entry', 'X-Ayatana-Desktop-Shortcuts', 'BumblebeeDisable')
		Exec = self.config.get('Desktop Entry', 'Exec')
		#TODO Check if this is really needed
		#self.config.set('Desktop Entry','OnlyShowIn','GNOME;Unity;")
		self.add_shortcut_section('BumblebeeDisable Shortcut Group', 'Launch with Bumblebee', 'ecoptirun -f ' + Exec) #Default setting is optional and forced
		self.add_shortcut_section('BumblebeeEnable Shortcut Group', 'Launch without Bumblebee', Exec)
		self.write_config_to_file(Config.user_desktop_file_directory + self.file_name_with_extension)
		if self.local == False: os.chmod(Config.user_desktop_file_directory + self.file_name_with_extension,0755)

	
	def add_shortcut_section(self,Section_title,Section_name,Section_exec):
		self.config.add_section(Section_title)
		self.config.set(Section_title, 'Name', Section_name)
		self.config.set(Section_title, 'Exec', Section_exec)
		self.config.set(Section_title, 'TargetEnvironment', 'Unity')

	def prepend_option(self,section,option,value):
		"""Function to prepend a value to an option inside section of a desktop file object"""
		if self.config.has_option(section,option) == True: self.config.set(section,option, value + ";" + self.config.get(section,option))
		else : self.config.set(section,option,value)
	
###FUNCTIONS TO UNCONFIGURE FILES OR REMOVE THEM
	def is_created(self):
		"""Function to check if the file is tagged as created for Bumblebee or not"""
		try:  #FIXME Bumblebee Enable must not be set in comment but somewhere else 
			if 'Bumblebee enabled' in self.config.get('Desktop Entry','Comment'): return True
			else : return False 
		except ConfigParser.NoOptionError: return False 

	def unconfigure_file(self):
		"""Function to unconfigure a file configured for Bumblebee : remove the shortcuts or remove the file if it's tagged as created for Bumblebee"""
		if self.is_created():
			os.remove(self.file_path)
			return True
		else: 
			self.remove_shortcuts()
			return False
		
	def remove_shortcuts(self):
		"""Function to remove shorcut section for bumblebee and remove the shortcuts to the desktop file object"""
		self.config.set('Desktop Entry','Exec',self.config.get('BumblebeeEnable Shortcut Group','Exec'))
		Shortcuts=self.config.get('Desktop Entry','X-Ayatana-Desktop-Shortcuts')
		if Shortcuts=='BumblebeeDisable' or Shortcuts=='BumblebeeEnable': self.config.remove_option('Desktop Entry','X-Ayatana-Desktop-Shortcuts')
		else : self.remove_prepend_option('Desktop Entry','X-Ayatana-Desktop-Shortcuts','BumblebeeDisable\;|BumblebeeEnable\;')
		self.config.remove_section('BumblebeeDisable Shortcut Group')
		self.config.remove_section('BumblebeeEnable Shortcut Group')
		self.write_config_to_file(self.file_path)

	def remove_prepend_option(self,section,option,value):
		"""Function to remove a value from an option inside section of a desktop file object"""
		if self.config.has_option(section,option) == True: self.config.set(section,option,re.sub(value,'',self.config.get(section,option)))


###FUNCTIONS TO CONFIGURE THE EXECUTION OF THE APPLICATION		
	
	def set_exec_config(self, mode, bits32, compression):
		"""Function to set the option for ecoptirun : default, 32 bits, on battery, compression"""
		option=''
		if bits32==True: option+='-32 '
		if not (compression == "default" or compression == Config.default_compression) : option+='-c '+ compression + ' '
		clean_exec= self.config.get('BumblebeeEnable Shortcut Group','Exec')
		self.config.set('BumblebeeDisable Shortcut Group','Exec','ecoptirun -f ' + option + clean_exec)
		if mode == Config.mode_keys['perf']: 
			self.set_exec_config_default('ecoptirun -f ' + option + clean_exec, 'BumblebeeDisable', 'BumblebeeEnable')
		elif mode == Config.mode_keys['eco']: 
			self.set_exec_config_default('ecoptirun ' + option + clean_exec, 'BumblebeeEnable', 'BumblebeeDisable')
		else: 
			self.set_exec_config_default(clean_exec, 'BumblebeeEnable', 'BumblebeeDisable')
		self.write_config_to_file(self.file_path)
	
	def set_exec_config_default(self,Exec,Initial_shortcut,Final_shortcut):
		self.config.set('Desktop Entry','Exec',Exec)
		self.config.set('Desktop Entry','X-Ayatana-Desktop-Shortcuts', re.sub(Initial_shortcut,Final_shortcut,self.config.get('Desktop Entry','X-Ayatana-Desktop-Shortcuts')))

if __name__=="__main__" : 
	print "DesktopFile.py can't run as a standalone application"
	quit()

