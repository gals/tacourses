# -*- coding: utf-8 -*-
"""
"""

from collections import MutableMapping, namedtuple
from itertools import ifilter
import re

import lib.http
import lib.html
from courses import Course, CourseStaff

HOURS_REGEX = re.compile("(\d{2}:\d{2})-(\d{2}:\d{2})")

class EventTypes(object):
	"""
	"""
	EXERCISE = "exercise"
	CLASS = "class"
	LAB = "lab"
	QA = "Q&A"
	PROJECT = "project"
	SEMINAR = "seminar"

EVENT_TYPES_MAPPING = {
	u"תרגיל": EventTypes.EXERCISE,
	u"שיעור": EventTypes.CLASS,
	u"מעבדה": EventTypes.LAB,
	u'שו"ת': EventTypes.QA,
	u"פרויקט": EventTypes.PROJECT,
	u"סמינר": EventTypes.SEMINAR
}

class TimetableEvent(object):
	"""
	"""

	def __init__(
		self,
		event_type,
		course,
		lecturer,
		start_hour,
		end_hour,
		room):
		"""
		"""
		self.type = event_type
		self.course = course
		self.lecturer = lecturer
		self.start_hour = start_hour
		self.end_hour = end_hour
		self.room = room

	def __repr__(self):
		return "<%s type=%r course=%r>" % (
			self.__class__.__name__,
			self.type,
			self.course)

class Timetable(MutableMapping):
	"""
	"""

	def __init__(self, name=None, table_id=None):
		"""
		"""
		self.name = name
		self.table_id = table_id

		days = {}
		for i in xrange(1, 8):
			days[i] = {}
		self._days = days

	def __repr__(self):
		return "<%s name=%r id=%r>" % (
			self.__class__.__name__,
			self.name,
			self.table_id)

	def __delitem__(self, key):
		"""
		"""
		del self._days[key]

	def __getitem__(self, key, default=None):
		"""
		"""
		return self._days.get(key, default)

	def __iter__(self):
		"""
		"""
		return iter(self._days)

	def __len__(self):
		"""
		"""
		return len(self._days)

	def __setitem__(self, key, value):
		"""
		"""
		self._days[key] = value

	def iter_events(self):
		"""
		"""
		for day, hours in self._days.iteritems():
			for hour in hours:
				yield self._days[day][hour]

	def events(self):
		"""
		"""
		return list(self.iter_events())

	def iter_courses(self):
		"""
		"""
		courses = {}
		for event in self.iter_events():
			event_course = event.course
			course_id = event_course.course_id
			lecturer = event.lecturer

			if course_id not in courses:
				courses[course_id] = Course(
					course_id,
					title=event_course.title,
					url=event_course.url,
					staff=CourseStaff())

			course = courses[course_id]
			staff = course.staff

			if event.type == EventTypes.CLASS:
				staff.lecturers.add(lecturer)
			elif event.type == EventTypes.EXERCISE:
				staff.assistants.add(lecturer)

		return courses.itervalues()

	def courses(self):
		"""
		"""
		return list(self.iter_courses())

TimetableLink = namedtuple("TimetableLink", ["id", "name", "url"])

class TimetableFetcher(object):
	"""
	"""

	def __init__(
		self,
		url,
		semester, 
		http=lib.http,
		html_parser=lib.html.parse):
		"""
		"""
		self.url = url
		self.semester = semester
		self._http = http
		self._html_parser = html_parser

	def __repr__(self):
		return "<%s url=%r semester=%r>" % (
			self.__class__.__name__,
			self.url,
			self.semester)

	def _build_timetable_url(self, table_id):
		"""
		"""
		# TODO: Get these URLs from the webpage?
		url = "https://mashdsp.tau.ac.il/asplinks/TimeTable1.asp?co=2,-3,5,16,6,75,74&cok=,http://www2.tau.ac.il/yedion/syllabus.asp?course=(cid=0-1-2-3-4-5-6-7-8-9)&year=2017,,,,"
		url += "&sm=%s" % (self.semester - 1)
		url += "&b=%s" % (table_id)
		url += "&fher=Arial&ftet=Arial&ftit=Arial&cher=282828&ctit=ff6820&ctet=282828&bher=1&btit=1&btet=0&bgch=ffff00&bgctit=ffffe0&bgctet=ffffe0&sitit=16&siher=14&sitet=12&bgc=ffffff&isHdr=1&bgi=&spd=0&sTime=1&cidd=4-8&h1=480&h2=1320&dura=60&fromd=0&tod=5&lang=1&Facu=5&db_num=2017"
		return url

	def _timetable_links(self):
		"""
		"""
		r = self._http.get(self.url)
		r.raise_for_status()

		html = self._html_parser(r.content)
		for link_tag in html.select("li a"):
			table_id = int(link_tag["id"])
			table_name = link_tag.text
			
			url = self._build_timetable_url(table_id)
			yield TimetableLink(
				id=table_id,
				name=table_name,
				url=url)

	def _split_html(self, html, tag_name):
		"""
		"""
		return lib.html.split(html, tag_name)

	def _parse_event_hours(self, hours):
		"""
		"""
		hours_match = HOURS_REGEX.match(hours)
		if not hours_match:
			raise ValueError(
				"Failed to parse hours: %r" % (hours))

		start_hour = hours_match.group(1)
		end_hour = hours_match.group(2)

		return start_hour, end_hour

	def _parse_course_id(self, data):
		"""
		"""
		return ".".join(data.split(".")[:-1])

	def _parse_event_tag(self, tag):
		"""
		"""
		div_tag = tag.find("div")
		if div_tag is None:
			return

		a_tag = div_tag.find("a")
		course_id = self._parse_course_id(a_tag.text)
		course_url = a_tag["href"]

		parts = self._split_html(div_tag, "br")
		stripped_parts = []
		for part in parts:
			stripped_parts.append(part.strip())

		course_title = stripped_parts[1]
		lecturer = stripped_parts[2]
		event_type = EVENT_TYPES_MAPPING.get(stripped_parts[3])
		start_hour, end_hour = self._parse_event_hours(
			stripped_parts[4])
		room = stripped_parts[5]

		course = Course(
			course_id,
			course_title,
			url=course_url)

		return TimetableEvent(
			event_type,
			course,
			lecturer,
			start_hour,
			end_hour,
			room)

	def timetables(self, name=None):
		"""
		"""
		if name:
			links = ifilter(
				lambda l: name in l.name,
				self._timetable_links())
		else:
			links = self._timetable_links()

		for i, link in enumerate(links):
			table_id = i + 1
			timetable = Timetable(
				link.name, 
				table_id=table_id)

			r = self._http.get(link.url)
			r.raise_for_status()

			html = self._html_parser(r.content)
			row_tags = html.find_all("tr")[1:]

			for row_tag in row_tags:
				col_tags = row_tag.find_all("td")
				hour = col_tags[0].text

				for i, event_tag in enumerate(col_tags[1:]):
					event = self._parse_event_tag(event_tag)
					if not event:
						continue
					day = i + 1
					timetable[day][hour] = event

			yield timetable