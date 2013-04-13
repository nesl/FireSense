
CAPTURE_OPTION_FILE=capture_output_options
TSHARK_OPTIONS=$(cat $CAPTURE_OPTION_FILE)
echo $TSHARK_OPTIONS

tshark -f "tcp" -s 512 -n -l -S -w captures/temp -b filesize:64 -b files:2 -T fields $TSHARK_OPTIONS
