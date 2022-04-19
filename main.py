import busio
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import digitalio
import adafruit_dht as dht

import time
import json
import requests

from alphasense_sensors import Alphasense_Sensors, debug


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
temp = 0;
umid = 0;
dht11 = dht.DHT11(board.D21)

def main():
    
    SDA_ADS = digitalio.DigitalInOut(board.D0)
    SCL_ADS = digitalio.DigitalInOut(board.D1)
    SDA_ADS.Pull = digitalio.Pull.UP
    SCL_ADS.Pull = digitalio.Pull.UP

    print(board.D1)

    i2c_ads = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c_ads, gain = 2/3, mode = 0)
    teste = 0b0100000000000000
    ads._write_register(0x01, teste)

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
    
    # nh3 = Alphasense_Sensors("NH3-B1", "77240205")
    nh3_we, nh3_ae = 0,0
    
    chan = AnalogIn(ads, ADS.P0)
    while(1):
        v = 12 * [0]

        for i in range(2*6): # 5 sensores duas saídas cada
            gpio27.value = i & 0b0001
            gpio18.value = (i & 0b0010) >> 1
            gpio23.value = (i & 0b0100) >> 2
            gpio24.value =  (i & 0b1000) >> 3
            # chan = AnalogIn(ads, ADS.P0)
            v[i] = chan.voltage * 1000
            
            time.sleep(0.1)
        try:
            temp = dht11.temperature
            umid = dht11.humidity
        except:
            print("Erro ao ler temperatura e umidade")

        print("Temperatura: ", temp)
        print("Umidade: ", umid)

        co_we, co_ae, ox_we, ox_ae, h2s_we, h2s_ae, so2_we, so2_ae, nh3_we, nh3_ae, no2_we, no2_ae = v
        # co_we, co_ae = v[0], v[1] # ok
        # ox_we, ox_ae = v[2], v[3] # ok
        # h2s_we, h2s_ae = v[4], v[5] #ok
        # so2_we, so2_ae = v[6], v[7]
        # nh3_we, nh3_ae = v[8], v[9]
        # no2_we, no2_ae = v[10], v[11´´
        
        print("Sensor CO")
        co.all_algorithms(co_we, co_ae, temp)
        print("")

        
        #h2s.all_algorithms(h2s_we, h2s_ae, temp)
        #no2.all_algorithms(no2_we, no2_ae)
        #so2.all_algorithms(so2_we, so2_ae)
        #ox.all_algorithms(ox_we, ox_ae)

        # print("CO Sensibilidade", co.sensitivity)
        # msg = {
	#        "field1": coPPB(co_we, co_ae, temp),
	#        "field2": h2s.PPB(h2s_we, h2s_ae, temp),
	#        "field3": no2.PPB(no2_we, no2_we, temp),
	#        "field4": so2.PPB(so2_we, so2_we, temp),
	#        "field5": ox.PPB(ox_we, ox_we, temp),
        # }
        # print(msg)
        # requests.post("https://api.thingspeak.com/update?api_key="+key, json=msg)
        time.sleep(5)


if __name__ == "__main__":
	main()
