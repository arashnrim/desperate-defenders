from datetime import datetime
import json
import random
import re
import os


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
    "threat_level": 0,
    "danger_level": 1,
    "target": 20,
    "killed": 0,
    "gold": 10
}

# A redundant copy of game_variables, in case game_variables has been
# amended but needs to revert back to the original values (i.e., on
# loading a corrupted saved game).
redundant_game_variables = game_variables.copy()

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


def spawn_enemy(override=False):
    """Spawns a random enemy in any row of the last column.
    Depends on spawn_entity().

    Parameters:
        override (bool): If True, spawns an enemy in the last column of
        the last row regardless of the current circumstances."""
    no_enemies = True
    for row in field:
        for cell in row:
            if cell != {} and cell["type"] == "enemy":
                no_enemies = False

    if no_enemies or override:
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
                            print("{} dies!".format(entity_ahead["name"]))
                            game_variables["gold"] += entity_ahead["reward"]
                            game_variables["killed"] += 1
                            game_variables["threat_level"] += entity_ahead["reward"]
                            field[r_index][ahead_col] = {}
                        break

            # Advances the enemies; the code below advances the enemies
            # and performs any attacks that are expected of the enemies.
            elif entity != {} and entity["type"] == "enemy":
                resulting_col = c_index - entity["moves"]
                future_cell = field[r_index][resulting_col]
                ahead_cell = field[r_index][c_index - 1]

                no_defense = True
                for cell_index in range(resulting_col, c_index):
                    if field[r_index][cell_index] != {} and field[r_index][cell_index]["type"] == "player":
                        no_defense = False
                        break

                if resulting_col < 0 and no_defense:
                    end_game(entity)
                else:
                    damage = random.randint(
                        entity["min_damage"], entity["max_damage"])

                    # Checks if the cell in front of the enemy is occupied
                    # by a defence entity. If so, the enemy attacks that
                    # entity instead.
                    if ahead_cell != {} and ahead_cell["type"] == "player":
                        ahead_cell["current_health"] -= damage

                        print("{} in lane {} bites {} for {} damage!".format(
                            entity["name"], chr(65 + r_index), ahead_cell["name"], damage))

                        if ahead_cell["current_health"] <= 0:
                            print("{} dies!".format(ahead_cell["name"]))
                            field[r_index][c_index - 1] = entity
                            print("{} advances!".format(entity["name"]))
                            field[r_index][c_index] = {}
                    # Checks if the cell the enemy wishes to occupy is
                    # empty; if not, there is another entity in the way.
                    elif future_cell != {}:
                        future_cell["current_health"] -= damage

                        print("{} in lane {} bites {} for {} damage!".format(
                            entity["name"], chr(65 + r_index), future_cell["name"], damage))

                        # TODO: Is there a way to merge the two below? They do the same thing!
                        if future_cell["current_health"] <= 0:
                            print("{} dies!".format(future_cell["name"]))
                            field[r_index][resulting_col] = entity
                            print("{} advances!".format(entity["name"]))
                            field[r_index][c_index] = {}
                    else:
                        field[r_index][resulting_col] = entity
                        print("{} advances!".format(entity["name"]))
                        field[r_index][c_index] = {}


def show_stats():
    """Shows the users statistics of the game. Includes the current turn
    number, threat level, danger level, amount of gold, and number of
    monsters killed."""
    stats = ""

    # Adds turn info to stats.
    stats += "Turn {:<2}".format(game_variables["turn"] + 1)
    stats += " " * 5

    # Adds threat level info to stats.
    stats += "Threat = [{:<10}]".format("-" * game_variables["threat_level"])
    stats += " " * 5

    # Adds danger level info to stats.
    stats += "Danger Level {:<2}".format(game_variables["danger_level"])
    stats += "\n"

    # Adds gold info to stats.
    stats += "Gold = {:>2}".format(game_variables["gold"])
    stats += " " * 3

    # Adds killed info to stats.
    stats += "Monsters killed = {}/{}".format(
        game_variables["killed"], game_variables["target"])

    print(stats)


def enhance_enemies():
    """Enhances the enemies in the field and increases the danger level
    by one."""
    print("The evil grows!")
    for row in field:
        for cell in row:
            if cell != {} and cell["type"] == "enemy":
                for stat in ["min_damage", "max_damage", "reward"]:
                    cell[stat] += 1
    for enemy in CHARACTERS["enemy"]:
        enemy["health"] += 1
    game_variables["danger_level"] += 1


def progress_game(previous_turn=0):
    """Begins all the processes needed to start or progress the game.

    Parameters:
        previous_turn (int): The turn number of the previous game."""
    # Checks if the conditions are met to warrant a win.
    if game_variables["killed"] >= game_variables["target"]:
        print("You have protected the city! You win!")
        exit()

    if game_variables["turn"] > 0 and game_variables["turn"] % 12 == 0:
        enhance_enemies()

    spawn_enemy()
    draw_field()
    show_stats()

    # Gives the player their choices.
    print("1. Buy unit" + " " * 5 + "2. End turn")
    print("3. Save game" + " " * 4 + "4. Quit")
    choice = get_choice(4)

    if choice == 1:
        purchase_defense()
    elif choice == 2:
        game_variables["turn"] += 1
    elif choice == 3:
        saved = save_game()
        if saved:
            print("\nGame saved!")
    elif choice == 4:
        print("\nSee you next time!")
        exit()

    if previous_turn != game_variables["turn"]:
        advance_entities()
        game_variables["gold"] += 1
        game_variables["threat_level"] += random.randint(
            1, game_variables["danger_level"])
        while game_variables["threat_level"] >= 10:
            spawn_enemy(override=True)
            game_variables["threat_level"] -= 10

    progress_game(game_variables["turn"])


