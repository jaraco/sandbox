from __future__ import print_function

import random
from collections import namedtuple

from jaraco.util.dictlib import RangeMap

Entrant = namedtuple('Entrant', 'id volume')
entrants = [
	Entrant(100, 120000),
	Entrant(102, 100),
	Entrant(103, 30000),
	# ...
]

def calculate_accumulated_volumes(entrants):
	# make acc_volume there so we have total
	global acc_volume
	acc_volume = 0
	for entrant in entrants:
		acc_volume += entrant.volume
		yield acc_volume


# create a map where a volume between 0 and total_volume produces gives
#  a weighted selection of Entrants.

weighted_entrants = RangeMap(zip(calculate_accumulated_volumes(entrants), entrants))

# now pick an entrant
for x in range(3):
	index = random.random()*acc_volume
	pick = weighted_entrants[index]
	print('picked', pick, '(%s)' % index)
