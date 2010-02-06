from __future__ import print_function
import sys
import subprocess
import itertools

def validate_pair(ob):
	try:
		if not (len(ob) == 2):
			print("Unexpected result:", ob, file=sys.stderr)
			raise ValueError
	except:
		return False
	return True

def consume(iter):
	try:
		while True: next(iter)
	except StopIteration:
		pass

def get_environment_from_batch_command(env_cmd, initial=None):
	"""
	Take a command (either a single command or list of arguments)
	and return the environment created after running that command.
	Note that if the command must be a batch file or .cmd file, or the
	changes to the environment will not be captured.
	
	If initial is supplied, it is used as the initial environment passed
	to the child process.
	"""
	if not isinstance(env_cmd, (list, tuple)):
		env_cmd = [env_cmd]
	env_cmd = subprocess.list2cmdline(env_cmd)
	tag = 'Done running command'
	cmd = 'cmd.exe /s /c "{env_cmd} && echo "{tag}" && set"'.format(**vars())
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=initial)
	lines = proc.stdout
	consume(itertools.takewhile(lambda l: tag not in l, lines))
	handle_line = lambda l: l.rstrip().split('=',1)
	pairs = map(handle_line, lines)
	valid_pairs = filter(validate_pair, pairs)
	result = dict(valid_pairs)
	proc.communicate()
	return result

def __test__():
	# test it
	cmd = [
		r'c:\program files (x86)\Microsoft Visual Studio 9.0\VC\vcvarsall.bat',
		'x86',
		]
	env = get_environment_from_batch_command(cmd)
