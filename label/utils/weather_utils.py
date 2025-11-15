import numpy as np
import os
import json
import urllib.request
import sys
import pandas as pd
import datetime
from config import bias_light_rian, bias_moderate_rian, bias_heavy_rian, bias_rainstorm, bias_light_snow, \
    bias_sunny, bias_overcast, bias_clody, bias_shower, bias_thunder_shower, bias_fog, bias_sleet, \
    bias_floating_dust, bias_blowing_sand

# 根据天气情况确定bias矩阵，输入天气列表（包含1~3个str元素），返回bias和bias_EC矩阵：
def bias_determine(weather):
    bias1 = None
    bias2 = None
    bias3 = None

    if len(weather) >= 1:
        if weather[0] in ['小雨', '小到中雨']:
            bias1 = bias_light_rian
        elif weather[0] == '中雨':
            bias1 = bias_moderate_rian
        elif weather[0] == '大雨':
            bias1 = bias_heavy_rian
        elif weather[0] in ['暴雨', '大暴雨', '雷雨']:
            bias1 = bias_rainstorm
        elif weather[0] == '小雪':
            bias1 = bias_light_snow
        elif weather[0] in ['晴', '未知']:
            bias1 = bias_sunny
        elif weather[0] == '阴':
            bias1 = bias_overcast
        elif weather[0] == '多云':
            bias1 = bias_clody
        elif weather[0] == '阵雨':
            bias1 = bias_shower
        elif weather[0] in ['雷阵雨', '零散雷雨']:
            bias1 = bias_thunder_shower
        elif weather[0] == '雾':
            bias1 = bias_fog
        elif weather[0] == '雨夹雪':
            bias1 = bias_sleet
        elif weather[0] == '浮尘':
            bias1 = bias_floating_dust
        elif weather[0] == '扬沙':
            bias1 = bias_blowing_sand

        if len(weather) >= 2:
            if weather[1] in ['小雨', '小到中雨']:
                bias2 = bias_light_rian
            elif weather[1] == '中雨':
                bias2 = bias_moderate_rian
            elif weather[1] == '大雨':
                bias2 = bias_heavy_rian
            elif weather[1] in ['暴雨', '大暴雨', '雷雨']:
                bias2 = bias_rainstorm
            elif weather[1] == '小雪':
                bias2 = bias_light_snow
            elif weather[1] == '晴':
                bias2 = bias_sunny
            elif weather[1] == '阴':
                bias2 = bias_overcast
            elif weather[1] == '多云':
                bias2 = bias_clody
            elif weather[1] == '阵雨':
                bias2 = bias_shower
            elif weather[1] in ['雷阵雨', '零散雷雨']:
                bias2 = bias_thunder_shower
            elif weather[1] == '雾':
                bias2 = bias_fog
            elif weather[1] == '雨夹雪':
                bias2 = bias_sleet
            elif weather[1] == '浮尘':
                bias2 = bias_floating_dust
            elif weather[1] == '扬沙':
                bias2 = bias_blowing_sand

            if len(weather) == 3:
                if weather[2] in ['小雨', '小到中雨']:
                    bias3 = bias_light_rian
                elif weather[2] == '中雨':
                    bias3 = bias_moderate_rian
                elif weather[2] == '大雨':
                    bias3 = bias_heavy_rian
                elif weather[2] in ['暴雨', '大暴雨', '雷雨']:
                    bias3 = bias_rainstorm
                elif weather[2] == '小雪':
                    bias3 = bias_light_snow
                elif weather[2] == '晴':
                    bias3 = bias_sunny
                elif weather[2] == '阴':
                    bias3 = bias_overcast
                elif weather[2] == '多云':
                    bias3 = bias_clody
                elif weather[2] == '阵雨':
                    bias3 = bias_shower
                elif weather[2] in ['雷阵雨', '零散雷雨']:
                    bias3 = bias_thunder_shower
                elif weather[2] == '雾':
                    bias3 = bias_fog
                elif weather[2] == '雨夹雪':
                    bias3 = bias_sleet
                elif weather[2] == '浮尘':
                    bias3 = bias_floating_dust
                elif weather[2] == '扬沙':
                    bias3 = bias_blowing_sand

    if len(weather) == 1:
        bias = bias1
    elif len(weather) == 2:
        bias = (bias1 + bias2) / 2 if bias1 is not None and bias2 is not None else (bias1 if bias1 is not None else bias2)
        if bias is None: bias = np.zeros_like(bias_light_rian) # 默认bias
    elif len(weather) == 3:
        bias = (bias1 + bias2 + bias3) / 3 if all(b is not None for b in [bias1, bias2, bias3]) else (bias1 if bias1 is not None else (bias2 if bias2 is not None else bias3))
        if bias is None: bias = np.zeros_like(bias_light_rian) # 默认bias
    else:
        bias = np.zeros_like(bias_light_rian) # 默认bias

    return [bias]


