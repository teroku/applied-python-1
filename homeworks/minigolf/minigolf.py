from abc import ABCMeta, abstractmethod


class Player:
    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class BaseMatch(metaclass=ABCMeta):
    def __init__(self, holes_number, players):
        self._holes_number = holes_number
        self._players = players
        self._finished = False
        self._cur_hole = 0
        self._cur_player = 0
        self._table = [tuple([player.name for player in players]),
                       *[(None,) * holes_number] * len(players)]
        self._cur_hole_hits = [0] * len(players)
        self._reverse_sort_order = False

    @property
    def finished(self):
        return self._finished

    @abstractmethod
    def hit(self, success=False):
        pass

    def get_winners(self):
        if not self.finished:
            raise RuntimeError("The match isn't over")

        hits_sums = [sum([self._table[hole_number + 1][player]
                          for hole_number in range(self._holes_number)])
                     for player in range(len(self._players))]
        total_score = [(player, hits) for player, hits in zip(self._players, hits_sums)]
        total_score.sort(key=lambda x: x[1], reverse=self._reverse_sort_order)
        winners = [total_score[0][0]]
        min_hits = total_score[0][1]
        for player, hits in total_score[1:]:
            if hits == min_hits:
                winners.append(player)
            else:
                break

        return winners

    def get_table(self):
        return self._table

    def update_data(self):
        if self._cur_hole + 1 == self._holes_number:
            self._finished = True
        else:
            self._cur_hole += 1
            self._cur_player = self._cur_hole
            self._cur_hole_hits = [0] * len(self._players)


class HitsMatch(BaseMatch):
    MAX_HITS = 10

    def __init__(self, holes_number, players):
        super().__init__(holes_number, players)
        self._still_played = [i for i in range(len(players))]
        self._reverse_sort_order = False

    def hit(self, success=False):
        if self.finished:
            raise RuntimeError("The match is over")

        self._cur_hole_hits[self._cur_player] += 1
        if success:
            cur_player_position = self._still_played.index(self._cur_player)
            self._still_played.remove(self._cur_player)
            if self._still_played:
                self._cur_player = self._still_played[cur_player_position % len(self._still_played)]
        else:
            if len(self._still_played) != 1:
                cur_player_position = self._still_played.index(self._cur_player)
                self._cur_player = self._still_played[(cur_player_position + 1) % len(self._still_played)]
            if self._cur_hole_hits[self._cur_player] == self.MAX_HITS - 1:
                self._cur_hole_hits[self._cur_player] = self.MAX_HITS
                self._still_played = []

        cur_hits_for_table = list(self._cur_hole_hits)
        for player in self._still_played:
            cur_hits_for_table[player] = None
        self._table[self._cur_hole + 1] = tuple(cur_hits_for_table)

        if len(self._still_played) == 0:
            self.update_data()

    def update_data(self):
        super().update_data()
        self._still_played = [i for i in range(len(self._players))]


class HolesMatch(BaseMatch):
    MAX_UNSUCCESSFUL_STEPS = 10

    def __init__(self, holes_number, players):
        super().__init__(holes_number, players)
        self._cur_hole_success_exists = False
        self._steps_count = 0
        self._reverse_sort_order = True

    def hit(self, success=False):
        if self.finished:
            raise RuntimeError("The match is over")

        if success:
            self._cur_hole_hits[self._cur_player] = 1
            self._cur_hole_success_exists = True
        self._cur_player = (self._cur_player + 1) % len(self._players)

        cur_hits_for_table = list(self._cur_hole_hits)
        if self._cur_player <= self._cur_hole:
            for i in range(self._cur_player, self._cur_hole):
                cur_hits_for_table[i] = None
        else:
            for i in range(self._cur_player, len(self._players)):
                cur_hits_for_table[i] = None
            for i in range(self._cur_hole):
                cur_hits_for_table[i] = None

        self._table[self._cur_hole + 1] = tuple(cur_hits_for_table)
        if self._cur_player % len(self._players) == self._cur_hole:
            self._steps_count += 1
            if self._cur_hole_success_exists or self._steps_count == self.MAX_UNSUCCESSFUL_STEPS:
                self.update_data()

    def update_data(self):
        super().update_data()
        self._cur_hole_success_exists = False
        self._steps_count = 0