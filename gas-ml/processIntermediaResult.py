'''
打分基本思路：分数越高，表具异常可能性越高
打分策略：根据周用气相似度、周用气均值以及周用气标准差判断
经验依据：一个正常的用户通常是具有一定规律的，大部分情况下每周用气量应该不会相差特别大

打分结果：打分应该分成两类，一类是无压力、温度的仪表；一类是有压力、温度的仪表
对于前者，只能通过长时间的用气行为进行判断；而对于后者，则打分结果应该分为两种情况，如果打分低且压力、温度存在异常，则表具异常的可能性较高，应优先排查这类表具。

注意：用气记录至少要超过半年，最好有2～3年的用气记录，太短的记录统计指标存在偏差

？？？？？？？？？到底是没有温度气压记录？还是记录为0，这个一定要阐述清楚？？？？？？？？？
'''

import pandas as pd
import numpy as np
import os

# 对统计指标打分，并返回低使用率的表具
def computeScore(strPath):
	df = pd.read_csv(strPath, header = None)

	lowUsage = []
	markIndex = {}

	for i in range(len(df)):
		if df.iloc[i][1] < 0.01 or df.iloc[i][5] <= 0:
			lowUsage.append(df.iloc[i][0])
		else:
			markIdx = df.iloc[i][6] * df.iloc[i][4] / df.iloc[i][5]
			markIndex[df.iloc[i][0]] = markIdx
			
	#result = pd.DataFrame(markIndex.items(), columns = ['id', 'score'])
	return lowUsage, markIndex

# 获取存在温度、压力异常的数据
def getTemperaturePressureException(strDir):
	ret = []

	for f in os.listdir(strDir):
		fileName = f
		f = os.path.join(strDir, f)
		if os.stat(f).st_size != 0:
			ret.append(fileName)

	return ret

# 将结果分类
def classifyResult(lowUsage, scoreIndex, exceptions):
	# 低使用率，且有异常的表具
	lowExceptions = []
	# 有温度压力记录，且存在异常的打分记录
	exceptionScore = {}
	# 无温度压力记录，且无异常的打分记录
	noExceptionScore = {}

	for meter in lowUsage:
		if hasException(meter, exceptions):
			lowExceptions.append(meter)

	for key, value in scoreIndex.items():
		if hasException(key, exceptions):
			exceptionScore[key] = value
		else:
			noExceptionScore[key] = value

	dfException = pd.DataFrame(exceptionScore.items(), columns=['id', 'score'])
	dfException = dfException.sort_values(by = 'score', ascending = False)

	dfNoException = pd.DataFrame(noExceptionScore.items(), columns=['id', 'score'])
	dfNoException = dfNoException.sort_values(by = 'score', ascending = False)

	return lowExceptions, dfException, dfNoException

# 判断一个id是否存在异常点，完全是由于命名不规范造成的这一步，本可省略
def hasException(strId, exceptions):
	lst = strId.split('.')
	strTmp = lst[0] + '_suspicious.' + lst[1]

	for strMeter in exceptions:
		if strTmp == strMeter:
			return True

	return False

# 处理数据
def dealScoreData(strDir):
	# 获取打分和低使用率表具
	scorePath = os.path.join(strDir, 'computeStatisticalIndex/all_computeStatisticalIndex.csv')
	lowUsage, markIndex = computeScore(scorePath)

	# 获取存在温度、压力异常的数据
	tpPath = os.path.join(strDir, 'suspicious')
	tpRecords = getTemperaturePressureException(tpPath)

	lowExceptions, dfException, dfNoException = classifyResult(lowUsage, markIndex, tpRecords)

	return lowExceptions, dfException, dfNoException

if __name__ == '__main__':
	lowExceptions, dfException, dfNoException = dealScoreData('./data/jk')
	print(lowExceptions)
	print(dfException)
	print(dfNoException)

