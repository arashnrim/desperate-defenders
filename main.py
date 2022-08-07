# Programming I
# Assignment
# Arash Nur Iman (REDACTED, REDACTED)
# Last updated on 7 August 2022

# Desperate Defenders is a tower defense game where the player defends
# a city from undead monsters. Tasked with several defense entities to
# fight against incoming waves of enemies, the player has to plan and
# play the game strategically in order to win.

import json
import os
import random
import re
from datetime import datetime
from math import inf
from textwrap import wrap
from typing import Union


def display_intro_menu():
    """Displays the menu to the user to start or restore a game."""
    for line in ["Desperate Defenders", "-" * 19, "Defend the city from undead monsters!", ""]:
        print(line)

    # Prints a warning to the user if their terminal height or width may
    # be too small to display the game properly.
    columns, lines = os.get_terminal_size()
    if lines < 21:
        print("Your terminal height may be too small to display the game properly. Please adjust your terminal size for the best experience!")
    if columns < 80:
        print("Your terminal width may be too small to display the game properly. Please adjust your terminal size for the best experience!")
    if lines < 21 or columns < 80:
        print()

    for index, line in enumerate(["Start a new game", "Load saved game", "Manage game variables", "Quit"]):
        print("{}. {}".format(index + 1, line))


def get_choice(upper_bound: int, lower_bound=1, message="Your choice? ", val_error_message="Your choice should be numeric.") -> int:
    """Prompts the user for a numeric choice and re-prompts them until
    a valid choice is provided.

    Parameters:
        upper_bound (int): The upper bound of the range of valid choices.
        lower_bound (int): The lower bound of the range of valid choices.
        message (str): The message to display to the player.
        val_error_message (str): The message to display if the player's choice is not valid (returns a ValueError).

    Returns:
        int: The user's choice.
    """
    while True:
        try:
            choice = int(input(message))
            assert lower_bound <= choice <= upper_bound
        except ValueError:
            print(val_error_message, end=" ")
        except AssertionError:
            print("Your choice should be between {} and {} (inclusive).".format(
                lower_bound, upper_bound), end=" ")
        else:
            return choice


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
        },
        {
            "id": "CANON",
            "name": "Cannon",
            "health": 8,
            "min_damage": 3,
            "max_damage": 5,
            "cost": 7
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
        },
        {
            "id": "WWOLF",
            "name": "Werewolf",
            "health": 10,
            "min_damage": 1,
            "max_damage": 4,
            "moves": 2,
            "reward": 3
        },
        {
            "id": "SKELE",
            "name": "Skeleton",
            "health": 10,
            "min_damage": 1,
            "max_damage": 3,
            "moves": 1,
            "reward": 3
        },
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

####################
# Settings functions
# All functions in this chunk handles the logic for displaying and editing
# the game settings.
####################


def manage_game_settings():
    """Displays the menu with the game settings, and allows the player
    to alter the game settings."""
    global field

    for line in ["Game settings", "-" * 19]:
        print(line)

    pretty_titles = ["Columns", "Rows", "Initial threat level",
                     "Initial danger level", "Target", "Initial gold"]
    pretty_descriptions = ["The number of columns in the game.",
                           "The number of rows in the game.",
                           "The initial threat level. Only values between 1 and 10 are valid, and a value of 10 will automatically spawn another enemy when the game begins.", "The initial danger level. This affects how fast the threat level fills up; the higher the danger level, the higher possibility of the threat level filling up faster.",
                           "The number of monsters to defeat to consider a win.",
                           "The amount of gold the game starts with."
                           ]
    variables = ["columns", "rows", "threat_level",
                 "danger_level", "target", "gold"]
    for index, variable in enumerate(variables):
        print("\n{}. {:<69} {} {}".format(index + 1, pretty_titles[index], game_variables[variable],
              "" if game_variables[variable] == redundant_game_variables[variable] else "[{}]".format(redundant_game_variables[variable])))
        for wrapped_line in wrap(pretty_descriptions[index], width=72):
            print(wrapped_line)
    print("\n{}. Back to main menu".format(len(variables) + 1))

    # Declares the restrictions values can have; used together with the
    # for loop below to replace repetitive lines of if-elifs.
    restrictions = [None, None, (1, 10), (1, 10), None, None]

    choice = get_choice(len(variables) + 1)
    if choice == len(variables) + 1:
        return

    # Technically a replacement for an if-elif statement spanning all
    # the cases. This is to save a little more space (if-elifs
    # continuously don't look that good) and also make the program
    # adaptable (if more variables are added in the future, the program
    # cater to them).
    for index in range(len(variables)):
        if choice == index + 1:
            print("\nNow changing {}; current value is {}.".format(
                pretty_titles[index].lower(), game_variables[variables[index]]))
            if restrictions[index] is None:
                game_variables[variables[index]] = get_choice(
                    inf, message="What value would you like to give this variable? ")

                # Handles special cases where the field needs to be
                # redeclared if the columns (index 0) or rows (index 1)
                # are changed.
                if index == 0 or index == 1:
                    field = [[{}] * game_variables["columns"]
                             for _ in range(game_variables["rows"])]
            else:
                game_variables[variables[index]] = get_choice(
                    restrictions[index][1], lower_bound=restrictions[index][0], message="What value would you like to give this variable? ")
            break

    print()
    manage_game_settings()

