"""
"""

import os
from hashlib import md5
import cPickle as pickle

import requests

DEFAULT_CACHE_DIR = "cache"

class HTTPCache(object):
	"""
	"""

	def __init__(self, cache_path):
		self.cache_path = cache_path

	def __repr__(self):
		return "<%s path=%r>" % (
			self.__class__.__name__,
			self.cache_path)

	def _hash(self, req):
		"""
		"""
		url, params, data = req
		return md5(url + str(data)).hexdigest()

	def _filename(self, req):
		"""
		"""
		return os.path.join(
			self.cache_path, self._hash(req))

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
		os.remove(self._filename(req))

	def __getitem__(self, req):
		"""
		"""
		if not req in self:
			return

		filename = self._filename(req)
		with open(filename, "rb") as f:
			return self._deserialize(f.read())

	def __setitem__(self, req, resp):
		"""
		"""
		filename = self._filename(req)
		with open(filename, "wb") as f:
			f.write(self._serialize(resp))

	def __contains__(self, req):
		"""
		"""
		return os.path.isfile(self._filename(req)) 

def default_cache():
	"""
	"""
	return HTTPCache(DEFAULT_CACHE_DIR)

def cached(f):
	"""
	"""
	def inner(url, data=None, params=None, 
		cache=None, *args, **kwargs):
		if cache is None:
			cache = default_cache()

		data = data or {}
		params = params or {}

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

def test():
	"""
	"""
	cache = default_cache()

	r = get("http://ynet.co.il", cache=cache)
	cached = cache[("http://ynet.co.il", {}, {})]
	assert cached.status_code == 200

	r = post("http://ynet.co.il/?a=1", cache=cache)
	cached = cache[("http://ynet.co.il/?a=1", {}, {})]
	assert cached.status_code == 200

if __name__ == "__main__":
	test()