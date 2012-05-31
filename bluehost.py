"""
Fabric recipes for bluehost
"""

import urllib2
import os
import sys
import types
import contextlib
import io
import textwrap

from fabric.api import run, cd, task
from fabric.contrib import files

@contextlib.contextmanager
def _tarball_context(url):
	"""
	Get a tarball, extract it, change to that directory, yield, then
	clean up.
	"""
	build_dir = os.path.basename(url).replace('.tar.gz', '').replace(
		'.tgz', '')
	run('wget {url} -O - | tar xz'.format(**vars()))
	try:
		with cd(build_dir):
			yield build_dir
	finally:
		run('rm -R {build_dir}'.format(**vars()))

def _url_module_import(url):
	"""
	Grab a python file from a URL and import it as a module
	"""
	data = urllib2.urlopen(url).read()
	name = os.path.basename(url)
	name, ext = os.path.splitext(name)
	module = sys.modules.setdefault(name, types.ModuleType(name))
	module.__file__ = url
	exec data in module.__dict__
	return module

@task
def install_distribute():
	"""
	Install distribute (setuptools) into the user's .local profile
	"""
	# get the latest version info from the installer_script
	distribute_setup = _url_module_import('http://python-distribute.org/distribute_setup.py')
	download_url = '{DEFAULT_URL}distribute-{DEFAULT_VERSION}.tar.gz'.format(**vars(distribute_setup))
	#prefix = '--prefix={prefix}'.format(**vars()) if prefix else ''
	if not files.exists('~/python-2.7.3'):
		build_python_version()
	with _tarball_context(download_url):
		run('~/python-2.7.3/bin/python2.7 setup.py install --user')

@task
def install_cherrypy(url_base = '/cp'):
	"""
	Install a CherryPy application as a FCGI application on `url_base`.
	"""
	run('.local/bin/easy_install cherrypy')
	run('.local/bin/easy_install flup')

	url_base = url_base.strip('/')
	# set up the FCGI handler
	files.append('public_html/.htaccess', [
		'AddHandler fcgid-script .fcgi',
		'RewriteRule ^{url_base}/(.*)$ /cgi-bin/cherryd.fcgi/$1 [last]'.format(**vars()),
	])
	# install the cherrypy conf
	files.append('public_html/cgi-bin/cherryd.conf', [
		'[global]',
		'server.socket_file=None',
		'server.socket_host=None',
		'server.socket_port=None',
	])

	# install the cherrypy fcgi handler
	files.append('public_html/cgi-bin/cherryd.fcgi', [
		'#!/bin/sh',
		'~/.local/bin/cherryd -P modules -c cherryd.conf -f -i app',
	])
	run('chmod 755 public_html/cgi-bin/cherryd.fcgi')

	run('mkdir -p public_html/cgi-bin/modules')
	files.append('public_html/cgi-bin/modules/app.py', [
		'import cherrypy',
		'class Application:',
		'\t"Define your application here"',
		'cherrypy.tree.mount(Application(), "/cgi-bin/cherryd.fcgi")',
	])

@task
def build_python_version(ver='2.7.3', prefix=None, alt=False):
	"""
	Install a given version of Python from source to the specified
	prefix.
	If `alt` is indicated, Python will be installed as alternate (i.e.
	no `python` executable).
	"""
	short_ver = ver[:3]
	if prefix is None: prefix = '~/Python-{ver}'.format(**vars())
	longver = 'Python-{ver}'.format(**vars())
	if not files.exists(longver):
		run('wget http://python.org/ftp/python/{ver}/{longver}.tgz -O - '
			'| tar xz'.format(**vars()))
	with cd(longver):
		# Linux has a de-facto standard of 4 bytes per unicode character.
		#  So to share binaries, we need to set this flag, which is
		#  different on Python2 versus Python3.
		unicode_flag = '--enable-unicode=ucs4' if ver.startswith('2') else '--with-wide-unicode'
		run('./configure --prefix {prefix} {unicode_flag}'.format(**vars()))
		run('make')
		type = 'altinstall' if alt else 'install'
		run('make {type}'.format(**vars()))
	run('rm -R {longver}'.format(**vars()))
	run('ln -s {prefix} python{short_ver}'.format(**vars()))

@task
def install_roundup(url_base = '/'):
	"""
	Install a Roundup Tracker as a FCGI application on `url_base`.
	"""

	run('.local/bin/easy_install roundup')
	run('.local/bin/easy_install flup')

	url_base = url_base.strip('/')
	# set up the FCGI handler
	files.append('public_html/.htaccess', [
		'AddHandler fcgid-script .fcgi',
		'RewriteRule ^{url_base}/(.*)$ /cgi-bin/roundup.fcgi/$1 [last]'.format(**vars()),
	])

	# install the cherrypy fcgi handler
	runner = io.StringIO(textwrap.dedent(u"""
		#!/home2/adamsrow/python2.7/bin/python
		import os
		from flup.server.fcgi import WSGIServer

		home = os.environ['HOME']
		tracker_home = os.path.join(home, 'Adams Row Tracker'))

		from roundup import configuration
		from roundup.cgi.wsgi_handler import RequestDispatcher

		srv = WSGIServer(RequestDispatcher(tracker_home))
		srv.run()
	""").lstrip())

	files.put(runner, 'public_html/cgi-bin/roundup.fcgi')
	run('chmod 755 public_html/cgi-bin/roundup.fcgi')
