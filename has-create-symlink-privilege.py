from __future__ import print_function
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

	def __eq__(self, other):
		return (
			self.high_part == other.high_part and
			self.low_part == other.low_part
			)

	def __ne__(self, other):
		return not (self==other)

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
symlink_luid = LUID()
res = LookupPrivilegeValue(None, u"SeCreateSymbolicLinkPrivilege", symlink_luid)
if not res > 0: raise RuntimeError("Couldn't lookup privilege value")

class TOKEN_INFORMATION_CLASS:
	TokenUser = 1
	TokenGroups = 2
	TokenPrivileges = 3
	# ... see http://msdn.microsoft.com/en-us/library/aa379626%28VS.85%29.aspx

SE_PRIVILEGE_ENABLED_BY_DEFAULT = (0x00000001L)
SE_PRIVILEGE_ENABLED            = (0x00000002L)
SE_PRIVILEGE_REMOVED            = (0x00000004L)
SE_PRIVILEGE_USED_FOR_ACCESS    = (0x80000000L)

class LUID_AND_ATTRIBUTES(ctypes.Structure):
	_fields_ = [
		('LUID', LUID),
		('attributes', wintypes.DWORD),
		]

	def is_enabled(self):
		return bool(self.attributes & SE_PRIVILEGE_ENABLED)

	def get_name(self):
		size = wintypes.DWORD(10240)
		buf = ctypes.create_unicode_buffer(size.value)
		res = LookupPrivilegeName(None, self.LUID, buf, size)
		if res == 0: raise RuntimeError
		return buf[:size.value]

	def __str__(self):
		res = self.get_name()
		if self.is_enabled(): res += ' (enabled)'
		return res

LookupPrivilegeName = ctypes.windll.advapi32.LookupPrivilegeNameW
LookupPrivilegeName.argtypes = (
	wintypes.LPWSTR, # lpSystemName
	ctypes.POINTER(LUID), # lpLuid
	wintypes.LPWSTR, # lpName
	ctypes.POINTER(wintypes.DWORD), #cchName
	)
LookupPrivilegeName.restype = wintypes.BOOL

class TOKEN_PRIVILEGES(ctypes.Structure):
	_fields_ = [
		('count', wintypes.DWORD),
		('privileges', LUID_AND_ATTRIBUTES*0),
		]

	def get_array(self):
		array_type = LUID_AND_ATTRIBUTES*self.count
		privileges = ctypes.cast(self.privileges, ctypes.POINTER(array_type)).contents
		return privileges

	def __iter__(self):
		return iter(self.get_array())

GetTokenInformation = ctypes.windll.advapi32.GetTokenInformation
GetTokenInformation.argtypes = [
	wintypes.HANDLE, # TokenHandle
	ctypes.c_uint, # TOKEN_INFORMATION_CLASS value
	ctypes.c_void_p, # TokenInformation
	wintypes.DWORD, # TokenInformationLength
	ctypes.POINTER(wintypes.DWORD), # ReturnLength
	]
GetTokenInformation.restype = wintypes.BOOL

# first call with zero length to determine what size buffer we need

return_length = wintypes.DWORD()
params = [
	token,
	TOKEN_INFORMATION_CLASS.TokenPrivileges,
	None,
	0,
	return_length,
	]

res = GetTokenInformation(*params)

# assume we now have the necessary length in return_length

buffer = ctypes.create_string_buffer(return_length.value)
params[2] = buffer
params[3] = return_length.value

res = GetTokenInformation(*params)
assert res > 0, "Error in second GetTokenInformation (%d)" % res

privileges = ctypes.cast(buffer, ctypes.POINTER(TOKEN_PRIVILEGES)).contents
print("found {0} privileges".format(privileges.count))

map(print, privileges)
