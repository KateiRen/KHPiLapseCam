#!/usr/bin/python 
# -*- coding: latin-1 -*-

# Doku von picamera: http://picamera.readthedocs.org/en/release-1.10/recipes1.html

#Shot: 25 Shutter: 6000000 ISO: 800
#-> 20150830-004414/image25.jpg 6254.36
#==> ergibt in der Datei
# 1/30 Sekunde mit ISO 6
#irgendwas stimmt da nicht
# alternativ mit raspistill probieren....

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
import CameraSettings.py

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", help="increase output verbosity",
                    action="store_true")
parser.parse_args()
 
MIN_INTER_SHOT_DELAY_SECONDS = timedelta(seconds=30) 
MIN_BRIGHTNESS = 20000 
MAX_BRIGHTNESS = 30000 

dopostprocessing = True
dodeflicker = True
verbosemode = True
useraspistill = True
displaycapturedimages = True

fps = 24
videolength = 2 # Minutes
capturelength = 30 # Minutes
totalshots = videolength * 60 * fps
intershotdelay = timedelta(seconds=capturelength * 60 / totalshots) # intershotdelay unit = timedelta in seconds

def main():
    
    idy = Identify(subprocess) # das ist ImageMagick
    if verbosemode==True:
        logging.basicConfig(level=logging.DEBUG)
    print "#######################"
    print "# KH Pi Cam Timelapse #"
    print "#######################"
	
    current_config = int((len(CONFIGS)-1)/2) # in der Mitte der Einstellungen starten
    width = 1296
    height = 730
    shot = 0
    prev_acquired = None
    last_acquired = None
    last_started = None
    
# Unterordner für die Bilder der Serie mit datetime.now() erstellen
    timestr = time.strftime("%Y%m%d-%H%M%S")
    os.mkdir(timestr, 0755 )
    print "Bild Nummer | Belichtungszeit | ISO | Helligkeit"

    try:
        while shot < totalshots:
            last_started = datetime.now()
            config = CONFIGS[current_config]
            #print "Auslösung: %d Belichtungszeit :%.2f sek ISO: %d" % (shot, float(config[0])/1000000, config[1])
            filename = timestr + '/image%05d.jpg' % shot
            #print "filename %s" % filename
            if useraspistill == False:
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
                if verbosemode == True:
                    optionstring = "-w %d -h %d -v -ISO %d --shutter %d -o %s" % (width, height, config[1], config[0], filename)
                    print optionstring
                os.system("raspistill " + optionstring)
                

            prev_acquired = last_acquired
            brightness = float(idy.mean_brightness(filename))
            last_acquired = datetime.now()
            
            #print "Bild Nummer | Belichtungszeit | ISO | Helligkeit"
            print "      %05d |      %.2f sek | %d | %s " % (shot, float(config[0])/1000000, config[1], brightness)
            #print "-> Datei: %s Helligkeit: %s" % (filename, brightness)

            if brightness < MIN_BRIGHTNESS and current_config < len(CONFIGS) - 1:
                current_config = current_config + 1
                if verbosemode == True:
                    print "Mittlere Helligkeit=%0.2f, erhöhe Belichtungszeit/ISO" %brightness
            elif brightness > MAX_BRIGHTNESS and current_config > 0:
                current_config = current_config - 1
                if verbosemode == True:
                    print "Mittlere Helligkeit=%0.2f, erhöhe Belichtungszeit/ISO" %brightness
            else:
                if last_started and last_acquired and last_acquired - last_started < intershotdelay:
                    print "Sleeping for %s" % str(intershotdelay - (last_acquired - last_started))
                    #print "Sleeping for %s" % (MIN_INTER_SHOT_DELAY_SECONDS - (last_acquired - last_started))
                    time.sleep((intershotdelay - (last_acquired - last_started)).seconds)
            shot = shot + 1
            
            # Wenn gewünscht, jedes Bild nach dem Schießen auf dem TFT anzeigen
            if displaycapturedimages == True:
                os.system("fbi -a -T 1 " +filename)

    except Exception,e:
        print str(e)
        
    print "\nEnde der Aufnahmephase\n"

     
    # Wenn gewünscht, nach dem Schießen der Einzelbilder gleich als Video zusammensetzen        
    if dopostprocessing == True:
        #os.system("sudo avconv -r 15 -i %s/image\%05d.jpg -codec libx264 time-lapse.mp4") % timestr
		if dodeflicker == True:
            print "Starte De-Flicker Post-Processing"
            os.systems("for a in "+timestr+"/*.jpg; do echo $a;mogrify -auto-gamma $a;done")
        print "Starte Erstellung des Videos"
        os.system("sudo avconv -y -r 24 -i %s/image\%05d.jpg -an -vcodec libx264 -q:v 1 time-lapse.mp4") % timestr

 

if __name__ == "__main__":
    main()
