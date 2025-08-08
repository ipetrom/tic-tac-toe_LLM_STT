class TicTacToeBoard:
    def __init__(self):
        # Plansza 3x3, puste pola oznaczone jako None
        self.board = [[None for _ in range(3)] for _ in range(3)]

    def make_move(self, player: str, row: int, col: int) -> bool:
        """
        Próbuje wykonać ruch. Zwraca True jeśli ruch poprawny, False jeśli pole zajęte.
        """
        if self.board[row][col] is None:
            self.board[row][col] = player
            return True
        return False

    def check_winner(self) -> str | None:
        """
        Sprawdza czy jest zwycięzca. Zwraca 'X', 'O' lub None.
        """
        # Sprawdź wiersze i kolumny
        for i in range(3):
            # Wiersz
            if self.board[i][0] == self.board[i][1] == self.board[i][2] and self.board[i][0] is not None:
                return self.board[i][0]
            # Kolumna
            if self.board[0][i] == self.board[1][i] == self.board[2][i] and self.board[0][i] is not None:
                return self.board[0][i]
        # Przekątne
        if self.board[0][0] == self.board[1][1] == self.board[2][2] and self.board[0][0] is not None:
            return self.board[0][0]
        if self.board[0][2] == self.board[1][1] == self.board[2][0] and self.board[0][2] is not None:
            return self.board[0][2]
        return None

    def is_full(self) -> bool:
        """
        Sprawdza czy plansza jest pełna (remis).
        """
        return all(all(cell is not None for cell in row) for row in self.board)

    def reset(self):
        """
        Resetuje planszę do stanu początkowego.
        """
        self.board = [[None for _ in range(3)] for _ in range(3)]

    def get_state(self) -> list[list[str | None]]:
        """
        Zwraca aktualny stan planszy.
        """
        return self.board
    
    def get_display(self) -> str:
        """
        Zwraca wizualną reprezentację planszy jako string.
        """
        display = ""
        for i, row in enumerate(self.board):
            row_display = " | ".join(cell if cell is not None else " " for cell in row)
            display += row_display + "\n"
            if i < 2:
                display += "---------\n"
        return display    