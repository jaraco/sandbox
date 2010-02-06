from __future__ import print_function
import os
import sys
import subprocess
import itertools


def create_test_dir():
	"""
	create a directory for the test
	"""
	test_dir = os.path.expanduser('~/build/python')
	build_existed_prior = os.path.exists(os.path.expanduser('~/build'))
	if os.path.exists(test_dir):
		print("Test directory already exists. Aborting", file=sys.stderr)
		raise SystemExit(1)
	os.path.makedirs(test_dir)

def checkout_source():
	cmd = [
		'svn', 'co',
		'http://svn.python.org/projects/python/branches/py3k',
		os.path.join(test_dir, 'python-py3k'),
	]
	result = subprocess.Popen(cmd).wait()
	if result != 0:
		print("Checkout failed", file=sys.stderr)
		raise SystemExit(result)

def find_vs9():
	# find VS9
	search_path = map(os.environ, ['PROGRAMFILES', 'PROGRAMFILES(X86)'])
	vs_candidate_dirs = [os.path.join(base, 'Microsoft Visual Studio 9.0') for base in search_path]
	return next(iter(filter(os.path.isdir, vs_candidate_dirs)))

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
	# construct the command that will alter the environment
	env_cmd = subprocess.list2cmdline(env_cmd)
	# create a tag so we can tell in the output when the proc is done
	tag = 'Done running command'
	# construct a cmd.exe command to do accomplish this
	cmd = 'cmd.exe /s /c "{env_cmd} && echo "{tag}" && set"'.format(**vars())
	# launch the process
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=initial)
	# parse the output sent to stdout
	lines = proc.stdout
	# consume whatever output occurs until the tag is reached
	consume(itertools.takewhile(lambda l: tag not in l, lines))
	# define a way to handle each KEY=VALUE line
	handle_line = lambda l: l.rstrip().split('=',1)
	# parse key/values into pairs
	pairs = map(handle_line, lines)
	# make sure the pairs are valid
	valid_pairs = filter(validate_pair, pairs)
	# construct a dictionary of the pairs
	result = dict(valid_pairs)
	# let the process finish
	proc.communicate()
	return result

def get_vcvars_env():
	vcvarsall = r'c:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\vcvarsall.bat'
	# even vcvarsall needs some environment to function properly
	initial = dict(VS90COMNTOOLS=os.environ['VS90COMNTOOLS'])
	return get_environment_from_batch_command(vcvarsall, initial)

env = get_vcvars_env()

# build Python in 32-bit mode
