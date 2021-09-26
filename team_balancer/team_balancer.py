import csv
import itertools

num_to_role = {0: 'top', 1: 'jg', 2: 'mid', 3: 'adc', 4: 'supp'}

players = {}

with open('scores.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')

    for row in reader:
        name = row[0].lower()
        roles = row[1:]

        players[name] = roles


current_players = [
    ("Int Overflow", ("jg")),
    ("AvocadoAvocado", ("adc", "supp")),
    ("stopvixky", ("adc")),
    ("70IQ", ("adc")),
    ("Dee See", ()),
    ("Dragon Stormz", ()),
    ("oyeeh", ("top", "jg")),
    ("meltthesnow", ("jg")),
    ("talons gf", ("adc")),
    ("honeydewkeki", ("top", "jg", "mid", "supp"))
]

team_iterations = []
team_iterations_sub1 = itertools.permutations(current_players[1:])

for i in range(5):
    for team in team_iterations_sub1:
        new_team = list(team)
        new_team.insert(i, current_players[0])
        team_iterations.append(new_team)

min_skill_gap = 100
best_teams = []

for iteration in team_iterations:
    teams = (iteration[0:5], iteration[5:])
    scores = [[], []]

    skip = False
    for num, team in enumerate(teams):
        for i, player in enumerate(team):
            name = player[0].lower()
            roles_to_avoid = player[1]
            if num_to_role[i] in roles_to_avoid:
                skip = True
                break
            # assume playing main role/champ
            scores[num].append(int(players[name][i]) +
                               int(players[name][5]))

    if not skip:
        avg_gap = abs(sum(scores[0]) - sum(scores[1]))
        skill_gap = 0
        for i in range(5):
            skill_gap += abs(scores[0][i] - scores[1][i])

        if skill_gap <= min_skill_gap:
            if skill_gap < min_skill_gap:
                best_teams = []
                min_skill_gap = skill_gap

            team_1 = [(player[0], num_to_role[i])
                      for i, player in enumerate(teams[0])]
            team_2 = [(player[0], num_to_role[i])
                      for i, player in enumerate(teams[1])]

            best_teams.append((team_1, team_2, avg_gap))


print(min_skill_gap)

with open("best_teams.txt", "w") as f:
    for team in best_teams:
        f.write("{}\n".format(team))
