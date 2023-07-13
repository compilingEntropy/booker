#!/usr/bin/env bash

# a fairly new version of ffmpeg and ffprobe is required for this.
# if you are having issues, try updating to the latest version of both programs.

#####
# this script fixes a very specific problem.
#
# sometimes, your audiobook playback might clip or skip words when using certain playback devices.
# this can happen if your device hears silence, then thinks that playback has stopped.
# some devices, which attempt to be "smart", will then go into a kind of power saving mode.
# the issue is, when the next word is spoken, the playback device has to "wake" and usually misses
# some content before it can begin playing again.
#
# if you have the issue of your playback device missing words or cutting the beginning off of
# phrases, and it is due to this problem, you can use this tool to fix it. it will essentially add
# a low volume, low frequency tone to your audiobook which will trick the device into not using
# its power saving mode.
#
# What volume / frequency you use to solve this will depend on your specific device. The defaults
# should work for most devices, but may be audible, which would be annoying. You'll have to play
# with it.
#
# For example, it would fix this guy's problem:
# https://www.reddit.com/r/audible/comments/jtkhdn/solutionworkaround_to_fix_the_audio_clipping/
#####

#####
# generally, experiment with -f and -v to get them as low as possible.
#
# -f   frequency (in hertz) to add to the file. use a low frequency so you can't hear it. if you go
#      too low, your playback device or bluetooth connection stream may filter the frequency out.
# -v   volume of the added noise. 1 will be just as loud as the original track. use low numbers
#      like 0.01 to make the sound inaudible. using a number too low may cause the frequency not to
#      be noticed by the playback device.
#
# -t   use this flag when testing. generates a file that is truncated after the first 5 minutes of
#      audio. that should be enough to test that the settings you're using work without having to
#      reencode the entire file. note that chapter data will mostly fail to add when using this
#      option.
#
# usage:
# ./add_noise.sh [file.m4b] [options]
# ./add_noise.sh ./Oathbringer.m4b -f 2 -v 0.0035 -t
#####

if [[ -f "$1" ]]; then
	orig="$1"
else
	echo 'No file given'
	exit 1
fi

#parse options
i=0
params=( "$@" )
for arg in "${params[@]}"; do
	if [[ "$arg" == "-f" ]]; then
		frequency="${params[$i+1]}"
	fi
	if [[ "$arg" == "-v" ]]; then
		volume="${params[$i+1]}"
	fi
	if [[ "$arg" == '-t' ]]; then
		encode_test=1
	fi
	((i++))
done
if [[ -z "$frequency" ]]; then
	frequency='20'
fi
if [[ -z "$volume" ]]; then
	volume='0.01'
fi

base="$(basename ${orig} .m4b)"
runtime="$(ffprobe -i ${orig} -show_entries format=duration -v quiet -of csv='p=0')"
if (( encode_test == 1 )); then
	duration='300'
	fixed="${base}_${frequency}_${volume}_${duration}.m4b"
else
	duration="$((${runtime%%.*}-1))"
	fixed="${base}_${frequency}_${volume}.m4b"
fi

if [[ -f ./"$fixed" ]]; then
	echo "File '${fixed}' already exists, continuing will delete it."
	ls -lh ./"$fixed"
	ans='?'
	while [[ "$ans" != 'y' && "$ans" != 'n' && -n "$ans" ]]; do
		read -p 'Continue? [y/N]: ' ans
		if [[ "$ans" == 'y' ]]; then
			echo 'Continuing...'
		fi
	done
	if [[ "$ans" != 'y' ]]; then
		exit
	fi
fi
rm -f ./"$fixed"
# echo ffmpeg -f lavfi -i "sine=frequency=${frequency}:sample_rate=44100[out0];amovie=${orig}[out1]" -filter_complex "[0:a:0]aformat=fltp:sample_rates=44100:channel_layouts=stereo,volume=${volume}[a1];[0:a:1]aformat=fltp:sample_rates=44100:channel_layouts=stereo[a2];[a1][a2]amerge=inputs=2" -ac 2 -vn -c:a libfdk_aac -movflags faststart -vbr 1 -shortest -map_metadata 0 -map_chapters 0 -t "$duration" ./"$fixed"
ffmpeg -f lavfi -i "sine=frequency=${frequency}:sample_rate=44100[out0];amovie=${orig}[out1]" -filter_complex "[0:a:0]aformat=fltp:sample_rates=44100:channel_layouts=stereo,volume=${volume}[a1];[0:a:1]aformat=fltp:sample_rates=44100:channel_layouts=stereo[a2];[a1][a2]amerge=inputs=2" -ac 2 -vn -c:a libfdk_aac -movflags faststart -vbr 1 -shortest -map_metadata 0 -map_chapters 0 -t "$duration" ./"$fixed"

[[ -f ./"$fixed" ]] || exit 1

mp4tags -song "$(exiftool -m -s3 -title ${orig})" "$fixed"
mp4tags -artist "$(exiftool -m -s3 -artist ${orig})" "$fixed"
mp4tags -album "$(exiftool -m -s3 -album ${orig})" "$fixed"
mp4tags -writer "$(exiftool -m -s3 -composer ${orig})" "$fixed"
mp4tags -description "$(exiftool -m -s3 -description ${orig})" "$fixed"
mp4tags -longdesc "$(exiftool -m -s3 -longdescription ${orig})" "$fixed"
mp4tags -type "$(exiftool -m -s3 -mediatype ${orig})" "$fixed"
mp4tags -comment "$(exiftool -m -s3 -comment ${orig})" "$fixed"
mp4tags -encodedby "freq:${frequency},vol:${volume}" "$fixed"
# exiftool -ee -tagsFromFile "$orig" -G0:1 "$fixed"

mp4art --remove "$fixed"
mp4art --extract "$orig"
mp4art --add "${base}.art"*".jpg" ./"$fixed"
rm -f "${base}.art"*".jpg"

mp4chaps -r "$fixed"
mp4chaps -x "$orig"
mv "$base.chapters.txt" ./"$(basename -s .m4b ${fixed}).chapters.txt"
mp4chaps -i "$fixed"
rm -f ./"$(basename -s .m4b ${fixed}).chapters.txt"
