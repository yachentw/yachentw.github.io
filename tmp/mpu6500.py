#-*- coding: utf-8 -*-
#!/usr/bin/python
import time
from enum import Enum
import RPi.GPIO as GPIO
import spidev
import struct

class Accel(Enum):
    accel_2g = 0x00
    accel_4g = 0x01
    accel_8g = 0x02
    accel_16g = 0x03

class Gyro(Enum):
    gyro_250s = 0x00
    gyro_500s = 0x01
    gyro_1000s = 0x02
    gyro_2000s = 0x03

MPU6500_WHO_AM_I = 0x75
MPU6500_I_AM = 0x70
MPU6500_PWR_MGMT_1 = 0x6B
MPU6500_ACCEL_XOUT_H = 0x3B
MPU6500_ACCEL_YOUT_H = 0x3D
MPU6500_ACCEL_ZOUT_H = 0x3F
MPU6500_GYRO_XOUT_H = 0x43
MPU6500_GYRO_YOUT_H = 0x45
MPU6500_GYRO_ZOUT_H = 0x47
MPU6500_RA_CONFIG = 0x1A
MPU6500_RA_SMPLRT_DIV = 0x19
MPU6500_RA_GYRO_CONFIG = 0x1B
MPU6500_RA_ACCEL_CONFIG = 0x1C
MPU6500_RA_INT_PIN_CFG = 0x37
MPU6500_RA_INT_ENABLE = 0x38
MPU6500_RA_SIGNAL_PATH_RESET = 0x68
MPU6500_GYRO_XOFF_H = 0x13
MPU6500_GYRO_YOFF_H = 0x15
MPU6500_GYRO_ZOFF_H = 0x17
MPU6500_ACCEL_XOFF_H = 0x77
MPU6500_ACCEL_YOFF_H = 0x7A
MPU6500_ACCEL_ZOFF_H = 0x7D

accelSensitivity = Accel.accel_2g
gyroSensitivity = Gyro.gyro_250s
# samplingRate = 0x00
lowPassFilter = 0x06
spi = spidev.SpiDev()
# MPU6500_INTPIN = 18

cali_offset = {'ax' : 0, 'ay': 0, 'az' : 0}

def init():
    spi.open(0, 0)
    spi.max_speed_hz = 1000000
#    GPIO.setup(MPU6500_INTPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  
#    GPIO.add_event_detect(MPU6500_INTPIN, GPIO.RISING, callback=mpu6500IntISR)

def testWhoAmI():
    ans = readMPU6500(MPU6500_WHO_AM_I, 1)
    if ans[0] == MPU6500_I_AM:
        return True
    else:
        return False

def writeMPU6500(reg, val):
    spi.xfer2([reg, val])

def writeRegBytes(reg, vals):
    packet = [0] * (len(vals) + 1)
    packet[0] = reg
    packet[1:(len(vals)+1)] = vals
    spi.xfer2(packet)

def readMPU6500(reg, byteNum):
    totalLen = byteNum + 1
    packet = [0] * totalLen
    packet[0] = reg | 0x80
    reply = spi.xfer2(packet)
    return reply[1:totalLen]

def calibration():
    axo, = struct.unpack('>h', bytes(readMPU6500(MPU6500_ACCEL_XOFF_H, 2)))
    ayo, = struct.unpack('>h', bytes(readMPU6500(MPU6500_ACCEL_YOFF_H, 2)))
    azo, = struct.unpack('>h', bytes(readMPU6500(MPU6500_ACCEL_ZOFF_H, 2)))
    print("axo: %d, ayo: %d, azo: %d" % (axo, ayo , azo))
    meanall = [0]*7
    for r in range(500):
        reply = readMPU6500All()
        for i in range(len(reply)):
            if (i % 2) != 0:
                val = struct.unpack('>h', bytes(reply[i-1:i+1]))[0]
                meanall[i//2] += val
        time.sleep(0.01)
    return [x//500 for x in meanall]
    
def configModule():
    writeMPU6500(MPU6500_PWR_MGMT_1, 0x80) # 1<<7 reset the whole module first
    time.sleep(0.05)
    writeMPU6500(MPU6500_PWR_MGMT_1, 0x01) # PLL with Z axis gyroscope reference
    time.sleep(0.05)
    writeMPU6500(MPU6500_RA_CONFIG, lowPassFilter)
    time.sleep(0.05)
    # writeMPU6500(MPU6500_RA_SMPLRT_DIV, samplingRate)
    # time.sleep(0.05)
    writeMPU6500(MPU6500_RA_GYRO_CONFIG, gyroSensitivity.value << 3) # Gyro full scale setting
    time.sleep(0.05)
    writeMPU6500(MPU6500_RA_ACCEL_CONFIG, accelSensitivity.value << 3) # Accel full scale setting
    time.sleep(0.05)
    # writeRegBytes(MPU6500_ACCEL_XOFF_H, struct.pack('>h', cali_offset['ax']))
    # time.sleep(0.01)
    # writeRegBytes(MPU6500_ACCEL_YOFF_H, struct.pack('>h', cali_offset['ay']))
    # time.sleep(0.01)
    # writeRegBytes(MPU6500_ACCEL_ZOFF_H, struct.pack('>h', cali_offset['az']))
    # time.sleep(0.01)

    writeMPU6500(MPU6500_RA_INT_PIN_CFG, 0x10) # 1<<4 interrupt status bits are cleared on any read operation
    time.sleep(0.05)
    # writeMPU6500(MPU6500_RA_INT_ENABLE, 0x01) # interupt occurs when data is ready.
    # time.sleep(0.05)
    writeMPU6500(MPU6500_RA_SIGNAL_PATH_RESET, 0x07) # reset gyro and accel sensor
    time.sleep(0.05)



def readMPU6500All():
    packet = [0] * 15
    packet[0] = MPU6500_ACCEL_XOUT_H | 0x80
    reply = spi.xfer2(packet)
    return reply[1:15]

# def mpu6500IntISR(channel):
#     reply = readMPU6500All()
#     strList = []
#     for i in range(len(reply)):
#         if (i % 2) != 0:
#             strList.append("%02x%02x" % (reply[i-1], reply[i]))
#     print (' '.join(strList))


def close():
    writeMPU6500(MPU6500_PWR_MGMT_1, 0x80) # 1<<7 reset the whole module first
    spi.close()
