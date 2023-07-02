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

## bonus scripts
Over the years I've developed some helper scripts for this workflow, and I'm releasing them here in the hopes they will be helpful to you.

### add_noise.sh
Adds a low, quiet pure-frequency sine wave to the audiobook. Fixes the problem where your playback device cuts out after the narrator pauses or after a quiet moment. Audible doesn't even fix this! See more details (including usage) at the top of the script.

### send_files.sh
If you run booker on a remote server instead of locally, this script may help. You can use it to send the files from your device to a different device for processing.
