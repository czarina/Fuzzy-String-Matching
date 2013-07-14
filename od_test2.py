import csv 
import re
import itertools
import Levenshtein

# Retrieve raw data from CSV files, process to standardized formatting and prepare to match
def getData():

	# Open CSV files
	csv_file_object1 = csv.reader(open('name-match-question.csv', 'rU')) 
	csv_file_object2 = csv.reader(open('name-match-question-2.csv', 'rU')) 

	# Original names stored in orig1, orig2
	orig1 = []
	orig2 = []

	# Processed names stored in names1, names2
	names1 = []
	names2 = []

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

	print "Names to match: ", len(orig1)
	return names1, names2, orig1, orig2

# Match store names from different sources by checking if one name is a substring of another
def basicMatch(names1, names2, orig1, orig2):

	# Store matches
	matched = []

	# Check if each pair of names from two lists is a match
	for pair in itertools.product(names1, names2):
		
		# Store processed names for comparison
		x = pair[0][0]
		y = pair[1][0]

		nameThreshold = 6

		# Test for match if each processed name is significantly long
		if len(x)>nameThreshold and len(y)>nameThreshold:
			# Store original names to insert into Matched array if we find a match
			origName1 = orig1[pair[0][1]]
			origName2 = orig2[pair[1][1]]

			# Ratchet acceptable ratio of string lengths to constitute a match
			ratchet = 2.5

			# If either name is a subset of the other, declare a match
			if(x in y or y in x):

				floatX = float(len(x))
				floatY = float(len(y))

				if(max(floatX / floatY, floatY / floatX) < ratchet):
					
					# If neither of the names has previously been matched, declare a new match
					# and remove from list of available names
					matched, appendMatch = conflictedMatch(matched, origName1, origName2)

					if(appendMatch):
						matched.append([origName1, origName2])

	print "Basic matches: ", len(matched)

	return names1, names2, orig1, orig2, matched
	
# For names unmatched by basicMatch, fuzzyMatch declares a match if all characters of a string
# are found in order (possibly with other characters in between) in a second string
def fuzzyMatch(names1, names2, orig1, orig2, matched):

	longNames1, longNames2 = returnLongNames(names1, names2, orig1, orig2, matched)

	# Check if each pair of names is a "fuzzy" match
	for pair in itertools.product(longNames1, longNames2):

		str1 = pair[0][0]
		str2 = pair[1][0]

		# Set the shorter and longer name
		if len(str1)<len(str2):
			shorter = str1
			longer = str2
		else:
			shorter = str2
			longer = str1

		# Move pointers through the shorter and longer name
		point1 = 0
		point2 = 0

		# Iterate through characters of both names until a match is found or we hit a break condition
		while True:

			# If current pointers point to equal characters, advance both pointers.
			# Otherwise, advance pointer of longer name
			if(shorter[point1] == longer[point2]):
				point1 +=1
				point2 +=1
			else:
				point2 +=1

			# If not all characters in shorter name are found in order within longer name, no match
			if(point2 == len(longer) and point1 < len(shorter)):
				break

			# If all characters in shorter name are found in order within longer name, match found
			if(point1 == len(shorter)):
				
				matched, appendMatch = conflictedMatch(matched, orig1[pair[0][1]], orig2[pair[1][1]])
				
				if(appendMatch):
					matched.append([orig1[pair[0][1]], orig2[pair[1][1]]])
				break

	print "+ Fuzzy Matches: ", len(matched)
	return names1, names2, orig1, orig2, matched

# Check for typos using Levenshtein distances
def leven(names1, names2, orig1, orig2, matched):

	longNames1, longNames2 = returnLongNames(names1, names2, orig1, orig2, matched)

	# Number of acceptable typos
	typoThreshold = 1

	# Check if each pair of names is a match with a typo
	for pair in itertools.product(longNames1, longNames2):
			
		str1 = pair[0][0]
		str2 = pair[1][0]

		if Levenshtein.distance(str1, str2) <= typoThreshold:

			matched, appendMatch = conflictedMatch(matched, orig1[pair[0][1]], orig2[pair[1][1]])
					
			if(appendMatch):
				matched.append([orig1[pair[0][1]], orig2[pair[1][1]]])
	
	print "+ Levenshtein matches: ", len(matched)
	return orig1, orig2, matched

