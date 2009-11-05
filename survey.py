#!python
from __future__ import print_function

import pickle
import xlwt 

class Topic(list):
	def __str__(self):
		return '{0} ({1})'.format(self.name, len(self))

	def __init__(self, name):
		super(Topic, self).__init__()
		self.name = name

	@classmethod
	def from_questions(cls):
		questions = parse_questions()
		topic = None
		for q in questions:
			if cls.is_topic(q):
				if topic: yield topic
				topic = cls(q)
			else:
				topic.append(q)
		if topic: yield topic

	@staticmethod
	def is_topic(text):
		return len(text) < 50 and not '?' in text

	@staticmethod
	def save_topics(topics):
		pickle.dump(topics, open('topics.pickle', 'wb'))

	@staticmethod
	def load_topics():
		return pickle.load(open('topics.pickle', 'rb'))

def generate_spreadsheet(topics):
	import xlwt
	wb = xlwt.Workbook()
	for topic in topics:
		sheet = wb.add_sheet(topic.name)
		style = get_style({'alignment':(('horz', xlwt.Alignment.HORZ_CENTER),)})
		sheet.write_merge(0,0,0,2,"Title", style)
	wb.save('audit (generated).xls')
	return wb, sheet

def parse_questions():
	import xlrd
	wb = xlrd.open_workbook('IT Audit Survey.xls')
	s = wb.sheets()[0]
	questions = [s.row(n)[0].value for n in range(s.nrows)]
	return filter(None, questions)

def print_all(x):
	map(print, x)

def write(ws, row, col, data, style=None):
	"""
	Write data to row, col of worksheet (ws) using the style
	information.
	Again, I'm wrapping this because you'll have to do it if you
	create large amounts of formatted entries in your spreadsheet
	(else Excel, but probably not OOo will crash).
	"""
	style = get_style(style) if style is not None else ws.write.im_func.func_defaults[1]
	ws.write(row, col, data, style)

STYLE_FACTORY = {}
def get_style(style):
	"""
	Style is a dict maping key to values.
	Valid keys are: background, format, alignment, border
	The values for keys are lists of tuples containing (attribute,
	value) pairs to set on model instances...
	"""
	#print "KEY", style
	style_key = tuple(style.items())
	s = STYLE_FACTORY.get(style_key, None)
	if s is not None: return s

	s = xlwt.XFStyle()
	for key, values in style.items():
		if key == "background":
			p = xlwt.Pattern()
			for attr, value in values:
				p.__setattr__(attr, value)
			s.pattern = p
		elif key == "format":
			s.num_format_str = values
		elif key == "alignment":
			a = xlwt.Alignment()
			for attr, value in values:
				a.__setattr__(attr, value)
			s.alignment = a
		elif key == "border":
			b = xlwt.Formatting.Borders()
			for attr, value in values:
				b.__setattr__(attr, value)
			s.borders = b
		elif key == "font":
			f = get_font(values)
			s.font = f
	STYLE_FACTORY[style_key] = s
	return s

if __name__ == '__main__':
	topics = tuple(Topic.from_questions())
	print_all(topics)
	Topic.save_topics(topics)
	topics = Topic.load_topics()
	wb, sheet = generate_spreadsheet(topics)

