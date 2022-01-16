import pyqtgraph as pg
import numpy as np
import psutil
import time

from pymyolinux import MyoDongle

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

def joint_event_handler(emg_list, orient_w, orient_x, orient_y, orient_z,
                        accel_1, accel_2, accel_3, gyro_1, gyro_2, gyro_3, sample_num):
    DataVisualize.all_emgData_list.append(emg_list[1])
    DataVisualize.plot.setData(DataVisualize.all_emgData_list, pen='g')

    print("-------------------------------------------------------------------------------------------")
    print((emg_list[0], emg_list[1], emg_list[2], emg_list[3], emg_list[4], emg_list[5], emg_list[6], emg_list[7]))
    print((orient_w, orient_x, orient_y, orient_z, accel_1, accel_2, accel_3, gyro_1, gyro_2, gyro_3))
    print((orient_w / MYOHW_ORIENTATION_SCALE, orient_x / MYOHW_ORIENTATION_SCALE, orient_y / MYOHW_ORIENTATION_SCALE,
           orient_z / MYOHW_ORIENTATION_SCALE, accel_1 / MYOHW_ACCELEROMETER_SCALE,
           accel_2 / MYOHW_ACCELEROMETER_SCALE, accel_3 / MYOHW_ACCELEROMETER_SCALE,
           gyro_1 / MYOHW_GYROSCOPE_SCALE, gyro_2 / MYOHW_GYROSCOPE_SCALE, gyro_3 / MYOHW_GYROSCOPE_SCALE))




"""# 获取CPU使用率的定时回调函数
def get_cpu_info(emg_list):

    #cpu = "%0.2f" % psutil.cpu_percent(interval=1)
    data_list.append(emg_list)
    plot.setData(data_list, pen='g')
"""

class DataVisualize:
    all_emgData_list=[]
    device_1 = MyoDongle("/dev/ttyACM0")
    device_1.clear_state()

    myo_devices = device_1.discover_myo_devices()
    if len(myo_devices) > 0:
        device_1.connect(myo_devices[0])
    else:
        print("No devices found, exiting...")
        exit()

    ###
    app = pg.mkQApp()  # 建立app
    win = pg.GraphicsWindow()  # 建立窗口
    win.setWindowTitle(u'pyqtgraph 实时波形显示工具')
    win.resize(800, 500)  # 小窗口大小
    # 创建图表
    historyLength = 100  # 横坐标长度
    p = win.addPlot()  # 把图p加入到窗口中
    p.showGrid(x=True, y=True)  # 把X和Y的表格打开
    p.setRange(xRange=[0, historyLength], yRange=[0, 100], padding=0)
    p.setLabel(axis='left', text='CPU利用率')  # 靠左
    p.setLabel(axis='bottom', text='时间')
    p.setTitle('CPU利用率实时数据')  # 表格的名字
    plot = p.plot()
    timer = pg.QtCore.QTimer()
    #def datacollection(self):

        # device_1.add_imu_handler()
        # device_1.add_emg_handler()
    device_1.enable_imu_readings()
    device_1.enable_emg_readings()
    device_1.add_joint_emg_imu_handler(joint_event_handler)


    timer.timeout.connect(joint_event_handler)  # 定时刷新数据显示

        #device_1.scan_for_data_packets_conditional()
    device_1.scan_for_data_packets(10)

    #def ui(self):
    # pyqtgragh初始化
    # 创建窗口


    timer.start(1000)  # 多少ms调用一次
    app.exec_()


if __name__ == '__main__':
    MYO=DataVisualize