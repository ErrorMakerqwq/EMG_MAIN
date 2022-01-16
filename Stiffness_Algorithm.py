# Intrinsic constant stiffness
from pymyolinux import MyoDongle
import pyqtgraph as pg
import numpy as np
import psutil
K_j = 0

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

# 用butterworth滤波器预处理消除干扰信号
def Preprocessing(emg_list):
    '''def Envelope_graph_processing(emg_list):
    # Muscle activation indicator
    p = 0
    newemg_list=[]
    # 1.Noise treatment

    # 2.Amplitude correction
    for i in range(N):

        newemg_list.append(abs(emg_list[i]))
    # 3.Smoothing and calculate Muscle activation indicator



        #Savitzky-Golay filter
    newemg_list= savgol_filter(newemg_list,5,2)

    #calculate Muscle activation indicator
    for i in range (1,N):
        p=p+abs(newemg_list[i])

    return newemg_list,p

'''


# Remove linear noise from signal
"""def removeLinearNoise(data):
    mean_value = np.mean(
        [data[np.random.randint(0, 500)], data[np.random.randint(0, 500)], data[np.random.randint(0, 500)]])
    print("now the mean of emg is ", mean_value)

    for i in range(len(data)):
        data[i] = data[i] - mean_value

    return data"""




# import
from math import sqrt
from statistics import mean

import matplotlib.pyplot as plt
from random import random

import numpy as np
from scipy import signal
from scipy.signal import savgol_filter

# N indicates the number of channels to collect EMG N= 8
# Human arm stiffness
Ken = 0
# End joint stiffness
Kj = 0

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


def joint_event_handler(emg_list, orient_w, orient_x, orient_y, orient_z,
                                accel_1, accel_2, accel_3, gyro_1, gyro_2, gyro_3, sample_num):

    DataVisualize.all_emgData_list.append(emg_list[1])

    print("-------------------------------------------------------------------------------------------")
    print((emg_list[0], emg_list[1], emg_list[2], emg_list[3], emg_list[4], emg_list[5], emg_list[6], emg_list[7]))
    #print((orient_w, orient_x, orient_y, orient_z, accel_1, accel_2, accel_3, gyro_1, gyro_2, gyro_3))
    print((orient_w / MYOHW_ORIENTATION_SCALE, orient_x / MYOHW_ORIENTATION_SCALE, orient_y / MYOHW_ORIENTATION_SCALE,
                orient_z / MYOHW_ORIENTATION_SCALE, accel_1 / MYOHW_ACCELEROMETER_SCALE,
                accel_2 / MYOHW_ACCELEROMETER_SCALE, accel_3 / MYOHW_ACCELEROMETER_SCALE,
                gyro_1 / MYOHW_GYROSCOPE_SCALE, gyro_2 / MYOHW_GYROSCOPE_SCALE, gyro_3 / MYOHW_GYROSCOPE_SCALE))

class DataVisualize:
    all_emgData_list=[]

    def datacollection(self):
        device_1 = MyoDongle("/dev/ttyACM0")
        device_1.clear_state()

        myo_devices = device_1.discover_myo_devices()
        if len(myo_devices) > 0:
            device_1.connect(myo_devices[0])
        else:
            print("No devices found, exiting...")
            exit()

        # device_1.add_imu_handler()
        # device_1.add_emg_handler()
        device_1.enable_imu_readings()
        device_1.enable_emg_readings()
        device_1.add_joint_emg_imu_handler(joint_event_handler)

        #device_1.scan_for_data_packets_conditional()
        device_1.scan_for_data_packets(5)

    def ui(self):
        return


if __name__ == '__main__':

    Myo = DataVisualize
    Myo.datacollection(DataVisualize)
    print(Myo.all_emgData_list)



    x = np.linspace(1, 500, len(Myo.all_emgData_list))
    emg_list =Myo.all_emgData_list
  #  print(emg_list)

    newemg_list1=emg_list[:]
    newemg_list1 = butter_bandpass_filtfilt(newemg_list1, 4,10, 500,samping_frq)
   # print(newemg_list1)

    #去除线性噪声
   # newemg_list1 = removeLinearNoise(newemg_list)
   # print(newemg_list1)

    newemg_list2=newemg_list1[:]
    newemg_list2=dataSquareRoot(dataSquaring(butter_lowpass_filtfilt(newemg_list2,4,500,samping_frq)))
    #print(newemg_list2)
   # newemg_list2 = dataSquareRoot(butter_lowpass_filtfilt(dataSquaring(newemg_list2)))

    #  print(newemg_list1)

    #print(newemg_list2)

    plt.plot(x, emg_list, marker='o', markersize=3,label="Original_emg")  # 绘制折线图，添加数据点，设置点的大小
    plt.plot(x, newemg_list1, marker='o', markersize=3,label="Through bandpass filter")
    plt.plot(x, newemg_list2, marker='o', markersize=3,label="Final_emg")
    plt.legend(loc='upper left')
   # plt.plot(x, newemg_list2, marker='o', markersize=3)
    plt.show()

