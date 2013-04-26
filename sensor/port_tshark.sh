
CAPTURE_OPTION_FILE=capture_output_options
TSHARK_OPTIONS=$(cat $CAPTURE_OPTION_FILE)
echo $TSHARK_OPTIONS
CAPTURE_FILTER='tcp port 21 or 22 or 23 or 24 or 80 or 110 or 113 or 143 or 194 or 220 or 443 or 993 or 994 or 995 or 1723 or 2195 or 2196 or 3031 or 3283 or 3389 or 3724 or 3784 or 5190 or 5222 or 5900 or 5988 or 6665 or 6666 or 6667 or 6668 or 6669 or 8080'

tshark -f "$CAPTURE_FILTER" -s 512 -n -l -S -w captures/temp -b filesize:512 -b files:10 -T fields $TSHARK_OPTIONS
