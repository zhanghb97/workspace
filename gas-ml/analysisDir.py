'''
处理一个目录的所有文件
'''
import meter
import pandas as pd
import os

# 分析一个目录
def analysis(strDir):
	df = pd.DataFrame(columns = ["meterid", "category", "similary", "exceptionnum"])

	emptyGas = []

	for f in os.listdir(strDir):
		try:
			if f[-4:] == ".csv":
				idName = f[:-4]
				strPath = os.path.join(strDir, f)
				objMeter = meter.Meter(idName, strPath, '', '', True)
				objMeter.loadData()

				if objMeter.isEmptyGas():
					emptyGas.append(idName)

				# 计算相似性
				objMeter.computeSimilaryByDTW()

				# 计算可能的异常点个数
				objMeter.getExceptions()
				objMeter.getSmallFlowRatio()

				tmp = pd.DataFrame({"meterid": idName, "category": objMeter._category, "similary": objMeter._similar,
									"exceptionnum": objMeter._exceptionNum, "smallratio": objMeter._smallRatio},
								   index=["0"])
				df = df.append(tmp, ignore_index=True)
		except:
			print("error:"+f)
	return df, emptyGas

# 分析df
def sortBySimilar(df):
	ret = {}
	for name, group in df.groupby("category"):
		tmpDf = group.sort_values("similary", ascending = False)
		ret[name] = tmpDf

	return ret

# 写入未使用过的空表id
def writeEmpty(strPath, emptyGas):
	print("emptyGas: ", len(emptyGas))
	with open(strPath, 'w') as f:
		for meterId in emptyGas:
			f.write(meterId)
			f.write("\r\n")

# 将结果写入待定的目录
def writeResult(strDir, dicDfs):
	for (key, value) in dicDfs.items():
		fileName = str(key) + ".csv"
		strPath = os.path.join(strDir, fileName)
		value.to_csv(strPath)

# 低流量运行的表具
def computeSmallFlowMeter(df, strPath):
	result = {}
	for i in range(len(df)):
		if df.iloc[i]["smallratio"] > 0.1:
			tmpValue = (df.iloc[i]["similary"] + 1) * df.iloc[i]["smallratio"]
			result[df.iloc[i]["meterid"]] = tmpValue

	tmpCSV = pd.DataFrame(result.items(), columns = ["meterid", "smallflow"])
	tmpCSV = tmpCSV.sort_values("smallflow", ascending = False)

	tmpCSV.to_csv(strPath)

# 流量暴增的表具
def computeProblemMeter(df, strPath):
	result = {}
	for i in range(len(df)):
		if df.iloc[i]["exceptionnum"] != 0:
			tmpValue = (df.iloc[i]["similary"] + 1) * df.iloc[i]["exceptionnum"]
			result[df.iloc[i]["meterid"]] = tmpValue

	tmpCSV = pd.DataFrame(result.items(), columns = ["meterid", "probability"])
	tmpCSV = tmpCSV.sort_values("probability", ascending = False)

	tmpCSV.to_csv(strPath)

# 组合，供main调用
def combineCall(strDealDir, saveDir):
	# 处理目录
	df, empty = analysis(strDealDir)
	dfs = sortBySimilar(df)

	# 写入排序结果，similar越大，表示不符合程度越高
	writeResult(saveDir, dfs)
	# 未使用燃气的表具
	strTmpPath = os.path.join(saveDir, 'empty.txt')
	writeEmpty(strTmpPath, empty)

	strProblemPath = os.path.join(saveDir, "problem.csv")
	strSmallFlow = os.path.join(saveDir, "smallflow.csv")

	# 将极有可能存疑的表具写入文件
	computeProblemMeter(df, strProblemPath)
	computeSmallFlowMeter(df, strSmallFlow)

