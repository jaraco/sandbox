from random import shuffle
import itertools

teams = 'ABCDEFG'

fixed_pairs = list(itertools.combinations(teams, 2))
shuffle(fixed_pairs)

def print_pair(pair):
	print(' vs '.join(pair))

map(print_pair, fixed_pairs)
