# -*- coding: utf-8 -*-
"""
"""

import codecs
from itertools import imap
import jinja2

from timetables import TimetableFetcher

def fetch_timetables(url, semester, name_predicate=None):
	"""
	"""
	fetcher = TimetableFetcher(url, semester)
	return fetcher.timetables(
		name_predicate=name_predicate)

def group_timetables(tables):
	"""
	"""
	grouped = {}
	for i, table in enumerate(tables):
		for course in table.iter_courses():
			course_id = course.course_id
			if not course_id in grouped:
				grouped[course_id] = []

			grouped[course_id].append(course)

	return grouped

def render_template(filename, 
	templates_dir="templates", **context):
	"""
	"""
	env = jinja2.Environment(
		loader=jinja2.FileSystemLoader(templates_dir)
	)

	template = env.get_template(filename)
	return template.render(**context)

def contains_strings(s, strings):
	"""
	"""
	return any(imap(s.__contains__, strings))

def calculate_score(
	course,
	goodnames=None,
	badnames=None,
	neutralnames=None):
	"""
	"""
	goodnames = goodnames or []
	badnames = badnames or []
	neutralnames = neutralnames or []

	# TODO: Calculate score with SymPy?

def create_report(
	filename,
	timetables):
	"""
	"""
	context = {
		"grouped": group_timetables(timetables)
	}

	with codecs.open(filename, "w", "utf-8") as f:
		f.write(render_template("report.html", **context))

def main():
	"""
	"""
	timetables = fetch_timetables(
		"https://www.eng.tau.ac.il/yedion/2017-18/eng_manot_2017_sem1.htm",
		semester=1,
		name_predicate=u"0512-0101")

	create_report("report-1.html", timetables)

	timetables = fetch_timetables(
		"https://www.eng.tau.ac.il/yedion/2017-18/eng_manot_2017_sem2.htm",
		semester=2,
		name_predicate=u"0512-0102")

	create_report("report-2.html", timetables)

if __name__ == "__main__":
	main()