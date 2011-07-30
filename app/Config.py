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

import os
import glob
import re
import gtk
import ConfigParser

#DESKTOP FILES PATH
user_home_directory = os.path.expanduser('~')
user_relative_desktop_file_directory = '/.local/share/applications/'
user_desktop_file_directory = user_home_directory + user_relative_desktop_file_directory
global_desktop_file_directory = '/usr/share/applications/'

#ICONS FILE PATH
icon_file_directory = '/usr/share/bumblebee-ui/icons/'

#CONFIG FILES PATH
ui_config_file_directory = user_desktop_file_directory
ui_config_file_path = ui_config_file_directory + 'bumblebee-ui.cfg'

#ACCEPTED COMPRESSION
compression_list=['jpeg','proxy','rgb','yuv','xv']

#MODE LIST
#TODO Need to be set to a list maybe
mode_keys={'perf':"Performance",
	'eco':"Power Save",
	'option':"Optional"}

#ICON FILES THEME
icon_size=24
default_icon_name='application-x-executable'

#APP SETTINGS COLOR THEME
configured_color='#00FF33'
to_configure_color='#FFFF33'
to_unconfigure_color='#FF0033'

#BUMBLEBEE DEFAULT CONFIGURATION
config_file_path='/etc/default/bumblebee'
[default_compression]=[re.sub(r'VGL_COMPRESS=(.*)\n', r'\1', line) for line in open(config_file_path) if 'VGL_COMPRESS' in line]

#CATEGORIES CONFIGURATION

####TODO There might be a way to get those key from a menu configuration file
categorie_list=[['Game',	'applications-games'],
		['AudioVideo',	'applications-multimedia'],
		['Graphics',	'applications-graphics'],
		['Network',	'applications-internet'],
		['Office',	'applications-office'],
		['Settings',	'applications-system'],
		['System',	'applications-electronics'],
		['Utility',	'applications-utilities']]
unmatch_categorie=['Miscellaneous','applications-other']
uncategorized_categorie=['Uncategorized', 'application-x-executable']

#TODO : There might be a way to use string formatting to simplify the config definition
#FIXME There must be a better way to store config

if __name__=="__main__" : 
	print "Config.py can't run as a standalone application"
	quit()

