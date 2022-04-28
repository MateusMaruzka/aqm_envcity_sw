import digitalio
import board
import busio
import adafruit_rfm9x

RADIO_FREQ_MHZ = 915.0
CS = digitalio.DigitalInOut(board.D19)
RESET = digitalio.DigitalInOut(board.D26)
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
rfm9x = adafruit_rfm9x.RFM9x(spi, CS, RESET, RADIO_FREQ_MHZ)

# Apply new modem config settings to the radio to improve its effective range
rfm9x.signal_bandwidth = 62500
rfm9x.coding_rate = 6
rfm9x.spreading_factor = 8
rfm9x.enable_crc = True
