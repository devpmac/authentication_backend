from sys import exit
from users import Users, Logs, DB_PATH
from users import Interface, InvalidAction, MaxTries


if __name__ == "__main__":
    users = Users(db_path=DB_PATH)
    logs = Logs(db_path=DB_PATH)
    menu = Interface(users=users, logs=logs)

    while True:
        print("0 - Exit system")
        for i, opt in menu.options.items():
            print(f"{i} - {opt}")

        choice = input("Choice: ")
        if choice == "0":
            print("Farewell!\n")
            exit()

        elif choice in menu.options:
            try:
                menu.actions[menu.options[choice]]()
            except (InvalidAction, MaxTries) as msg:
                print(msg)

        else:
            print("Unrecognized command.\n")
