#!/usr/bin/python 
# -*- coding: latin-1 -*-

#nohup python KHPiCamTLMQTT.py &

# Doku von picamera: http://picamera.readthedocs.org/en/release-1.10/recipes1.html

#Shot: 25 Shutter: 6000000 ISO: 800
#-> 20150830-004414/image25.jpg 6254.36
#==> ergibt in der Datei
# 1/30 Sekunde mit ISO 6
#irgendwas stimmt da nicht
# alternativ mit raspistill probieren....

# Optionen für Framerate und End-Dauer des Videos und Dauer der Aufnahme als Basis für Delay und Max_Shots

# Camera Settings um dritte Spalte für "1/200 Sekunde" erweitern


from datetime import datetime 
from datetime import timedelta 
import paho.mqtt.client as mqtt
import subprocess 
# sudo apt-get install imagemagick
import time 
import picamera
from wrappers import Identify 
import os, sys #fuer mkdir ...
import logging
import argparse # siehe http://stackoverflow.com/questions/14097061/easier-way-to-enable-verbose-logging implementieren
import CameraSettings
CONFIGS = CameraSettings.CONFIGS

parser = argparse.ArgumentParser()
parser.add_argument("--verbose", help="increase output verbosity",
                    action="store_true")
parser.parse_args()
 
MIN_INTER_SHOT_DELAY_SECONDS = timedelta(seconds=30) 
MIN_BRIGHTNESS = 20000 
MAX_BRIGHTNESS = 30000 

dovideoencoding = True
# sudo apt-get install libav-tools

dodeflicker = False
verbosemode = False
useraspistill = True
displaycapturedimages = False

# fps = 12
# videolength = 0.1 # Minutes
# capturelength = 10 # Minutes
fps = 24
videolength = 1 # Minutes
capturelength = 11520 # Minutes
totalshots = videolength * 60 * fps
#intershotdelay = timedelta(seconds=capturelength * 60 / totalshots) # intershotdelay unit = timedelta in seconds
intershotdelay = capturelength * 60 / totalshots # [Sekunden]

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))



def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.connect("192.168.178.101", 1883, 60)
    client.loop_start()

    teststart=float(time.time()) # Startzeit abspeichern und am Ende mit der Endzeit anzeigen
    idy = Identify(subprocess) # das ist ImageMagick
    if verbosemode==True:
        logging.basicConfig(level=logging.DEBUG)
    print "#######################"
    print "# KH Pi Cam Timelapse #"
    print "#######################"
    print "\nAufnahmedauer: %d Minuten" % capturelength
    print "Anzahl Aufnahmen: %d" % totalshots
    print "Pause zwischen den Fotos: %d Sekunden" % intershotdelay

    current_config = int((len(CONFIGS)-1)/2) # in der Mitte der Einstellungen starten
    width = 1296
    height = 730
    shot = 0
    prev_acquired = None
    last_acquired = None
    last_started = None
    comment="Start"
    
