#http://msdn.microsoft.com/en-us/library/ms705973%28VS.85%29.aspx
from comtypes.gen import ADHOCLib
from comtypes import GUID
from ctypes import POINTER

mgr = ADHOCLib.Dot11AdHocManager()
networks = mgr.GetIEnumDot11AdHocNetworks()