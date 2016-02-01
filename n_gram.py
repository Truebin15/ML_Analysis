import csv


def Ngram(seq, nsize):
	res = []
	length = len(seq) - nsize + 1

	for i in range(length):
		res.append(seq[i:i+nsize])

	return res


def NgramExtract(nsize):
	address = 'Video Observations.csv'
	entry = str(nsize) + '_grams'
	target_file = 'ngram_' + str(nsize) + '_play.csv'
	# target_file = 'ngram_' + str(nsize) + '_interact.csv'

	with open(target_file, 'w', newline='') as out:
		writer = csv.writer(out, delimiter=',')
		writer.writerow(['filename', entry])
		
		with open(address) as fin:
			reader = csv.reader(fin, dialect='excel')
			counter = 0

			for row in reader:
				fileName = row[0]
				if fileName == 'Video File' or fileName == '':
					continue

				# For play
				if row[13] == '0':
					continue

				# For interact
				# if row[13] == '1':
				# 	continue

				counter += 1
				gestures = row[8]
				grams = Ngram(gestures, nsize)

				for ele in grams:
					writer.writerow([fileName, ele])

			print('The number videos: ', counter)


if __name__ == '__main__':
	start = 1
	end = 2

	for i in range(start, end):
		NgramExtract(i)
	print('Done!')
