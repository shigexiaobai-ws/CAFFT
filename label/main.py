# main.py
import pandas as pd
import numpy as np
import os
import copy
from config import data_route, mtx, mtx_backup # 仍然保留 mtx 和 bias 相关导入，如果天气 bias 也不需要，可以进一步删除
from utils.matrix_utils import add_bias, Consistency_test, normalization # 这些矩阵工具函数可能不再需要，如果确定不用可以删除导入
from utils.weather_utils import bias_determine, genLocation_Date_Weather_Dict, getWeatherConditionByCoordinateAndDate # weather_utils 保留，suddenTurn_label 还需要天气信息
from behavior_analysis.driving_behavior import  acce_decelerate_label, SlideOnFrameOut_label, overspeed_label, \
    fatigueDriving_label, suddenTurn_label # 导入所有标签生成函数

np.seterr(divide='ignore', invalid='ignore')

carID_list = [name for name in os.listdir(data_route) if name.__len__() == 7]
for k in range(len(carID_list)):
    carID = carID_list[k]
    DIR = data_route + '/' + carID
    roadNum = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name)) and os.path.splitext(name)[1] == '.csv'])  # 该车辆的路段数
    # roadNum=int(roadNum/2)
    print("当前carID：", carID)
    print("路段数：", roadNum)

    for i in range(1, roadNum + 1):
        input_file = data_route + "/" + carID + "/Road" + str(i) + ".csv" # 输入文件名
        output_file = data_route + "/" + carID + "/Road" + str(i) + "_labeled.csv" # 输出文件名 (添加 "_labeled" 后缀)
        f = open(input_file)
        df = pd.read_csv(f)
        print("\n*******正在处理" + carID + " Road" + str(i) + "*******")

        # 获取天气信息 (如果不需要天气 bias 和 suddenTurn_label，可以删除)
        weather_dict = genLocation_Date_Weather_Dict()
        # weather = list(getWeatherConditionByCoordinateAndDate(df, weather_dict))  # Weather function is time consuming, comment out if not needed
        # print("当前路段天气：", weather)
        # bias = bias_determine(weather) # bias_determine 现在只返回安全 bias
        # mtx_adjust = add_bias(mtx, bias[0]) # Bias function is not used for default matrix.
        mtx_adjust = mtx #  mtx_adjust 矩阵可能不再需要，如果一致性检验和权重计算也删除，这个也可以删除

        # 一致性检验和权重计算可以删除，因为不再需要评分

        # 生成危险驾驶行为标签
        print("  正在生成急加速/急减速标签...")
        acc_decelerate_labels = acce_decelerate_label(df)
        print("  正在生成熄火滑行标签...")
        slide_frameOut_labels = SlideOnFrameOut_label(df)
        print("  正在生成超速标签...")
        overspeed_labels = overspeed_label(df)
        print("  正在生成疲劳驾驶标签...")
        fatigueDriving_labels = fatigueDriving_label(df)
        print("  正在生成急转弯标签...")
        suddenTurn_labels, suddenTurn_count = suddenTurn_label(df, weather_dict) # suddenTurn_label 返回标签和次数

        # 将标签添加到 DataFrame
        df['is_rapid_acc_decel'] = acc_decelerate_labels
        df['is_slide_frame_out'] = slide_frameOut_labels
        df['is_overspeed'] = overspeed_labels
        df['is_fatigue_driving'] = fatigueDriving_labels
        df['is_sudden_turn'] = suddenTurn_labels

        # 打印急转弯次数 (或其他需要统计的次数)
        print("  急转弯次数:", suddenTurn_count)

        # 删除评分计算和输出部分

        # 输出到新的 CSV 文件 (labeled 文件)
        df.to_csv(output_file, encoding='gbk', index=False)
        print(f"  已保存 labeled 数据到: {output_file}")

        mtx = copy.deepcopy(mtx_backup)  # 恢复初始判断矩阵,  mtx 矩阵可能不再需要恢复，如果矩阵相关代码都删除，这个也可以删除

    print("所有车辆的 labeled 数据处理完成！")