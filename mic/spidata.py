#!/usr/bin/python
#-------------------------------------------------------------------------------
# Name:        MCP3002 Measure 5V
# Purpose:     Measure the 5V Supply of the Raspberry Pi
#
# Author:      paulv
#
# Created:     22-10-2015
# Copyright:   (c) paulv 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import spidev # import the SPI driver
from time import sleep

DEBUG = False
vref = 3.3 * 1000 # V-Ref in mV (Vref = VDD for the MCP3002)
resolution = 2**10 # for 10 bits of resolution
calibration = 38 # in mV, to make up for the precision of the components

# MCP3002 Control bits
#
#   7   6   5   4   3   2   1   0
#   X   1   S   O   M   X   X   X
#
# bit 6 = Start Bit
# S = SGL or \DIFF SGL = 1 = Single Channel, 0 = \DIFF is pseudo differential
# O = ODD or \SIGN
# in Single Ended Mode (SGL = 1)
#   ODD 0 = CH0 = + GND = - (read CH0)
#       1 = CH1 = + GND = - (read CH1)
# in Pseudo Diff Mode (SGL = 0)
#   ODD 0 = CH0 = IN+, CH1 = IN-
#       1 = CH0 = IN-, CH1 = IN+
#
# M = MSBF
# MSBF = 1 = LSB first format
#        0 = MSB first format
# ------------------------------------------------------------------------------


# SPI setup
spi_max_speed = 1000000 # 1 MHz (1.2MHz = max for 2V7 ref/supply)
# reason is that the ADC input cap needs time to get charged to the input level.
CE = 0 # CE0 | CE1, selection of the SPI device

spi = spidev.SpiDev()
spi.open(1,CE) # Open up the communication to the device
spi.max_speed_hz = spi_max_speed

#
# create a function that sets the configuration parameters and gets the results
# from the MCP3002
#
def read_mcp3002(channel):
    # see datasheet for more information
    # 8 bit control :
    # X, Strt, SGL|!DIFF, ODD|!SIGN, MSBF, X, X, X
    # 0, 1,    1=SGL,     0 = CH0  , 0   , 0, 0, 0 = 96d
    # 0, 1,    1=SGL,     1 = CH1  , 0   , 0, 0, 0 = 112d
    if channel == 0:
        cmd = 0b01100000
    else:
        cmd = 0b01110000

    if DEBUG : print"cmd = ", cmd

    spi_data = spi.xfer2([cmd,0]) # send hi_byte, low_byte; receive hi_byte, low_byte

    if DEBUG : print("Raw ADC (hi-byte, low_byte) = {}".format(spi_data))

    # receive data range: 000..3FF (10 bits)
    # MSB first: (set control bit in cmd for LSB first)
    # spidata[0] =  X,  X,  X,  X,  X,  0, B9, B8
    # spidata[1] = B7, B6, B5, B4, B3, B2, B1, B0
    # LSB: mask all but B9 & B8, shift to left and add to the MSB
    adc_data = ((spi_data[0] & 3) << 8) + spi_data[1]
    return adc_data
