import pandas as pd
import numpy as np
import datetime
import math
from utils.weather_utils import getWeatherConditionByCoordinateAndDate

# # 车速稳定性判断，返回布尔值列表，标记每行是否车速不稳定
# def Speed_Stability_Label(df, threshold=40): # 可以调整阈值
#     speed_std = Speed_Stability(df) # 复用之前的函数计算标准差
#     labels = [speed_std > threshold] * len(df) # 所有行标记为相同结果 (路段级别不稳定)
#     return labels # 返回与 DataFrame 行数相同的列表，值都一样
#
# # 复用之前的函数计算车速标准差，仅供 Speed_Stability_Label 调用
# def Speed_Stability(df):
#     return np.std(df['gps_speed'], ddof=1)

# 急加速急减速判断，返回布尔值列表，标记每行是否急加速或急减速
def acce_decelerate_label(df, accelerate_threshold=3, decelerate_threshold=-3, time_interval_threshold=3): # 阈值可调
    rows = df.shape[0]
    labels = [False] * rows # 初始化标签列表
    currentState = False  # false表示当前时间正在减速
    sumTime = 0   #保存一段加速/减速的累计时间

    for i in range(0, rows - 1):
        lastItem = df.iloc[i]
        currentItem = df.iloc[i + 1]
        # 取出前后相邻的时间，计算差值
        lastTime = datetime.datetime.strptime(lastItem.iloc[10], '%Y-%m-%d %H:%M:%S')
        currentTime = datetime.datetime.strptime(currentItem.iloc[10], '%Y-%m-%d %H:%M:%S')
        delta = currentTime - lastTime
        # 时间间隔小于等于阈值，考虑加减速
        timeInterval = delta.total_seconds()
        if timeInterval <= time_interval_threshold:
            lastSpeed = lastItem.iloc[11]
            currentSpeed = currentItem.iloc[11]
            a = (currentSpeed - lastSpeed) / (3.6 * timeInterval)   # 计算加速度

            if a < decelerate_threshold: # 急减速
                for j in range(i, max(-1, i-2), -1): # 往前标记 (最多往前标记3行，包括当前行)
                    labels[j] = True
            elif a > accelerate_threshold: # 急加速
                for j in range(i, max(-1, i-2), -1): # 往前标记 (最多往前标记3行，包括当前行)
                    labels[j] = True
    return labels

# 熄火滑行判断，返回布尔值列表，标记每行是否熄火滑行
def SlideOnFrameOut_label(df, speed_threshold=50, time_interval_threshold=0): # 阈值可调
    rows = df.shape[0]
    labels = [False] * rows
    isSlide = False
    startTime = 0
    startlng = 0
    startlat = 0

    for i in range(0, rows):
        item = df.iloc[i]
        acc_state = item.iloc[5]
        gps_speed = item.iloc[11]

        if acc_state == 0 and gps_speed < speed_threshold:
            if not isSlide:  # 开始熄火滑行
                isSlide = True
                startTime = datetime.datetime.strptime(item.iloc[10], '%Y-%m-%d %H:%M:%S')
                startlat = item.iloc[4]
                startlng = item.iloc[3]
            labels[i] = True # 标记当前行为熄火滑行
        elif isSlide: # 结束熄火滑行后，也标记最后一段为熄火滑行 (可以根据需求调整)
            labels[i] = True
            isSlide = False # 结束标记

    return labels

# 超速判断，返回布尔值列表，标记每行是否超速
def overspeed_label(df, speed_max=80, time_threshold=3): # 阈值可调
    labels = [False] * len(df)
    flag_list = [0] * (df.__len__() + 3)  # 初始化一个flag,用来标记当前记录是否已扫描
    for i in df.index:
        if df.loc[i]['gps_speed'] > speed_max and flag_list[i] == 0:
            t1 = i  # 超速开始时间
            n = i + 1
            while n < df.__len__() and df.loc[n]['gps_speed'] > speed_max:
                flag_list[n] = 1
                n += 1
            t2 = n - 1  # 超速结束时间
            time_len = pd.to_datetime(df.loc[t2]['location_time']) - pd.to_datetime(df.loc[t1]['location_time'])
            time_len = time_len.total_seconds()
            if time_len >= time_threshold:#为防止gps漂移，超速时长至少为阈值才会被记录
                for j in range(t1, n): # 标记超速时间段内的所有行
                    labels[j] = True
    return labels


