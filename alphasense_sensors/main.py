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

CO_key = "XIFCNV2MOZ0F97VV"
OX_key = "4G4A0JHIJJN87QP5"
h2s_no2_so2_key = "X0T5ZL9A8FB4MB0E"
key = "PM8R5UZXO6T0A86U"

gpio27 = digitalio.DigitalInOut(board.D27)
gpio27.direction = digitalio.Direction.OUTPUT

gpio18 = digitalio.DigitalInOut(board.D18)
gpio18.direction = digitalio.Direction.OUTPUT

gpio23 = digitalio.DigitalInOut(board.D23)
gpio23.direction = digitalio.Direction.OUTPUT

gpio24 = digitalio.DigitalInOut(board.D24)
gpio24.direction = digitalio.Direction.OUTPUT


gpio27.value = 0 
gpio18.value = 0
gpio23.value = 0
gpio24.value = 0

# mV / ppb -> V / ppm

dht11 = dht.DHT11(board.D21)

def main():
    
    SDA_ADS = digitalio.DigitalInOut(board.D0)
    SCL_ADS = digitalio.DigitalInOut(board.D1)
    SDA_ADS.Pull = digitalio.Pull.UP
    SCL_ADS.Pull = digitalio.Pull.UP

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
    ads._write_register(0x01, teste)
    temp = 10
    umid = 10

    while(1):
        v = 12 * [0]

        for i in range(2*6): # 5 sensores duas saídas cada
            gpio27.value = i & 0b0001
            gpio18.value = (i & 0b0010) >> 1
            gpio23.value = (i & 0b0100) >> 2
            gpio24.value =  (i & 0b1000) >> 3
            time.sleep(0.1)
            v[i] = chan.voltage * 1000

        try:
            temp = dht11.temperature
            umid = dht11.humidity
        except:
            print("Erro ao ler temperatura e umidade")

        print("Temperatura: ", temp, " ","Umidade: ", umid)

        co_we, co_ae = v[6:8]
        ox_we, ox_ae = v[4:6]
        h2s_we, h2s_ae = v[2:4]
        so2_we, so2_ae = v[0:2]
        nh3_we, nh3_ae = v[10:12]
        no2_we, no2_ae = v[8:10]

        print("Sending H2S, NO2, SO2 info")
        print("h2s voltage", h2s_we, " : ", h2s_ae)
        print("no2 voltage", no2_we, " : ", no2_ae)
        print("so2 voltage", so2_we, " : ", so2_ae)

        msg = {
        "field1": h2s_we,
        "field2": h2s_ae,
        "field3": no2_we,
        "field4": no2_ae,
        "field5": so2_we,
        "field6": so2_ae,
        "field7": temp,
        "field8": umid 
        }

        requests.post("https://api.thingspeak.com/update?api_key=" + h2s_no2_so2_key, json = msg)

        print("Sending CO info") 
        a1, a2, a3, a4 = co.all_algorithms(co_we, co_ae, temp)
        co_msg = {
        "field1" : a1,
        "field2" : a2,
        "field3" : a3,
        "field4" : a4,
        "field5" : co_we,
        "field6" : co_ae,
        "field7" : temp,
        "field8" : umid }
        
        requests.post("https://api.thingspeak.com/update?api_key=" + CO_key, json = co_msg)
        
        print("\nSending OX info")
        a1, a2, a3, a4 = ox.all_algorithms(ox_we, ox_ae, temp)
        ox_msg = {
        "field1": a1,
        "field2": a2,
        "field3": a3,
        "field4": a4,
        "field5": ox_we,
        "field6": ox_ae,
        "field7": temp,
        "field8": umid }

        requests.post("https://api.thingspeak.com/update?api_key=" + OX_key, json = ox_msg)

        time.sleep(50)


if __name__ == "__main__":
	main()
