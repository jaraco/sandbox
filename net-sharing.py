"""
Tools for managing internet connection sharing on Windows, inspired by
VirtualRouterPlus
"""

import ctypes
import comtypes
# see jaraco.video for an example of comtypes usage

conn = '...'

get_INetSharingConfigurationForINetConnection = ctypes.windll.hnetcfg.get_INetSharingConfigurationForINetConnection
