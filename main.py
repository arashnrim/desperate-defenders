import random
import re


def display_intro_menu():
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

CHARACTERS = {
    "player": [
        {
            "id": "ARCHR",
            "name": "Archer",
            "health": 5,
            "min_damage": 1,
            "max_damage": 4,
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

game_variables = {
    "columns": 7,
    "rows": 5,
    "turn": 0,
    "target": 20,
    "killed": 0,
    "alive": 0,
    "gold": 10
}

# This variable keeps track of how the game is played. It is a row by
# column (defined in game_variables) matrix. Cells in the matrix can
# have one of two values:
# - {}: There is nothing occupying the cell.
# - A dict containing the following keys:
#   - id (str): The id of the entity occupying the cell.
#   - type (str): The type of entity occupying the cell.
#       - "player"
#       - "enemy"
#   - current_health (int): The current health of the entity occupying
# the cell.
#   - health (int): The maximum health of the entity occupying the cell.
#   - min_damage (int): The minimum damage the entity can deal.
#   - max_damage (int): The maximum damage the entity can deal.
#   - moves (int): The number of moves the entity can make.
#   - reward (int): The reward the entity gives the player. (if type is
# enemy)
field = [[{}] * game_variables["columns"]
         for _ in range(game_variables["rows"])]


def end_game(catalyst_entity: dict):
    """Ends the game and gives the player guilt. Seriously, how could
    they let this happen?

    Parameters:
        catalyst_entity (dict): The entity that caused the end of the game.
    """
    print("A {} has reached the city! All is lost!".format(
        catalyst_entity["name"]))
    print("You have lost the game. :(")
    exit()


def draw_field():
    """Prints the field in a player-friendly format."""
    print(" ", end="")

    # Dynamically determines the columns the player can play on. This is
    # done by splitting the number of columns and allocating the first
    # half to the player.
    user_columns = game_variables["columns"] // 2
    for column in range(user_columns):
        print(" {:^5}".format(column + 1), end="")
    print()

    for row in range(game_variables["rows"] + 1):
        # Prints the border pattern.
        print(" ", end="")
        print("+-----" * game_variables["columns"] + "+")

        if row < game_variables["rows"]:
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
                for col in range(game_variables["columns"]):
                    cell, value = field[row][col], ""
                    if cell != {} and row_line == 0:
                        value = cell["id"]
                    elif cell != {} and row_line == 1:
                        value = str(
                            cell["current_health"]) + "/" + str(cell["health"])
                    print("|{:^5}".format(value), end="")
                print("|", end="\n" if row_line == 0 else "")
            print()


def spawn_entity(entity: dict, position: tuple) -> bool:
    """Spawns a given entity in the last column in a random row.

    Parameters:
        entity (dict): The entity to spawn.
        position (tuple): The position to spawn the entity, comprised of (row, col).

    Returns:
        bool: True if the entity was spawned, False if not.
    """
    placed_entity = entity.copy()
    placed_entity["type"] = "enemy" if placed_entity in CHARACTERS["enemy"] != -1 else "player"
    placed_entity["current_health"] = placed_entity["health"]

    # Checks if the entity can be spawned in the given position.
    if field[position[0]][position[1]] == {}:
        field[position[0]][position[1]] = placed_entity
        return True
    else:
        return False


def spawn_enemy():
    """Spawns a random enemy in any row of the last column if there are
    no monsters in the grid. Depends on spawn_entity()."""
    no_enemies = True
    for row in field:
        for cell in row:
            if cell != {} and cell["type"] == "enemy":
                no_enemies = False

    if no_enemies:
        enemy = random.choice(CHARACTERS["enemy"])
        position = (random.randint(
            0, game_variables["rows"] - 1), game_variables["columns"] - 1)
        spawn_entity(enemy, position)


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
            # Checks if the provided row and col values are valid.
            row, col = position[0].upper(), int(position[1:])
            if ord(row) - 65 <= game_variables["rows"] and col - 1 <= game_variables["columns"] // 2:
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
            if game_variables["gold"] - defenses[choice - 1]["cost"] >= 0:
                game_variables["gold"] -= defenses[choice - 1]["cost"]
                position = get_position()
                if spawn_entity(defenses[choice - 1], position):
                    game_variables["gold"] -= defenses[choice - 1]["cost"]
                    game_variables["turn"] += 1
                else:
                    print("Failed to place unit. Is something already there?")
                break
            else:
                print("Not enough coins!")
        else:
            break


def advance_entities():
    """Performs all the logical code to advance the round, including
    performing damage calculations and advancing enemies."""
    for r_index in range(len(field)):
        for c_index in range(game_variables["columns"]):
            entity = field[r_index][c_index]

            # Activates the archers; the code below performs the
            # attacking in a way that is expected of the archers.
            if entity != {} and entity["id"] == "ARCHR":
                for ahead_col in range(c_index + 1, game_variables["columns"]):
                    # Checks the first entity that lies in front of the
                    # archer that is an enemy, and deals damage to it.
                    entity_ahead = field[r_index][ahead_col]
                    if entity_ahead != {} and entity_ahead["type"] == "enemy":
                        damage = random.randint(
                            entity["min_damage"], entity["max_damage"])
                        entity_ahead["current_health"] -= damage

                        print("{} in lane {} shoots {} for {} damage!".format(
                            entity["name"], chr(65 + r_index), entity_ahead["name"], damage))

                        if entity_ahead["current_health"] <= 0:
                            game_variables["gold"] += entity_ahead["reward"]
                            field[r_index][ahead_col] = {}
                        break

            # Advances the enemies; the code below advances the enemies
            # and performs any attacks that are expected of the enemies.
            elif entity != {} and entity["type"] == "enemy":
                resulting_col = c_index - entity["moves"]
                future_cell = field[r_index][resulting_col]
                if resulting_col >= 0:
                    # Checks if the cell the enemy wishes to occupy is
                    # empty; if not, there is another entity in the way.
                    if future_cell != {}:
                        damage = random.randint(
                            entity["min_damage"], entity["max_damage"])
                        future_cell["current_health"] -= damage

                        print("{} in lane {} bites {} for {} damage!".format(
                            entity["name"], chr(65 + r_index), future_cell["name"], damage))

                        # TODO: Is there a way to merge the two below? They do the same thing!
                        if future_cell["current_health"] <= 0:
                            field[r_index][resulting_col] = entity
                            print("{} advances!".format(entity["name"]))
                            field[r_index][c_index] = {}
                    else:
                        field[r_index][resulting_col] = entity
                        print("{} advances!".format(entity["name"]))
                        field[r_index][c_index] = {}
                else:
                    end_game(entity)


def display_game(previous_turn=0):
    """Begins all the processes needed to start or progress the game.

    Parameters:
        previous_turn (int): The turn number of the previous game."""
    draw_field()

    # Gives the player their choices.
    print("1. Buy unit" + " " * 5 + "2. End turn")
    print("3. Save game" + " " * 4 + "4. Quit")
    choice = get_choice(4)

    if choice == 1:
        # TODO: Implement purchasing
        purchase_defense()
    elif choice == 2:
        # TODO: Advance the round
        game_variables["turn"] += 1
    elif choice == 3:
        # TODO: Save the game
        pass
    elif choice == 4:
        print("\nSee you next time!")
        exit()

    if previous_turn != game_variables["turn"]:
        game_variables["gold"] += 1
        spawn_enemy()
        advance_entities()

    display_game(game_variables["turn"])

####################
# Execution point
# The game begins here.
####################


if __name__ == "__main__":
    display_intro_menu()
    choice = get_choice(3)

    if choice == 1:
        spawn_enemy()
        display_game()
    elif choice == 2:
        # TODO: Restore and continue a saved game
        pass
    elif choice == 3:
        exit()
else:
    print("This file is not meant to be imported. Please run this file with `python3`.")
