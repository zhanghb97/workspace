import pandas as pd
import numpy as np
import os, math
import util
from dtaidistance import dtw
import features

'''
表具单元
'''
class Meter(object):
	"""_id: 标识表具的唯一标识
	   _csvPath: 当前暂时用csv文件表述，后续根据需要修改
	   _industry: 标识属于哪一个行业
	   _address: 标识地址，用于区域分化（最好用经纬度标志，暂时忽略）
	   _hasPressureTemperature: 是否有温度和压力记录（暂时由使用者根据表具类型标识）
	   _df: 加载的pandas dataframe
	   _suspiciousPoints: 对于有温度和压力的记录，记录其可疑点
	   _statisticalIndex: 对于没有温度和压力的记录，通过长时间的数据积累，获取其相似性等指标，并打分
	   _dayDf: 
	   _weekDf:
	   _predictPeriods: 预测周期
	   _exceptionNum: 超出正常点的个数
	"""
	def __init__(self, id, csvPath, industry, address, hasPressureTemperature):
		super(Meter, self).__init__()
		self._id = id
		self._path = csvPath
		self._industry = industry
		self._address = address
		self._hasPressureTemperature = hasPressureTemperature
		self._df = None
		self._suspiciousPoints = []
		self._statisticIndex = {}
		self._dayDf = None
		self._weekDf = None
		self._predictPeriods = 7

		self._category = -1
		self._similar = float("inf")
		self._exceptionNum = 0
		self._smallRatio = 0

	# 加载数据
	def loadData(self):
		self._df = pd.read_csv(self._path)
		self._df['Data_Date'] = pd.to_datetime(self._df['Data_Date'], format="%Y-%m-%d %H:%M:%S")
		self._df = self._df.set_index('Data_Date')

	# 根据DTW计算相似度
	def computeSimilaryByDTW(self):
		if util.getDayCounts(self._df) < 49:
			print("days: ", util.getDayCounts(self._df))
			print("The duration is too short!!!")
			return

		self._dayDf, self._weekDf = util.getRecordByDay(self._df)

		if self.isEmptyGas():
			return

		#print(self_dayDf)

		weekMean = util.getWeekMeanValue(self._weekDf)
		weekMean = util.normalizeByZeroOne(weekMean)

		dis = [dtw.distance(weekMean, features.Stable_Feature), dtw.distance(weekMean, features.Concave_Feature), dtw.distance(weekMean, features.Convexity_Feature), dtw.distance(weekMean, features.Slop_Feature), dtw.distance(weekMean, features.Slop_Reverse_Feature), dtw.distance(weekMean, features.V_Feature)]

		for i in range(len(dis)):
			if dis[i] < self._similar:
				self._similar = dis[i]
				self._category = i


	# 检查是否存在一个表具记录是否带两块表的情况
	def hasTwoMeters(self):
		startRecord = self._df.iloc[0]['Standard_Sum']
		for i in range(1, len(self._df)):
			if self._df.iloc[i]['Standard_Sum'] < startRecord:
				return True
			else:
				startRecord = self._df.iloc[i]['Standard_Sum']

		return False

	# 增加两个标记
	def _dealMeterRecord(self):
		df = self._df
		dIndex = df.index

	    # 阀门是否打开标识
		lstOpen = []
	    # 差值标识
		lstDif = [0]

		if df.iloc[0]['Working_Flow'] == 0:
			lstOpen.append(0)
		else:
			lstOpen.append(1)

		for i in range(1, len(dIndex)):
			if df.iloc[i]['Working_Flow'] == 0:
				lstOpen.append(0)
			else:
				lstOpen.append(1)

			lstDif.append(abs(df.iloc[i]['Pressure'] - df.iloc[i - 1]['Pressure']))

		df['isOpen'] = lstOpen
		df['dif'] = lstDif   
	    
		self._df = df

	# 对于有温度压力数据的记录，获取可能有问题的时刻
	def getSuspiciousRecord(self):
		self._dealMeterRecord()
		dfs = util.getDfs(self._df)
		records = util.flatList(util.analysisDfs(dfs))

		index = self._df.index
		for i in records:
			self._suspiciousPoints.append(index[i])

	# 如果有足够多的数据，可以直接用用气数据进行判断
	def computeStatisticalIndex(self):
		if util.getDayCounts(self._df) < 49:
			print("days: ", util.getDayCounts(self._df))
			print("The duration is too short!!!")
			return
		self._dayDf, self._weekDf = util.getRecordByDay(self._df)
		#print(self._weekDf)
		print(self._dayDf)

		ratio, dayMean, dayStd, weekStd, weekMean, weekSimValue = util.computeStatistic(self._weekDf)
		self._statisticIndex['ratio'] = ratio
		self._statisticIndex['dayMean'] = dayMean
		self._statisticIndex['dayStd'] = dayStd
		self._statisticIndex['weekStd'] = weekStd
		self._statisticIndex['weekMean'] = weekMean
		self._statisticIndex['weekSimValue'] = weekSimValue

	# 大部分情况下，直接按照前几天的周期预测后期的用气情况
	def predictGas(self):
		lstUp = []
		lstDown = []

		for i in range(self._predictPeriods):
			lstUp.append(self._dayDf.iloc[i]['DateValue'])
			lstDown.append(self._dayDf.iloc[i]['DateValue'])

		for i in range(self._predictPeriods, len(self._dayDf)):
			arr = self._dayDf.iloc[i - self._predictPeriods : i]['DateValue']
			mean = np.mean(arr)
			std = np.std(arr)

			lstUp.append(mean + std * 2)
			if mean - 2 * std > 0:
				lstDown.append(mean - 2 * std)
			else:
				lstDown.append(0)

		self._dayDf['PredictLow'] = lstDown
		self._dayDf['PredictHigh'] = lstUp

	# 判断是否用气为0
	def isEmptyGas(self):
		if self._weekDf is not None:
			weekMatrix = self._weekDf.copy().values
			weekMatrix.cumsum(0)

			weekSum = weekMatrix[6, :]

			weekSum[weekSum > 0] = 1

			if np.sum(weekSum) == 0:
				return True

		return False

	# 微小流量数据问题
	def getSmallFlowRatio(self):
		if self.isEmptyGas() == False:
			if self._dayDf is not None:
				npDateValue = self._dayDf['DateValue'].copy().values
				npDateValue[npDateValue >= 1] = 0
				npDateValue[npDateValue == 0] = 0
				npDateValue[npDateValue > 0 ] = 1

				self._smallRatio = np.sum(npDateValue) / len(npDateValue)

	# 判断是否有可能存在用气异常情况
	# 通常情况下，用气超过4个标准差的极有可能存在问题
	def getExceptions(self):
		if self.isEmptyGas() == False:
			if self._dayDf is not None:
				dayMean = self._dayDf['DateValue'].mean()
				dayStd = self._dayDf['DateValue'].std() 

				# 边界线
				upBorder = dayMean + 4 * dayStd
				downBorder = dayMean - 4 * dayStd
				if downBorder <= 0:
					downBorder = 0

				tmpNp1 = self._dayDf['DateValue'].copy().values
				tmpNp2 = self._dayDf['DateValue'].copy().values

				tmpNp1[tmpNp1 <= upBorder] = 0
				tmpNp1[tmpNp1 > upBorder] = 1

				allBorderIdx = np.where(tmpNp1 > 0)

				# 最开始的用气量暴增可能是聚合问题
				startException = False

				if len(allBorderIdx[0]) > 0:
					if allBorderIdx[0][0] > 0:
						tmp = self._dayDf['DateValue'].copy().values[:allBorderIdx[0][0] - 1]
						#tmp[tmp == 0] = 0
						tmpZero = np.where(tmp == 0)
						if len(tmpZero[0]) > 0 and len(tmpZero[0]) / len(tmp) > 0.8:
							startException = True

				self._exceptionNum = np.sum(tmpNp1)

				if startException == True:
					if np.sum(tmpNp1) >= 1:
						self._exceptionNum = self._exceptionNum - 1

				if downBorder > 0:
					tmpNp2[tmpNp2 <= downBorder] = 0
					tmpNp2[tmpNp2 > downBorder] = 1

					self._exceptionNum = self._exceptionNum + (len(tmpNp2) - np.sum(tmpNp2))

	def printSimilar(self):
		print(self._category)
		print(self._similar)

	def printIndex(self):
		print(self._statisticIndex)

	def printPredict(self):
		print(self._dayDf)

	def printSuspiciousPoint(self):
		for i in self._suspiciousPoints:
			print(i)