import busio
import board
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time
import digitalio

gpio17 = digitalio.DigitalInOut(board.D17)
gpio17.direction = digitalio.Direction.OUTPUT

gpio27 = digitalio.DigitalInOut(board.D27)
gpio27.direction = digitalio.Direction.OUTPUT

gpio22 = digitalio.DigitalInOut(board.D22)
gpio22.direction = digitalio.Direction.OUTPUT


gpio17.value = False
gpio27.value = False


def main():
	i2c = busio.I2C(board.SCL, board.SDA)
	print("Hello World")
	ads = ADS.ADS1115(i2c)
	while True:
		
		print("---------------")
		for i in [False, True]:

			gpio22.value = i
			chan = AnalogIn(ads, ADS.P0)
			print("Lendo canal ", int(i))
			print(chan.value, chan.voltage)
			
		
		time.sleep(4)

if __name__ == "__main__":
	main()