# Unterordner für die Bilder der Serie mit datetime.now() erstellen
    timestr = time.strftime("%Y%m%d-%H%M%S")
    os.mkdir(timestr, 0755 )
    
    try:
        #das erste Mal außerhalb der Schleife, später schon nach dem Sleep damit Änderungen der Belichtung mit gestoppt werden
        starttime = float(time.time())
        while shot < totalshots:
            #last_started = datetime.now()
            config = CONFIGS[current_config]
            filename = timestr + '/image%05d.jpg' % shot
            client.publish("zigbee2mqtt/Lampe_Schreibtisch/set", "{   \"state\": \"ON\", \"transition\": \"2\" }")
            time.sleep(2)
            if useraspistill == False:
                with picamera.PiCamera() as camera:
                    camera.exif_tags['IFD0.Artist'] = 'Karsten Hartlieb'
                    camera.exif_tags['IFD0.Copyright'] = 'Copyright (c) 2015 Karsten Hartlieb'
                    camera.resolution = (width, height)
                    camera.exposure_mode = 'off'
                    camera.shutter_speed = config[2]
                    camera.iso = config[0]
                    camera.start_preview()
                    # Give the camera some time to adjust to conditions
                    time.sleep(2)
                    camera.capture(filename)
                    camera.stop_preview()
                    time.sleep(2)
            else:
                optionstring = "-w %d -h %d -t 1 -ISO %d --shutter %d -o %s" % (width, height, config[0], config[2], filename)
                if verbosemode == True:
                    optionstring = "-w %d -h %d -v -t 1 -ISO %d --shutter %d -o %s" % (width, height, config[0], config[2], filename)
                    print optionstring
                os.system("raspistill " + optionstring)

            time.sleep(2)    
            client.publish("zigbee2mqtt/Lampe_Schreibtisch/set", "{   \"state\": \"OFF\", \"transition\": \"2\" }")

            #prev_acquired = last_acquired
            brightness = float(idy.mean_brightness(filename))
            #last_acquired = datetime.now()
            
            if shot%20 == 0:
                # alle paar Zeilen die Überschrift widerholen
                print "\nBildNr.| Shutter  | ISO | Helligkeit | Kommentar"
                print "------------------------------------------------------------"
            #print " %05d |      %.2f sek   | %d |    %s  | %s" % (shot, float(config[0])/1000000, config[1], brightness, comment)
            print " %05d | %s | %d |      %5.0f | %s" % (shot, config[1], config[0], brightness, comment)

            if brightness < MIN_BRIGHTNESS and current_config < len(CONFIGS) - 1:
                current_config = current_config + 1
                comment = "Belichtungskorrektur"
                if verbosemode == True:
                    print "Mittlere Helligkeit=%0.2f, erhöhe Belichtungszeit/ISO" %brightness
            elif brightness > MAX_BRIGHTNESS and current_config > 0:
                current_config = current_config - 1
                comment = "Belichtungskorrektur"
                if verbosemode == True:
                    print "Mittlere Helligkeit=%0.2f, erhöhe Belichtungszeit/ISO" %brightness
            else:
                comment=""
                endtime = float(time.time()) #datetime.now()
                #print "Dauer der Auslösung: %f" % (endtime-starttime)
                #if ((endtime - starttime) > timedelta(seconds=int(intershotdelay))):
                #if (int((endtime - starttime).strftime("%S")) > intershotdelay):
                if ((int(endtime) - int(starttime)) < intershotdelay):
                    #print "bis hier gehts noch"
                    #time.sleep((intershotdelay - (endtime - starttime)).seconds)
                    time.sleep(intershotdelay - (endtime - starttime))
                else:
                    comment="Zeitüberschreitung"
                #if last_started and last_acquired and last_acquired - last_started < intershotdelay:
                    #if verbosemode==True:
                        #print "Sleeping for %s" % str(intershotdelay - (last_acquired - last_started))
                    
                    #time.sleep((intershotdelay - (last_acquired - last_started)).seconds)
                    
            starttime = float(time.time())
            shot = shot + 1
            
            # Wenn gewünscht, jedes Bild nach dem Schießen auf dem TFT anzeigen aber Konsolen-Ausgabe unterdrücken
            if displaycapturedimages == True:
                # hier wird jedesmal ein neuer Prozess gestartet, wie kann man das verhindern?
                os.system("fbi -a -T 1 " +filename + " 2> /dev/null")

    except Exception,e:
        print str(e)

    testende = float(time.time())

    print "Geplante Dauer der Aufnahmephase: %d Stunden, %d Minuten" % (capturelength/60, capturelength - int(capturelength/60)*60)
    print "Reale Dauer der Serie: %d Stunden, %d Minuten" % ((testende - teststart)/3600, (testende - teststart)/60- int((testende - teststart)/3600)*60)

    if displaycapturedimages == True:
        # Ausgabe wieder auf Terminal zurückbiegen
        # klappt das?
        os.system("con2bmap 1 1")
    print "\nEnde der Aufnahmephase"

    if dodeflicker == True:
        print "\nStarte De-Flicker Post-Processing\n"
        commandstring = "for a in "+timestr+"/*.jpg; do echo $a;mogrify -auto-gamma $a;done"
        print commandstring
        os.system(commandstring)

    # Wenn gewünscht, nach dem Schießen der Einzelbilder gleich als Video zusammensetzen        
    if dovideoencoding == True:
        print "\nStarte Erstellung des Videos\n"
        #commandstring = "sudo avconv -y -r 24 -i %s/image\%05d.jpg -an -vcodec libx264 -q:v 1 time-lapse.mp4" %  timestr
        #commandstring = "sudo avconv -y -r 24 -i " + timestr +"/image\%05d.jpg -an -vcodec libx264 -q:v 1 time-lapse.mp4"
        commandstring = "sudo avconv -y -r 24 -i " + timestr +"/image%05d.jpg -an -vcodec libx264 -q:v 1 " + timestr + "/" + timestr + "_time-lapse.mp4"
        print commandstring
        os.system(commandstring)

    #weil das Skript mit SU läuft, gehören auch alle Files root, das korrigieren wir mal schnell noch
    os.system("chown -R pi " + timestr)

 

if __name__ == "__main__":
    main()
