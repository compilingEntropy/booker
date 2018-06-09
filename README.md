# booker
Convert mp3 files to a m4b file with chapter support, id3 data, and a thumbnail

Compatible with od. Call via convert.py. Output files are vbr, and the quality scale is 1-5, with 1 being the smallest file and the lowest quality. Default is 1 (audiobooks don't need to be that high quality), but the quality can be set via the -q flag if you don't like how it sounds at a 1.

Examples:
```
./convert.py -q 2 ~/audiobooks/oathbringer/
./convert.py ~/audiobooks/oathbringer/
./convert.py -h
```

Compatibility:
- Works for me on CentOS 7, ymmv

Requirements:
- python3.6 or higher
- ffmpeg compiled with libfdk_aac encoder support
- libmp4v2 utils

