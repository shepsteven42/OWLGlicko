import argparse
import json
import urllib.request as url
import os
import csv
import MyGlicko as glicko2
from statistics import mean
import random
from outcomes import calc_prob_win_ft4, get_wins_ft4, calc_prob_win_rs, get_wins_rs
import numpy

def period_range(x):
    x = int(x)
    if x <= 0:
        raise argparse.ArgumentTypeError("Period cannot be less or equal to 0")
    return x

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--update", action="store_true",
	help="Update match data from api.overwatchleague.com")
parser.add_argument("--random", action="store_true",
	help="Randomize game order before rating. Use this to mitigate recency bias.")
parser.add_argument("--score", action="store_true",
	help="Score the system parameters' prediction accuracy throughout the season.")
parser.add_argument("-c", "--crosstable", action="store_true",
	help="Generate expected outcomes in each maptype. Outputs to Crosstable.csv.")
parser.add_argument("-t", "--timeline", action="store_true",
	help="Generate rating history, taken at the end of every rating period. Outputs to Timeline.csv.")
parser.add_argument("-p", "--periods", type=period_range, default=25, metavar='PERIOD',
	help="Split the season into P rating periods. Default=25")
parser.add_argument("-r", "--rating", type=float, default=1500, metavar='RATING',
	help="Set the starting rating for each player. Default=1500")
parser.add_argument("-d", "--deviation", type=float, default=400, metavar='DEV',
	help="Set the starting rating deviation for each player. Default=400")
parser.add_argument("-v", "--volatility", type=float, default=0.08, metavar='VOL',
	help="Set the starting volatility for each player. Default=0.08")

args = parser.parse_args()

team_names = [
	"ATL","BOS","CDH","DAL","FLA",
	"GLA","GZC","HOU","HZS","LDN",
	"NYE","PAR","PHI","SEO","SFS",
	"SHD","TOR","VAL","VAN","WAS"
]
maptypes = ["control","assault","hybrid", "escort", "all"]
randCount = 50


