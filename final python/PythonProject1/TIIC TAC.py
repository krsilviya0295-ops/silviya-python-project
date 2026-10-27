

# ==========================================
# Mini Project: Tic-Tac-Toe Game
# Language: Python 3.x
# Interface: Console (CLI)
# Players: 2
# ==========================================

def display_board(board):
    """Display the Tic-Tac-Toe board."""
    print()
    print("       TIC-TAC-TOE")
    print()
    for row in range(3):
        print("   " + " | ".join(board[row]))
        if row < 2:
            print("  ---+---+---")
    print()


def check_winner(board, mark):
    """Check whether the given mark has won."""
    # Check rows
    for row in board:
        if all(cell == mark for cell in row):
            return True

    # Check columns
    for col in range(3):
        if all(board[row][col] == mark for row in range(3)):
            return True

    # Check diagonals
    if all(board[i][i] == mark for i in range(3)):
        return True

    if all(board[i][2 - i] == mark for i in range(3)):
        return True

    return False


def get_move(board, player, mark):
    """Get and validate the current player's move."""
    while True:
        print(f"Player {player}'s turn ({mark})")

        try:
            position = input(
                "Enter a cell number (1-9): "
            ).strip()

            # Handle empty input
            if position == "":
                print("Input cannot be empty. Try again.")
                continue

            # Handle non-numeric input
            if not position.isdigit():
                print("Please enter a valid number.")
                continue

            position = int(position)

            # Handle out-of-range input
            if position < 1 or position > 9:
                print("Choose a number between 1 and 9.")
                continue

            # Convert cell number to row and column
            row = (position - 1) // 3
            col = (position - 1) % 3

            # Check whether the cell is occupied
            if board[row][col] in ("X", "O"):
                print("That cell is occupied. Try again.")
                continue

            return row, col

        except (ValueError, EOFError):
            print("Invalid input. Please try again.")


def play_game(scores):
    """Run one complete round of Tic-Tac-Toe."""
    # Numbers show available positions
    board = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"]
    ]

    current_player = 1
    marks = {1: "X", 2: "O"}

    while True:
        display_board(board)

        mark = marks[current_player]
        row, col = get_move(board, current_player, mark)

        # Place the player's mark
        board[row][col] = mark

        # Check for a winner
        if check_winner(board, mark):
            display_board(board)
            print(f"Congratulations! Player {current_player} ({mark}) wins!")
            scores[current_player] += 1
            break

        # Check for a draw
        if all(
            cell in ("X", "O")
            for row_data in board
            for cell in row_data
        ):
            display_board(board)
            print("The game is a draw!")
            scores["draws"] += 1
            break

        # Switch players
        current_player = 2 if current_player == 1 else 1


def main():
    """Main function to manage multiple rounds."""
    scores = {1: 0, 2: 0, "draws": 0}

    print("=" * 35)
    print("   WELCOME TO TIC-TAC-TOE!")
    print("=" * 35)
    print("Player 1: X")
    print("Player 2: O")
    print("Select a cell using numbers 1-9.")
    print("The board positions are:")
    print(" 1 | 2 | 3")
    print("---+---+---")
    print(" 4 | 5 | 6")
    print("---+---+---")
    print(" 7 | 8 | 9")

    while True:
        play_game(scores)

        # Display the running score
        print("\n========== SCOREBOARD ==========")
        print(f"Player 1 (X): {scores[1]}")
        print(f"Player 2 (O): {scores[2]}")
        print(f"Draws:        {scores['draws']}")
        print("================================")

        # Ask whether to play again
        while True:
            choice = input(
                "\nWould you like to play again? (yes/no): "
            ).strip().lower()

            if choice in ("yes", "y"):
                break
            elif choice in ("no", "n"):
                print("\nThanks for playing Tic-Tac-Toe!")
                print("Goodbye!")
                return
            else:
                print("Please enter yes or no.")


# Start the program
if __name__ == "__main__":
    main()

