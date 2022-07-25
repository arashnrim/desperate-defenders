from random import randint


def display_intro_menu() -> int:
    """Displays the menu to the user to start or restore a game."""
    for line in ["Desperate Defenders", "-" * 19, "Defend the city from undead monsters!", ""]:
        print(line)
    for index, line in enumerate(["Start a new game", "Load saved game", "Quit"]):
        print("{}. {}".format(index + 1, line))


def get_choice(upper_bound: int, lower_bound=1, val_error_message="Your choice should be numeric.") -> int:
    """Prompts the user for a numeric choice and re-prompts them until
    a valid choice is provided.

    Parameters:
        upper_bound (int): The upper bound of the range of valid choices.
        lower_bound (int): The lower bound of the range of valid choices.
        val_error_message (str): The message to display if the user's choice is not valid (returns a ValueError).

    Returns:
        int: The user's choice.
    """
    while True:
        try:
            choice = int(input("Your choice? "))
            assert lower_bound <= choice <= upper_bound
        except ValueError:
            print(val_error_message, end=" ")
        except AssertionError:
            print("Your choice should be between {} and {} (inclusive).".format(
                lower_bound, upper_bound), end=" ")
        else:
            return choice


####################
# Game functions
# All functions in this chunk handles the logic for executing the game.
####################
GAME_VARIABLES = {
    "columns": 7,
    "rows": 5,
    "turn": 0,
    "target": 20,
    "killed": 0,
    "alive": 0,
    "gold": 10
}

CHARACTERS = {
    "player": [
        {
            "id": "ARCHR",
            "name": "Archer",
            "health": 5,
            "min_damage": 1,
            "max_damage": 5,
            "cost": 5
        },
        {
            "id": "WALL",
            "name": "Wall",
            "health": 20,
            "min_damage": 0,
            "max_damage": 0,
            "cost": 3
        }
    ],
    "enemy": [
        {
            "id": "ZOMBI",
            "name": "Zombie",
            "health": 15,
            "min_damage": 3,
            "max_damage": 6,
            "moves": 1,
            "reward": 2
        }
    ]
}

# Creates a rows by columns matrix of empty dictionaries. The matrix is
# used to store the locations of the player's units and the enemies.
grid = [[{}] * GAME_VARIABLES["columns"]
        for _ in range(GAME_VARIABLES["rows"])]


def print_grid():
    """Prints the map in a player-friendly format."""

    # Prints the alphabetical columns the player can play on.
    print(" ", end="")
    user_columns = GAME_VARIABLES["columns"] // 2
    for column in range(user_columns):
        print(" {:^5}".format(column + 1), end="")
    print()

    for row in range(GAME_VARIABLES["rows"] + 1):
        # Prints the border pattern.
        print(" ", end="")
        print("+-----" * GAME_VARIABLES["columns"] + "+")

        if row < GAME_VARIABLES["rows"]:
            # Prints the row alphabet.
            print("{}".format(chr(65 + row)), end="")

            # Iterates twice, one for each line the row occupies.
            for row_line in range(2):
                if row_line == 1:
                    print(" ", end="")
                # Iterates through each cell, filling the cell with
                # either the name of the entity or the health of the
                # entity depending on which row line it is. If no entity
                # is present, an empty space is printed instead.
                for col in range(GAME_VARIABLES["columns"]):
                    if grid[row][col] == {}:
                        print("|{:^5}".format(""), end="")
                    else:
                        if row_line == 0:
                            print("|{:^5}".format(
                                grid[row][col]["id"]), end="")
                        elif row_line == 1:
                            print("|{:^5}".format(
                                str(grid[row][col]["current_health"]) + "/" + str(grid[row][col]["health"])), end="")
                print("|", end="\n" if row_line == 0 else "")
            print()
        else:


def display_game():
    """Begins all the processes needed to start or progress the game."""

    # Spawns a random enemy if the game has just begun.
    if GAME_VARIABLES["turn"] == 0:
        row = randint(0, GAME_VARIABLES["rows"] - 1)
        spawn_entity(CHARACTERS["enemy"][0],
                     (row, GAME_VARIABLES["columns"] - 1))

    print_grid()

    # Gives the player their choices.
    print("1. Buy unit" + " " * 5 + "2. End turn")
    print("3. Save game" + " " * 4 + "4. Quit")
    choice = get_choice(4)

    if choice == 1:
        # TODO: Implement purchasing
        pass
    elif choice == 2:
        # TODO: Advance the round
        pass
    elif choice == 3:
        # TODO: Save the game
        pass
    elif choice == 4:
        # TODO: Exit
        pass


####################
# Execution point
# The game begins here.
####################

if __name__ == "__main__":
    display_intro_menu()
    choice = get_choice(3)

    if choice == 1:
        # TODO: Start a new game
        display_game()
        pass
    elif choice == 2:
        # TODO: Restore and continue a saved game
        pass
    elif choice == 3:
        exit()
else:
    print("This file is not meant to be imported. Please run this file with `python3`.")
