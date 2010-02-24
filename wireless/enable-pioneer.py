from comtypes.client import GetModule
GetModule('adhoc.tlb')
from comtypes.gen import ADHOCLib
from comtypes import GUID
from ctypes import POINTER

# fails with
"""
{45357166-FF38-4302-8F5C-DF5B703A6E3D}
Traceback (most recent call last):
  File "C:\Python\lib\pdb.py", line 1283, in main
    pdb._runscript(mainpyfile)
  File "C:\Python\lib\pdb.py", line 1202, in _runscript
    self.run(statement)
  File "C:\Python\lib\bdb.py", line 368, in run
    exec cmd in globals, locals
  File "<string>", line 1, in <module>
  File ".\enable-pioneer.py", line 7, in <module>
    mgr = ADHOCLib.Dot11AdHocManager()
  File "C:\Python\lib\site-packages\comtypes-0.6.3dev-py2.6.egg\comtypes\_comobject.py", line 348, in __new__
    self.__prepare_comobject()
  File "C:\Python\lib\site-packages\comtypes-0.6.3dev-py2.6.egg\comtypes\_comobject.py", line 375, in __prepare_comobject
    self._COMObject__typelib = LoadRegTypeLib(*self._reg_typelib_)
  File "C:\Python\lib\site-packages\comtypes-0.6.3dev-py2.6.egg\comtypes\typeinfo.py", line 473, in LoadRegTypeLib
    _oleaut32.LoadRegTypeLib(byref(GUID(guid)), wMajorVerNum, wMinorVerNum, lcid, byref(tlib))
  File "_ctypes/callproc.c", line 925, in GetResult
WindowsError: [Error -2147319779] Library not registered"""
mgr = ADHOCLib.Dot11AdHocManager()
networks = mgr.GetIEnumDot11AdHocNetworks()