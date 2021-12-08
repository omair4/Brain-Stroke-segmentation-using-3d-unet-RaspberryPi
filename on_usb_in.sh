#!/bin/bash


flag="False"
i=0


sudo python3 /home/pi/brain_stroke/usb_preprocessor.py

sudo echo 3 > /proc/sys/vm/drop_caches


sudo echo 3 > /proc/sys/vm/drop_caches
while [ "$flag" == "False" ]; do
	((i++))
	sudo sync	
	sudo echo 3 > /proc/sys/vm/drop_caches	
	if sudo python3 /home/pi/brain_stroke/predictor.py;then
		flag="TRUE"
	fi

	if [ "$i" = 3 ]; then
		break
	fi
done


sudo rm -r /home/pi/brain_stroke/preprocess/
sudo mkdir /home/pi/brain_stroke/preprocess/

if [ "$flag" == "False" ]; then
	sudo python3 led_error.py
	sudo reboot
fi

sudo echo 3 > /proc/sys/vm/drop_caches


if sudo python3 /home/pi/brain_stroke/uploader.py;then
		echo "Upload Complete! Check USB or Website"
	fi

sudo rm -r /home/pi/brain_stroke/outputs/
sudo mkdir /home/pi/brain_stroke/outputs/

sudo shutdown
