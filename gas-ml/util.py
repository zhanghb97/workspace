import pandas as pd
import numpy as np

import datetime, math

'''
通用接口
'''

# 将数据分成连续的片，根据是否打开阀门（暂时自我判定）
def getDfs(df):
    dfs = []
    iStart = 0
    currentState = df.iloc[0]['isOpen']
    for j in range(1, len(df)):
        if df.iloc[j]['isOpen'] != currentState:
            tmpDf = df.iloc[iStart : j]
            dfs.append(tmpDf)
            
            currentState = df.iloc[j]['isOpen']
            iStart = j
            
    return dfs

# 判断每个df是否有可能存在异常
def analysisDfs(dfs):
    ret = []
    
    dfCounts = len(dfs)
    startCounts = 0
    
    for i in range(0, len(dfs)):
        ret.append(analysisUnit(startCounts, dfs[i]))
        startCounts = startCounts + len(dfs[i])
        
    return ret
    
# 分析一个具体的子片段
def analysisUnit(countsBefore, df):
    ret = []
    
    for i in range(1, len(df)):
        if df.iloc[i]['Pressure'] == 0 or df.iloc[i]['dif'] * 1.0 / df.iloc[i]['Pressure'] > 0.1:
            ret.append(countsBefore + i)
            
    return ret

# 将所有记录展开成一个list
def flatList(lst):
    ret = []
    for arr in lst:
        for elm in arr:
            ret.append(elm)
            
    return ret

# 寻找第一个星期一
def findFirstMonday(dIndex):
	for dt in dIndex:
		if dt.date().weekday() == 1:
			return dt.date()

# 寻找最后一个星期日
def findLastSunday(dIndex):
	j = len(dIndex) - 1
	while j >= 0:
		if dIndex[j].date().weekday() == 0:
			return dIndex[j].date()
		else:
			j = j - 1

# 计算总共有多少天
def getDayCounts(df):
	dIndex = df.index

	dayCount = (dIndex[-1] - dIndex[0]).days
	return dayCount

# 按天获取记录, 掐头去尾
def getRecordByDay(df):
	dicDay = {}
	dicWeek = {}

	dIndex = df.index

	start = findFirstMonday(dIndex)
	end = findLastSunday(dIndex)

	weekDay = start
	weekRecord = []
	i = 0

	currentDay = start
	nextDay = currentDay + datetime.timedelta(days = 1)

	while (end - currentDay).days >= 0:
		gas = 0

		if nextDay in df.index:
			tmpDf = df[currentDay : nextDay]

			if len(tmpDf) > 0:
				gas = tmpDf.iloc[-1]['Standard_Sum'] - tmpDf.iloc[0]['Standard_Sum']

			dicDay[currentDay] = gas
		else:
			dicDay[currentDay] = 0

		if i == 7:
			dicWeek[weekDay] = weekRecord
			weekRecord = []
			i = 0

			weekDay = currentDay

		weekRecord.append(gas)
		i = i + 1

		currentDay = nextDay
		nextDay = currentDay + datetime.timedelta(days = 1)

	return pd.DataFrame(dicDay.items(), columns=['Date', 'DateValue']), pd.DataFrame(dicWeek)

# 计算日使用率
def computeRatio(df):
	weekMatrix = df.copy().values
	weekMatrix[weekMatrix > 0] = 1

	numVec = weekMatrix == 0
	num = weekMatrix[numVec].size

	row, col = weekMatrix.shape
	return 1 - (num * 1.0) / (row * col)

# 计算平均每日用气量
def computeMean(df):
	weekMatrix = df.copy().values
	return weekMatrix.mean()

# 计算日标准差
def computeDayStandard(df):
	weekMatrix = df.copy().values
	return weekMatrix.std()

# 计算两个向量之间的相似度
def computeVectorSimilar(v1, v2):
	up = np.dot(v1, v2)

	down1 = np.dot(v1, v1)
	down2 = np.dot(v2, v2)

	# 若有一向量为0，则其对相似度计算无贡献，也无法观察规律，不妨将其设置为0
	if down1 == 0 or down2 == 0:
		return 0
	else:
		return up / math.sqrt(down1 * down2) 

# 计算相似度矩阵
def computeSimilar(df):
	dayMatrix = df.copy().values
	dayMatrix[dayMatrix > 0] = 1

	trans = dayMatrix.T

	units, unitNum = dayMatrix.shape

	# 初始化相似矩阵
	simMatrix = -np.ones((unitNum, unitNum))

	for i in range(unitNum):
		for j in range(unitNum):
			if i == j:
				simMatrix[i, j] = 1.0
			elif simMatrix[j, i] != -1.0:
				simMatrix[i, j] = simMatrix[j, i]
			else:
				simMatrix[i, j] = computeVectorSimilar(trans[i], trans[j])

	return simMatrix

# 计算最终的相似度
# 思想：如果某个向量与其它所有向量的相似度之和最大，则其平均相似度可以衡量用气习惯
# 返回相似度和对应的基准日，基准日可以用来做用气预测
def getSimilarIndex(simMatrix):
	tmp = simMatrix.copy()
	tmp = tmp.cumsum(0)

	row, col = tmp.shape

	# 获取最后一行的累加和
	lastRow = tmp[row - 1, :]

	similar = np.max(lastRow)
	baseIdx = np.argmax(lastRow)

	return similar / row, baseIdx

'''
# 计算周用气方差
def computeWeekSqr(df):
	weekMatrix = df.copy().values
	weekMatrix.cumsum(0)

	weekSum = weekMatrix[6, :]
	return weekSum.var()
'''

# 计算周均值
def computeWeekMean(df):
	weekMatrix = df.copy().values
	weekMatrix.cumsum(0)

	weekSum = weekMatrix[6, :]
	return weekSum.mean()

# 计算周标准差
def computeWeekStard(df):
	weekMatrix = df.copy().values
	weekMatrix = weekMatrix.cumsum(0)

	weekSum = weekMatrix[6, :]
	return weekSum.std()

# 获取各项指标
def computeStatistic(weekFrm):
	#weekFrm = pd.DataFrame(weekDf)

	# 日使用率
	ratio = computeRatio(weekFrm)
	# 日均值
	dayMean = computeMean(weekFrm)
	# 日标准差
	dayStd = computeDayStandard(weekFrm)

	# 周相似度
	weekSim = computeSimilar(weekFrm)
	weekSimValue, weekIdx = getSimilarIndex(weekSim)
	# 周方差
	#weekVar = computeWeekSqr(weekFrm)
	# 周标准差
	weekStd = computeWeekStard(weekFrm)
	# 周均值
	weekMean = computeWeekMean(weekFrm)

	return ratio, dayMean, dayStd, weekStd, weekMean, weekSimValue

# 用气量归一化，归一化并不改变形态
# 必须确保数据不小于0
def normalizeByZeroOne(listPar):
	ret = []

	up = max(listPar)
	down = min(listPar)
	if up == down:
		ret = [0 for i in range(len(listPar))]
	else:
		for v in listPar:
			ret.append((v - down) / (up -down))

	return ret

# 计算每周用气量均值，以7天为一个周期
def getWeekMeanValue(df):
	weekMatrix = df.copy().values
	weekMatrix.cumsum(0)

	weekSum = 1 / 7 * weekMatrix[6, :]
	return weekSum

# 获取id对应的文件名称
def getFileIdName(strFileName):
	return strFileName[:-4]


