from comtypes.gen import ADHOCLib
from comtypes import GUID
from ctypes import POINTER

mgr = ADHOCLib.IDot11AdHocManager()
p = POINTER(GUID)()
mgr.GetIEnumDot11AdHocNetworks(mgr)