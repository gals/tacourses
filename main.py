# -*- coding: utf-8 -*-
"""
"""

import codecs
from collections import OrderedDict
import jinja2

from timetables import TimetableFetcher
import score

def fetch_timetables(url, semester, name=None):
	"""
	"""
	fetcher = TimetableFetcher(url, semester)
	return list(fetcher.timetables(name=name))

def group_courses(tables):
	"""
	"""
	grouped = {}
	for table in tables:
		for course in table.iter_courses():
			course_id = course.course_id
			if not course_id in grouped:
				grouped[course_id] = {}
			grouped[course_id][table.table_id] = course
	return grouped

def iter_grouped_courses(courses):
	"""
	"""
	for timetables in courses.itervalues():
		for table_id, course in timetables.iteritems():
			yield (table_id, course)

def render_template(filename, 
	templates_dir="templates", **context):
	"""
	"""
	env = jinja2.Environment(
		loader=jinja2.FileSystemLoader(templates_dir)
	)

	template = env.get_template(filename)
	return template.render(**context)

def _sort_dict_by_attr(d, attr, reverse=True):
	"""
	"""
	return OrderedDict(sorted(
		d.iteritems(),
		key=lambda (k, v): getattr(v, attr),
		reverse=reverse
	))

def _sort_dict_by_score(d, reverse=True):
	"""
	"""
	return _sort_dict_by_attr(d, "_score")

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

	courses = group_courses(timetables)
	table_scores = {}

	for table_id, course in iter_grouped_courses(courses):
		course_score = score.calculate(
			course,
			good_names,
			neutral_names,
			bad_names)
		course._score = course_score

		if table_id not in table_scores:
			table_scores[table_id] = []

		table_scores[table_id].append(course_score)

	for table in timetables:
		scores = table_scores[table.table_id]
		table._score = sum(scores) / (len(scores) * 1.0)

	sorted_courses = {}
	for course_id, tables in courses.iteritems():
		sorted_courses[course_id] = _sort_dict_by_score(tables)

	sorted_timetables = sorted(
		timetables, key=lambda t: t._score, reverse=True)

	context = {
		"courses": sorted_courses,
		"timetables": sorted_timetables
	}

	with codecs.open(filename, "w", "utf-8") as f:
		f.write(render_template("report.html", **context))

def main():
	"""
	"""
	# TODO (1): Create a .json config file / command line arguments?
	# TODO (2): Grab timetables links from javascript? (scrap/selenium)

	good_names = []
	neutral_names = []
	bad_names = []

	timetables = fetch_timetables(
		"https://www.eng.tau.ac.il/yedion/2017-18/eng_manot_2017_sem1.htm",
		semester=1,
		name=u"0512-0101")

	create_report("report-1.html", timetables,
		good_names=good_names,
		neutral_names=neutral_names,
		bad_names=bad_names)

	timetables = fetch_timetables(
		"https://www.eng.tau.ac.il/yedion/2017-18/eng_manot_2017_sem2.htm",
		semester=2,
		name=u"0512-0102")

	create_report("report-2.html", timetables,
		good_names=good_names,
		neutral_names=neutral_names,
		bad_names=bad_names)

if __name__ == "__main__":
	main()