"""
"""

import os
from hashlib import md5
import cPickle as pickle
from functools import wraps
import unittest
import shutil
import requests
import httpretty

DEFAULT_CACHE_DIR = "cache"

class HTTPCache(object):
	"""
	"""

	def __init__(self, cache_dir=DEFAULT_CACHE_DIR):
		"""
		"""
		self.cache_dir = cache_dir

	def __repr__(self):
		return "<%s dir=%r>" % (
			self.__class__.__name__,
			self.cache_dir)

	def _hash(self, url, params=None, data=None):
		"""
		"""
		params = params or {}
		data = data or {}

		key = "".join(map(str, [url, params, data]))
		return md5(key).hexdigest()

	def _build_cache_path(self, *args, **kwargs):
		"""
		"""
		return os.path.join(
			self.cache_dir, self._hash(*args, **kwargs))

	def _serialize(self, resp):
		"""
		"""
		return pickle.dumps(resp)

	def _deserialize(self, data):
		"""
		"""
		return pickle.loads(data)

	def __delitem__(self, req):
		"""
		"""
		if not isinstance(req, tuple):
			req = (req, )

		os.remove(self._build_cache_path(*req))

	def __getitem__(self, req):
		"""
		"""
		if not isinstance(req, tuple):
			req = (req, )

		if not req in self:
			return

		path = self._build_cache_path(*req)
		with open(path, "rb") as f:
			return self._deserialize(f.read())

	def __setitem__(self, req, resp):
		"""
		"""
		if not isinstance(req, tuple):
			req = (req, )

		if self.cache_dir:
			if not os.path.isdir(self.cache_dir):
				os.makedirs(self.cache_dir)

		path = self._build_cache_path(*req)
		with open(path, "wb") as f:
			f.write(self._serialize(resp))

	def __contains__(self, req):
		"""
		"""
		if not isinstance(req, tuple):
			req = (req, )

		return os.path.isfile(
			self._build_cache_path(*req))

def cached(f):
	"""
	"""
	@wraps(f)
	def inner(
		url,
		data=None,
		params=None, 
		cache=None,
		*args,
		**kwargs):
		if cache is None:
			cache = HTTPCache()

		params = params or {}
		data = data or {}

		req = (url, params, data)
		if req in cache:
			return cache[req]

		resp = f(
			url,
			data=data,
			params=params,
			*args,
			**kwargs)
		cache[req] = resp
		return resp

	return inner

@cached
def post(*args, **kwargs):
	"""
	"""
	return requests.post(*args, **kwargs)

@cached
def get(*args, **kwargs):
	"""
	"""
	return requests.get(*args, **kwargs)

class TestHTTPCache(unittest.TestCase):
	"""
	"""

	@classmethod
	def setUpClass(cls):
		"""
		"""
		cls._cache = HTTPCache("test_cache")

		httpretty.register_uri(
			httpretty.GET,
			"http://a.com",
			body="a" * 5)

		httpretty.register_uri(
			httpretty.POST,
			"http://b.com",
			body="b" * 5)

	@classmethod
	def tearDownClass(cls):
		"""
		"""
		shutil.rmtree(cls._cache.cache_dir)

	def setUp(self):
		"""
		"""
		httpretty.enable()

	def tearDown(self):
		"""
		"""
		httpretty.reset()
		httpretty.disable()

	def test_1_sends_request_if_not_in_cache(self):
		"""
		"""
		resp = get(
			"http://a.com",
			cache=self._cache)
		self.assertTrue(httpretty.has_request())

		resp = post(
			"http://b.com",
			data={"b": 2},
			cache=self._cache)
		self.assertTrue(httpretty.has_request())

	def test_2_loads_response_from_cache(self):
		"""
		"""
		resp = get(
			"http://a.com",
			cache=self._cache)
		cached = self._cache["http://a.com"]

		self.assertFalse(httpretty.has_request())
		self.assertEquals(cached.text, "a" * 5)

		resp = post(
			"http://b.com",
			data={"b": 2},
			cache=self._cache)
		cached = self._cache[("http://b.com", {}, {"b": 2})]

		self.assertFalse(httpretty.has_request())
		self.assertEquals(cached.text, "b" * 5)

if __name__ == "__main__":
	unittest.main(verbosity=2)