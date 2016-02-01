import os
import csv
import time
import json
import datetime
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction import DictVectorizer
from sklearn import tree

'''
# For weka
def GenerateTestDataArff():
	with open('TestData.arff', 'w') as fp:
		ft = open('raw.arff', 'r')
		line = ft.readlines()
		start = 0

		for i in range(0, len(line)):
			if line[i].rstrip('\n') == "@data":
				start = i
				continue

		for i in range(0, len(line)):
			if i < start:
				fp.write(line[i])
			elif i == start:
				fp.write("@attribute Playing {0,1}\n")
				fp.write(line[i])
			else:
				fp.write(line[i].rstrip('\n') + ',?\n')

	print("Done!")

def writeHeader(file):
	file.write("@relation 'session'\n")
	file.write("\n")
	file.write("@attribute TUTORIAL MOODE numeric\n")
	file.write("@attribute SST numeric\n")

def GenerateArff():
	with open('Session.arff', 'w') as fp:
		writeHeader(fp)
		ft = open('Session.csv', 'r')
		line = ft.readlines()

		for i in range(1, len(line)):
			fp.write(line[i].rstrip('\n') + ',?\n')

	print('Done!')
'''

# Extract features from each log file in a dictionary
def ExtractFeatures(address):
	# print(address)
	duration = -1
	left = 0
	right = 0
	up = 0
	down = 0

	# The status of each user id
	# 0 means not registered, 1 means registered 
	id_status = [0]*6
	# The queue of calculation
	users = [0]
	# Features the gestures stream
	gestures = []
	# Features total gestures
	gesturesNum = 0

	with open(address) as flog:
		reader = csv.reader(flog, dialect='excel')
		# lastRow = reader.next()
		
		for row in reader:
			lastRow = row
			# print(row)

			# Skip the first two lines
			if row == []:
				continue

			if row[0] == 'Time':
				continue

			# duration as a flag
			if duration == -1:
				startRow = row
				duration = 0

			# add the ids to users
			if row[2] == ' RSARR':
				# The id is from 1 while the id_status is from 0
				# so -1 is needed to access the id_status
				current_id = int(row[1]) - 1 
				
				# If current_id has not been registered
				if id_status[current_id] == 0:
					id_status[current_id] = 1
					current_num = users[-1] + 1
					users.append(current_num)

			if row[2] == ' RSGON':
				current_id = int(row[1]) - 1

				# If current_id has been registered
				if id_status[current_id] == 1:
					id_status[current_id] = 0
					current_num = users[-1] - 1
					users.append(current_num)
			

			# count the number of gestures
			if row[2] == ' RMRIG':
				gesturesNum += 1
				right += 1
				gestures.append('R')
			elif row[2] == ' RMLEF':
				gesturesNum += 1
				left += 1
				gestures.append('L')
			elif row[2] == ' RMORE':
				gesturesNum += 1
				up += 1
				gestures.append('U')
			elif row[2] == ' RDONE':
				gesturesNum += 1
				down += 1
				gestures.append('D')
		
		# Feature total unique gestures
		gesturesUnique = len(set(gestures))

		# About time
		startTime = time.strptime(startRow[0].split('.')[0], '%H:%M:%S')
		endTime = time.strptime(lastRow[0].split('.')[0], '%H:%M:%S')
		stime = datetime.timedelta(hours=startTime.tm_hour, minutes=startTime.tm_min, seconds=startTime.tm_sec).total_seconds()
		etime = datetime.timedelta(hours=endTime.tm_hour, minutes=endTime.tm_min, seconds=endTime.tm_sec).total_seconds()
		
		# Feature session start time in string
		ssTime = startRow[0]
		# Feature duration in number of second
		duration = etime - stime
		# Features total users
		usersNum = max(users)

		res = {"Duration": duration, "TotalUsers": usersNum,
		"TotalUniqueGestures": gesturesUnique, "Left": left, "Right": right,
		"Up": up, "Down": down}
		return res


# Generate test data in json format
def GenerateTestData():
	dataPath = 'sessions'
	testData = []

	# Scan every log file in the folder
	for filename1 in os.listdir(dataPath):
		address1 = dataPath+'/'+filename1
		for filename2 in os.listdir(address1):
			address2 = address1+'/'+filename2
			res = ExtractFeatures(address2)
			testData.append(res)

	print('The size of test:\n', len(testData))

	# Output the test data in json format
	with open('TestData.json', 'w') as fout:
		fout.write(json.dumps(testData))

	print('Test Data Done!')
	return testData


# Generate training data
def GenerateTrainingData():
	address = 'Video Observations.csv'
	dataPath = 'sessions'
	trainData = []
	target = []
	count = 0

	with open(address) as fin:
		reader = csv.reader(fin, dialect='excel')

		# Find the training data file name 
		# according to video observation file
		for row in reader:
			fileName = row[0]
			if fileName == 'Video File' or fileName == '':
				continue

			# Collect the target class, the colum O in Video Observation
			target.append(row[13])
			# count += 1
			# print(count)

			# Find the exact log file according to the name
			folderName = ''.join(fileName[10:20])
			address2 = dataPath + '/'+folderName

			# Extract features for training data file
			for fileName2 in os.listdir(address2):
				time1 = ''.join(fileName[-12:-4])
				time2 = ''.join(fileName2[-12:-4])
				if time1 == time2:
					filePath = address2 + '/' + fileName2
					# count += 1
					# print(count, filePath)
					res = ExtractFeatures(filePath)
					trainData.append(res)
					break

	print('The size of train:\n', len(trainData))

	# Output the training data in json format
	with open('TrainingData.json','w') as fout:
		fout.write(json.dumps(trainData))
	print('Training Data Done!')
	
	# Output the target class in json format
	with open('TargetClass.json','w') as tout:
		tout.write(json.dumps(target))
	print('Target Class Done!')
	# print(target)	

	return trainData, target


# Build decision tree for the real use 
def DecisonTreeBuilder(TrainData, Target, TestData):
	vec = DictVectorizer()
	TrainDataArray = vec.fit_transform(TrainData).toarray()
	TestDataArray = vec.fit_transform(TestData).toarray()
	
	print('Training length:', len(TrainDataArray))
	print('Training width:', len(TrainDataArray[1]))
	
	print('Test length:', len(TestDataArray))
	print('Test width:', len(TestDataArray[1]))

	classifier = tree.DecisionTreeClassifier()
	classifier = classifier.fit(TrainDataArray, Target)
	PredictionRes = classifier.predict(TestDataArray)
	print('The prediction result is:\n')
	print(PredictionRes)

# For performance test
def DTforTest(train, target, test, target_test):
	classifier = tree.DecisionTreeClassifier()
	classifier = classifier.fit(train, target)
	PredictionRes = classifier.predict(test)
	print('The prediction result is:\n', PredictionRes)
	print('The real result is:\n', target_test)

	count = 0
	# Measures
	for index in range(len(PredictionRes)):
		if PredictionRes[index] == target[index]:
			count += 1
	print("The accuracy is:", count/len(PredictionRes))


if __name__ == "__main__":
	# testData = GenerateTestData()
	train, target = GenerateTrainingData()
	vec = DictVectorizer()
	trainData = vec.fit_transform(train).toarray()
	Data_train, Data_test, target_train, target_test = train_test_split(trainData, target, test_size=0.33, random_state=42)
	DTforTest(Data_train, target_train, Data_test, target_test)

	# print('Data_train is:\n', len(target_train))
	# print('Data_test is:\n', len(target_test))
	# DecisonTreeBuilder(Data_train, target_train, Data_test)
	print('Done!')
