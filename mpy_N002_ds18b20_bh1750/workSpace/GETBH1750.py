import machine
import onewire, ds18x20
import time
from machine import I2C

# init eps8266 i2c
#scl = machine.Pin(5)
#sda = machine.Pin(4)
#i2c = machine.I2C(scl,sda)
i2c = machine.I2C(scl=machine.Pin(5), sda=machine.Pin(4))
#i2c = I2C.init(scl, sda, *, freq=400000)

OP_SINGLE_HRES1 = 0x20
OP_SINGLE_HRES2 = 0x21
OP_SINGLE_LRES = 0x23
DELAY_HMODE = 180  # 180ms in H-mode
DELAY_LMODE = 24  # 24ms in L-mode

ds_pin = machine.Pin(0)#D3
ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
roms = ds_sensor.scan()

def getlux():
	lux = sample(i2c)
	return str(lux)

def sample(i2c, mode=OP_SINGLE_HRES1, i2c_addr=0x23):
    i2c.writeto(i2c_addr, b"\x00")  # make sure device is in a clean state
    i2c.writeto(i2c_addr, b"\x01")  # power up
    i2c.writeto(i2c_addr, bytes([mode]))  # set measurement mode
    time.sleep_ms(DELAY_LMODE if mode == OP_SINGLE_LRES else DELAY_HMODE)
    raw = i2c.readfrom(i2c_addr, 2)
    i2c.writeto(i2c_addr, b"\x00")  # power down again
    # we must divide the end result by 1.2 to get the lux
    return ((raw[0] << 24) | (raw[1] << 16)) // 78642

def getds18x20():
	global ds_sensor,roms
	ds_sensor.convert_temp()
	tt=""
	for rom in roms:
		tt=tt+str(ds_sensor.read_temp(rom))
		print(tt)
	#ii=int(tt)*0.1
	return tt

def main():
    while True:
        print(getlux())
        ss=getds18x20()
        print(ss)

if __name__ == '__main__':
    main()

