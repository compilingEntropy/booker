#!/usr/bin/env python3.6

import pydub
import json
import re
import os

class Book:
	"""This is a book object"""
	def __init__(self, path):
		# todo: ensure path exists and is a directory
		self.path = path
		self.book_data = BookData(path + 'data.json')
		self._files = self._init_files()
		self._chapters = self._init_chapters()

	## Properties
	def _get_files(self):
		return self._files
	def _get_chapters(self):
		return self._chapters

	# array containing file dicts, each with 'filename', 'size', and 'od-path' entries
	files = property(_get_files, None, None, None)
	# array containing chapter dicts, each with 'filename', 'size', and 'od-path' entries
	chapters = property(_get_chapters, None, None, None)


	## Functions
	# returns the name of an mp3 file, given its size
	def _get_file_name_with_size(self, size):
		directory = os.fsencode(self.path)
		for file in os.listdir(directory):
			filename = os.fsdecode(file)
			if filename.endswith('.mp3'):
				statinfo = os.stat(directory + file)
				if statinfo.st_size == size:
					return filename

	def _init_files(self):
		files = list()
		for file in self.book_data.files:
			size = file['-odread-file-bytes']
			filename = self._get_file_name_with_size(size)
			files.append({
				'filename': filename,
				'size': size,
				'od-path': file['-odread-original-path']
			})
		return files

	def _get_file_name_with_odpath(self, odpath):
		for file in self._files:
			if file['od-path'] == odpath:
				return file['filename']
		return None

	def _init_chapters(self):
		chapters = list()
		for chapter in self.book_data.chapters:
			ch = dict()
			ch['title'] = chapter['title']
			info = chapter['path'].split('#')
			if len(info) > 0:
				ch['od-path'] = info[0]
				ch['filename'] = self._get_file_name_with_odpath(ch['od-path'])
			else:
				ch['od-path'] = None
				ch['filename'] = None
			if len(info) > 1:
				ch['time-offset'] = info[1]
			else:
				ch['time-offset'] = None
			chapters.append(ch)
		return chapters


class BookData:
	"""This is a book data object"""
	def __init__(self, path):
		self.data = self.get_data(path)

	## Properties
	def _get_title(self):
		return self.data['title']
	def _get_creator(self):
		return self.data['creator']
	def _get_description(self):
		return self.data['description']
	def _get_language(self):
		return self.data['language']
	def _get_chapters(self):
		return self.data['nav']['toc']
	def _get_files(self):
		return self.data['spine']

	# dict containing 'main' and 'subtitle' keys
	title = property(_get_title, None, None, None)
	# array containing creator dicts, each with a 'name', 'role', 'bio'
	creator = property(_get_creator, None, None, None)
	# dict containing 'short' and 'full' keys
	description = property(_get_description, None, None, None)
	# string, ISO 2 Letter Language Code
	language = property(_get_language, None, None, None)
	# array of dicts, each dict containing 'title' and 'path' keys
	chapters = property(_get_chapters, None, None, None)
	"""
	array of dicts, each dict containing:
		path
		media-type
		audio-duration
		audio-bitrate
		-odread-spine-position
		-odread-file-bytes
		-odread-original-path
	"""
	files = property(_get_files, None, None, None)

	## Functions
	def get_data(self, book_index='data.json'):
		"""read the book data json blob into a dict"""
		with open(book_index, 'r') as file:
			data = dict(json.load(file))

		return data




