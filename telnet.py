import os, sys, string, re, time
from telnetlib import Telnet
from getpass import getpass

# set up some logging to describe what's going on
import logging
# change the level to WARNING or ERROR to eliminate unwanted INFO and DEBUG output
logging.basicConfig( level = logging.DEBUG )
log = logging.getLogger('main')

sample_input = """30	value30
20	value20
"""

def main():
	global UserName, Password
	UserName=raw_input('What is your username?\t')
	Password=getpass('What is your password?\t')

	#input_file = open( 'list.txt' ).read()
	input_file = sample_input
	# input should be the Store followed by some whitespace, followed by the MAC.
	pattern = '^(?P<Store>\d+)\s+(?P<MAC>\S+)'
	matches = re.finditer( pattern, input_file )
	map( ProcessItem, matches )

def PromptResponse( prompt, response ):
	log.debug( 'Waiting for prompt "%s"', prompt )
	Connection.read_until( prompt )
	Connection.write( response + '\n' )
	time.sleep(4)
	
def Login( ):
	log.debug( 'Waiting for username prompt' )
	PromptResponse( 'Username: ', UserName )
	PromptResponse( 'Password: ', Password )
	PromptResponse( '002>', 'en' )
	PromptResponse( 'Password: ', Password )
	
def ProcessItem( match ):
	Store = int(match.groupdict()['Store'])
	MAC = match.groupdict()['MAC']
	log.debug( 'Store is %d', Store )
	log.debug( 'MAC is %s', MAC )

	global Connection
	host = 'LLL%05dNXX2' % Store
	log.info( 'Connecting to host %s', host )
	Connection= Telnet(host)
	Login( )
	HandlePrompt( MAC )
	CloseConnection(MAC,Store)

def HandlePrompt(MAC):	
	prompt=Connection.read_some()
	log.debug( 'Read the following: "%s"', prompt )
	if str(prompt)[-2:-1]==')':
		log.debug( 'recognized prompt ") "' )
		command = 'set cam permanent filter ' + MAC + ' 1\n'
		Connection.write(command)
	elif str(prompt)[-1:]=="#":
		log.debug( 'recognized prompt "#"' )
		Connection.write('config\n')
		Connection.write('\n')
		Connection.write('mac-address-table static ' + MAC + ' vlan 1 drop\n')
		Connection.write('exit\n')
		Connection.write('write\n')
	else:
		log.warning( 'Could not recognize prompt:' )
		log.warning( prompt )

def CloseConnection(MAC,Store):
	Connection.write('exit\n')
	Connection.close()
	log.info( 'Closed the connection for the network %s at store %d', MAC, Store )

main()