# 将天气情况的描述拆分出来,返回一个集合
def splitWeatherTag(conditions):
    result = []
    if '转' in conditions:
        tmpTag = conditions.strip().split('转')
        for tag in tmpTag:
            if '-' in tag:
                result.extend(tag.strip().split('-'))
                continue
            result.append(tag)

    elif '-' in conditions:
        tmpTag = conditions.strip().split('-')
        for tag in tmpTag:
            if '转' in tag:
                result.extend(tag.strip().split('转'))
                continue
            result.append(tag)
    else:
        result.append(conditions)
    result = set(result)
    print(result)
    return result


# 根据气象数据返回字典，key为省市区，日期组成的列表，value为conditions属性
def genLocation_Date_Weather_Dict():
    weatherFile ="E:/teddy/test/Data/附件2-气象数据.csv"

    # 有中文的文件一定要设置编码
    df = pd.read_csv(weatherFile, encoding='gbk', low_memory=False)
    rows = df.shape[0]
    resultDict = {}
    for i in range(0, rows):
        item = df.iloc[i]
        tmpProvince = item['province']
        tmpCity = item['prefecture_city']
        tmpCounty = item['county']
        condition = item['conditions']
        tmpDate = datetime.datetime.strptime(item['record_date'], '%d/%m/%Y').date()
        resultKey = (tmpProvince, tmpCity, tmpCounty, tmpDate)
        resultDict[resultKey] = condition

    return resultDict


# 基于百度地图API下的经纬度信息来解析地理位置信息,并获取对应时间地点的天气情况
# curDate必须为%d/%m/%Y 形式
def getWeatherConditionByCoordinateAndDate(df, weatherDict):
    item = df.iloc[0]
    lng = item['lng']
    lat = item['lat']
    DateandTime = datetime.datetime.strptime(item['location_time'], '%Y-%m-%d %H:%M:%S')
    curDate = DateandTime.date()  # 提取日期

    # 转换坐标api,将WGS84坐标转换为BD09II
    transUrl = 'http://api.map.baidu.com/geoconv/v1/?coords=' + str(lng) + ',' + str(
        lat) + '&from=1&to=5&ak=omccBE0lR4imoVYekaRdNsSW9NiiMief'
    tranReq = urllib.request.urlopen(transUrl)
    tranResult = tranReq.read().decode('utf-8')
    # 返回的是str类型，使用json读取
    tranResult = json.loads(tranResult)
    tranStatus = tranResult.get('status')
    if tranStatus != 0:
        # 转换失败
        print("coodinate transform error!")
        sys.exit(1)
    coodinate = tranResult.get('result')[0]  # 返回的是列表，使用[0]提取，为字典类型
    lng = coodinate['x']
    lat = coodinate['y']
    print("经度",lng)
    print("纬度",lat)
    # 使用转换后的经纬度查询省市区
    url = 'http://api.map.baidu.com/geocoder/v2/?location=' + str(lat) + ',' + str(
        lng) + '&output=json&pois=1&ak=omccBE0lR4imoVYekaRdNsSW9NiiMief'
    req = urllib.request.urlopen(url)  # json格式的返回数据
    res = req.read().decode("utf-8")  # 将其他编码的字符串解码成unicode
    resultJson = json.loads(res).get('result')
    address = resultJson.get('addressComponent')
    # 获取坐标对应的省市区

    province = address.get('province').strip('省')
    city = address.get('city').strip('市')
    district = address.get('district')[:-1]
    print(province)
    print(city)
    print(district)

    tmpKey = (province, city, district, curDate)
    if tmpKey in weatherDict:
        return splitWeatherTag(weatherDict[tmpKey])
    # 找不到对应地点的天气情况，返回字符串集合'未知'
    print("未知")
    return ['未知']