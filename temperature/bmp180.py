import time
import smbus
from ctypes import c_short

# Converted from http://www.raspberrypi-spy.co.uk/

def convertToString(data):
    # Simple function to convert binary data into
    # a string
    return str((data[1] + (256 * data[0])) / 1.2)

def getShort(data, index):
    # return two bytes from data as a signed 16-bit value
    return c_short((data[index] << 8) + data[index + 1]).value

def getUshort(data, index):
    # return two bytes from data as an unsigned 16-bit value
    return (data[index] << 8) + data[index + 1]

class Bmp180(object):

    def __init__(self):
        self.addr = 0x77
        self.last_temp = None
        self.last_pressure = None

        #bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
        self.bus = smbus.SMBus(1) # Rev 2 Pi uses 1

        self.chip_id, self.chip_version = self.read_id()
        print "Chip ID: {0} v{1}".format(self.chip_id, self.chip_version)

    def read_id(self):
        # Register Address
        reg_addr = 0xD0

        try:
            (chip_id, chip_version) = self.bus.read_i2c_block_data(self.addr, reg_addr, 2)
        except IOError:
            print 'Error reading chip id'
            chip_id = 'Unknown'
            chip_version = 0 

        return (chip_id, chip_version)

    def read_data(self):
        # Register Addresses
        reg_calib = 0xaa
        reg_meas = 0xf4
        reg_msb = 0xf6

        # control register address
        crv_temp = 0x2e
        crv_pres = 0x34

        # oversample setting
        oversample = 3 # 0 - 3

        # Read calibration data from EEPROM
        cal = self.bus.read_i2c_block_data(self.addr, reg_calib, 22)

        # Convert byte data to word values
        word_ac1 = getShort(cal, 0)
        word_ac2 = getShort(cal, 2)
        word_ac3 = getShort(cal, 4)
        word_ac4 = getUshort(cal, 6)
        word_ac5 = getUshort(cal, 8)
        word_ac6 = getUshort(cal, 10)
        word_b1 = getShort(cal, 12)
        word_b2 = getShort(cal, 14)
        # word_mb = getShort(cal, 16)
        word_mc = getShort(cal, 18)
        word_md = getShort(cal, 20)

        # Read temperature
        self.bus.write_byte_data(self.addr, reg_meas, crv_temp)
        time.sleep(0.005)
        (msb, lsb) = self.bus.read_i2c_block_data(self.addr, reg_msb, 2)
        u_temp = (msb << 8) + lsb

        # Read pressure
        self.bus.write_byte_data(self.addr, reg_meas, crv_pres + (oversample << 6))
        time.sleep(0.04)
        (msb, lsb, xsb) = self.bus.read_i2c_block_data(self.addr, reg_msb, 3)
        u_pressure = ((msb << 16) + (lsb << 8) + xsb) >> (8 - oversample)

        # Refine temperature
        X1 = ((u_temp - word_ac6) * word_ac5) >> 15
        X2 = (word_mc << 11) / (X1 + word_md)
        B5 = X1 + X2
        temperature = (B5 + 8) >> 4

        # Refine pressure
        B6 = B5 - 4000
        B62 = B6 * B6 >> 12
        X1 = (word_b2 * B62) >> 11
        X2 = word_ac2 * B6 >> 11
        X3 = X1 + X2
        B3 = (((word_ac1 * 4 + X3) << oversample) + 2) >> 2

        X1 = word_ac3 * B6 >> 13
        X2 = (word_b1 * B62) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (word_ac4 * (X3 + 32768)) >> 15
        B7 = (u_pressure - B3) * (50000 >> oversample)

        P = (B7 * 2) / B4

        X1 = (P >> 8) * (P >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = (-7357 * P) >> 16
        pressure = P + ((X1 + X2 + 3791) >> 4)

        self.last_temp = temperature/10.0
        self.last_pressure = pressure/ 100.0
        return (self.last_temp, self.last_pressure)