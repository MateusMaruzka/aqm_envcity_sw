import busio
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import digitalio
import adafruit_dht as dhtfram 
import time
import json
import requests
from statistics import mean


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

    chan = AnalogIn(ads, ADS.P0)
    ads._write_register(0x01, teste)
    v = [0] * 5
    while(1):

        for i in range(5): # 5 sensores duas saídas cada
            gpio27.value = 0
            gpio18.value = 0
            gpio23.value = 1
            gpio24.value = 0 
           # chan = AnalogIn(ads, ADS.P0)
            v[i] = chan.voltage * 1000
            time.sleep(0.1)

        print("i4", mean(v))

        for i in range(5):

            gpio27.value = 1
            gpio18.value = 0
            gpio23.value = 1
            gpio24.value = 0
            v[i] = chan.voltage * 1000
            time.sleep(0.1)

        print("i5", mean(v))
        print("")
        # co_we, co_ae = v[0], v[1] # ok
        # ox_we, ox_ae = v[2], v[3] # ok
        # h2s_we, h2s_ae = v[4], v[5] #ok
        # so2_we, so2_ae = v[6], v[7]
        # nh3_we, nh3_ae = v[8], v[9]
        # no2_we, no2_ae = v[10], v[11´´


if __name__ == "__main__":
	main()
