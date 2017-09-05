"""
"""

class CourseStaff(object):
	"""
	"""

	def __init__(
		self,
		lecturers=None,
		assistants=None):
		"""
		"""
		self.lecturers = lecturers or set()
		self.assistants = assistants or set()

	def __repr__(self):
		return "<%s lecturers=%r assistants=%r>" % (
			self.__class__.__name__,
			self.lecturers,
			self.assistants)

class Course(object):
	"""
	"""

	def __init__(
		self,
		course_id,
		title=None,
		url=None,
		staff=None):
		"""
		"""
		self.course_id = course_id
		self.title = title
		self.url = url
		self.staff = staff or CourseStaff()

	def __repr__(self):
		return "<%s course_id=%r title=%r>" % (
			self.__class__.__name__,
			self.course_id,
			self.title)