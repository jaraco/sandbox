import ctypes
from ctypes import wintypes

GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
GetCurrentProcess.restype = wintypes.HANDLE
OpenProcessToken = ctypes.windll.advapi32.OpenProcessToken
OpenProcessToken.argtypes = (wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE))
OpenProcessToken.restype = wintypes.BOOL

class LUID(ctypes.Structure):
	_fields_ = [
		('low_part', wintypes.DWORD),
		('high_part', wintypes.LONG),
		]

LookupPrivilegeValue = ctypes.windll.advapi32.LookupPrivilegeValueW
LookupPrivilegeValue.argtypes = (
	wintypes.LPWSTR, # system name
	wintypes.LPWSTR, # name
	ctypes.POINTER(LUID),
	)
LookupPrivilegeValue.restype = wintypes.BOOL

token = wintypes.HANDLE()
TOKEN_ALL_ACCESS = 0xf01ff
res = OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, token)
if not res > 0: raise RuntimeError("Couldn't get process token")
luid = LUID()
res = LookupPrivilegeValue(None, u"SeCreateSymbolicLinkPrivilege", luid)
if not res > 0: raise RuntimeError("Couldn't lookup privilege value")
