import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

weights = {"Goal": 1, "OwnGoal": -1, "Miss": 0, "ST": 0.1, "S": 0.05, "WOXL": 1, "LOXW": -1, "TOXL": 0.5, "TOXW": -0.5}

def evaluate(df: pd.DataFrame, st, s, ppda):
    xG = 0
    eval = 0
    for _, row in df.iterrows():
        x = float(row["xG"])
        xG += x
        if row["Result"] == "Goal":
            eval += (weights["Goal"] - x)
        elif row["Result"] == "OwnGoal":
            eval += (weights["OwnGoal"] - x)
        else:
            eval += (weights["Miss"] - x)
    sides = (weights["ST"] * st) + (weights["S"] * s) + 1/ppda
    #print(1/ppda)
    norm = ((eval + sides)/(xG + sides))*10
    return xG, eval, norm

def add_match(campionato):
	base_url = "https://understat.com/match/"
	match_id = str(input("Match id: "))
	url = base_url + match_id

	res = requests.get(url)
	soup = BeautifulSoup(res.content, 'lxml')
	scripts = soup.find_all('script')
	actual = scripts[1].string
	#print(actual)

	data = json.loads(actual[actual.index("('")+2:actual.index("')")].encode('utf8').decode('unicode_escape'))
	actual = actual[actual.index("')")+2:]
	#print(actual)
	match_info = json.loads(actual[actual.index("('")+2:actual.index("')")].encode('utf8').decode('unicode_escape'))
	#pp.pprint(match_info)

	xg = []
	result = []
	team = []
	team_h = None
	team_a = None
	data_h = data['h']
	data_a = data['a']

	for index in range(len(data_h)):
		for key in data_h[index]:
			if key == 'xG':
				xg.append(data_h[index][key])
			if key == 'result':
				result.append(data_h[index][key])
			if key == 'h_team':
				team_h = data_h[index][key]
				team.append(data_h[index][key])

	for index in range(len(data_a)):
		for key in data_a[index]:
			if key == 'xG':
				xg.append(data_a[index][key])
			if key == 'result':
				result.append(data_a[index][key])
			if key == 'a_team':
				team_a = data_a[index][key]
				team.append(data_a[index][key])

	h_ppda = 0
	a_ppda = 0
	h_st = 0
	a_st = 0
	h_s = 0
	a_s = 0
	h_goals = 0
	a_goals = 0

	for key in match_info:
		if key == "a_ppda":
			a_ppda = float(match_info[key])
		if key == "h_ppda":
			h_ppda = float(match_info[key])
		if key == "a_shotOnTarget":
			a_st = float(match_info[key])
		if key == "h_shotOnTarget":
			h_st = float(match_info[key])
		if key == "a_shot":
			a_s = float(match_info[key])
		if key == "h_shot":
			h_s = float(match_info[key])
		if key == "h_goals":
			h_goals = float(match_info[key])
		if key == "a_goals":
			a_goals = float(match_info[key])

	col_names = ["xG", "Result", "Team"]
	df = pd.DataFrame([xg, result, team], index=col_names)
	df = df.T
	#print(df)

	df_h = df[df["Team"] == team_h]
	df_a = df[df["Team"] == team_a]

	h_xG, h_eval, h_norm = evaluate(df_h, h_st, h_s, h_ppda)
	a_xG, a_eval, a_norm = evaluate(df_a, a_st, a_s, a_ppda)
	if h_goals > a_goals and h_xG < a_xG:
		h_norm += weights["WOXL"]
		a_norm += weights["LOXW"]
	if h_goals < a_goals and h_xG > a_xG:
		h_norm += weights["LOXW"]
		a_norm += weights["WOXL"]
	if h_goals == a_goals and h_xG < a_xG:
		h_norm += weights["TOXL"]
		a_norm += weights["TOXW"]
	if h_goals == a_goals and h_xG > a_xG:
		h_norm += weights["TOXW"]
		a_norm += weights["TOXL"]

	print("Team " + team_h + " \n\tExpected goals: " + str(h_xG) + "\n\tEval: " + str(h_eval) + "\n\tFinal: " + str(h_norm))
	print("Team " + team_a + " \n\tExpected goals: " + str(a_xG) + "\n\tEval: " + str(a_eval) + "\n\tFinal: " + str(a_norm))

	if team_h not in campionato:
		campionato[team_h] = {"num": 1, "avg-xG": h_xG, "avg-Eval": h_eval, "Final": h_norm}
	else:
		campionato[team_h]["avg-xG"] = (campionato[team_h]["avg-xG"] * campionato[team_h]["num"] + h_xG) / (campionato[team_h]["num"] + 1)
		campionato[team_h]["avg-Eval"] = (campionato[team_h]["avg-Eval"] * campionato[team_h]["num"] + h_eval) / (campionato[team_h]["num"] + 1)
		campionato[team_h]["num"] += 1
		campionato[team_h]["Final"] += h_norm

	if team_a not in campionato:
		campionato[team_a] = {"num": 1, "avg-xG": a_xG, "avg-Eval": a_eval, "Final": a_norm}
	else:
		campionato[team_a]["avg-xG"] = (campionato[team_a]["avg-xG"] * campionato[team_a]["num"] + a_xG) / (campionato[team_a]["num"] + 1)
		campionato[team_a]["avg-Eval"] = (campionato[team_a]["avg-Eval"] * campionato[team_a]["num"] + a_eval) / (campionato[team_a]["num"] + 1)
		campionato[team_a]["num"] += 1
		campionato[team_a]["Final"] += a_norm

	with open("campionato.json", "w") as file:
		json.dump(campionato, file, indent=4)


def display_leaderboard(campionato):
	leaderboard = []
	for team in campionato:
		leaderboard.append((team, campionato[team]["Final"]))
	leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)
	for i in range(len(leaderboard)):
		print(f"{i+1}. {leaderboard[i][0]}: {leaderboard[i][1]}")