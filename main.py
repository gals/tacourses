# -*- coding: utf-8 -*-
"""
"""

import codecs
import jinja2

from timetables import TimetableFetcher
import score

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
				grouped[course_id] = {}

			grouped[course_id][i + 1] = course

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

def create_report(
	filename,
	timetables,
	good_names=None,
	neutral_names=None,
	bad_names=None):
	"""
	"""
	good_names = good_names or []
	neutral_names = neutral_names or []
	bad_names = bad_names or []

	grouped = group_timetables(timetables)

	for courses in grouped.itervalues():
		for table_id, course in courses.iteritems():
			course._score = score.calculate(
				course,
				good_names,
				neutral_names,
				bad_names)

	context = {
		"grouped": grouped,
	}

	with codecs.open(filename, "w", "utf-8") as f:
		f.write(render_template("report.html", **context))

def main():
	"""
	"""
	good_names = []
	neutral_names = []
	bad_names = []

	timetables = fetch_timetables(
		"https://www.eng.tau.ac.il/yedion/2017-18/eng_manot_2017_sem1.htm",
		semester=1,
		name_predicate=u"0512-0101")

	create_report("report-1.html", timetables,
		good_names=good_names,
		neutral_names=neutral_names,
		bad_names=bad_names)

	timetables = fetch_timetables(
		"https://www.eng.tau.ac.il/yedion/2017-18/eng_manot_2017_sem2.htm",
		semester=2,
		name_predicate=u"0512-0102")

	create_report("report-2.html", timetables,
		good_names=good_names,
		neutral_names=neutral_names,
		bad_names=bad_names)

if __name__ == "__main__":
	main()