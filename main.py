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

        else:
####################
# Execution point
# The game begins here.
####################


if __name__ == "__main__":
    display_intro_menu()
    choice = get_choice(3)

    if choice == 1:
        # TODO: Start a new game
        pass
    elif choice == 2:
        # TODO: Restore and continue a saved game
        pass
    elif choice == 3:
        exit()
else:
    print("This file is not meant to be imported. Please run this file with `python3`.")
