# -*- coding: UTF-8 -*-
'''
@Project ：PythonMyoLinux-master 
@File    ：TEST.py
@IDE     ：PyCharm
@Author  ：ErrorMaker(LLJ)
@Date    ：2022/1/11 上午12:24
@Module characteristics：******
'''

import queue

from gui_demo.data_tools import DataTools
import gui_main as gm
from pymyolinux import MyoDongle

import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation  # 动图的核心函数
import numpy as np
from scipy import signal

import csv
import matplotlib.pyplot as plt
import tensorflow
from pyfirmata import Arduino,util

global samping_frq
samping_frq = 6000
# Accelerometer values are multipled by the following constant (and are in units of g)
global MYOHW_ACCELEROMETER_SCALE
MYOHW_ACCELEROMETER_SCALE=2048.0
# Gyroscope values are multipled by the following constant (and are in units of deg/s)
global MYOHW_GYROSCOPE_SCALE
MYOHW_GYROSCOPE_SCALE = 16.0
# Orientation values are multipled by the following constant (units of a unit quaternion)
global MYOHW_ORIENTATION_SCALE
MYOHW_ORIENTATION_SCALE = 16384.0

global SIZEOFDATA,SIZEOFDATA1
SIZEOFDATA1=200
SIZEOFDATA=20





def dataSquaring(data):
    for i in range(len(data)):
        data[i] = pow(data[i], 2)
    return data


def dataSquareRoot(data):
    for i in range(len(data)):
        data[i] = data[i] ** 0.5
    return data

def butter_bandpass_filtfilt(data, order, low_fq, high_fq, samping_frq):
    wn1 = 2 * low_fq / samping_frq
    wn2 = 2 * high_fq / samping_frq

    b, a = signal.butter(order, [wn1, wn2], 'bandpass', analog=False)
    output = signal.filtfilt(b, a, data, axis=0)

    return output

def butter_lowpass_filtfilt(data, order, fc, samping_frq):
    wn = 2 * fc / samping_frq

    b, a = signal.butter(order, wn, 'lowpass', analog=False)
    output = signal.filtfilt(b, a, data)

    return output


def data_preprocess(data):
    cur_data=data
    new_data1 = butter_bandpass_filtfilt(cur_data, 4, 10, 500, samping_frq)
    new_data2 = dataSquareRoot(dataSquaring(butter_lowpass_filtfilt(new_data1, 4, 500, samping_frq)))
    return new_data2


def joint_event_handler(emg_list, orient_w, orient_x, orient_y, orient_z,
                                accel_1, accel_2, accel_3, gyro_1, gyro_2, gyro_3, sample_num):

    for j in range(0,8):
        if len(EMG_DATA[j])==SIZEOFDATA1:
            i=0
            while(i<SIZEOFDATA1-1):
                EMG_DATA[j][i]=EMG_DATA[j][i+1]
                i=i+1
            EMG_DATA[j][SIZEOFDATA1 - 1] = emg_list[j]
            print("***")
        else:
            EMG_DATA[j].append(emg_list[j])
            print("+++")



   # print("-------------------------------------------------------------------------------------------")
   # print((emg_list[0], emg_list[1], emg_list[2], emg_list[3], emg_list[4], emg_list[5], emg_list[6], emg_list[7]))
    #print((orient_w, orient_x, orient_y, orient_z, accel_1, accel_2, accel_3, gyro_1, gyro_2, gyro_3))
   # print((orient_w / MYOHW_ORIENTATION_SCALE, orient_x / MYOHW_ORIENTATION_SCALE, orient_y / MYOHW_ORIENTATION_SCALE,
   #             orient_z / MYOHW_ORIENTATION_SCALE, accel_1 / MYOHW_ACCELEROMETER_SCALE,
   #            accel_2 / MYOHW_ACCELEROMETER_SCALE, accel_3 / MYOHW_ACCELEROMETER_SCALE,
 #           gyro_1 / MYOHW_GYROSCOPE_SCALE, gyro_2 / MYOHW_GYROSCOPE_SCALE, gyro_3 / MYOHW_GYROSCOPE_SCALE))


def FIFO(ForceData_list):
	if len(ForceData_list) == SIZEOFDATA:
		i = 0
		while (i < SIZEOFDATA - 1):
			ForceData_list[i] = ForceData_list[i + 1]
			i = i + 1
		ForceData_list[SIZEOFDATA - 1] = force
		print("***")
	else:
		ForceData_list.append(force)
		print("+++")
	return ForceData_list




