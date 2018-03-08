# coding: utf-8
import sys
sys.path.append("../../")
import asyncio


import Client
import GlobalParameters as gp

class Stats(Client.ClientInterface):
    def __init__(self, name = "statistique", file = None):
        super().__init__(name, file, active=False)
        self.is_finished = False
        self.stats_first = MyStats(0) #stats liées à l'ia level 1  
        self.stats_second = MyStats(1) #stats liées à l'ia level 2 


    def update_play(self, data):
        player = data["actual_player"]
        nb_points_gagne = 0
        nb_lines = 0

        if player == 0 :
            nb_points_gagne = data["score"][self.stats_first.id] - self.stats_first.score_last_turn
        else :
            nb_points_gagne = data["score"][self.stats_second.id] - self.stats_first.score_last_turn

        if nb_points_gagne == 40 :
            nb_lines = 1
        elif nb_points_gagne == 100 :
            nb_lines = 2
        elif nb_points_gagne == 300 :
            nb_lines = 3
        elif nb_points_gagne == 1200 :
            nb_lines = 4

        if player == self.stats_first.id :
            self.stats_first.score_last_turn = data["score"][self.stats_first.id]
            self.stats_first.nb_line_current_game += nb_lines
        else :
            self.stats_second.score_last_turn = data["score"][self.stats_second.id]
            self.stats_second.nb_line_current_game += nb_lines

    def play(data) :
        pass

    def on_init_game(self, data):
        pass

    def on_finished_game(self,data):
        self.score_last_turn = 0
        self.is_finished = True

        #On gère les scores et les wins
        score_player1 = data["score"][self.stats_first.id]
        score_player2 = data["score"][self.stats_second.id]

        self.stats_first.scores += [score_player1]
        self.stats_second.scores += [score_player2]

        if score_player1 == gp.SCORE_DEPASSEMENT :
            self.stats_first.loose_by_height += 1
            self.stats_second.win_by_height += 1

        elif score_player2 == gp.SCORE_DEPASSEMENT :
            self.stats_second.loose_by_height += 1
            self.stats_first.win_by_height += 1

        elif score_player1 > score_player2 :
            self.stats_first.wins_by_points += 1
            self.stats_second.loose_by_points += 1

        elif score_player2 > score_player1 :
            self.stats_first.loose_by_points += 1
            self.stats_second.wins_by_points += 1

        elif score_player2 == score_player1 :
            self.stats_first.egalite += 1
            self.stats_second.egalite += 1

        #on gère les lignes réalisées
        self.stats_first.scores += [self.stats_first.nb_lines]
        self.stats_second.scores += [self.stats_second.nb_lines]
        self.nb_line_current_game = 0



    async def run(self, level1, level2, nb_games_to_observe = 10) :
        await super().init_train()
        for _ in range(nb_games_to_observe) :
            if level1==level2:
                ias=[[level1,2]]
            else:
                ias=[[level1,1],[level2,1]]
            await super().new_game(ias=ias,viewers=[4,self.my_client.pid])
            self.is_finished = False
            while not self.is_finished :
                await asyncio.sleep(0)



    def save(self):
        pass

    def load(self):
        pass

class MyStats() :
    def __init__(self, id) :
        self.id = id

        self.nb_line_current_game = 0
        self.score_last_turn = 0

        self.nb_lines = list()
        self.scores = list()
        self.wins_by_points = 0
        self.loose_by_points = 0
        self.win_by_height = 0
        self.loose_by_height = 0
        self.egalite = 0

    def __str__(self) :
        string = "Id : " + str(self.id) + "\n"
        string += "Ratio gagnée/perdues : " + str(self.win_by_height + self.wins_by_points) \
            + "/" + str(self.loose_by_height + self.loose_by_points) + " : " \
            + str((self.wins_by_points + self.win_by_height)/(self.loose_by_points + self.loose_by_height)) \
            + "\n"
        string += "Parmis les parties gagnées, " + str(self.wins_by_points) + \
         " parties ont été gagné par les points (nb de coups max atteint) et " + str(self.win_by_height) +\
         " parce que son adversaire a atteint dépasser la hauteur maximum.\n"
        string += "De même, " + str(self.loose_by_points) + " parties ont été pardu par le nb de points et " + \
            str(self.loose_by_height) + " par la hauteur maximale.\n"
        string += str(self.egalite) + "parties ont été fini par une égalité.\n"
        string += "Nombre de lignes réalisées : " + str(self.nb_lines) + "\n"
        string += "Scores obtenus : " + str(self.scores) + "\n"
        return string

if __name__ == "__main__":
    statistique = Stats()
    AI_LOOP = asyncio.get_event_loop()
    AI_LOOP.run_until_complete(statistique.run(0, 0))
    print(statistique.stats_first, statistique.stats_second)