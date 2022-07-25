from random import randint
import re


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


def spawn_entity(entity, position):
    """Spawns a given entity in the last column in a random row.

    Parameters:
        entity (dict): The entity to spawn.
        position (tuple): The position to spawn the entity, comprised of (row, col).

    Returns:
        bool: True if the entity was spawned, False if not.
    """
    entity["current_health"] = entity["health"]

    # Checks if the entity can be spawned in the given position.
    if grid[position[0]][position[1]] == {}:
        grid[position[0]][position[1]] = entity
        return True
    else:
        return False


def get_position() -> tuple:
    """Prompts the user for a position and re-prompts them until
    a valid position is provided.

    Returns:
        tuple: The user-provided position, comprised of (row, col).
    """
    while True:
        try:
            position = input("Place where? ")
            assert re.match(r"[A-Za-z]\d{1,2}", position)
        except AssertionError:
            print(
                "Please provide the position in the format XY (X is an alphabet, Y is a numeral).", end=" ")
        else:
            # # Checks if the provided row and col values are valid.
            row, col = position[0].upper(), int(position[1:])
            if ord(row) - 65 <= GAME_VARIABLES["rows"] and col - 1 <= GAME_VARIABLES["columns"] // 2:
                return ord(row) - 65, col - 1
            else:
                # TODO: Make less ambiguous statements
                print("Please provide a valid position.", end=" ")


def purchase_defense():
    """Prompts the player to purchase a defense unit."""
    defenses = CHARACTERS["player"]

    print("What unit do you wish to buy?")
    for index in range(len(defenses) + 1):
        if index < len(defenses):
            print("{}. {} ({} gold)".format(
                index + 1, defenses[index]["name"], defenses[index]["cost"]))
        else:
            print("{}. Don't buy".format(index + 1))

    while True:
    choice = get_choice(len(defenses) + 1)
    if choice != len(defenses) + 1:
            if GAME_VARIABLES["gold"] - defenses[choice - 1]["cost"] >= 0:
                GAME_VARIABLES["gold"] -= defenses[choice - 1]["cost"]
        position = get_position()
        if spawn_entity(defenses[choice - 1], position):
            GAME_VARIABLES["gold"] -= defenses[choice - 1]["cost"]
            GAME_VARIABLES["turn"] += 1
        else:
            print("Failed to place unit. Is something already there?")
                break
            else:
                print("Not enough coins!")
        else:
            break

    display_game()


def display_game(previous_turn=0):
    """Begins all the processes needed to start or progress the game.

    Parameters:
        previous_turn (int): The turn number of the previous game."""
    print_grid()

    # Gives the player their choices.
    print("1. Buy unit" + " " * 5 + "2. End turn")
    print("3. Save game" + " " * 4 + "4. Quit")
    choice = get_choice(4)

    if choice == 1:
        # TODO: Implement purchasing
        purchase_defense()
    elif choice == 2:
        # TODO: Advance the round
        GAME_VARIABLES["turn"] += 1
    elif choice == 3:
        # TODO: Save the game
        pass
    elif choice == 4:
        # TODO: Exit
        pass

    if previous_turn != GAME_VARIABLES["turn"]:
        # spawn_enemy()
        advance_entities()

    display_game(GAME_VARIABLES["turn"])

####################
# Execution point
# The game begins here.
####################


if __name__ == "__main__":
    display_intro_menu()
    choice = get_choice(3)

    if choice == 1:
        # TODO: Start a new game
        spawn_enemy()
        display_game()
        pass
    elif choice == 2:
        # TODO: Restore and continue a saved game
        pass
    elif choice == 3:
        exit()
else:
    print("This file is not meant to be imported. Please run this file with `python3`.")
