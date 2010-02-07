#!python

"""
This script fully automates the checkout, patch, compile, test cycle
for the Windows symlink support patch.

Prerequisites:
	Visual Studio 2008
	Subversion command-line client
	GNU patch
"""

from __future__ import print_function
import os
import sys
import re
import subprocess
import itertools
import traceback
import urllib2
import urllib
import urlparse
from optparse import OptionParser
from BeautifulSoup import BeautifulSoup

def create_test_dir():
	"""
	create a directory for the test
	"""
	global test_dir
	test_dir = os.path.expanduser('~/build/python')
	test_dir = os.path.normpath(test_dir)
	assert not '/' in test_dir
	build_existed_prior = os.path.exists(os.path.expanduser('~/build'))
	if os.path.exists(test_dir):
		print("Test directory already exists. Aborting", file=sys.stderr)
		raise SystemExit(1)
	os.makedirs(test_dir)

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

def patch_number(link):
	number = re.compile(r'\d+(\.\d+)?')
	return float(number.search(link.string).group(0))

def find_patches(soup):
	files = soup.find(attrs='files')
	links = files.findAll(text=re.compile(r'.*\.patch'))
	links.sort(key=patch_number, reverse=True)
	return links

def get_patches(soup):
	for link in find_patches(soup):
		yield get_patch(link.parent['href'])

bug_url = 'http://bugs.python.org/issue1578269'

def get_patch(link_ref):
	href = urlparse.urljoin(bug_url, link_ref)
	url = urllib2.urlopen(href)
	filename = urllib.unquote(os.path.basename(href))
	return filename, url.read()

def get_soup():
	return BeautifulSoup(urllib2.urlopen(bug_url).read())

def apply_patch():
	filename, patch = next(get_patches(get_soup()))
	patch_target = os.path.join(test_dir, 'python-py3k')
	print("Applying {filename} on {patch_target}".format(**vars()))
	orig_dir = os.getcwd()
	os.chdir(patch_target)
	cmd = 'patch -p0 -t'
	proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
	stdout, stderr = proc.communicate(patch)
	os.chdir(orig_dir)
	if proc.returncode != 0:
		print("Error applying patch", file=sys.stderr)
		raise SystemExit(1)

def find_vs9():
	"Find VS9"
	keys = ['PROGRAMFILES', 'PROGRAMFILES(X86)']
	search_path = [os.environ.get(key) for key in keys if os.environ.has_key(key)]
	vs_candidate_dirs = [os.path.join(base, 'Microsoft Visual Studio 9.0') for base in search_path]
	has_VC_child = lambda dir: os.path.isdir(os.path.join(dir, 'VC'))
	tests = os.path.isdir, has_VC_child
	test_adequacy = lambda candidate: all(t(candidate) for t in tests)
	return next(iter(itertools.ifilter(test_adequacy, vs_candidate_dirs)))

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

def get_vcvars_env(*params):
	vs9 = find_vs9()
	vcvarsall = os.path.join(find_vs9(), 'VC', 'vcvarsall.bat')
	if not os.path.isfile(vcvarsall):
		print("Couldn't find vcvarsall", file=sys.stderr)
		raise SystemExit(1)
	# even vcvarsall needs some environment to function properly
	initial = dict(VS90COMNTOOLS=os.environ['VS90COMNTOOLS'])
	initial=None
	return get_environment_from_batch_command([vcvarsall]+list(params), initial)

env32 = get_vcvars_env()
env64 = get_vcvars_env('x64')

def construct_build_command(args=[]):
	"""
	Inspired by build.bat
	"""
	parser = OptionParser()
	parser.add_option('-c', '--conf', default='Release')
	parser.add_option('-p', '--platf', default='Win32')
	parser.add_option('-r', '--rebuild', action='store_true', default=False)
	parser.add_option('-d', '--debug', dest='conf', action='store_const', const='Debug')
	options, args = parser.parse_args(args)

	cmd = [
		'cmd', '/c',
		'vcbuild',
		'/useenv',
		'pcbuild.sln',
		'|'.join([options.conf, options.platf])
	]
	if options.rebuild:
		cmd[-1:-1] = ['/rebuild']
	return cmd

# build Python in 32-bit mode
def do_32_build():
	cmd = construct_build_command()
	return subprocess.Popen(cmd, env=env32).wait()

def do_64_build():
	cmd = construct_build_command(['-p', 'x64'])
	return subprocess.Popen(cmd, env=env64).wait()

def run_test(*params):
	cmd = [
		'rt.bat',
		'-q',
		] + list(params)
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	stdout, stderr = proc.communicate()
	if not proc.returncode == 0:
		print("Warning: rt.bat returned {proc.returncode}".format(**vars()))
	return proc.returncode, stdout, stderr

def save_test_results(results, filename):
	code, stdout, stderr = results
	open(filename, 'w').write(str(code))
	open(filename+':stdout', 'w').write(stdout)
	open(filename+':stderr', 'w').write(stderr)

def cleanup():
	os.chdir(orig_dir)
	cmd = ['cmd', '/c', 'rmdir', '/s', '/q', test_dir]
	res = subprocess.Popen(cmd).wait()
	if not res == 0:
		print("Error cleaning up", file=sys.stderr)
		raise SystemExit(1)

# orchestrate the test
def orchestrate_test():
	global orig_dir
	orig_dir = os.getcwd()
	create_test_dir()
	try:
		checkout_source()
		apply_patch()
		os.chdir(os.path.join(test_dir, 'python-py3k', 'pcbuild'))
		res = do_32_build()
		print("result of 32-bit build is {0}".format(res))
		filename = os.path.join(orig_dir, '32-bit test results')
		save_test_results(run_test(), filename)
		res = do_64_build()
		print("result of 64-bit build is {0}".format(res))
		filename = os.path.join(orig_dir, '64-bit test results')
		save_test_results(run_test('-x64'), filename)
	except:
		#traceback.print_exc()
		raise
	finally:
		print("Cleaning up...")
		cleanup()

if __name__ == '__main__' and not 'skip' in sys.argv:
	orchestrate_test()
