from enum import Enum
import copy

class CellType(Enum):
    PIGGY = 1
    VALID = 2

class Coin:
    ...


class Move:
    def __init__(self, player, player1, player2, hole_index):
        self.player = player
        self.player1 = player1
        self.player2 = player2
        self.hole_index = hole_index

    def __str__(self):
        return f"{self.player.name} chose hole {self.hole_index}"


class Hole:
    def __init__(self, cell_type=CellType.VALID, count=0):
        self._cell_type = cell_type
        self._count = count

        if cell_type == CellType.PIGGY:
            self._count = -1

    @property
    def cell_type(self):
        return self._cell_type
    
    @cell_type.setter
    def cell_type(self, value):
        self._cell_type = value

    @property
    def count(self):
        return self._count
    
    @count.setter
    def count(self, value):
        self._count = value

class Board:
    def __init__(self, Player1, Player2):
        self.player1 = Player1
        self.player2 = Player2

    def display(self):
        raise NotImplementedError("Subclasses should implement this method.")


class StandardBoard(Board):
    def __init__(self, Player1, Player2):
        super().__init__(Player1, Player2)
        self.player1.set_holes([Hole(CellType.VALID) for i in range(7)])
        self.player2.set_holes([Hole(CellType.VALID) for i in range(7)])

    def display(self):
        print(f"{self.player1}")
        for i in range(7):
            to_show = self.player1.holes[6-i].count if self.player1.holes[6-i].cell_type == CellType.VALID else "P"
            print(f"{to_show:<2} ", end="  ")
        print("")
        for i in range(7):
            to_show = self.player2.holes[i].count if self.player2.holes[i].cell_type == CellType.VALID else "P"
            print(f"{to_show:<2} ", end="  ")
        print(f"\n{self.player2}")

class Game:
    def __init__(self, board):
        self.board = board
        self.moves = []

    def done(self):
        return (not self.board.player1.has_move() and not self.board.player1.count) or \
        (not self.board.player2.has_move() and not self.board.player2.count)
    
    def set_for_next_round(self, player1, player2):
        coins_per_hole = 5
        if player1.count < 5 or player2.count < 5:
            coins_per_hole = 1
        player1.reset(coins_per_hole)
        player2.reset(coins_per_hole)

    def play(self, player1, player2):
        move_count = 0
        self.set_for_next_round(player1, player2)

        #self.board.display()
        while not self.done():
            special_case = False
            if move_count and (player1.count==0 and player2.count==0):
                special_case = True


            self.play_one_round(player1, player2, special_case)
            move_count += 1
            if self.done():
                break

            self.set_for_next_round(player1, player2)

            #self.board.display()
            player1, player2 = player2, player1  # Swap players for next round

    def play_one_round(self, player, other_player, special_case):
        while True:
            if not player.has_move():
                break
            self.play_turn(player, other_player, special_case)
            if not other_player.has_move():
                break
            self.play_turn(other_player, player, special_case)

        player.claim_remaining()
        other_player.claim_remaining()

    def skip_piggy(self, holes, index):
        while holes[index].cell_type == CellType.PIGGY:
            index = (index + 1) % 14
        return index

    def get_next_move_index(self, holes, move_index):
        move_index += 1
        move_index %= len(holes)
        return self.skip_piggy(holes, move_index)

    def claim_hole(self, holes, index):
        claim_index = self.get_next_move_index(holes, index)
        claim_hole = holes[claim_index]
        to_claim = claim_hole.count
        claim_hole.count = 0

        if to_claim > 0: # FIXME. Should not be fixed values in case of piggy.
            # Also claim other side
            if claim_index == 0:
                claim_index = 0
            if claim_index == 1:
                claim_index = 12
            elif claim_index == 2:
                claim_index = 11
            elif claim_index == 3:
                claim_index = 10
            elif claim_index == 4:
                claim_index = 9
            elif claim_index == 5:
                claim_index = 8
            elif claim_index == 6:
                claim_index = 7
            elif claim_index == 7:
                claim_index = 7
            elif claim_index == 8:
                claim_index = 5
            elif claim_index == 9:
                claim_index = 4
            elif claim_index == 10:
                claim_index = 3
            elif claim_index == 11:
                claim_index = 2
            elif claim_index == 12:
                claim_index = 1
            elif claim_index == 13:
                claim_index = 0

            other_claim_hole = holes[claim_index]
            to_claim += other_claim_hole.count
            other_claim_hole.count = 0
        return to_claim

    def play_turn(self, player, other_player, special_case):
        move_index = player.make_move(special_case, copy.deepcopy(self), copy.deepcopy(player), copy.deepcopy(other_player))
        self.moves.append(Move(player, self.board.player1, self.board.player2, move_index))
        self.do_move(player, other_player, 0, move_index, special_case)

    def do_move_internal(self, player, other_player, cur_count, move_index, special_case):
        holes = player.holes + other_player.holes
        move_index = self.skip_piggy(holes, move_index) # Safe
        if cur_count == 0:
            cur_count = holes[move_index].count
            holes[move_index].count = 0
            move_index = self.get_next_move_index(holes, move_index)
            return False, 0, cur_count, move_index


        to_claim = 0
        holes[move_index].count += cur_count if special_case else 1
        cur_count -= cur_count if special_case else 1
        move_index = self.get_next_move_index(holes, move_index)
        if cur_count == 0 and holes[move_index].count == 0:
            to_claim = self.claim_hole(holes, move_index)
            return True, to_claim, cur_count, None
        return False, to_claim, cur_count, move_index

    def do_move(self, player, other_player, cur_count, move_index, special_case):
        turn_done = False
        while not turn_done:
            turn_done, claim_count, cur_count, move_index = self.do_move_internal(player, other_player, cur_count, move_index, special_case)
            player.claim_holes()
            other_player.claim_holes()
            #self.board.display()
            if turn_done:
                #print(f"{player.name} claims {claim_count} coins!\n")
                player.count += claim_count
                #self.board.display()
