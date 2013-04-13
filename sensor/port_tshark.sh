
CAPTURE_OPTION_FILE=capture_output_options
TSHARK_OPTIONS=$(cat $CAPTURE_OPTION_FILE)
echo $TSHARK_OPTIONS
CAPTURE_FILTER='tcp port 22 or 80 or 113 or 143 or 194 or 201 or 202 or 204 or 206 or 220 or 443 or 993 or 994 or 995 or 5190 or 21 or 24 or 110 or 1503 or 1716 or 1723 or 2195 or 2196 or 3724 or 3784 or 5222 or 6665 or 6666 or 6667 or 6668 or 6669 or 3031 or 3283 or 5900 or 5988 or 3389 or 5290 or 5222 or 1533 or 8000 or 8080 or 8001 or 8081'

tshark -f "$CAPTURE_FILTER" -s 512 -n -l -S -w captures/temp -b filesize:512 -b files:10 -T fields $TSHARK_OPTIONS