####################
# Game restoration and saving functions
# All functions in this chunk handles the logic for saving and restoring
# games.
####################


SAVE_GAME_FILE_NAME = "saved_game.dd"


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
                field = [[{}] * game_variables["columns"]
                         for _ in range(game_variables["rows"])]
                for r_index, row in enumerate(saved_field):
                    row = row.strip().split(";")
                    for c_index, cell in enumerate(row):
                        cell_data = json.loads(cell)
                        field[r_index][c_index] = cell_data
            if field_restored:
                changed.append("Field")

            # Checks if the program has encountered any issue while
            # restoring the game. If so, the program prompts the user
            # to see if they'd like to start a new game; if so, the
            # save file is renamed and a new game will begin. Otherwise,
            # the program will end.
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

                    # Restores game_variables and field using the
                    # redundant variable and recreating the field.
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
# Game functions
# All functions in this chunk handles the logic for executing the game.
####################


def end_game(type: str, catalyst_entity=None):
    """Ends the game in different ways, depending on the given type
    (expecting either a type value of \"win\" or \"loss\").

    Depending on the given type, this function handles the printing of
    the required text and ends the program.

    Parameters:
        type (str): The type of end game to perform.
        catalyst_entity (dict): The entity that caused the end of the
        game. Expected only if type is \"loss\".
    """
    if type == "win":
        print("You have protected the city! You win!")
    elif type == "loss":
        print("A {} has reached the city! All is lost!".format(
            catalyst_entity["name"]))
        print("You have lost the game. :(")
    exit()


def get_position(message="Place where?") -> Union[tuple, None]:
    """Prompts the user for a position and re-prompts them until
    a valid position is provided.

    Parameters:
        message (str): The message to display to the player. The message
        should be whitespace-stripped (no trailing whitespaces).

    Returns:
        tuple: The user-provided position, comprised of (row, col).
    """
    while True:
        try:
            position = input("{} Type X to cancel. ".format(message))
            assert re.match(
                r"([A-Za-z]\d{1,2})|[Xx]", position), "Please provide the position in the format XY (where X is an alphabet, Y is a numeral)."

            # Checks if the provided row and col values are valid.
            row, col = position[0].upper(), int(position[1:])
            assert 0 <= ord(row) - 65 <= game_variables["rows"] - 1, "Please provide a valid row between A and {}.".format(
                chr(65 + game_variables["rows"]))
            assert col <= game_variables["columns"] // 2, "Please provide a valid column between 1 and {}.".format(
                game_variables["columns"] // 2)
        except KeyboardInterrupt:
            print()
            break
        except AssertionError as error:
            print(error, end=" ")
        else:
            # Checks if the user cancelled the placement.
            if position.lower() == "x":
                return None

            return ord(row) - 65, col - 1


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
    """Spawns a provided entity at the provided position.

    This function also handles the logic validating if a placement is
    possible; if not (such as when an entity is in the way, or some
    other problem that would forbid the placement of the entity), this
    function handles that by returning False. Otherwise, it returns True.

    Parameters:
        entity (dict): The entity to spawn.
        position (tuple): The position to spawn the entity, comprised of (row, col).

    Returns:
        bool: True if the entity was spawned, False if not.
    """
    placed_entity = entity.copy()
    if placed_entity in CHARACTERS["enemy"]:
        placed_entity["type"] = "enemy"
    elif placed_entity in CHARACTERS["player"]:
        placed_entity["type"] = "player"
        placed_entity["upgrade_count"] = 0
    placed_entity["current_health"] = placed_entity["health"]

    # Checks if the entity can be spawned in the given position.
    if field[position[0]][position[1]] == {}:
        field[position[0]][position[1]] = placed_entity
        return True
    else:
        return False


