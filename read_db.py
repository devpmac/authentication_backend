from users import Users, Logs, DB_PATH
from users import Interface


if __name__ == "__main__":
    users = Users(db_path=DB_PATH)
    logs = Logs(db_path=DB_PATH)
    menu = Interface(users=users, logs=logs)

    print("\nAll Users:")
    print("pkey, user_email, pw, register_date, locked_until")
    for i in users.read_all():
        print(i)

    print("\nAll logs:")
    print("pkey, access_attempt_time, success, user_id")
    for i in logs.read_all():
        print(i)
