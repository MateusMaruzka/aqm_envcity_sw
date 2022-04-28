import board
import busio
import adafruit_ads1x15.ads1115 as ADS

print(dir(board))
print("Board I2C SCL", board.D0.id)
print("Board I2C SDA", board.SDA)

i2c = busio.I2C(board.SCL, board.SDA)

print(i2c.scan())
i2c.deinit()
