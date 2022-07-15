def display_intro_menu():
    """Displays the menu prompting the user to start or restore a game."""
    for line in ["Desperate Defenders", "-" * 19, "Defend the city from undead monsters!", ""]:
        print(line)
    for index, line in enumerate(["Start a new game", "Load saved game", "Quit"]):
        print("{}. {}".format(index + 1, line))

    # Prompts the user for a choice. If the choice is invalid, the user
    # will be reprompted again until a valid choice is given.
    while True:
        try:
            choice = int(input("Your choice? "))
            assert 1 <= choice <= 3
        except ValueError:
            print("Your choice should be numeric.", end=" ")
        except AssertionError:
            print("Your choice should be between 1 and 3 (inclusive).", end=" ")
        else:
            break

    if choice == 1:
        # TODO: Start a new game
        pass
    elif choice == 2:
        # TODO: Restore and continue a saved game
        pass
    elif choice == 3:
        exit()


if __name__ == "__main__":
    display_intro_menu()
else:
    print("This file is not meant to be imported. Please run this file with `python3`.")
