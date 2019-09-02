import csv
from statistics import mean, mode
import random
import argparse
import os

def alpha_range(x):
    x = float(x)
    if x < 0 or x > 1:
        raise argparse.ArgumentTypeError("Alpha out of range [0,1]")
    return x

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--alpha", type=alpha_range, default=0, metavar='A',
	help="Default 0. Factor to bias match outcome probabilities from Crosstable values towards 50/50. 0<=a<=1")
parser.add_argument("-s", "--seed", action="store_true",
	help="Add existing match outcomes before running bracket simulations.")

args = parser.parse_args()

# Generates all possible brackets given the initial bracket specified
def get_seeds(b = []):
	q = [b]
	result = []
	while len(q) > 0:
		bi = q.pop(0)
		if len(bi) == 18:
			result += [bi]
			continue
		q.append(bi + [-1])
		q.append(bi + [1])
	return result

# Pulls head-to-head expected outcomes from Crosstable.csv
def get_probs(file="Crosstable.csv"):
	if not os.path.exists(file):
		raise NameError("'Crosstable.csv' not found. Run 'OWLGLicko.py -c' first.")
	result = {}
	with open(file, mode='r') as infile:
		infile.readline()
		reader = csv.reader(infile)
		X = True
		for i in reader:
			V = i[0].strip()
			H = i[1].strip()
			p = float(i[8].strip())
			if not(V in result.keys()):
				result[V] = {}
			result[V][H] = p
	return result

probs = get_probs()

# Generate probabilities for every possible bracket variation
def simulate_seeded(seed = []):
	seeds = get_seeds(seed)	
	print("  All child seeds computed. Running", "2^"+str(18 - len(seed)), "simulations...")	
	winners = {}
	ranklist = {
		"VAN": {},
		"NYE": {},
		"SFS": {},
		"HZS": {},
		"GLA": {},
		"ATL": {},
		"LDN": {},
		"SEO": {},
		"GZC": {},
		"PHI": {},
		"SHD": {},
		"CDH": {}
	}
	b = Bracket(seeds[0])
	count = 0
	for s in seeds:
		# count += 1
		# if count % 1000 == 0:
		# 	print("Bracket #", count)
		b.set_seed(s)
		r, w = b.results()
		pbracket = b.eval()
		if not(w in winners):
			winners[w] = 0
		winners[w] += pbracket
		for t in ranklist:
			if not(r[t] in ranklist[t].keys()):
				ranklist[t][r[t]] = 0
			ranklist[t][r[t]] += pbracket

	total = 0
	for t in winners:
		total += winners[t]
	sorted_winners = sorted(winners.items(), key=lambda kv: kv[1])
	print()
	print("  Team | Chance of 1st")
	print("  -----|--------------")
	sorted_winners.reverse()
	for i in sorted_winners:
		print("  ", i[0], "|", round(i[1] / total, 4))
	print()

	average_ranks = {}

	with open("Placings.csv", "w") as outfile:
		csvstring = "Team,"
		for i in [1,2,3,4,5,7,9,11]:
			csvstring += str(i) + ","
		csvstring += "Avg Place"
		outfile.write(csvstring+"\n")
		for t in ranklist:
			csvstring = t + ","
			e = 0
			d = sum(ranklist[t].values())
			for i in [1,2,3,4,5,7,9,11]:
				if i not in ranklist[t].keys():
					ranklist[t][i] = 0
				e += i * ranklist[t][i]
				csvstring += str(ranklist[t][i] / d) +","
			csvstring += str(e/d)
			outfile.write(csvstring+"\n")
			average_ranks[t] = e/d

	sorted_ranks = sorted(average_ranks.items(), key=lambda kv: kv[1])
	print("  Team | Avg Rank")
	print("  -----|---------")
	for i in sorted_ranks:
		print("  ", i[0], "|", round(i[1], 4))
	print()

	print("Writing results to 'Placings.csv'...")

# Structure of 2 teams, up to 2 child matches, and the specified outcome of the match
class Match:
	def __init__(self, outcome, team1=None, team2=None, child1 = (None, 0), child2 = (None, 0)):
		self.team1 = team1
		self.team2 = team2
		self.outcome = outcome
		self.child1 = child1
		self.child2 = child2
		self.update()
	
	def set_team(self, i, t):
		if i == 1:
			self.team1 = t
		if i == 2:
			self.team2 = t

	def set_child(self, i, c):
		if i == 1:
			self.child1 = c
		if i == 2:
			self.child2 = c

	def set_teams(self, t1, t2):
		self.set_team(1, t1)
		self.set_team(2, t2)

	def set_children(self, c1, c2):
		self.set_child(1, c1)
		self.set_child(2, c2)

	# Returns probability team1 will win against team2
	def prob(self):
		t1 = self.team1
		t2 = self.team2
		if t1 == None:
			t1 = self.get_team_child(1)
		if t2 == None:
			t2 = self.get_team_child(2)
		if t1 == None or t2 == None:
			return None
		if t1 < t2:
			p = probs[t1][t2]
		else:
			p = 1 - probs[t2][t1]

		if self.outcome == 1:
			return (1-args.alpha)*p + args.alpha*0.5
		if self.outcome == -1:
			return (1-args.alpha)*(1-p) + args.alpha*0.5
		else:
			return None

	def update(self):
		t1 = self.get_team_child(1)
		t2 = self.get_team_child(2)
		if t1 != None:
			self.team1 = t1
		if t2 != None:
			self.team2 = t2

	def get_team_child(self, i):
		if i == 1:
			c = self.child1
		if i == 2:
			c = self.child2
		if c[0] == None:
			return None
		if c[1] == 0:
			return c[0].winner()
		if c[1] == 1:
			return c[0].loser()
		else:
			return None

	def teams(self):
		return [self.team1, self.team2]
	
	def winner(self):
		if self.outcome == 1:
			return self.team1
		elif self.outcome == -1:
			return self.team2
		else:
			return None
	
	def loser(self):
		if self.outcome == -1:
			return self.team1
		elif self.outcome == 1:
			return self.team2
		else:
			return None
	
	def print(self):
		print(self.teams())
		print(self.prob())
		print(self.winner())
		print()

