# -*- coding: utf-8 -*-
"""
"""

import codecs
from itertools import ifilter
import jinja2

from timetables import TimetableFetcher

def fetch_timetables(url, semester, name_predicate=None):
	"""
	"""
	fetcher = TimetableFetcher(url, semester)
	timetables = fetcher.timetables()

	if name_predicate:
		return ifilter(
			lambda t: name_predicate in t.name,
			timetables)
	
	return timetables

def group_proposals(tables):
	"""
	"""
	proposals = {}
	for i, table in enumerate(tables):
		for course in table.iter_courses():
			course_id = course.course_id
			if not course_id in proposals:
				proposals[course_id] = []

			proposals[course_id].append(course)

	return proposals

def render_template(filename, 
	templates_dir="templates", **context):
	"""
	"""
	env = jinja2.Environment(
		loader=jinja2.FileSystemLoader(templates_dir)
	)

	template = env.get_template(filename)
	return template.render(**context)

def create_report(filename, timetables):
	"""
	"""
	context = {
		"course_proposals": group_proposals(timetables)
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