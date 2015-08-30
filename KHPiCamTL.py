#!/usr/bin/python 
# -*- coding: latin-1 -*-

# Doku von picamera: http://picamera.readthedocs.org/en/release-1.10/recipes1.html

#Shot: 25 Shutter: 6000000 ISO: 800
#-> 20150830-004414/image25.jpg 6254.36
#==> ergibt in der Datei
# 1/30 Sekunde mit ISO 6
#irgendwas stimmt da nicht
# alternativ mit wrapper oder OS call für raspistill probieren....
# wrapper für mkdir bauen?

# Optionen für Framerate und End-Dauer des Videos und Dauer der Aufnahme als Basis für Delay und Max_Shots

from datetime import datetime 
from datetime import timedelta 
import subprocess 
import time 
import picamera
from wrappers import Identify 
import os, sys #fuer mkdir ...
import logging
import argparse # siehe http://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging implementieren
 
MIN_INTER_SHOT_DELAY_SECONDS = timedelta(seconds=30) 
MIN_BRIGHTNESS = 20000 
MAX_BRIGHTNESS = 30000 

DOPOSTPROCESSING = False
VERBOSEMODE = False
USERASPISTILL = False

# Wertepaare für Belichtungsdauer (Mikrosekunden) und ISO
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
    
    
    logging.basicConfig(level=logging.DEBUG)
    
    print "KH Pi Cam Timelapse"
#    camera = GPhoto(subprocess)
    idy = Identify(subprocess) # das ist ImageMagick
    
    current_config = int((len(CONFIGS)-1)/2) # in der Mitte der Einstellungen starten
    width = 1296
    height = 730
    shot = 0
    prev_acquired = None
    last_acquired = None
    last_started = None
    useraspistill = True

# Unterordner für die Bilder der Serie mit datetime.now() erstellen
    timestr = time.strftime("%Y%m%d-%H%M%S")
    os.mkdir(timestr, 0755 );

    try:
        while True:
            last_started = datetime.now()
            config = CONFIGS[current_config]
            print "Auslösung: %d Belichtungszeit :%.2f sek ISO: %d" % (shot, float(config[0])/1000000, config[1])
            filename = timestr + '/image%05d.jpg' % shot
            print "filename %s" % filename
            if USERASPISTILL == False:
                with picamera.PiCamera() as camera:
                    camera.exif_tags['IFD0.Artist'] = 'Karsten Hartlieb'
                    camera.exif_tags['IFD0.Copyright'] = 'Copyright (c) 2015 Karsten Hartlieb'
                    camera.resolution = (width, height)
                    camera.exposure_mode = 'off'
                    camera.shutter_speed = config[0]
                    camera.iso = config[1]
                    camera.start_preview()
                    # Give the camera some time to adjust to conditions
                    time.sleep(2)
                    camera.capture(filename)
                    camera.stop_preview()
            else:
                optionstring = "-w %d -h %d -ISO %d --shutter %d -o %s" % (width, height, config[1], config[0], filename)
                if VERBOSEMODE == True:
                    print optionstring
                os.system("raspistill " + optionstring)
                

            prev_acquired = last_acquired
            brightness = float(idy.mean_brightness(filename))
            last_acquired = datetime.now()

            print "-> Datei: %s Helligkeit: %s" % (filename, brightness)

            if brightness < MIN_BRIGHTNESS and current_config < len(CONFIGS) - 1:
                current_config = current_config + 1
                if VERBOSEMODE == True:
                    print "Mittlere Helligkeit=%.2f, erhöhe Belichtungszeit/ISO"
            elif brightness > MAX_BRIGHTNESS and current_config > 0:
                current_config = current_config - 1
                if VERBOSEMODE == True:
                    print "Mittlere Helligkeit=%.2f, erhöhe Belichtungszeit/ISO"
            else:
                if last_started and last_acquired and last_acquired - last_started < MIN_INTER_SHOT_DELAY_SECONDS:
                    #print "Sleeping for %s" % str(MIN_INTER_SHOT_DELAY_SECONDS - (last_acquired - last_started))
                    print "Sleeping for %s" % (MIN_INTER_SHOT_DELAY_SECONDS - (last_acquired - last_started))
                    time.sleep((MIN_INTER_SHOT_DELAY_SECONDS - (last_acquired - last_started)).seconds)
            shot = shot + 1
    except Exception,e:
        print str(e)
        
    if DOPOSTPROCESSING = True:
            os.system("sudo avconv -r 15 -i %s/image\%05d.jpg -codec libx264 time-lapse.mp4") % timestr



if __name__ == "__main__":
    main()
