import meter
import pandas as pd
import analysisDir

if __name__ == '__main__':
	# 第一个阐述为待处理的目录，第二个参数为结果保存的目录，在第二个目录中，有一个problem.csv文件，可能性越高，约有可能存在异常
	analysisDir.combineCall("D:/workspaces_goldcard/00_project/01_data_visual/ml/data/20190618_dealDataSorted/jk4.0/collection_record", './result/nyy_jk4.0')
	# 处理目录
	#df, empty = analysisDir.analysis("../data/tianxin_collection_record")
	#dfs = analysisDir.sortBySimilar(df)
	# 写入排序结果，similar越大，表示不符合程度越高
	#analysisDir.writeResult('./result', dfs)
	#analysisDir.writeEmpty('./result/empty.txt', empty)
	#objMeter = meter.Meter('meterId201901141728344420103096709946', './data/meterId201901141728344420103096709946.csv', '', '', True)
	#objMeter.loadData()

	#objMeter.computeSimilaryByDTW()
	#objMeter.printSimilar()

	# 计算相似度等指数
	#objMeter.computeStatisticalIndex()
	#objMeter.printIndex()


	# 计算可以点
	#objMeter.getSuspiciousRecord()
	#objMeter.printSuspiciousPoint()

	# 预测
	#objMeter.predictGas()
	#objMeter.printPredict()