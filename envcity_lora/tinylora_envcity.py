import time
import busio
import digitalio
import board
import adafruit_rfm9x 
from adafruit_tinylora.adafruit_tinylora import TTN, TinyLoRa

cs = digitalio.DigitalInOut(board.D19)
rst = digitalio.DigitalInOut(board.D26)
irq = digitalio.DigitalInOut(board.D21)

# Apply new modem config settings to the radio to improve its effective range 
# rfm9x.signal_bandwidth = 62500 
#rfm9x.coding_rate = 6
#rfm9x.enable_crc = True  

spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

rfm9x = adafruit_rfm9x.RFM9x(spi, cs, rst, 915)

# Apply new modem config settings to the radio to improve its effective range
rfm9x.tx_power = 23
rfm9x.spreading_factor = 12

# TTN Device Address, 4 Bytes, MSB
devaddr = bytearray([0x26, 0x0D, 0x92, 0x64])

# TTN Network Key, 16 Bytes, MSB
nwkey = bytearray([0x6F, 0x45, 0xBA, 0xF8, 0x6E, 0x95, 0x5B, 0x76, 0x13, 0x53, 0x11, 0x6A, 0x50, 0x39, 0xE9, 0x4A])

# TTN Application Key, 16 Bytess, MSB
app = bytearray([0x9D, 0xA3, 0x4C, 0x43, 0xC5, 0xDB, 0x20, 0xE9, 0x27, 0x38, 0x6B, 0x82, 0xB1, 0x92, 0x3A, 0x4D])

ttn_config = TTN(devaddr, nwkey, app, country="AU")

lora = TinyLoRa(spi, cs, irq, rst, ttn_config, channel = 1)

while True:

    data = bytearray([0x01] * 5)
    try:
        print("Sending packet...")
        lora.send_data(data, len(data), lora.frame_counter)
        print("Packet sent!")
    except:
        print("erro");

    lora.frame_counter += 1
    time.sleep(30)

