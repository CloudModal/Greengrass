"""
@author: sun
@license: (C) Copyright 2016-2019, Light2Cloud (Beijing) Web Service Co., LTD
@contact: wenhaijie@light2cloud.com
@software: Greengrass
@file: raspberry_aqi.py
@ide: PyCharm
@time: 2020/6/2 17:42
@desc:
"""
import os
import sys
import time
import json
import serial
import logging
import platform
import threading
import greengrasssdk
import RPi.GPIO as GPIO

from threading import Timer


# Setup logging to stdout
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Creating a greengrass core sdk client
client = greengrasssdk.client("iot-data")

# Retrieving platform information to send from Greengrass Core
my_platform = platform.platform()


# GPIO编号
CHANNEL = 40
POST = "/dev/ttyUSB0"
ser = serial.Serial(POST, 9600, timeout=30)

# When deployed to a Greengrass core, this code will be executed immediately
# as a long-lived lambda function.  The code will enter the infinite while
# loop below.
# If you execute a 'test' on the Lambda Console, this test will fail by
# hitting the execution timeout of three seconds.  This is expected as
# this function never returns a result.


# 哔1次，时长作为参数传递
def beep(seconds):
    GPIO.output(CHANNEL, GPIO.HIGH)
    time.sleep(seconds)
    GPIO.output(CHANNEL, GPIO.LOW)


# 哔N次，时长、间隔时长、重复次数作为参数传递
def beepAction(secs, sleepsecs, times):
    for i in range(times):
        beep(secs)
        time.sleep(sleepsecs)


def get_arduino_data(ser):
    count = ser.inWaiting()
    if count != 0:
        line = ser.read(count)
        recv = str(line, encoding='utf-8')
        ser.reset_input_buffer()
        return recv


# show raspberry temperature,CPU,memory
def get_cpu_temp():
    temp = os.popen('vcgencmd measure_temp').readline()
    temp_float = float(temp.replace('temp=', '').replace('\'C\n', ''))
    if temp_float > 80:
        logger.warning('CPU Temperature is too high, pls cool it down')

    return float(temp_float)


def get_cpu_usage():
    time1 = os.popen('cat /proc/stat').readline().split()[1:5]
    time.sleep(0.2)
    time2 = os.popen('cat /proc/stat').readline().split()[1:5]
    delta_used = int(time2[0]) - int(time1[0]) + int(time2[2]) - int(time1[2])
    delta_total = delta_used + int(time2[3]) - int(time1[3])
    cpu_usage = float(delta_used) / float(delta_total) * 100
    return cpu_usage


def get_ram():
    ram = os.popen('free').read().split()[7:10]
    ram0 = float(ram[0]) / 1024
    ram1 = float(ram[1]) / 1024
    percent = ram1 / ram0 * 100
    ram2 = float(ram[2]) / 1024

    ram = {
        "RAM Total": '%.1f MB' % ram0,
        "RAM Used": '%.1f MB, %.2f' % (ram1, percent) + '%',
        "RAM Free": '%.1f MB' % ram2
    }
    return ram


def get_disk():
    disk = os.popen('df -h /').read().split()[8:12]

    return {
        'Disk total': '%s ' % disk[0],
        'Disk Used': '%s ' % disk[1] + 'and is %s' % disk[3],
        'Disk Free': '%s ' % disk[2]
    }


def greengrass_hello_world_run():
    try:

        recv = get_arduino_data(ser)
        if recv:
            qa = recv.replace('\n', '').replace('\r', '').split(',')
        else:
            beepAction(0.1, 0.1, 3)
            qa = '无法获取来自传感器的数据....!'

        if not my_platform:
            client.publish(
                topic="raspberry/office", queueFullPolicy="AllOrException",
                payload="Hello world! Sent from Greengrass Core."
            )
        else:
            client.publish(
                topic="raspberry/office",
                queueFullPolicy="AllOrException",
                payload=json.dumps(qa, ensure_ascii=False),
            )
    except serial.serialutil.SerialException:
        pass

    except serial.serialutil.SerialException:
        logger.error("Could not open port Permission denied")

    except Exception as e:
        logger.error("Failed to publish message: " + repr(e))

    # Asynchronously schedule this function to be run again in 5 seconds
    Timer(6, greengrass_hello_world_run).start()


# Start executing the function above
greengrass_hello_world_run()


# This is a dummy handler and will not be invoked
# Instead the code above will be executed in an infinite loop for our example
def function_handler(event, context):
    return