# Structure of Matches for a while Playoff Bracket
class Bracket:
	def __init__(self, seed):
		self.matches = []
		for i in range(18):
			self.matches.append(Match(seed[i]))
		self.update()

	def update(self):
		rank = {
			"VAN":1,
			"NYE":2,
			"SFS":3,
			"HZS":4,
			"GLA":5,
			"ATL":6,
			"LDN":7,
			"SEO":8,
			"GZC":9,
			"PHI":10,
			"SHD":11,
			"CDH":12
		}

		#PLAYINS
		self.matches[0].set_teams("GZC", "CDH")
		self.matches[1].set_teams("PHI", "SHD")
		
		self.matches[2].set_team(1, "LDN")
		self.matches[3].set_team(1, "SEO")
		if rank[self.matches[0].winner()] > rank[self.matches[1].winner()]:
			self.matches[2].set_child(2, (self.matches[0], 0))
			self.matches[3].set_child(2, (self.matches[1], 0))
		else:
			self.matches[2].set_child(2, (self.matches[1], 0))
			self.matches[3].set_child(2, (self.matches[0], 0))
		self.matches[2].update()
		self.matches[3].update()
		
		# PLAYOFFS
		self.matches[4].set_team(1, "VAN")
		self.matches[5].set_teams("HZS", "GLA")
		self.matches[6].set_team(1, "NYE")   
		self.matches[7].set_teams("SFS", "ATL")
		if rank[self.matches[2].winner()] > rank[self.matches[3].winner()]:
			self.matches[4].set_child(2, (self.matches[2], 0))
			self.matches[6].set_child(2, (self.matches[3], 0))
		else:
			self.matches[4].set_child(2, (self.matches[3], 0))
			self.matches[6].set_child(2, (self.matches[2], 0))

		self.matches[8].set_children((self.matches[4],1), (self.matches[5],1))
		self.matches[9].set_children((self.matches[6],1), (self.matches[7],1))
		self.matches[10].set_children((self.matches[4],0), (self.matches[5],0))
		self.matches[11].set_children((self.matches[6],0), (self.matches[7],0)) 
		self.matches[12].set_children((self.matches[11],1), (self.matches[8],0))
		self.matches[13].set_children((self.matches[10],1), (self.matches[9],0)) 
		self.matches[14].set_children((self.matches[12],0), (self.matches[13],0))  
		self.matches[15].set_children((self.matches[10],0), (self.matches[11],0))
		self.matches[16].set_children((self.matches[15],1), (self.matches[14],0))  
		self.matches[17].set_children((self.matches[15],0), (self.matches[16],0))

		for i in range(18):
			self.matches[i].update()

	def set_seed(self, seed):
		for i in range(18):
			self.matches[i].outcome = seed[i]
		self.update()
	
	# Joint probability of all Match outcomes
	def eval(self):
		r = 1
		for m in self.matches:
			r *= m.prob()
		return r

	def print(self):
		for i in self.matches:
			print(i.team1, i.team2, i.outcome)

	def results(self):
		r = {}
		w = self.matches[17].winner()
		r[self.matches[17].winner()] = 1
		r[self.matches[17].loser()]  = 2
		r[self.matches[16].loser()]  = 3
		r[self.matches[14].loser()]  = 4
		r[self.matches[12].loser()]  = 5
		r[self.matches[13].loser()]  = 5
		r[self.matches[8].loser()]   = 7
		r[self.matches[9].loser()]   = 7
		r[self.matches[2].loser()]   = 9
		r[self.matches[3].loser()]   = 9
		r[self.matches[0].loser()]   = 11
		r[self.matches[1].loser()]   = 11
		return r, w

def get_inputs():
	print("\nFollow the prompts to seed the bracket with match outcomes.")
	b = Bracket([1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])
	s = []
	for i in range(18):
		print(b.matches[i].teams())
		instring = input(" What is the outcome for this match?\n 1 for team1, -1 for team2, 0 to exit ")
		instring = int(instring)
		while not(instring in [1, -1, 0]):
			print(" Invalid input")
			instring = input(" What is the outcome for this match?\n 1 for team1, -1 for team2, 0 to exit ")
			instring = int(instring)

		if instring == 0:
			b.update()
			break
		if instring in [1, -1]:
			s.append(instring)
			b.matches[i].outcome = instring
			b.update()
	return s


def main():
	s = []
	if args.seed:
		user_sat = False
		while(not(user_sat)):
			s = get_inputs()
			print(s)
			instring = input(" Are you satisfied with this seed? Y/N ")
			while instring not in ["Y", "N", "y", "n"]:
				print(" Invalid input")
				print(s)
				instring = input(" Are you satisfied with this bracket seed? Y/N ")
				instring = str(instring)
			if instring in ["Y", "y"]:
				user_sat = True
		print()
	print("Running simulation with initial bracket seed:", s)
	simulate_seeded(s)

main()