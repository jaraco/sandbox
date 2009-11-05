#!python
from __future__ import print_function

import pickle
import xlwt 
from itertools import count, repeat
import sys

BLACK = 0
class Topic(list):
	def __str__(self):
		return '{0} ({1})'.format(self.name, len(self))

	def __init__(self, name):
		super(Topic, self).__init__()
		self.name = name

	@classmethod
	def from_questions(cls, raw_items=None):
		items = raw_items or parse_questions()
		topic = None
		for item in items:
			if cls.is_topic(item):
				if topic: yield topic
				topic = cls(item)
			else:
				topic.append(item)
		if topic: yield topic

	@staticmethod
	def is_topic(text):
		return len(text) < 50 and not '?' in text

	def pretty_print(self, file=sys.stdout):
		print(self.name, file=file)
		for q in self:
			q = q.encode('utf-8')
			print('\t'+q, file=file)

	@staticmethod
	def save_topics(topics):
		#pickle.dump(topics, open('topics.pickle', 'wb'))
		f = open('topics.txt', 'w')
		for t in topics:
			t.pretty_print(f)

	@staticmethod
	def load_topics():
		questions = open('topics.txt')
		questions = map(str.strip, questions)
		questions = [q.decode('utf-8') for q in questions]
		return Topic.from_questions(questions)
		#pickle.load(open('topics.pickle', 'rb'))

all_thin_black = tuple(
	zip('left bottom right top'.split(), repeat(xlwt.Formatting.Borders.THIN)) +
	zip('left_colour bottom_colour right_colour top_colour'.split(), repeat(BLACK))
	)
				
def generate_spreadsheet(topics):
	import xlwt
	wb = xlwt.Workbook()
	for topic in topics:
		sheet = wb.add_sheet(topic.name)
		style = dict(
			alignment = (('horz', xlwt.Alignment.HORZ_CENTER),),
			font = (("bold", True),),
			border = all_thin_black,
			)
		# this equation is supposed to get the value from the sheet name, but only seems
		#  to get the last active sheet name
		title = xlwt.Formula('RIGHT(CELL("filename"),LEN(CELL("filename"))-SEARCH("]",CELL("filename")))')
		# override because the function doesn't work
		title = topic.name
		sheet.write_merge(0,0,0,2,title, get_style(style))
		write(sheet, 1, 1, "Answer", style)
		write(sheet, 1, 2, "Clarification", style)
		sheet.panes_frozen = True
		sheet.horz_split_pos = 2
		sheet.fit_width_to_pages = 1
		for row_n, q in zip(count(2), topic):
			style = dict(
				alignment = (("wrap", xlwt.Alignment.WRAP_AT_RIGHT),),
				border = all_thin_black,
			)
			write(sheet, row_n, 0, q, style)
			write(sheet, row_n, 1, '', style)
			write(sheet, row_n, 2, '', style)
		for col_n in range(3):
			# width units are 1/256 the width of the zero character in the default font (first font record encountered).
			width = 256*30
			width += int(width*.5*bool(col_n)) # expand every column but the first
			sheet.col(col_n).width = width
			
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

FONT_FACTORY = {}
def get_font(values):
	"""
	'height' 10pt = 200, 8pt = 160
	"""
	font_key = values
	f = FONT_FACTORY.get(font_key, None)
	if f is not None: return f
	f = xlwt.Font()
	for attr, value in values:
		f.__setattr__(attr, value)
	FONT_FACTORY[font_key] = f
	return f

def initial_import():
	topics = tuple(Topic.from_questions())
	print_all(topics)
	Topic.save_topics(topics)


if __name__ == '__main__':
	topics = Topic.load_topics()
	wb, sheet = generate_spreadsheet(topics)