# Pulls new match data from api.overwatchleague.com and outputs to MapList.csv in the working directory
def update_mapfile():
	print(" Update triggered. Updating MapFile...")
	contents = url.urlopen("https://api.overwatchleague.com/schedule").read()

	schedule = json.loads(contents)
	stages = schedule["data"]["stages"]

	strings = []
	
	CSVString = "GameID, MatchID, Visitor, Vabbr, Home, Habbr, V Score, H Score, Draws, GameNo, VPoints, HPoints, BuildID, InstanceID, MapGUID, State, Start Date, StageID, Match Type, V1, V2, V3, V4, V5, V6, H1, H2, H3, H4, H5, H6 \n"
	strings.append(CSVString)

	for s in stages:
		StageName = s["name"]
		print("  Updating matches in", StageName, "...")
		count = 0
		if StageName != "All-Stars":
			for m in s["matches"]:
				if count % 10 == 9:
					print("    ", count+1, "matches parsed")
				count = count + 1
				if m["state"] == "CONCLUDED":
					MatchID = m["id"]
					Visitor = m["competitors"][0]["name"]
					Vabbr   = m["competitors"][0]["abbreviatedName"]
					Home	= m["competitors"][1]["name"]
					Habbr   = m["competitors"][1]["abbreviatedName"]
					VID		= m["competitors"][0]["id"]
					HID		= m["competitors"][1]["id"]
					VScore 	= m["wins"][0]
					HScore	= m["wins"][1]
					Draws	= m["ties"][0]
					SDate	= m["startDateTS"]
					StageID = m["bracket"]["id"]
					MatchType = m["bracket"]["type"]
					State 	= m["state"]
					contents = url.urlopen("https://api.overwatchleague.com/match/" + str(MatchID)).read()
					MatchJson = json.loads(contents)
					for g in m["games"]:
						GameID	= g["id"]
						GameNo	= g["number"]
						VPoints = g["points"][0]
						HPoints = g["points"][1]
						try:
							BuildID = g["attributes"]["build"]
						except:
							BuildID = 60433
						MapGUID = g["attributes"]["mapGuid"]
						Instance = g["attributes"]["instanceID"]
						VPlayers = []
						HPlayers = []
						for p in MatchJson["games"][GameNo - 1]["players"]:
							if VID == p["team"]["id"]:
								VPlayers.append(p["player"]["id"])
							else:
								HPlayers.append(p["player"]["id"])
						VPString = ""
						HPString = ""
						for i in VPlayers:
							VPString = VPString + str(i) + " , "
						for i in HPlayers:
							HPString = HPString + str(i) + " , "
						CSVString = (	str(GameID) + " , " +
										str(MatchID) + " , " + 
										str(Visitor) + " , " + 
										str(Vabbr) + " , " + 
										str(Home) + " , " + 
										str(Habbr) + " , " + 
										str(VScore) + " , " + 
										str(HScore) + " , " + 
										str(Draws) + " , " + 
										str(GameNo) + " , " + 
										str(VPoints) + " , " + 
										str(HPoints) + " , " + 
										str(BuildID) + " , " + 
										str(Instance) + " , " + 
										str(MapGUID) + " , " + 
										str(State) + " , " + 
										str(SDate) + " , " + 
										str(StageID) + " , " + 
										str(MatchType) + " , " + 
										VPString + HPString
										+ str(0) + "\n"
									)
						strings.append(CSVString)
				else:
					try:
						MatchID = m["id"]
						Visitor = m["competitors"][0]["name"]
						Vabbr   = m["competitors"][0]["abbreviatedName"]
						Home	= m["competitors"][1]["name"]
						Habbr   = m["competitors"][1]["abbreviatedName"]
						VID		= m["competitors"][0]["id"]
						HID		= m["competitors"][1]["id"]
						VScore 	= m["wins"][0]
						HScore	= m["wins"][1]
						Draws	= m["ties"][0]
						SDate	= m["startDateTS"]
						StageID = m["bracket"]["id"]
						MatchType = m["bracket"]["type"]
						State 	= m["state"]

						CSVString = (	str("") + " , " +
											str(MatchID) + " , " + 
											str(Visitor) + " , " + 
											str(Vabbr) + " , " + 
											str(Home) + " , " + 
											str(Habbr) + " , " + 
											str(VScore) + " , " + 
											str(HScore) + " , " + 
											str(Draws) + " , " + 
											" , , , , , , " +
											str(State) + " , " + 
											str(SDate) + " , " + 
											str(StageID) + " , " + 
											str(MatchType) + " , " +
											"\n"
										)
						strings.append(CSVString)
					except:
						pass
	MapCSV = open("MapList.csv", "w")
	for s in strings:
		MapCSV.write(s)
	MapCSV.close()
	print("MapFile update complete.")
	print()

# Converts match data from Maplist.csv into Glicko-usable form
def get_matches(mapfile="MapList.csv"):
	contents = url.urlopen("https://api.overwatchleague.com/maps").read()
	maps = json.loads(contents)
	mapLookup = {}

	result = []
	for m in maps:
		GUID = m["guid"]
		TYPE = m["type"]
		mapLookup[GUID] = TYPE

	with open(mapfile, mode='r') as infile:
		infile.readline()
		reader = csv.reader(infile)
		X = True
		for i in reader:
			if i[15].strip() == "CONCLUDED":
				outcome = 0.5
				V = i[3].strip()
				H = i[5].strip()
				maptype = mapLookup[i[14].strip()]
				if i[10] > i[11]:
					outcome = 1.
				elif i[11] > i[10]:
					outcome = 0.

				result.append([V, H, maptype, outcome])
	return result

# Uses Glicko ratings to generate head-to-head expected outcomes
def crosstable_predictions(teams, maptypes, outfile="Crosstable.csv"):
	draw_odds = {
		"control":	0.00,
		"assault":	0.073089701,
		"hybrid":	0.02302631579,
		"escort":	0.00,
		"all":		0.01966955153
	}
	with open(outfile, "w") as out:
		result = []
		csvstring = "team 1, team 2, control, assault, hybrid, escort, all, rs, ft4\n"
		out.write(csvstring)
		rsmatches = get_wins_rs()
		ft4matches = get_wins_ft4()
		for t1 in teams:
			for t2 in teams:
				if t1 < t2:
					csvstring = t1 + "," + t2 + ","
					probs = {}
					for mt in maptypes:
						result.append(t1)
						result.append(t2)
						r1 = teams[t1][mt].rating
						rd1 = teams[t1][mt].rd
						r2 = teams[t2][mt].rating
						rd2 = teams[t2][mt].rd
						m = teams[t1][mt].expected_outcome(r2, rd2)
						probs[mt] = {}
						probs[mt][1] 	= m / (1+draw_odds[mt])
						probs[mt][0] 	= draw_odds[mt] / (1+draw_odds[mt])
						probs[mt][-1] 	= (1-m) / (1+draw_odds[mt])
						csvstring += str(m) + ","
					p1 = calc_prob_win_rs(probs, rsmatches)
					p2 = calc_prob_win_ft4(probs, ft4matches)
					# print("  ", t1, t2, p2)
					out.write(csvstring + str(p1) + "," + str(p2) + "\n")

