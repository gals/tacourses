"""
"""

from itertools import imap

def contains_strings(s, strings):
	"""
	"""
	return any(imap(s.__contains__, strings))