####################
# Game restoration and saving functions
# All functions in this chunk handles the logic for saving and restoring
# games.
####################

SAVE_GAME_FILE_NAME = "saved_game.dd"

# def get_file_name() -> str:
#     """Prompts the user for a string to a valid file name and re-prompts
#     them until a valid file name (that exists) is provided.

#     Returns:
#         str: A valid file name.
#     """
#     while True:
#         file_name = input("Enter the file name of your saved game: ")
#         if re.match(r"^[a-zA-Z0-9_]+$", file_name):
#             if file_name in os.listdir():
#                 return file_name
#             else:
#                 print("The saved game does not exist. Try again.", end=" ")
#         else:
#             print("The name of the file should only contain letters, numbers, and underscores. Try again.", end=" ")


def load_game() -> bool:
    """Attempts to restore a saved game.

    Returns:
        bool: True if the game has been restored successfully, False otherwise.
    """
    global game_variables, redundant_game_variables, field, redundant_field
    if not(SAVE_GAME_FILE_NAME in os.listdir()):
        print("No saved game found. If you have it stored somewhere else or named differently, move the file and rename it to \"saved_game.dd\" and try again.")
        return False
    else:
        with open(SAVE_GAME_FILE_NAME, "r") as file:
            data = file.readlines()
            changed = []

            # Restores the game variables.
            variables_restored = True
            stored_game_variables = data[5:data.index("\n", 5)]
            for index, variable in enumerate(stored_game_variables):
                try:
                    key, value = variable.split(",")
                    assert key in game_variables
                except AssertionError:
                    print("Error in line {} ({}): The key {} is not known to the game.".format(
                        5 + index, variable.strip(), key))
                    variables_restored = False
                except ValueError:
                    print("Error in line {} ({}): The game variables are not in the right format.".format(
                        5 + index, variable.strip()))
                    variables_restored = False
                else:
                    value = value.strip()
                    game_variables[key] = int(
                        value) if value.isdigit() else value
            if variables_restored:
                changed.append("Game variables")

            # Restores the field.
            field_restored = True
            saved_field = data[data.index("# Field #\n") + 1:]
            if len(saved_field) != game_variables["rows"]:
                print(
                    "Error in restoring field: The game-set number of rows does not match the saved number of rows.")
                field_restored = False
            else:
                for r_index, row in enumerate(saved_field):
                    row = row.strip().split(";")
                    for c_index, cell in enumerate(row):
                        cell_data = json.loads(cell)
                        field[r_index][c_index] = cell_data
            if field_restored:
                changed.append("Field")

            if len(changed) != 2:
                print(
                    "\n[!] Some data could not be restored. The game may be in an inconsistent state.")
                print("The following have been fully restored, though:")
                for change in changed:
                    print("- {}".format(change))

                confirm = input(
                    "Start a new game? Your data will be preserved in a separate file for you to investigate. (y/N) ")
                if confirm.lower() == "y":
                    preserved_file_name = datetime.now().strftime("%Y%m%d-%H%M%S") + ".dd"
                    with open(preserved_file_name, "w") as preserved_file:
                        preserved_file.writelines(data)
                    os.remove(SAVE_GAME_FILE_NAME)

                    game_variables = redundant_game_variables.copy()
                    field = [[{}] * game_variables["columns"]
                             for _ in range(game_variables["rows"])]
                    return True
                else:
                    return False
            else:
                return True


def save_game() -> bool:
    """Saves the game to a file.

    Returns:
        bool: True if the game was saved successfully, False otherwise.
    """
    if SAVE_GAME_FILE_NAME in os.listdir():
        confirm = input("A saved game already exists. Overwrite? (y/N): ")
        if confirm.lower() != "y":
            return False

    with open(SAVE_GAME_FILE_NAME, "w") as file:
        lines = []

        # Writes the headers in the file to identify the file as a saved
        # game.
        lines.extend(["### DESPERATE DEFENDERS SAVE FILE ###",
                     "\nThis file was created by the Desperate Defenders game. Do not change the ", "\nvalues in this file; otherwise, your game may change or be corrupted!"])

        # Writes the game variables to the file.
        lines.append("\n\n# Game variables #")
        for key, value in game_variables.items():
            lines.append("\n{},{}".format(key, value))

        # Writes the field to the file.
        lines.append("\n\n# Field #")
        for row in field:
            row_values = ""
            for c_index, cell in enumerate(row):
                # JSON is practically similar to Python's dictionary
                # format (in this use case). Therefore, we can use the
                # json package to handle reading and writing.
                row_values += json.dumps(cell)
                if c_index != len(row) - 1:
                    row_values += ";"
            lines.append("\n{}".format(row_values))

        # Writes the lines to the file.
        file.writelines(lines)
        return True

####################
# Execution point
# The game begins here.
####################


if __name__ == "__main__":
    display_intro_menu()
    choice = get_choice(3)

    if choice == 1:
        progress_game()
    elif choice == 2:
        loaded = load_game()
        if loaded:
            print("")
            progress_game()
    elif choice == 3:
        exit()
else:
    print("This file is not meant to be imported. Please run this file with `python3`.")
