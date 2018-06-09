#!/usr/bin/env python3.6

'''
Well I *was* using pydub, but it used *obscene* amounts of
memory, and somehow even small inputs would exceed the 4gb
that a wav file can be (even though I don't use wav files,
pydub does internally...). so yeah maybe I'm just bad at
programming or python or something, but you get a cruddy
cli wrapper for this one too.
'''

import subprocess

class ffmpeg:
	"""An ffmpeg object"""
	def __init__(self):
		pass

	def _is_installed(self, executable):
		result = subprocess.run(['env', executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
		if result.returncode != 127:
			return True
		else:
			return False

	def _runffmpeg(self, args):
		executable = 'ffmpeg'
		assert(self._is_installed(executable))
		command = ['env', executable, *args]
		return subprocess.run(command).returncode

	def convert(self, files, outfile, quality=1):
		if not quality: quality = 1
		file_str = str.join('|', files)
		command = ['-y', '-i', 'concat:'+file_str, '-c:a', 'libfdk_aac', '-vbr', str(quality), outfile]
		return self._runffmpeg(command)

		