def spawn_enemy(override=False):
    """Spawns a random enemy in any row of the last column. Depends on
    spawn_entity().

    By default, an enemy will only be spawned when there are no more
    enemies on the board. In some special cases though, like when the
    threat level surpases the limit, an override can be used to spawn
    the enemy regardless of the state of the field.

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
                if position is None:
                    break
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

            # Activates the defense entities; the code below performs
            # the attacking in a way that is expected of the
            # entities.
            if entity != {} and entity["id"] in ["ARCHR", "CANON"]:
                for ahead_col in range(c_index + 1, game_variables["columns"]):
                    # Checks the first entity that lies in front of the
                    # defense entity that is an enemy, and deals damage
                    # to it. Additional checks are done to also check if
                    # the turn is even (for the cannon).
                    entity_ahead = field[r_index][ahead_col]
                    if (entity["id"] in ["ARCHR", "SKELE"] or (entity["id"] == "CANON" and game_variables["turn"]) % 2) and (entity_ahead != {} and entity_ahead["type"] == "enemy"):
                        damage = random.randint(
                            entity["min_damage"], entity["max_damage"])
                        # Manages the additional case where skeletons
                        # take half the damage from archers.
                        if entity_ahead["id"] == "SKELE" and entity["id"] == "ARCHR":
                            damage = damage // 2
                        entity_ahead["current_health"] -= damage

                        print("[>] {} in lane {} shoots {} for {} damage!".format(
                            entity["name"], chr(65 + r_index), entity_ahead["name"], damage))

                        if entity_ahead["current_health"] <= 0:
                            print("[>] {} dies!".format(entity_ahead["name"]))
                            game_variables["gold"] += entity_ahead["reward"]
                            game_variables["killed"] += 1
                            game_variables["threat_level"] += entity_ahead["reward"]
                            field[r_index][ahead_col] = {}
                        elif entity["id"] == "CANON" and ahead_col + 1 < len(field[r_index]):
                            # Checks if the entity can be moved back by
                            # a cell. If a random choice is true, the
                            # entity may be moved back.
                            if field[r_index][ahead_col + 1] == {} and random.choice([True, False]):
                                field[r_index][ahead_col + 1] = entity_ahead
                                field[r_index][ahead_col] = {}
                                print("[>] {} was blasted back by the cannon!".format(
                                    entity_ahead["name"]))
                                break
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
                    end_game("loss", catalyst_entity=entity)
                else:
                    damage = random.randint(
                        entity["min_damage"], entity["max_damage"])

                    # Checks if the cell in front of the enemy is occupied
                    # by a defence entity. If so, the enemy attacks that
                    # entity instead.
                    if ahead_cell != {} and ahead_cell["type"] == "player":
                        ahead_cell["current_health"] -= damage

                        print("[<] {} in lane {} bites {} for {} damage!".format(
                            entity["name"], chr(65 + r_index), ahead_cell["name"], damage))

                        if ahead_cell["current_health"] <= 0:
                            print("[<] {} dies!".format(ahead_cell["name"]))
                            field[r_index][c_index - 1] = entity
                            print("[<] {} advances!".format(entity["name"]))
                            field[r_index][c_index] = {}
                    # Checks if the cell the enemy wishes to occupy is
                    # empty; if not, there is another entity in the way.
                    elif future_cell != {}:
                        future_cell["current_health"] -= damage

                        print("[<] {} in lane {} bites {} for {} damage!".format(
                            entity["name"], chr(65 + r_index), future_cell["name"], damage))

                        # TODO: Is there a way to merge the two below? They do the same thing!
                        if future_cell["current_health"] <= 0:
                            print("[<] {} dies!".format(future_cell["name"]))
                            field[r_index][resulting_col] = entity
                            print("[<] {} advances!".format(entity["name"]))
                            field[r_index][c_index] = {}
                    else:
                        field[r_index][resulting_col] = entity
                        print("[<] {} advances!".format(entity["name"]))
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
    by one.

    The enhancement to health only affects future enemies; current
    enemies on the field are not affected when an enhancement takes
    place.
    """
    print("The evil grows!")
    for row in field:
        for cell in row:
            if cell != {} and cell["type"] == "enemy":
                for stat in ["min_damage", "max_damage", "reward"]:
                    cell[stat] += 1
    for enemy in CHARACTERS["enemy"]:
        enemy["health"] += 1
    game_variables["danger_level"] += 1


