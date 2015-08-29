#!/usr/bin/python 
# -*- coding: latin-1 -*-

# Doku von picamera: http://picamera.readthedocs.org/en/release-1.10/recipes1.html

  
from datetime import datetime 
from datetime import timedelta 
import subprocess 
import time 
import picamera
from wrappers import Identify 
import os, sys #fuer mkdir ...
 
MIN_INTER_SHOT_DELAY_SECONDS = timedelta(seconds=30) 
MIN_BRIGHTNESS = 20000 
MAX_BRIGHTNESS = 30000 

CONFIGS = [(625,100),
	(1000,100),
	(1250,100),
	(2000,100),
	(3125,100),
	(4000,100),
	(5000,100),
	(6250,100),
	(10000,100),
	(12500,100),
	(16667,100),
	(20000,100),
	(25000,100),
	(33333,100),
	(50000,100),
	(66667,100),
	(76923,100),
	(100000,100),
	(166667,100),
	(200000,100),
	(250000,100),
	(300000,100),
	(500000,100),
	(600000,100),
	(800000,100),
	(1000000,100),
	(1600000,100),
	(2500000,100),
	(3200000,100),
	(4000000,100),
	(6000000,100),
	(6000000,200),
	(6000000,400),
	(6000000,800)]
	
def main():
    print "KH Pi Cam Timelapse"
#    camera = GPhoto(subprocess)
    idy = Identify(subprocess) # das ist ImageMagick
    
    current_config = (len(CONFIGS) - 1) / 2 # in der Mitte der Einstellungen starten
    shot = 0
    prev_acquired = None
    last_acquired = None
    last_started = None

# unterordner für die Bilder der Serie mit datetime.now() erstellen
    timestr = time.strftime("%Y%m%d-%H%M%S")
    os.mkdir( timestr, 0755 );

    try:
        while True:
            last_started = datetime.now()
            config = CONFIGS[current_config]
            print "Shot: %d Shutter: %s ISO: %d" % (shot, config[0], config[1])
            
            with picamera.PiCamera() as camera:
                camera.exif_tags['IFD0.Artist'] = 'Karsten Hartlieb'
                camera.exif_tags['IFD0.Copyright'] = 'Copyright (c) 2015 Karsten Hartlieb'
                camera.resolution = (1296, 730)
                camera.exposure_mode = 'off'
                camera.shutter_speed = config[0]
                camera.iso = config[1]
                camera.start_preview()
                #camera.exposure_compensation = 2
                #camera.exposure_mode = 'spotlight'
                #camera.meter_mode = 'matrix'
                #camera.image_effect = 'gpen'

                # Give the camera some time to adjust to conditions
                time.sleep(2)
                filename = timestr + '/image%02d.jpg' % shot
                camera.capture(filename)
                camera.stop_preview()
            

            prev_acquired = last_acquired
            brightness = float(idy.mean_brightness(filename))
            last_acquired = datetime.now()

            print "-> %s %s" % (filename, brightness)

            if brightness < MIN_BRIGHTNESS and current_config < len(CONFIGS) - 1:
                current_config = current_config + 1
            elif brightness > MAX_BRIGHTNESS and current_config > 0:
                current_config = current_config - 1
            else:
                if last_started and last_acquired and last_acquired - last_started < MIN_INTER_SHOT_DELAY_SECONDS:
                    print "Sleeping for %s" % str(MIN_INTER_SHOT_DELAY_SECONDS - (last_acquired - last_started))

                    time.sleep((MIN_INTER_SHOT_DELAY_SECONDS - (last_acquired - last_started)).seconds)
            shot = shot + 1
    except Exception,e:
        print str(e)


if __name__ == "__main__":
    main()