# Assigns ratings to each team based on the games specified
def rating_pool(games, rating=args.rating, rd = args.deviation, vol = args.volatility, period=args.periods, randomizer = args.random, tau=0.8):
	teams = {}
	for t in team_names:
		teams.update({t:{}})
		for m in maptypes:
			teams[t].update({m:glicko2.Player(rating=rating, rd=rd, vol=vol, tau=tau)})

	elo_over_time = {}
	for t in team_names:
		elo_over_time.update({t:{}})
		for m in maptypes:
			elo_over_time[t].update({m:[]})

	count = {"control":0, "hybrid":0, "assault":0, "escort":0, "all":0}
	score = {"control":0, "hybrid":0, "assault":0, "escort":0, "all":0}
	score2 = {"control":0, "hybrid":0, "assault":0, "escort":0, "all":0}

	if randomizer:
		random.shuffle(games)

	period_size = round(len(games)/period)
	num_periods = period
	ranges = []
	for i in range(int(num_periods)):
		r = [i * period_size, (i+1)*period_size]
		if r[1] > len(games):
			r[1] = len(games)
			ranges.append(r)
			break
		ranges.append(r)

	for r in ranges:
		gameset = games[r[0]:r[1]]
		to_update = {}
		for t in teams:
			to_update[t] = {}
		for t in teams:
			for m in maptypes:
				to_update[t][m] = {"ratings":[], "rds":[], "outcomes":[]}
		for g in gameset:
			t1 = g[0]
			t2 = g[1]
			mt = g[2]
			oc = g[3]

			to_update[t1][mt]["ratings"] 	+= [teams[t2][mt].rating]
			to_update[t1][mt]["rds"] 		+= [teams[t2][mt].rd]
			to_update[t1][mt]["outcomes"] 	+= [oc]
			to_update[t2][mt]["ratings"] 	+= [teams[t1][mt].rating]
			to_update[t2][mt]["rds"] 		+= [teams[t1][mt].rd]
			to_update[t2][mt]["outcomes"] 	+= [1-oc]

			expected = teams[t1][mt].expected_outcome(teams[t2][mt].rating, teams[t2][mt].rd)
			s = (round(expected) * oc + round(1-expected)*(1-oc))
			score[mt] += s
			count[mt] += 1

			mt = "all"
			to_update[t1][mt]["ratings"] 	+= [teams[t2][mt].rating]
			to_update[t1][mt]["rds"] 		+= [teams[t2][mt].rd]
			to_update[t1][mt]["outcomes"] 	+= [oc]
			to_update[t2][mt]["ratings"] 	+= [teams[t1][mt].rating]
			to_update[t2][mt]["rds"] 		+= [teams[t1][mt].rd]
			to_update[t2][mt]["outcomes"] 	+= [1-oc]

			expected = teams[t1][mt].expected_outcome(teams[t2][mt].rating, teams[t2][mt].rd)
			s = (round(expected) * oc + round(1-expected)*(1-oc))
			score[mt] += s
			count[mt] += 1
		for t in teams:
			for m in maptypes:
				if len(to_update[t][m]["ratings"]) > 0:
					teams[t][m].update_player(to_update[t][m]["ratings"],to_update[t][m]["rds"],to_update[t][m]["outcomes"])
				else:
					teams[t][m].did_not_compete()
		if args.timeline:
			for team in teams:
				for m in maptypes:
					elo_over_time[team][m].append(teams[team][m].rating)

	if args.timeline:
		for team in teams:
			for m in maptypes:
				elo_over_time[team][m].append(teams[team][m].rating)
	
	for m in score:
		score[m] /= count[m]

	return teams, elo_over_time, score

