import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.game_logic import TicTacToeBoard  

board1 = TicTacToeBoard()#

board1.make_move('X', 0, 0)
board1.make_move('O', 1, 1)
board1.make_move('X', 0, 1)
board1.make_move('O', 2, 2)
board1.make_move('X', 0, 2)

winner = board1.check_winner()
#print(f'Zwycięzca: {winner}') 

#board1.reset()
#print(board1.get_state())

def main():
    game = TicTacToeBoard()
    current_player = "X"

    print("Witaj w grze Kółko-Krzyżyk!")
    
    while True:
        print(game.get_display())
        print(f"Ruch gracza {current_player}")
        
        try:
            row = int(input("Podaj wiersz (0-2): "))
            col = int(input("Podaj kolumnę (0-2): "))
        except ValueError:
            print("Podaj liczby!")
            continue

        if row not in range(3) or col not in range(3):
            print("Niepoprawne współrzędne! Spróbuj jeszcze raz.")
            continue

        if not game.make_move(current_player, row, col):
            print("To pole jest już zajęte! Spróbuj jeszcze raz.")
            continue

        winner = game.check_winner()
        if winner:
            print(game.get_display())
            print(f"Gracz {winner} wygrał! 🎉")
            break

        if game.is_full():
            print(game.get_display())
            print("Remis! 🟰")
            break

        # Zmiana gracza
        current_player = "O" if current_player == "X" else "X"

if __name__ == "__main__":
    main()
