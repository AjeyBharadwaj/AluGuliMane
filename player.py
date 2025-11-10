import random
from board import CellType
import copy

class Player:
    def __init__(self, name, count=0):
        self.name = name
        self._holes = None
        self._count = count

    @property
    def id(self):
        return self.name.lower().replace(" ", "_")

    @property
    def holes(self):
        return self._holes

    @property
    def count(self):
        return self._count
    
    @count.setter
    def count(self, value):
        self._count = value

    def set_holes(self, holes):
        self._holes = holes

    def __str__(self):
        return f"{self.name}:({sum(hole.count for hole in self.holes)} + {self.count})"
    
    def has_move(self):
        for hole in self.holes:
            if hole.count > 0:
                return True
        return False

    def make_move(self, special_case, game, original_player, original_other_player):
        # return random number bettween 0 and 6 for now
        while True:
            move = random.randint(0, 6)
            if self.holes[move].count > 0:
                return move

    def claim_holes(self):
        for hole in self.holes:
            if hole.count == 4:
                self.count += hole.count
                hole.count = 0

    def claim_remaining(self):
        for hole in self.holes:
            self.count += hole.count
            hole.count = 0

    def reset(self, per_hole=5):
        for hole in self.holes:
            if self.count >= per_hole:
                hole.count = per_hole
                hole.cell_type = CellType.VALID
                self.count -= per_hole
            else:
                hole.cell_type = CellType.PIGGY
                hole.count = 0

    def get_claim_for_move(self, move_index, special_case, game, original_player, original_other_player):
        player = copy.deepcopy(original_player)
        other_player = copy.deepcopy(original_other_player)
        if self.holes[move_index].cell_type == CellType.VALID and self.holes[move_index].count > 0:
            game.do_move(player, other_player, 0, move_index, special_case)
            return player.count
        return 0
    
    def get_claims_for_all_moves(self, special_case, game, original_player, original_other_player):
        claims = []
        for i in range(len(self.holes)):
            claims.append(self.get_claim_for_move(i, special_case, game, original_player, original_other_player))
        return claims

class IntelligentPlayer(Player):
    def make_move(self, special_case, game, original_player, original_other_player):
        claims = self.get_claims_for_all_moves(special_case, game, original_player, original_other_player)
        return claims.index(max(claims)) if claims else self.super().make_move(special_case, game, original_player, original_other_player)

class DumbPlayer(Player):
    def make_move(self, special_case, game, original_player, original_other_player):
        claims = self.get_claims_for_all_moves(special_case, game, original_player, original_other_player)
        return claims.index(min(claims)) if claims else self.super().make_move(special_case, game, original_player, original_other_player)