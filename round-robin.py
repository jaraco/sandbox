from random import shuffle
from sets import ImmutableSet

teams = 'ABCDEFG'

# create a class to identify two opposing teams
class OpponentPair(ImmutableSet):
	def __init__(self, team_a, team_b):
		assert team_a != team_b, "team_a and team_b must be distinct"
		super(self.__class__, self).__init__((team_a,team_b))

get_distinct_pairs = lambda items: (OpponentPair(x,y) for x in items for y in items if x != y)

distinct_pairs = get_distinct_pairs(teams)

# remove duplicate pairings
# Note, since OpponentPair((A,B)) == OpponentPair((B,A)), the two
#  will be considered the same, and only one will remain.
unique_pairs = set(distinct_pairs)

# put the pairs into a list to fix their order (sets are orderless)
fixed_pairs = list(unique_pairs)

# randomize the order
shuffle(fixed_pairs)

def print_pair(pair):
	print '%s vs %s' % tuple(pair)

map(print_pair, fixed_pairs)
