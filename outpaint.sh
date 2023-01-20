#!/bin/sh -e
# Script for generating mask and base image for outpainting
# ./outpaint.sh filename width:height [lrud] outputfile
#
# If you want to make a 512x768 image that outpaints downward:
# ./outpaint.sh filename 512:768 d outputfile

: ${1:?} ${2:?} ${3:?} ${4:?}

out="$4"
maskout="${4%.*}.mask.png"

case "$3" in
	l)
		x=ow-iw
		;;
	r)
		x=0
		;;
	u)
		y=oh-ih
		;;
	d)
		y=0
		;;
esac
x=${x:-"-1"}
y=${y:-"-1"}

res_x=${2%:*}
res_y=${2#*:}
if [ "$res_x" -lt "$res_y" ]; then
	res="$res_x"
else
	res="$res_y"
fi

ffmpeg -i "$1" -filter_complex \
"scale=$res:$res:force_original_aspect_ratio=decrease,split[out][maskout];
[out]pad=$2:$x:$y:white[out];
[maskout]drawbox=c=black:t=fill,pad=$2:$x:$y:white[maskout]" \
-map '[out]' "$out" -map '[maskout]' "$maskout"

