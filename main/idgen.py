ID_SEPERATOR = 100000

class IdGenerator:

    def __init__(self):
        self.team_tickets = {}

    def give_ticket(self, team):



        team_ticket = self.get_team_ticket(team)


        return team * ID_SEPERATOR + team_ticket


    def get_team_ticket(self, team):

        team_gen = self.team_tickets.get(team, None)

        if team_gen == None:

            self.team_tickets[team] = 0
            team_gen = self.team_tickets.get(team, None)

        self.team_tickets[team] += 1

        return team_gen

    def __repr__(self):

        return f"team_tickets: {self.team_tickets}"
