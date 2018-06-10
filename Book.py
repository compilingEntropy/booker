#!/usr/bin/env python3.6

import json
import os

class Book:
	"""This is a book object"""
	def __init__(self, path):
		assert(os.path.isdir(path))
		self.path = path
		self.book_data = BookData(path)
		self._files = self._init_files()
		self._chapters = self._init_chapters()
		self._cover = self._find_cover()

	## Properties
	def _get_files(self):
		return self._files
	def _get_chapters(self):
		return self._chapters
	def _get_cover(self):
		return self._cover

	# array containing file dicts, each with 'filename', 'size', 'duration', and 'od-path' entries
	files = property(_get_files, None, None, None)
	# array containing chapter dicts, each with 'filename', 'time-offset', 'title', and 'od-path' entries
	chapters = property(_get_chapters, None, None, None)
	# string containing the name of the highest resolution jpeg file in self.path
	cover = property(_get_cover, None, None, None)


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
				'od-path': file['-odread-original-path'],
				'duration': file['audio-duration']
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
				ch['time-offset'] = int(info[1])
			else:
				ch['time-offset'] = None

			chapters.append(ch)

			if 'contents' in chapter:
				for cont_ch in chapter['contents']:
					if 'path' in cont_ch:
						od_path = cont_ch['path'].split('#')[0]
						chapters.append({
							'title': None,
							'od-path': od_path,
							'filename': self._get_file_name_with_odpath(od_path),
							'time-offset': None
						})
		return chapters

	# returns the name of an mp3 file, given its size
	def _find_cover(self):
		cover_options = dict()
		directory = os.fsencode(self.path)
		for file in os.listdir(directory):
			filename = os.fsdecode(file)
			if filename.endswith('.jpeg'):
				statinfo = os.stat(directory + file)
				cover_options[statinfo.st_size] = filename
		largest_file = 0
		for size, filename in cover_options.items():
			if size > largest_file:
				largest_file = size
		return cover_options[largest_file]

class BookData:
	"""This is a book data object"""
	def __init__(self, path):
		self.path = path
		self.data = self.get_data()

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
	# array of dicts, each dict containing 'title' and 'path' (and occasionally 'contents') keys
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
	def get_data(self):
		"""read the book data json blob into a dict"""
		data = None

		directory = os.fsencode(self.path)

		for file in os.listdir(directory):
			filename = self.path + os.fsdecode(file)
			if filename.endswith('.unknown') or filename.endswith('.json'):
				try:
					with open(filename, 'r') as file:
						data = dict(json.load(file))
					break
				except:
					continue

		return data
