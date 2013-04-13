
while :
do
	rm captures/*
	./port_tshark.sh | python processor.py
done
