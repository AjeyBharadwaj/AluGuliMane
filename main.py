from board import StandardBoard, Game
from player import Player, IntelligentPlayer, DumbPlayer

if __name__ == "__main__":
    for i in range(0, 10):
        player1 = IntelligentPlayer("Alice", count=35)
        player2 = DumbPlayer("Bob", count=35)
        board = StandardBoard(player1, player2)
        game = Game(board)
        game.play(player1, player2)

        print(f"It took {len(game.moves)} moves to finish the game.")

    pass