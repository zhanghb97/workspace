'''
定义各种特征，暂时根据业胜和个人的理解构造
一年365天
'''
import numpy as np

# 类别为0
# 一年用气都比较平稳的特征
Stable_Feature = np.zeros(52)

# 类别为1
# 凹形特征
Concave_Feature = np.ones(52)
Concave_Feature[21:29] = 0

# 类别为2
# 凸形特征
Convexity_Feature = np.zeros(52)
Convexity_Feature[21:29] = 1

# 类别为3
# 坡形特征
Slop_Feature = np.zeros(52)
for i in range(26):
	Slop_Feature[i + 26] = 1 / 26 * (i + 1)

# 类别为4
# 反坡形特征
Slop_Reverse_Feature = np.zeros(52)
for i in range(26):
	Slop_Reverse_Feature[i] = 1 - 1 / 26 * i

# 类别为5
# V型特征
V_Feature = np.zeros(52)
for i in range(26):
	V_Feature[i] = 1 - 1 / 26 * i
for i in range(26):
	V_Feature[i + 26] = 1 / 26 * (i + 1)