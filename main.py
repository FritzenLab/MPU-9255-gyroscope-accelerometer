from machine import I2C, Pin
import time
import struct

# I2C setup — adjust pins for your board
i2c = I2C(0, scl=Pin(5), sda=Pin(4))  # RP2040 example

MPU_ADDR = 0x68

def write_reg(reg, val):
    i2c.writeto_mem(MPU_ADDR, reg, bytes([val]))

def read_bytes(reg, length):
    return i2c.readfrom_mem(MPU_ADDR, reg, length)

# Initialize MPU9255 (accel/gyro only)
def mpu_init():
    write_reg(0x6B, 0x00)  # PWR_MGMT_1: wake up
    time.sleep_ms(10)
    write_reg(0x1B, 0x00)  # GYRO_CONFIG: ±250°/s
    write_reg(0x1C, 0x00)  # ACCEL_CONFIG: ±2g
    print("MPU9255 initialized (gyro/accel only)")

def read_accel():
    data = read_bytes(0x3B, 6)
    ax, ay, az = struct.unpack(">hhh", data)
    return ax / 1638, ay / 1638, az / 1638  # Scale for ±2g

def read_gyro():
    data = read_bytes(0x43, 6)
    gx, gy, gz = struct.unpack(">hhh", data)
    return gx / 131, gy / 131, gz / 131  # Scale for ±250°/s

def read_temp_raw():
    # Read 2 bytes: TEMP_OUT_H (0x41), TEMP_OUT_L (0x42)
    data = i2c.readfrom_mem(MPU_ADDR, 0x41, 2)
    temp_raw = struct.unpack(">h", data)[0]  # Big-endian signed short
    return temp_raw

def read_temp_celsius():
    raw = read_temp_raw()
    temp_c = (raw / 333.87) + 21.0
    return temp_c

# --- Main program ---
mpu_init()

while True:
    ax, ay, az = read_accel()
    gx, gy, gz = read_gyro()
    temp_c = read_temp_celsius()
    
    print("Accel (m/s^2):", ax, ay, az)
    print("Gyro (°/s):", gx, gy, gz)
    print("Temperature: {:.2f} °C".format(temp_c))
    print("------")
    time.sleep(0.5)
