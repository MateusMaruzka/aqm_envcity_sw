import busio
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time
import digitalio
import json
import requests

key = "PM8R5UZXO6T0A86U"

gpio17 = digitalio.DigitalInOut(board.D17)
gpio17.direction = digitalio.Direction.OUTPUT

gpio27 = digitalio.DigitalInOut(board.D27)
gpio27.direction = digitalio.Direction.OUTPUT

gpio22 = digitalio.DigitalInOut(board.D22)
gpio22.direction = digitalio.Direction.OUTPUT


gpio17.value = False
gpio27.value = False

nt = 3
WEe = 0.343
AEe = 0.328
kt = 1
WEo = 0.353
AEo = 0.328
sensitivity = 0.363 # mV / ppb -> V / ppm

# CO_f1 = (Vwe - 343) - 3*(Vae - 328)
# CO_f2 = (Vwe - 343) - kt*(Vae - 328)*(WEo/AEo)
# float co_ppm = (v[0] - 0.343) - nt*(v[1] - 0.328);

def main():

	i2c = busio.I2C(1, 0)

	print("Teste: Alphasense CO-B4")
	v = [0] * 2
	ads = ADS.ADS1115(i2c)
	while True:
		
#		print("---------------")
		for i in [False, True]:

			gpio22.value = i
			chan = AnalogIn(ads, ADS.P0)
			v[int(i)] = chan.voltage
		
		WEu, AEu = v
		WEc = (WEu - WEe) - nt*(AEu - AEe)
		WEc_f2 = (WEu - WEe) - kt*(WEo/AEo)*(AEu - AEe)
		COppm_f1 = (WEc / sensitivity)
		COppm_f2 = WEc_f2 / sensitivity
		#print("WEc:", WEc, "WEu:", WEu, "AEu:", AEu)
		print("COppm(f1)", COppm_f1, "COppm_f2", COppm_f2)

		msg = {
                    "field1": COppm_f1,
                    "field2": WEu,
                    "field3": AEu
                    }
		requests.post("https://api.thingspeak.com/update?api_key="+key, json=msg)
		time.sleep(5)

if __name__ == "__main__":
	main()
