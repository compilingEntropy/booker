#!/usr/bin/env bash

# requires a file named LIBBYROOT in libby's root dir
# you can use Filza or something to find the dir the first time
if [[ -f /tmp/libby.path ]] && [[ -d "$( cat /tmp/libby.path )" ]]; then
	cd "$( cat /tmp/libby.path )"
else
	cd "$( find /var/mobile/Containers/Data/ -type f -name 'LIBBYROOT' -print -quit 2> /dev/null | sed -r 's|LIBBYROOT|Documents/Responses/|g' | tee /tmp/libby.path )"
fi

ask() {
	echo "$1"
	read -p 'Y/n: ' answer
	if [[ "$answer" != 'n' ]]; then
		return 0
	else
		return 1
	fi
}

for file in ./*.unknown; do
	if file "$file" | grep -q 'JSON'; then
		book="$( jq -r '.title.main' "$file" )"
		if ask "Use '${book}'?"; then
			json="$file"
			title="$(echo "$book" | tr -dc '[[:alnum:]\-]')"
			echo "$file" > /tmp/file_list.txt
			break
		fi
	fi
done

if [[ -z "$json" ]]; then
	echo "No json files found"
	exit 1
fi
if [[ -z "$title" ]]; then
	echo "Title is empty?"
	exit 1
fi

# it's not fast or efficient, I probably should just figure out how to test if a value is in a list...
# but, it allows multiple books to be checked-out simultaneously and only have the relevant files sent
while read -r size; do
	for file in ./*.mp3; do
		if (( "$( stat -c '%s' "$file" )" == "$size" )); then
			echo "$file" >> /tmp/file_list.txt
		fi
	done
done <<< "$( jq -r '.spine[]."-odread-file-bytes"' "$json" )"

# Take all the jpegs newer than 30 days. I don't know how to figure out which one matters.
# As of the latest update, these will only be used as a backup anyway, since we now try to download the cover.
find . -type f -mtime -30 -name '*.jpeg' -print >> /tmp/file_list.txt

# insert your own destination here
rsync -Phav --files-from=/tmp/file_list.txt ./ home:~/data/audiobooks/"$title"/
