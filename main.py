import busio
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import digitalio
# import adafruit_dht as dht

import time
import json
import requests


from alphasense_sensors import Alphasense_Sensors

key = "PM8R5UZXO6T0A86U"

gpio27 = digitalio.DigitalInOut(board.D27)
gpio27.direction = digitalio.Direction.OUTPUT

gpio18 = digitalio.DigitalInOut(board.D18)
gpio18.direction = digitalio.Direction.OUTPUT

gpio23 = digitalio.DigitalInOut(board.D23)
gpio23.direction = digitalio.Direction.OUTPUT

gpio24 = digitalio.DigitalInOut(board.D24)
gpio24.direction = digitalio.Direction.OUTPUT


gpio27.value = 0 # s0, s1, s2 s3 
gpio18.value = 0 
gpio23.value = 0
gpio24.value = 0

# mV / ppb -> V / ppm

# dht11 = dht.DHT11(board.)


def main():
    
    SDA_ADS = digitalio.DigitalInOut(board.D0)
    SCL_ADS = digitalio.DigitalInOut(board.D1)
    SDA_ADS.Pull = digitalio.Pull.UP
    SCL_ADS.Pull = digitalio.Pull.UP

    print(board.D1)

    i2c_ads = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c_ads)

    co = Alphasense_Sensors("CO-B4", "162741357")
    # print(co.sensitivity)

    h2s = Alphasense_Sensors("H2S-B4", "163740262")
    # print(h2s.sensitivity)
    
    no2 = Alphasense_Sensors("NO2-B43F", "202742056")
    # print(no2.sensitivity)
    
    so2 = Alphasense_Sensors("SO2-B4", "164240347")
    # print(so2.sensitivity)
    
    ox = Alphasense_Sensors("OX-B431", "204240457")
    # print(ox.sensitivity)
    
    while(1):
	    v = 12 * [0]
	    
	    for i in range(2*6): # 5 sensores duas saídas cada
	        
	        gpio27.value = i & 0b0001
	        gpio18.value = (i & 0b0010) >> 1
	        gpio23.value = (i & 0b0100) >> 2
	        gpio24.value =  (i & 0b1000) >> 3
	        
	        chan = AnalogIn(ads, ADS.P0)
	        v[i] = chan.voltage
	        
	        time.sleep(0.1)


	    co_we, co_ae = v[0], v[1]
	    h2s_we, h2s_ae = v[2], v[3]
	    no2_we, no2_ae = v[4], v[5]
	    so2_we, so2_ae = v[6], v[7]
	    ox_we, ox_ae = v[8], v[9]
	    
	    
	    msg = {
	        "field1": co.PPM(co_we, co_ae),
	        "field2": h2s.PPM(h2s_we, h2s_ae),
	        "field3": no2.PPM(no2_we, no2_we),
	        "field4": so2.PPM(so2_we, so2_we),
	        "field5": ox.PPM(ox_we, ox_we),
	    }
	    print(msg)
	    requests.post("https://api.thingspeak.com/update?api_key="+key, json=msg)

	    time.sleep(5)


if __name__ == "__main__":

	main()
