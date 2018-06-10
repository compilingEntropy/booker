#!/usr/bin/env python3.6

from Book import Book
import m4a
import ffmpeg
from pathlib import Path
import argparse
import os

parser = argparse.ArgumentParser(description='Convert mp3 files to a m4b file with chapter support, id3 data, and a thumbnail')

parser.add_argument('-q', '--quality', type=int, choices=[1, 2, 3, 4, 5], help='A value between [1..5], with higher numbers being better output quality.')
parser.add_argument('path', help='Path of the audiobook directory')
args = parser.parse_args()

class Audiobook:
	"""This is an audiobook object"""
	def __init__(self, path):
		if not path.endswith('/'):
			path += '/'
		assert(os.path.isdir(path))
		self.path = path
		self.od_book = Book(path)
		self.ffmpeg = ffmpeg.ffmpeg()
		self.m4a = None
		self.file = None

	def convert(self, quality):
		print('Converting...')
		files = [self.path+file['filename'] for file in self.od_book.files]
		outfile = self.path+'outfile.m4a'
		self.ffmpeg.convert(files, outfile, quality)
		self.m4a = m4a.m4a(outfile)
		self.file = outfile
		print('Converted!')

	def decorate(self):
		print('Decorating...')
		if not self.file:
			self.file = self.path+'outfile.m4a'
			assert(os.path.isfile(self.file))
		if not self.m4a:
			self.m4a = m4a.m4a(self.file)
		self.m4a.add_art(self.path+self.od_book.cover)
		getrole = lambda r: str.join(', ', [person['name'] for person in self.od_book.book_data.creator if person['role'] == r])
		metadata = {
			'title': self.od_book.book_data.title['main'],
			'subtitle': self.od_book.book_data.title['subtitle'],
			'shortdesc': self.od_book.book_data.description['short'],
			'fulldesc': self.od_book.book_data.description['full'],
			'author': getrole('author'),
			'narrator': getrole('narrator')
		}
		self.m4a.add_tags(metadata)
		ch_index = self.write_chapter_index(self.generate_chapters())
		self.m4a.add_chaps(ch_index)
		print('Decorated!')

	def _fdur(self, od_path):
		for file in self.od_book.files:
			if file['od-path'] == od_path:
				return file['duration']

	def _tconv(self, seconds):
		s, r = divmod(seconds, 1)
		m, s = divmod(s, 60)
		h, m = divmod(m, 60)
		t = "%02d:%02d:%02d" % (h, m, s) + ("%.03f" % r).lstrip('0')
		return t

	def generate_chapters(self):
		chapter_list = list()
		beg_ch = 0

		prev_file_wrap = 0
		next_file_wrap = self._fdur(self.od_book.chapters[0]['od-path'])
		current_file = self.od_book.chapters[0]['od-path']

		for ch in self.od_book.chapters:
			if not ch['time-offset'] and ch['od-path'] == current_file:
				chapter_list.append((self._tconv(0), ch['title']))
				beg_ch += 1
			else:
				break

		for ch in self.od_book.chapters[beg_ch:]:
			if not ch['title']:
				if ch['od-path'] != current_file:
					prev_file_wrap = next_file_wrap
					next_file_wrap += self._fdur(ch['od-path'])
					current_file = ch['od-path']
				continue
			elif not ch['time-offset']:
				t = next_file_wrap
				prev_file_wrap = next_file_wrap
				next_file_wrap += self._fdur(ch['od-path'])
			elif ch['od-path'] != current_file:
				prev_file_wrap = next_file_wrap
				next_file_wrap += self._fdur(ch['od-path'])
				t = ch['time-offset'] + prev_file_wrap
			else:
				t = ch['time-offset'] + prev_file_wrap
			current_file = ch['od-path']
			chapter_list.append((self._tconv(t), ch['title']))

		return chapter_list

	def write_chapter_index(self, chapter_list):
		ch_file = self.path + 'outfile.chapters.txt'
		with open(ch_file, 'w') as file:
			for ch in chapter_list:
				file.write(' '.join(str(i) for i in ch)+"\n")
		assert(os.path.isfile(self.path + 'outfile.chapters.txt'))
		return ch_file

	def rename(self):
		print('Renaming...')
		assert(os.path.isfile(self.file))
		os.rename(self.file, self.file.replace('.m4a', '.m4b'))
		self.file = self.file.replace('.m4a', '.m4b')
		os.rename(self.file, self.file.replace('outfile', self.od_book.book_data.title['main']))
		self.file = self.file.replace('outfile', self.od_book.book_data.title['main'])
		print('Renamed! Your file is at: ' + self.file)

aud = Audiobook(args.path)
aud.convert(args.quality)
aud.decorate()
aud.rename()
