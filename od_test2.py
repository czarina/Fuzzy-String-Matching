import csv 
import re
import itertools

# Retrieve raw data from CSV files, process to standardized formatting and prepare to match
def getData():

	# Open CSV files
	csv_file_object1 = csv.reader(open('name-match-question.csv', 'rU')) 
	csv_file_object2 = csv.reader(open('name-match-question-2.csv', 'rU')) 

	# Original names stored in orig1, orig2
	orig1 = []
	orig2 = []

	# Processed names and matched pairs
	names1 = []
	names2 = []
	matched = []

	count0 = 0
	count1 = 0

	# Retrieving raw data from CSV files
	for row in csv_file_object1:

		#Store original names
		orig1.append(str(row))

		# Standardize formatting of names
		name = cleanName(str(row), 1)
		names1.append([name, count0])
		
		count0 += 1

	for row in csv_file_object2:

		#Store original names
		orig2.append(str(row))

		# Standardize formatting of names
		name = cleanName(str(row), 2)
		names2.append([name, count1])

		count1 += 1

# Match store names from different sources by checking if one name is a substring of another
def basicMatch():

	# Check if each pair of names from two lists is a match
	for pair in itertools.product(names1, names2):
		
		# Store processed names for comparison
		x = pair[0][0]
		y = pair[1][0]

		# Store original names to insert into Matched array if we find a match
		origName1 = orig1[pair[0][1]]
		origName2 = orig2[pair[1][1]]

		# Ratchet acceptable ratio of string lengths to constitute a match
		ratchet = 2.0

		# If either name is a subset of the other, declare a match
		if(x in y or y in x):

			floatX = float(len(x))
			floatY = float(len(y))

			if(max(floatX / floatY, floatY / floatX) < ratchet):
				
				# If neither of the names has previously been matched, declare a new match
				# and remove from list of available names
				try:
					if(names1.index(pair[0])>=0 and names2.index(pair[1])>=0):
						names1.remove(pair[0])
						names2.remove(pair[1])
						matched.append([origName1, origName2])
				except ValueError:
					pass
	
# For names unmatched by basicMatch, fuzzyMatch declares a match if all characters of a string
# are found in order (possibly with other characters in between) in a second string, 
def fuzzyMatch():
	list1 = []
	list2 = []

	for x in names1:
		if len(x[0])>=10:
			list1.append(x)

	for y in names2:
		if len(y[0])>=10:
			list2.append(y)

	for pair in itertools.product(list1, list2):

		str1 = pair[0][0]
		str2 = pair[1][0]

		if len(str1)<len(str2):
			shorter = str1
			longer = str2
		else:
			shorter = str2
			longer = str1

		origName1 = orig1[pair[0][1]]
		origName2 = orig2[pair[1][1]]

		point1 = 0
		point2 = 0
		flag = True

		while flag:

			if(shorter[point1] == longer[point2]):
				point1 +=1
				point2 +=1
			else:
				point2 +=1

			if(point2 == len(longer) and point1 < len(shorter)):
				break

			if(point1 == len(shorter)):

				leftMatches = [x[0] for x in matched]
				rightMatches = [x[1] for x in matched]

				if (str1 in leftMatches):
					conflict = matched[leftMatches.index(str1)][1]
					if(len(str2)>len(conflict)):
						matched.remove([str1, conflict])
					else:
						break

				elif (str2 in rightMatches):
					conflict = matched[rightMatches.index(str2)][0]
					if(len(str1)>len(conflict)):
						matched.remove([conflict, str2])
					else:
						break

				matched.append([origName1, origName2])
				break

	
	matched.sort(key = lambda row: row[0])
	orig1.sort()
	orig2.sort()

	print len(matched)

	matchedWriter = csv.writer(open("matched.csv", "wb"))

	for i in range(len(matched)):
		matchedWriter.writerow(matched[i])

	unmatchedWriter = csv.writer(open("unmatched.csv", "wb"))

	for y in orig1:
		if y not in [m[0] for m in matched] and y not in [m[1] for m in matched]:
			unmatchedWriter.writerow([y])

	unmatchedWriter.writerow("NEW FILE")

	for y in orig2:
		if y not in [m[1] for m in matched] and y not in [m[0] for m in matched]:
			unmatchedWriter.writerow([y])


def cleanName(name, listNum):
	name = name.lower()

	#remove stopwords
	rx = re.compile(r'\ban\b|\bthe\b|\band\b|\ba\b|\binc\b|\bcorp\b|\bllc\b|\bat\b')
	name = rx.sub(' ', name)

	#replace abbreviations
	if(listNum==2):
		name = name.replace(" ctr", " center")
		name = name.replace(" svc", " service")
	name = name.replace(" ave ", " avenue ")
	name = name.replace(" st ", " street ")

	#remove punctuation
	name = re.sub('[^A-Za-z0-9]+', '', name)

	return name

def main():

	# Prepare data for matching
	getData()
	basicMatch()
	fuzzyMatch()