# Sort and output successful matches
def printResults(orig1, orig2, matched):
	
	# Sort matches alphabetically
	for i in range(len(matched)):
		matched[i][0] = str(matched[i][0])[2:len(matched[i][0])-2]
		matched[i][1] = str(matched[i][1])[2:len(matched[i][1])-2]

	matched.sort(key = lambda row: row[0])
	orig1.sort()
	orig2.sort()

	print "Final percent of names matched: ", float(len(matched))/float(len(orig1))

	matchedWriter = csv.writer(open("matched.csv", "wb"))

	for i in range(len(matched)):
		matchedWriter.writerow(matched[i])

	# For debugging purposes - print unmatched names 
	unmatchedWriter = csv.writer(open("unmatched.csv", "wb"))

	for y in orig1:
		if y not in [m[0] for m in matched] and y not in [m[1] for m in matched]:
			unmatchedWriter.writerow([y])

	for y in orig2:
		if y not in [m[1] for m in matched] and y not in [m[0] for m in matched]:
			unmatchedWriter.writerow([y])

# Clean and standardized formatting of raw names to prepare for matching
def cleanName(name, listNum):
	
	# Set all characters to lowercase
	name = name.lower()

	# Remove common stopwords
	stopwords = re.compile(r'\ban\b|\bthe\b|\band\b|\ba\b|\bat\b')
	name = stopwords.sub(' ', name)

	# Remove common general store-related words/abbreviations
	storewords = re.compile(r'\bctr\b|\bcenter\b|\bsvc\b|\bservice\b|\binc\b|\bcorp\b|\bstore\b|\bllc\b|\brestaurant\b|\bshop\b|\brepair\b|\brpr\b|\bstudio\b|\bcafe\b')
	name = storewords.sub(' ', name)

	# Remove common location words/abbreviations
	locwords = re.compile(r'\bst\b|\bstreet\b|\bave\b|\bavenue\b|\bblvd\b|\bboulevard\b')
	name = locwords.sub(' ', name)

	# Remove punctuation
	name = re.sub('[^A-Za-z0-9]+', '', name)

	return name

# Resolve conflicted matches - if a new match A is identified for a name B that has already been 
# matched to C, declares the longer of A and C the likelier match to B
def conflictedMatch(matched, str1, str2):

	leftMatches = [x[0] for x in matched]
	rightMatches = [x[1] for x in matched]

	if (str1 in leftMatches):
		conflict = matched[leftMatches.index(str1)][1]
		if(len(str2)>len(conflict)):
			matched.remove([str1, conflict])
			return matched, True
		else:
			return matched, False

	elif (str2 in rightMatches):
		conflict = matched[rightMatches.index(str2)][0]
		if(len(str1)>len(conflict)):
			matched.remove([conflict, str2])
			return matched, True
		else:
			return matched, False

	return matched, True

# Only perform matching on longer names yet to be matched; likelihood of false matches increases for shorter names 
# with "fuzzier" techniques
def returnLongNames(names1, names2, orig1, orig2, matched):

	lenCutoff = 10

	longNames1 = []
	longNames2 = []

	for x in names1:
		if len(x[0])>=lenCutoff and orig1[x[1]] not in [z[0] for z in matched]:
			longNames1.append(x)

	for y in names2:
		if len(y[0])>=lenCutoff and orig2[y[1]] not in [z[1] for z in matched]:
			longNames2.append(y)

	return longNames1, longNames2

def main():

	# Prepare data for matching
	names1, names2, orig1, orig2 = getData()

	# Perform basic matching
	names1, names2, orig1, orig2, matched = basicMatch(names1, names2, orig1, orig2)

	# Perform "fuzzy" matching
	names1, names2, orig1, orig2, matched = fuzzyMatch(names1, names2, orig1, orig2, matched)

	# Check Levenshtein distances
	orig1, orig2, matched = leven(names1, names2, orig1, orig2, matched)

	# Print results to file
	printResults(orig1, orig2, matched)

main()