def enhance_defense():
    """Enhances the selected defense in the field. The enhancement can
    only be applied to archers and walls, and enhancements to both are
    as follows:
    - Archers: min_damage + 1, max_damage + 1, health + 1
    - Walls: health + 5

    It is assumed that, as with enemies being advanced, enhancing
    defense does not advance the game by a turn.
    """
    position = get_position("Upgrade which cell?")
    if position is None:
        return

    # Checks if the entity at the given position is a valid entity.
    row, col = position
    entity = field[row][col]
    message = ""
    if entity == {}:
        message = "There is no entity in lane {}, column {}!"
    elif entity["type"] == "enemy":
        message = "The entity in lane {}, column {} is an enemy!"
    elif entity["id"] not in ["ARCHR", "WALL"]:
        message = "The entity in lane {}, column {} is not an archer or a wall! It cannot be upgraded."

    if message != "":
        print(message.format(chr(65 + row), col + 1))
    else:
        stats = []
        value = 0
        if entity["id"] == "ARCHR":
            if game_variables["gold"] < 8 + 2 * entity["upgrade_count"]:
                print("You do not have enough gold to upgrade this archer!")
                return

            stats = ["min_damage", "max_damage", "current_health", "health"]
            value = 1
            game_variables["gold"] -= 8 + 2 * entity["upgrade_count"]
        elif entity["id"] == "WALL":
            if game_variables["gold"] < 6 + 2 * entity["upgrade_count"]:
                print("You do not have enough gold to upgrade this wall!")
                return

            stats = ["current_health", "health"]
            value = 5
            game_variables["gold"] -= 6 + 2 * entity["upgrade_count"]

        for stat in stats:
            entity[stat] += value

        print("{} in lane {}, column {} upgraded!".format(
            entity["name"], chr(65 + row), col + 1))


def progress_game(previous_turn=0):
    """Begins all the processes needed to start or progress the game.

    Parameters:
        previous_turn (int): The turn number of the previous game."""
    # Checks if the conditions are met to warrant a win.
    if game_variables["killed"] >= game_variables["target"]:
        end_game("win")

    if game_variables["turn"] > 0 and game_variables["turn"] % 12 == 0:
        enhance_enemies()

    spawn_enemy()
    draw_field()
    show_stats()

    # Gives the player their choices.
    print("1. Buy unit" + " " * 5 + "2. Upgrade unit")
    print("3. End turn" + " " * 5 + "4. Save game")
    print("5. Quit")
    choice = get_choice(5)

    if choice == 1:
        purchase_defense()
    elif choice == 2:
        enhance_defense()
    elif choice == 3:
        game_variables["turn"] += 1
    elif choice == 4:
        saved = save_game()
        if saved:
            print("\nGame saved!")
    elif choice == 5:
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
# Execution point
# The game begins here.
####################

if __name__ == "__main__":
    while True:
        display_intro_menu()
        choice = get_choice(4)

        if choice == 1:
            progress_game()
        elif choice == 2:
            loaded = load_game()
            if loaded:
                print()
                progress_game(previous_turn=game_variables["turn"])
        elif choice == 3:
            manage_game_settings()
        elif choice == 4:
            exit()
else:
    print("This file is not meant to be imported. Please run this file with `python3`.")
