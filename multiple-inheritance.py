from __future__ import print_function

class Alpha(object):
	def output(self):
		print('Alpha')
		super(Alpha, self).output()

class Beta(object):
	def output(self):
		print('Beta')

class Gamma(Alpha, Beta):
	def output(self):
		print('Gamma')
		super(Gamma, self).output()

g = Gamma()
g.output()