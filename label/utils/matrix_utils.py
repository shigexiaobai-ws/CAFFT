import numpy as np

# 原始判断矩阵加上bias:
def add_bias(mtx, bias_mtx):
    for i in range(mtx.shape[0]):
        for j in range(mtx.shape[0]):
            if i < j:  # 对于矩阵的右上三角
                v = mtx[i, j]
                B = bias_mtx[i, j]
                if v >= 1:
                    if v + B >= 1:
                        v2 = v + B
                    elif v + B < 1:
                        v2 = 1 / (2 - (v + B))
                elif v < 1:
                    if (1 / v) - B >= 1:
                        v2 = 1 / ((1 / v) - B)
                    elif (1 / v) - B < 1:
                        v2 = 2 + B - (1 / v)
                mtx[i, j] = v2
            elif i > j:  # 对于矩阵的左下三角
                mtx[i, j] = 1 / mtx[j, i]
    return mtx

# 一致性检验,输入判断矩阵，输出CR值：
def Consistency_test(mtx):
    n = mtx.shape[0]
    a, b = np.linalg.eig(mtx)
    max_chrct_value = max(a)  # 求判断矩阵的最大特征值
    max_chrct_value = max_chrct_value.real
    CI = (max_chrct_value - n) / (n - 1)
    RI = np.array([0, 0, 0, 0.52, 0.89, 1.12, 1.24, 1.36, 1.41, 1.46, 1.49, 1.52, 1.54, 1.56, 1.58])
    CR = CI / RI[n]
    return round(CR, 3)

# 列向量归一化：
def normalization(mtx):  # 比例归一化
    for i in range(mtx.shape[1]):  # 对矩阵的每一列进行循环
        sum_val = mtx[:, i].sum()  # 当前列的和
        for j in range(mtx.shape[0]):  # 对每一列的每个元素进行循环
            mtx[j, i] = mtx[j, i] / sum_val
    return mtx