def main():
	
	if args.update:
		update_mapfile()
	elif not(os.path.exists("MapList.csv")):
		print(" MapList.csv does not exist. Updating...")
		update_mapfile()

	print(" Initializing rating system with parameters:")
	print("", args.rating, args.deviation, args.volatility, args.periods)

	games = get_matches("MapList.csv")
	if args.random:
		print(" Rating " + str(len(games)) + " games " + str(randCount) + " times...")
		teams_list = []
		elo_over_time_list = []
		score_list = []
		for i in range(randCount):
			t, eot, s = rating_pool(games)
			teams_list.append(t)
			elo_over_time_list.append(eot)
			score_list.append(s)
		
		teams = teams_list.pop()
		elo_over_time = elo_over_time_list.pop()
		score = score_list.pop()
		for i in range(randCount-1):
			other = teams_list.pop()
			for t in teams:
				for m in maptypes:
					teams[t][m].rating = ((i+1)*teams[t][m].rating + other[t][m].rating) / (i+2)
					teams[t][m].rd = ((i+1)*teams[t][m].rd + other[t][m].rd) / (i+2)
					teams[t][m].vol = ((i+1)*teams[t][m].vol + other[t][m].vol) / (i+2)
			other = elo_over_time_list.pop()
			for t in teams:
				for m in maptypes:
					for k in range(len(elo_over_time[t][m])):
						elo_over_time[t][m][k] = ((i+1)*elo_over_time[t][m][k] + other[t][m][k]) / (i+2)
			other = score_list.pop()
			for m in maptypes:
				score[m] = ((i+1)*score[m] + other[m]) / (i+2)

	else:
		print(" Rating " + str(len(games)) + " games...")
		teams, elo_over_time, score = rating_pool(games)

	# print(" scores:")
	# for m in maptypes:
	# 	print("",round(score[m], 3))
	with open("Ratings.csv", "w") as outfile:
		csvstring = "Team" + ","
		for m in maptypes:
			csvstring += m + ","
		csvstring += "\n"
		outfile.write(csvstring)
		for i in teams:
			csvstring = i + ","
			for m in maptypes:
				csvstring += str(teams[i][m].rating) + ","
			csvstring +="\n"
			outfile.write(csvstring)
		print(" Ratings output to file 'Ratings.csv'")

	if args.timeline:
		with open("Timeline.csv", "w") as outfile:
			for m in maptypes:
				csvstring = m + '\n'
				outfile.write(csvstring)
				for i in elo_over_time:
					csvstring = i + ","
					for j in elo_over_time[i][m]:
						csvstring += str(j) + ","
					csvstring+= "\n"
					outfile.write(csvstring)
				csvstring = '\n'
				outfile.write(csvstring)
			print(" Timeline output to file 'Timeline.csv'")

	if args.crosstable:
		crosstable_predictions(teams, maptypes)
		print(" Crosstable output to file 'Crosstable.csv'")

def testparams():
	games = get_matches()
	results = []
	maxes = {}


	for m in maptypes:
		maxes[m] = [0,0,0,0,0,0,0,0,0]
	for rd in numpy.arange(400, 401, 25):
		for vol in numpy.arange(0.08,0.081, 0.01):
			for period in [20,40,60,80,100,200,400,800,1000,1200]:
				for tau in numpy.arange(0.2,0.8, 0.1):
					teams, elo_over_time, score = rating_pool(games, rating=args.rating, rd=rd, vol=(vol), period =(period), tau=tau, randomizer = False)
					# for t in teams:
					# 	print(t, teams[t]["control"].rating)
					r = []
					r.append(rd)
					r.append(vol)
					r.append(period)
					r.append(tau)
					for m in maptypes:
						r.append(score[m])
					results.append(r)
					i = 4
					for m in maptypes:
						if maxes[m][i] < score[m]:
							maxes[m] = r
						i+=1
					for i in range(len(r)):
						r[i] = round(r[i], 5)
					print(r)
	print()
	for m in maptypes:
		print(m[0], maxes[m])

	with open("TestParams.csv", "w") as outfile:
		csvstring = "RD, VOL, PER,"
		for m in maptypes:
			csvstring+=m + ","
		outfile.write(csvstring + "\n")
		for i in results:
			csvstring = ""
			for k in i:
				csvstring+= str(k) + ","
			outfile.write(csvstring+ "\n")

main()