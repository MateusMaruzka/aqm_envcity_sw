import busio
import board
import digitalio

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import adafruit_dht as dht

import time
import requests
import pickle
from json import dumps,loads
from datetime import date

from alphasense_sensors.alphasense_sensors import Alphasense_Sensors
from typing import List, TypeVar, Iterable

from adafruit_tinylora.adafruit_tinylora import TTN, TinyLoRa
from envcity_lora.tinylora_envcity import devaddr, nwkey, appkey

cs = digitalio.DigitalInOut(board.D19)
rst = digitalio.DigitalInOut(board.D26)
irq = digitalio.DigitalInOut(board.D21)

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
ttn_config = TTN(devaddr, nwkey, appkey, country="AU")
lora = TinyLoRa(spi, cs, irq, rst, ttn_config) #, channel = 1)
lora.set_datarate("SF12BW125")

# 6,144 / 2^15 = 0,0001875 -> 00001875 -> Worst case 8 bytes per sensor
# 0,0001875 -> 0,1875 mV

# MUX Pins
# GPIO27 -> S0 ; GPIO18 -> S1 ; GPIO23 -> S2 ; GPIO24 -> S3
def config_mux_pins(pins = [board.D27, board.D18, board.D23, board.D24]):
    gpio_obj = [None] * len(pins)

    for i in range(len(gpio_obj)):
        gpio_obj[i] = digitalio.DigitalInOut(pins[i])
        gpio_obj[i].direction = digitalio.Direction.OUTPUT

    return gpio_obj

# get_bit(value, N) retorna o valor do bit N em value, em que N=0 é o bit menos significativo.
# Ex: get_bit(0b1000, 3) -> 1
# Ex: get_bit(0b1001, 1) -> 0
get_bit = lambda value, idx: (value >> idx) & 1


# Configuracao dos pinos i2c para o conversor AD ADS1115
SDA_ADS = digitalio.DigitalInOut(board.D0)
SCL_ADS = digitalio.DigitalInOut(board.D1)
SDA_ADS.Pull = digitalio.Pull.UP
SCL_ADS.Pull = digitalio.Pull.UP
i2c_ads = busio.I2C(board.SCL, board.SDA)

# Instância do ADS1115
ads = ADS.ADS1115(i2c_ads, gain = 2/3, mode = 0)
teste = 0b0100000000000000 # Define o GND como negative pin
ads._write_register(0x01, teste)


def init_alphasense_sensors():

    co = Alphasense_Sensors("CO-B4", "162741357")

    h2s = Alphasense_Sensors("H2S-B4", "163740262")
    
    no2 = Alphasense_Sensors("NO2-B43F", "202742056")
    
    so2 = Alphasense_Sensors("SO2-B4", "164240347")
    
    ox = Alphasense_Sensors("OX-B431", "204240457")
    
    nh3 = Alphasense_Sensors("NH3-B1", "77240205")
    
    return co, h2s, no2, so2, ox, nh3

# Testando type hints
T = TypeVar('T', int, float)
Vector = Iterable[T]
def dictThingSpeak(data: Vector) -> dict:
    fields = [f"field{i}" for i in range(1, len(data) + 1)]
    return dict(zip(fields, data))



def save_data(fn: str, data):
    with open(fn, "a+b") as f:
        pickle.dump(data, f)

def datalogger(data):
    fn = date.today().strftime("%d_%m_%Y") + ".pickle"
    save_data("/home/pi/envcity_sw_lora/"+fn, data)

def main():

    co, h2s, no2, so2, ox, nh3 = init_alphasense_sensors()

    # GPIO27 -> S0 ; GPIO18 -> S1 ; GPIO23 -> S2 ; GPIO24 -> S3
    gpio27, gpio18, gpio23, gpio24 = config_mux_pins()

    chan = AnalogIn(ads, ADS.P0)
    ads._write_register(0x01, teste)

    # Instância do sensor de temperatura e umidade DHT11
    dht11 = dht.DHT11(board.D21)
    temp, umid = 20, 50

    while(True):
        
        v = 12 * [0]
        
        try:
            temp = dht11.temperature
            umid = dht11.humidity
        except:
            print("Erro ao ler temperatura e umidade")

        print("Temperatura: ", temp, " ","Umidade: ", umid)

        for i in range(2*6): # 5 sensores duas saídas cada

            gpio27.value, gpio18.value, gpio23.value, gpio24.value = [get_bit(i, idx) for idx in range(4)] 
            time.sleep(0.1)
            v[i] = chan.voltage * 1000

        # NAO ALTERAR
        v = [round(i, 4) for i in v]
        co_we, co_ae = v[6:8]
        ox_we, ox_ae = v[4:6]
        h2s_we, h2s_ae = v[2:4]
        so2_we, so2_ae = v[0:2]
        nh3_we, nh3_ae = v[10:12]
        no2_we, no2_ae = v[8:10]

        labels = ["co_we", "co_ae","ox_we", "ox_ae","h2s_we", "h2s_ae","so2_we", "so2_ae", \
        "nh3_we", "nh3_ae" ,"no2_we", "no2_ae", "temp", "umid"]

        data = dict(zip(labels, [co_we, co_ae,ox_we, ox_ae,h2s_we, h2s_ae,so2_we, so2_ae, \
        nh3_we, nh3_ae ,no2_we, no2_ae, temp, umid]))

        datalogger(data)

        co_ppb = co.PPB(co_we, co_ae, temp=temp)
        
        no2_ppb = no2.PPB(no2_we, no2_ae, temp=temp)
        ox_ppb = ox.PPB(ox_we - ox.no2_corr(no2_ppb/1000), ox_ae, temp=temp)
        
        h2s_ppb = h2s.PPB(h2s_we, h2s_ae, temp=temp)
        nh3_ppb = nh3.PPB(nh3_we, nh3_ae)
        so2_ppb = so2.PPB(so2_we, so2_ae, temp=temp)

        data = [co_ppb, no2_ppb, ox_ppb, h2s_ppb, nh3_ppb, so2_ppb, temp, umid]
        print(data)
        data = [int(ppb*1000) for ppb in data]
        print(data)
        data = dumps(data)[1:-1]
        data = bytearray(data, "ascii")

        try:
            print("Sending packet...")
            lora.send_data(data, len(data), lora.frame_counter)
            lora.frame_counter += 1
            print("Packet sent!")
        except:
            print("Falha ao enviar por LoRa")

        # print("Sending H2S, NO2, SO2 info")
        # data = [h2s_we, h2s_ae,no2_we,no2_ae,so2_we,so2_ae,temp,umid]
        # msg = dictThingSpeak(data)
        # requests.post("https://api.thingspeak.com/update?api_key=" + h2s_no2_so2_key, json = msg)

        # print("Sending CO info") 
        # a1, a2, a3, a4 = co.all_algorithms(co_we, co_ae, temp)
        # data = [a1, a2, a3, a4, co_we, co_ae, temp, umid]
        # co_msg = dictThingSpeak(data)
        # requests.post("https://api.thingspeak.com/update?api_key=" + CO_key, json = co_msg)
        
        # print("\nSending OX info") # Concentração de O
        # a1, a2, a3, a4 = ox.all_algorithms(ox_we, ox_ae, temp)
        # data = [a1, a2, a3, a4, ox_we, ox_ae, temp, umid]
        # ox_msg = dictThingSpeak(data)
        # requests.post("https://api.thingspeak.com/update?api_key=" + OX_key, json = ox_msg)

        time.sleep(60)


if __name__ == "__main__":
    main()

