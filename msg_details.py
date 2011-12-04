import sys
import OleFileIO_PL

filename = sys.argv[1]

assert OleFileIO_PL.isOleFile(filename)
# Open OLE file:
ole = OleFileIO_PL.OleFileIO(filename)
# Get list of streams:
#print ole.listdir()
# Test if known streams/storages exist:
if ole.exists('worddocument'):
    print "This is a Word document."
    print "size :", ole.get_size('worddocument')
    if ole.exists('macros/vba'):
         print "This document seems to contain VBA macros."

def get_stream(name):
	result = ole.openstream(name).read()
	try:
		result = result.decode('utf-16')
	except Exception:
		print "Could not decode", name
	return result

names = ole.listdir()
names = map('/'.join, names)
streams = dict(zip(names, map(get_stream, ole.listdir())))
