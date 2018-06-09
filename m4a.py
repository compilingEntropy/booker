#!/usr/bin/env python3.6

import subprocess
import os

class m4a:
	"""An m4a object"""
	def __init__(self, file):
		assert(os.path.isfile(file))
		self.file = file
		self.libmp4 = libmp4(file)

	def add_art(self, coverpic):
		self.libmp4.mp4art(['--remove'])
		return self.libmp4.mp4art(['--add', coverpic])

	def add_tags(self, data):
		self.libmp4.mp4tags(['-s', data['title']])
		self.libmp4.mp4tags(['-A', data['title']])
		self.libmp4.mp4tags(['-i', 'Audiobook'])
		self.libmp4.mp4tags(['-m', data['shortdesc']])
		self.libmp4.mp4tags(['-l', data['fulldesc']])
		self.libmp4.mp4tags(['-a', data['author']])
		self.libmp4.mp4tags(['-w', data['narrator']])
		self.libmp4.mp4tags(['-c', data['subtitle']])

	def add_chaps(self, ch_index):
		self.libmp4.mp4chaps(['-r'])
		return self.libmp4.mp4chaps(['-i'])

class libmp4:
	"""Libmp4 object.... Okay, confession: I'm a python scrub.
	This awesome libmp4v2 thing is a library, and as such can be
	included and interfaced with programmatically, alledgedly. I
	couldn't find a python implementation other than the partially
	complete implementation here: 
	https://github.com/valekhz/m4b-converter/blob/master/libmp4v2.py
	That thing is actually awesome; the problem is that it only
	does a couple of things. I did try, but I am just not good 
	enough at python to know how to extend it to properly support
	writes as well as reads. I didn't find much documentation on the
	library either, other than mp4(3), which was *way* sparse on the
	implementation details. Sorry, posterity, I have failed you.
	You get this crummy cli wrapper object instead. GG."""
	def __init__(self, file):
		assert(os.path.isfile(file))
		self.file = file

	def _is_installed(self, executable):
		result = subprocess.run(['env', executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		if result.returncode != 127:
			return True
		else:
			return False

	def _mp4bin(self, executable, args):
		assert(self._is_installed(executable))
		return subprocess.run(['env', executable, *args, self.file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode

	def mp4chaps(self, args):
		return self._mp4bin('mp4chaps', args)

	def mp4art(self, args):
		return self._mp4bin('mp4art', args)

	def mp4tags(self, args):
		return self._mp4bin('mp4tags', args)
