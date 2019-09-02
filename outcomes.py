import collections
import numpy


# with open("outcomes.csv", "w") as outfile:

# 	# C H A E C H E

# 	matches = []
# 	for c1 in [1, -1]:
# 		for h1 in [1, -1, 0]:
# 			for a1 in [1, -1, 0]:
# 				for e1 in [1, -1]:
# 					for c2 in [1, -1]:
# 						for h2 in [1, -1, 0]:
# 							for e2 in [1, -1]:
# 								for c3 in [1, -1]:
# 									for a2 in [1, -1, 0]:
# 										for h3 in [1, -1, 0]:
# 											for e3 in [1, -1]:
# 												for a3 in [1, -1, 0]:
# 													match = [c1, h1, a1, e1, c2, h2, e2, c3, h3, a2, e3, a3]
# 													for i in range(4, 13):
# 														if i == 13:
# 															print(i)
# 														counter = collections.Counter(match[0:i])

# 														if counter[1] == 4:
# 															if counter[-1] < 4:
# 																if not(match[0:i] in matches):
# 																	matches.append(match[0:i])
# 																break
																

# 	for m in matches:
# 		csvstring = ""
# 		for i in m:
# 			csvstring += str(i) + ","
# 		outfile.write(csvstring + "\n")



matches = []
def match_won(match):
	counter = collections.Counter(match)
	if counter[1] == 4:
		if counter[-1] < 4:
			return True
	else:
		return False

def match_valid(m):
	nodraws = [0,3,4,6,7,10]
	for i in nodraws:
		if len(m) > i:
			if m[i] == 0:
				return False
	return True

def convert_matches_ft4(matches, probs):
	result = []
	for m in matches:
		m1 = []
		order = [
			"control",
			"hybrid",
			"assault",
			"escort",
			"control",
			"hybrid",
			"escort",
			"control",
			"hybrid",
			"assault",
			"escort",
			"assault"
		]
		for i in range(len(m)):
			m1.append(probs[order[i]][m[i]])
		result.append(m1)
	return result

def convert_matches_rs(matches, probs):
	result = []
	for m in matches:
		m1 = []
		order = [
			"control",
			"assault",
			"hybrid",
			"escort",
			"control"
		]
		for i in range(len(m)):
			m1.append(probs[order[i]][m[i]])
		result.append(m1)
	return result

def get_wins_ft4(match = []):
	q = []
	w = []
	q.append(match)
	while len(q) > 0:
		m = q.pop(0)
		if match_valid(m):
			if match_won(m):
				w.append(m)
			elif len(m) == 12:
				continue
			else:
				for i in [1, 0, -1]:
					m1 = m.copy()
					m1.append(i)
					q.append(m1)
	return w

def calc_prob_win_ft4(probs, matches):
	mymatches = convert_matches_ft4(matches, probs)

	s = 0
	products = []
	for m in mymatches:
		products.append(numpy.prod(m))
	products.sort()
	for p in products:
		s += p
	return s

def get_wins_rs(match = []):
	w = []
	for c in [1,-1]:
		for a in [1,-1, 0]:
			for h in [1,-1, 0]:
				for e in [1,-1]:
					match = [c,a,h,e]
					if sum(match) == 0:
						match.append(1)
					if sum(match) > 0:
						w.append(match)
	return w

def calc_prob_win_rs(probs, matches):
	mymatches = convert_matches_rs(matches, probs)
	s = 0
	products = []
	for m in mymatches:
		products.append(numpy.prod(m))
	products.sort()
	for p in products:
		s += p
	return s

# def build_tree(n = {"length":1, "match":[]}):
# 	order = [
# 		"control",
# 		"hybrid",
# 		"assault",
# 		"escort",
# 		"control",
# 		"hybrid",
# 		"escort",
# 		"control",
# 		"hybrid",
# 		"assault",
# 		"escort",
# 		"assault"
# 	]
# 	if n["length"] < 12:
# 		for i in [1, 0, -1]:
# 			m = n["match"].copy()
# 			m.append(i)
# 			if match_valid(m):
# 				l = n["length"] + 1
# 				n[i] = {"length":l, "match":m}
# 				n[i]["maptype"] = order[l - 1]
# 				build_tree(n[i])
# 	return n

# def print_tree(t, spaces):
# 	if -1 in t.keys():
# 		print(spaces+str(-1) )
# 		print_tree(t[-1], spaces + "  ")
# 		print(spaces+str(0) )
# 		print_tree(t[0], spaces + "  ")
# 		print(spaces+str(1) )
# 		print_tree(t[1], spaces + "  ")

# def traverse_tree(t, m = []):
# 	for i in [-1, 0, 1]:
# 		sum = 0
# 		if i in t.keys():
# 			if(match_won(t[i]["match"])):
# 				print(t[i]["match"])
# 			sum = sum + traverse_tree(t[i])
			

# def print_tree_matches(t, m):
# 	for i in [-1, 0, 1]:
# 		if i in t.keys():
# 			m1 = m.copy()
# 			m1.append(i)
# 			print_tree_matches(t[i], m1)
# 		else:
# 			if match_won(m):
# 				print(m)
				


# t = build_tree()

# traverse_tree(t)