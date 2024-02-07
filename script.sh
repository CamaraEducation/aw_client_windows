#!/bin/bash

rm /home/camara/.camaranms/logs/camaranms_log.log
while true
do
	sleep 600
	bash /home/camara/.camaranms/main.sh 2>&1 | /home/camara/.camaranms/timestamp.sh >> /home/camara/.camaranms/logs/camaranms_log.log
done