if __name__ == '__main__':

    device_1 = MyoDongle("/dev/ttyACM1")
    device_1.clear_state()
    myo_devices = device_1.discover_myo_devices()
    if len(myo_devices) > 0:
        device_1.connect(myo_devices[0])
    else:
        print("No devices found, exiting...")
        exit()

    device_1.enable_imu_readings()
    device_1.enable_emg_readings()
    device_1.add_joint_emg_imu_handler(joint_event_handler)


    board = Arduino('/dev/ttyACM0')
    it = util.Iterator(board)

    ForceData_list = [] * SIZEOFDATA
    it.start()
    board.analog[0].enable_reporting()



#####################################################3
    POINTS = 100
    EMG_DATA=[0]*8
    emg_data0 = [0] * 100
    emg_data1 = [0] * 100
    emg_data2 = [0] * 100
    emg_data3 = [0] * 100
    emg_data4 = [0] * 100
    emg_data5 = [0] * 100
    emg_data6 = [0] * 100
    emg_data7 = [0] * 100

    EMG_DATA[0]=emg_data0
    EMG_DATA[1] = emg_data1
    EMG_DATA[2] = emg_data2
    EMG_DATA[3] = emg_data3
    EMG_DATA[4] = emg_data4
    EMG_DATA[5] = emg_data5
    EMG_DATA[6] = emg_data6
    EMG_DATA[7] = emg_data7
    # 设定整个画布的尺寸
    #plt.figure(figsize=(10, 10))

    # fig, ax = plt.subplots()

    f = open('/home/ubantu/Desktop/test.csv', 'w', encoding='utf-8')
    csv_writer = csv.writer(f)
    csv_writer.writerow(["emg_data0","emg_data1","emg_data2","emg_data3","emg_data4","emg_data5","emg_data6","emg_data7","force"])
    while True:




        force = board.analog[0].read()
        device_1.scan_for_data_packets(0.007)
        raw_emg_data0 = data_preprocess(emg_data0)
        raw_emg_data1 = data_preprocess(emg_data1)
        raw_emg_data2 = data_preprocess(emg_data2)
        raw_emg_data3 = data_preprocess(emg_data3)
        raw_emg_data4 = data_preprocess(emg_data4)
        raw_emg_data5 = data_preprocess(emg_data5)
        raw_emg_data6 = data_preprocess(emg_data6)
        raw_emg_data7 = data_preprocess(emg_data7)
        csv_writer.writerow([raw_emg_data0[-1],raw_emg_data1[-1],raw_emg_data2[-1],raw_emg_data3[-1],raw_emg_data4[-1],raw_emg_data5[-1],raw_emg_data6[-1],raw_emg_data7[-1],force])


        """ # emg_data0
        plt.clf()
        plt.subplot(8, 2, 1)
        plt.plot(emg_data0)

        plt.subplot(8, 2, 2)
        plt.plot(raw_emg_data0)

        # emg_data1
        plt.subplot(8, 2, 3)
        plt.plot(emg_data1)

        plt.subplot(8, 2, 4)
        plt.plot(raw_emg_data1)

        # emg_data2
        plt.subplot(8, 2, 5)
        plt.plot(emg_data2)

        plt.subplot(8, 2, 6)
        plt.plot(raw_emg_data2)
        # emg_data3
        plt.subplot(8, 2, 7)
        plt.plot(emg_data3)

        plt.subplot(8, 2, 8)
        plt.plot(raw_emg_data3)
        # emg_data4
        plt.subplot(8, 2, 9)
        plt.plot(emg_data4)

        plt.subplot(8, 2, 10)
        plt.plot(raw_emg_data4)
        # emg_data5
        plt.subplot(8, 2, 11)
        plt.plot(emg_data5)

        plt.subplot(8, 2, 12)
        plt.plot(raw_emg_data5)
        # emg_data6
        plt.subplot(8, 2, 13)
        plt.plot(emg_data6)

        plt.subplot(8, 2, 14)
        plt.plot(raw_emg_data6)
        # emg_data7
        plt.subplot(8, 2, 15)
        plt.plot(emg_data7)

        plt.subplot(8, 2, 16)
        plt.plot(raw_emg_data7)


      #  print(raw_emg_data0[0])


        plt.pause(0.01)
        plt.draw()
        """
    f.close()
#      newemg_data1 = emg_data0
   #     newemg_data1 = butter_bandpass_filtfilt(newemg_data1, 4, 10, 500, samping_frq)
#
  #      newemg_data2 = newemg_data1[:]
   #     newemg_data2 = dataSquareRoot(dataSquaring(butter_lowpass_filtfilt(newemg_data2, 4, 500, samping_frq)))
        # 显示时间
   #     plt.pause(0.01)




##################################################



