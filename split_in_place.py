from __future__ import division
import os
import sys
from win32file import CreateFile, SetEndOfFile, GetFileSize, SetFilePointer, ReadFile, WriteFile
import win32con
from itertools import tee, izip, imap

def xfrange(start, stop=None, step=None):
	"""
	Like xrange(), but returns list of floats instead

	All numbers are generated on-demand using generators
	"""

	if stop is None:
		stop = float(start)
		start = 0.0

	if step is None:
		step = 1.0

	cur = float(start)

	while cur < stop:
		yield cur
		cur += step


# from Python 2.6 docs
def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def get_one_hundred_pieces(size):
	"""
	Return start and stop extents for a file of given size
	that will break the file into 100 pieces of approximately
	the same length.
	
	>>> res = list(get_one_hundred_pieces(205))
	>>> len(res)
	100
	>>> res[:3]
	[(0, 2), (2, 4), (4, 6)]
	>>> res[-3:]
	[(199, 201), (201, 203), (203, 205)]
	"""
	step = size / 100
	cap = lambda pos: min(pos, size)
	approx_partitions = xfrange(0, size+step, step)
	int_partitions = imap(lambda n: int(round(n)), approx_partitions)
	partitions = imap(cap, int_partitions)
	return pairwise(partitions)

def save_file_bytes(handle, length, filename):
	hr, data = ReadFile(handle, length)
	assert len(data) == length, "%s != %s" % (len(data), length)
	h_dest = CreateFile(
		filename,
		win32con.GENERIC_WRITE,
		0,
		None,
		win32con.CREATE_NEW,
		0,
		None,
		)
	code, wbytes = WriteFile(h_dest, data)
	assert code == 0
	assert wbytes == len(data), '%s != %s' % (wbytes, len(data))

def handle_command_line():
	filename = sys.argv[1]
	h = CreateFile(
		filename,
		win32con.GENERIC_WRITE | win32con.GENERIC_READ,
		0,
		None,
		win32con.OPEN_EXISTING,
		0,
		None,
		)
	size = GetFileSize(h)
	extents = get_one_hundred_pieces(size)
	for start, end in reversed(tuple(extents)):
		length = end - start
		last = end - 1
		SetFilePointer(h, start, win32con.FILE_BEGIN)
		target_filename = '%s-%d' % (filename, start)
		save_file_bytes(h, length, target_filename)
		SetFilePointer(h, start, win32con.FILE_BEGIN)
		SetEndOfFile(h)

if __name__ == '__main__':
	handle_command_line()