# 疲劳驾驶判断，返回布尔值列表，标记每行是否疲劳驾驶 (仅标记超出4小时驾驶 *之后* 的行, 判断标准与原 fatigueDriving 相同)
def fatigueDriving_label(df, duration_threshold_hours=4): # 阈值可调
    labels = [False] * len(df)
    rows = df.shape[0]
    drive = False
    # setOffTime = datetime.datetime.strptime(df.loc[0]['location_time'], '%Y-%m-%d %H:%M:%S')
    startRestTime = None  # 开始休息的时间
    rest = False
    continuous_drive_start_time = None # 记录单次连续驾驶的开始时间，用于标记label

    for i in range(1, rows):
        item = df.iloc[i]
        curTime = datetime.datetime.strptime(df.loc[i]['location_time'], '%Y-%m-%d %H:%M:%S')
        lastTime = datetime.datetime.strptime(df.loc[i - 1]['location_time'], '%Y-%m-%d %H:%M:%S')
        timeInterval = (curTime - lastTime).total_seconds()

        # 出现相邻两条数据之间时间间隔大于20分钟，需要结束前面的统计
        if timeInterval > 1200 and drive:
            drive = False
            continuous_drive_start_time = None # 结束连续驾驶，重置开始时间

        # 开始单次连续驾驶行为
        if item.iloc[11] != 0 and not drive:
            drive = True
            continuous_drive_start_time = curTime # 记录单次连续驾驶开始时间
        elif item.iloc[11] == 0 and drive and not rest:
            startRestTime = curTime
            rest = True
        elif item.iloc[11] != 0 and drive and rest:
            restTime = lastTime - startRestTime
            rest = False
            if restTime.total_seconds() >= 1200:  # 休息够20分钟，开车状态变为false,重新记录单次连续驾驶行为
                # 结束当次连续驾驶
                drive = False
                continuous_drive_start_time = None # 结束连续驾驶，重置开始时间
        elif item.iloc[11] != 0 and drive and not rest:
            # 持续驾驶中，检查是否超过4小时阈值，并标记标签 (在持续驾驶过程中 *实时* 标记)
            if continuous_drive_start_time is not None:
                continuous_driving_duration = (curTime - continuous_drive_start_time).total_seconds()
                if continuous_driving_duration > duration_threshold_hours * 3600:
                    labels[i] = True # 标记当前行为疲劳驾驶


    # sumDriveTimeInHours = round(sumDriveTime / 3600, 2)  # 保留两位数,小时为单位
    return labels  # 返回时长, 次数, 和标签列表


# 急转弯判断，返回布尔值列表，标记每行是否急转弯
def suddenTurn_label(df, weatherDict, angular_velocity_threshold=math.pi/6, speed_threshold_ratio=1): # 阈值可调
    labels = [False] * len(df)
    count=0 # 仍然统计急转弯次数，可以用于分析
    rows=df.shape[0]
    condition = getWeatherConditionByCoordinateAndDate(df, weatherDict)
    # print(condition)
    #确定静摩擦系数
    mju=0
    for weaTag in condition:
        if weaTag=='大暴雨' or weaTag=='暴雨' or weaTag=='大雨' or weaTag=="雨夹雪":
            mju=0.3
            break
        elif '雨' in weaTag or '雪' in weaTag:
            mju=0.7
            continue
        else:
            #没有雨雪的情况
            if mju==0:
                mju=1
    # print(mju)
    for i in range(1,rows):
        item = df.iloc[i]
        lastItem = df.iloc[i - 1]
        lastSpeed = lastItem['gps_speed']
        speed = item['gps_speed']

        if lastSpeed > 0 and speed > 0:
            # 只有两个车辆的速度都大于0时才进行急转弯判断
            lastTime = datetime.datetime.strptime(lastItem['location_time'], '%Y-%m-%d %H:%M:%S')
            currentTime = datetime.datetime.strptime(item['location_time'], '%Y-%m-%d %H:%M:%S')
            timeInterval = (currentTime - lastTime).total_seconds()
            if timeInterval == 0:
                continue

            turnAngle = abs(item['direction_angle'] - lastItem['direction_angle'])
            #转弯角度不超过180
            if turnAngle > 180:
                turnAngle = 360 - turnAngle
            avgSpeed = (lastSpeed + speed) / 7.2  # 取平均值并转换单位为米每秒
            angular_velocity = (turnAngle * math.pi / 180) / timeInterval  # 角速度
            # print(avgSpeed)
            # print(angular_velocity)
            # print("\n")
            if angular_velocity > 0:
                #转弯角度不为零才计算转弯半径
                radius = round((avgSpeed/angular_velocity), 2)
                # print(radius)
                # print("\n")
                #根据静摩擦力提供向心力计算速度阈值，大于此速度为可能打滑
                speedThreshold=math.sqrt(mju*9.8*radius) * speed_threshold_ratio # 可以调整速度阈值比例
                # print(speedThreshold)
                # print(avgSpeed)

                if avgSpeed > speedThreshold:
                    labels[i] = True # 标记急转弯
                    count+=1
                    continue
                else:
                    if angular_velocity > angular_velocity_threshold: # 角速度阈值可调
                        #转弯角速度过大
                        labels[i] = True # 标记急转弯
                        count+=1
    # print(count)
    return labels, count # 返回标签列表和急转弯次数 (次数可以用于统计)


# 怠速预热判断和超长怠速判断不再需要，因为不进行节能分析，可以删除
# idle_preheating_label, overlong_idle_label, idle_preheating, overlong_idle 函数可以删除


def upperBoundBySpeed(speed): # 这个辅助函数可以保留， suddenTurn_label 函数会用到
    # 由速度计算转弯角度的上限值，超过此角度为急转弯
    if 0 < speed <= 40:
        return (-speed + 90) / 4
    elif 40 < speed <= 80:
        return (-speed + 100) / 5
    else:
        return (-speed + 180) / 25