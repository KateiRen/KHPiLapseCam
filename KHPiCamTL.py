#!/usr/bin/python 
 
 
from datetime import datetime 
from datetime import timedelta 
import subprocess 
import time 
 
 
from wrappers import GPhoto 
from wrappers import Identify 
from wrappers import NetworkInfo 
 
 
 
 
from ui import TimelapseUi 
 
 
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
	
	
def test_configs():
    camera = GPhoto(subprocess)

    for config in CONFIGS:
      camera.set_shutter_speed(secs=config[0])
      camera.set_iso(iso=str(config[1]))
      time.sleep(1)

def main():
    #print "Testing Configs"
    #test_configs()
    print "Timelapse"
    camera = GPhoto(subprocess)
    idy = Identify(subprocess)
    netinfo = NetworkInfo(subprocess)

    ui = TimelapseUi()

    current_config = 11
    shot = 0
    prev_acquired = None
    last_acquired = None
    last_started = None

    network_status = netinfo.network_status()
    current_config = ui.main(CONFIGS, current_config, network_status)

    try:
        while True:
            last_started = datetime.now()
            config = CONFIGS[current_config]
            print "Shot: %d Shutter: %s ISO: %d" % (shot, config[0], config[1])
            ui.backlight_on()
            ui.show_status(shot, CONFIGS, current_config)
            camera.set_shutter_speed(secs=config[0])
            camera.set_iso(iso=str(config[1]))
            ui.backlight_off()
            try:
              filename = camera.capture_image_and_download()
            except Exception, e:
              print "Error on capture." + str(e)
              print "Retrying..."
              # Occasionally, capture can fail but retries will be successful.
              continue
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
        ui.show_error(str(e))


if __name__ == "__main__":
    main()