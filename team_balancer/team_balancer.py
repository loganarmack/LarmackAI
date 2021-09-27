import csv
import itertools
from random import choice


class TeamBalancer:
    player_data = {}
    num_to_role = {0: 'top', 1: 'jg', 2: 'mid', 3: 'bot', 4: 'supp'}

    def __init__(self, gamemode):
        self.gamemode = gamemode
        self.players = []
        self.best_teams = []
        self.used_teams = []
        self.computed = False

        if not TeamBalancer.player_data:
            self.load_player_data()

    def get_num_players(self):
        return len(self.players)

    def add_player(self, name, roles):
        for player in self.players:
            if player[0].lower() == name.lower():
                return False

        self.players.append((name, roles))
        return True

    def balance(self):
        self.used_teams = []
        num_players = len(self.players)
        break_point = num_players // 2
        team_iterations = []

        # account for symmetric teams
        if num_players % 2 == 0:
            team_iterations_sub1 = itertools.permutations(
                self.players[1:]) if self.gamemode == "sr" else itertools.combinations(self.players[1:], break_point)
            for i in range(break_point):
                for team in team_iterations_sub1:
                    new_team = list(team)
                    new_team.insert(i, self.players[0])
                    team_iterations.append(new_team)
        else:
            team_iterations = itertools.permutations(
                self.players) if self.gamemode == "sr" else itertools.combinations(self.players, break_point)

        min_skill_gap = 999
        best_teams = []

        for iteration in team_iterations:
            if self.gamemode == "sr":
                teams = (iteration[:break_point], iteration[break_point:])
            else:
                teams = (
                    iteration, [team for team in self.players if team not in iteration])
            scores = ([], [])

            skip = False
            for num, team in enumerate(teams):
                for i, player in enumerate(team):
                    name = player[0].lower()
                    if name not in self.player_data:
                        name = "av"
                    roles_to_avoid = player[1]
                    if self.num_to_role[i] in roles_to_avoid:
                        skip = True
                        break

                    if self.gamemode == "aram":
                        scores[num].append(self.player_data[name]['overall'])
                    else:
                        scores[num].append(
                            self.player_data[name]['roles'][i] + self.player_data[name]['main_bonus'])

            if not skip:
                skill_gap = 0
                if self.gamemode == "aram":
                    skill_gap = abs(sum(scores[0]) - sum(scores[1]))
                else:
                    for i in range(break_point):
                        skill_gap += abs(scores[0][i] - scores[1][i])

                if skill_gap <= min_skill_gap:
                    if skill_gap < min_skill_gap:
                        best_teams = []
                        min_skill_gap = skill_gap

                    if self.gamemode == "aram":
                        team_1 = [player[0] for player in teams[0]]
                        team_2 = [player[0] for player in teams[1]]

                    else:
                        team_1 = [(player[0], self.num_to_role[i])
                                  for i, player in enumerate(teams[0])]
                        team_2 = [(player[0], self.num_to_role[i])
                                  for i, player in enumerate(teams[1])]

                    best_teams.append((team_1, team_2, skill_gap))

        self.best_teams = best_teams

        selected_teams = choice(best_teams)
        self.used_teams.append(selected_teams)

        self.computed = True
        return selected_teams

    def reroll(self):
        if not self.computed:
            return self.balance()

        if len(self.used_teams) == len(self.best_teams):
            selected_teams = "You've already gone through all the most fair teams."
        else:
            unused = [
                teams for teams in self.best_teams if teams not in self.used_teams]
            selected_teams = choice(unused)
            self.used_teams.append(selected_teams)
        return selected_teams

    @staticmethod
    def load_player_data():
        with open('team_balancer/scores.csv', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')

            for row in reader:
                name = row[0].lower().replace(" ", "")
                roles = [int(i) for i in row[1:-1]]
                main_bonus = int(row[-1])
                overall = sum(int(role) for role in roles) + main_bonus

                TeamBalancer.player_data[name] = {
                    'roles': roles,
                    'main_bonus': main_bonus,
                    'overall': overall
                }
