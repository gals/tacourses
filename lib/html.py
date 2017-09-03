"""
"""

from bs4 import BeautifulSoup, NavigableString, Tag

def parse(html):
	"""
	"""
	return BeautifulSoup(html, "html.parser")

def split(html, tag_name):
	"""
	"""
	parts = []
	buff = []
	for tag in html.children:
		if isinstance(tag, NavigableString):
			buff.append(tag)
			continue

		next_tag = tag.nextSibling
		if not isinstance(next_tag, Tag):
			continue

		if next_tag.name == tag_name.lower():
			parts.append("".join(buff))
			buff = []

	if buff:
		return parts + buff
