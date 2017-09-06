"""
"""

from sympy import Eq, solve, symbols

from utils import contains_strings

def score_table():
	"""
	"""
	good_lecturer, neutral_lecturer, bad_lecturer = symbols(
		'good_lecturer neutral_lecturer bad_lecturer') 
	good_ta, neutral_ta, bad_ta = symbols(
		'good_ta neutral_ta bad_ta')

	equations = [
		Eq(neutral_lecturer, 1),
		Eq(neutral_ta, neutral_lecturer / 2),

		Eq(good_lecturer, 3 * neutral_lecturer),
		Eq(good_ta, good_lecturer / 2),

		Eq(bad_lecturer, -2 * neutral_lecturer),
		Eq(bad_ta, bad_lecturer / 2),
	]

	return solve(equations, 
		[good_lecturer, bad_lecturer, neutral_lecturer,
		good_ta, neutral_ta, bad_ta])

_SCORE_TABLE = score_table()

def calculate(
	course,
	good_names=None,
	neutral_names=None,
	bad_names=None,
	score_table=_SCORE_TABLE):
	"""
	"""
	good_names = good_names or []
	neutral_names = neutral_names or []
	bad_names = bad_names or []

	good_lecturer, neutral_lecturer, bad_lecturer = symbols(
		'good_lecturer neutral_lecturer bad_lecturer') 
	good_ta, neutral_ta, bad_ta = symbols(
		'good_ta neutral_ta bad_ta') 

	counters = {
		good_lecturer: 0,
		neutral_lecturer: 0,
		bad_lecturer: 0,
		good_ta: 0,
		neutral_ta: 0,
		bad_ta: 0
	}

	lecturers_names_map = {
		good_lecturer: good_names,
		neutral_lecturer: neutral_names,
		bad_lecturer: bad_names,
	}

	staff = course.staff

	for name in staff.lecturers:
		for symbol, names in lecturers_names_map.iteritems():
			if contains_strings(name, names):
				counters[symbol] += 1

	assistants_names_map = {
		good_ta: good_names,
		neutral_ta: neutral_names,
		bad_ta: bad_names,
	}

	for name in staff.assistants:
		for symbol, names in assistants_names_map.iteritems():
			if contains_strings(name, names):
				counters[symbol] += 1

	score = 0
	for symbol, count in counters.iteritems():
		score += count * score_table[symbol]

	return score.evalf()

if __name__ == "__main__":
	print _SCORE_TABLE