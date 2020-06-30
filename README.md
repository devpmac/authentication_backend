# Authentication Backend

Code for a simple command line Python3 app for User Authentication/Registration, including a simple access log. Check below for [setup instructions](#setup).

- **Run app**: `python app.py`

For demonstration purposes, the **content** of the **database** can be **read** via:

- `python read_db.py`

#### Notes:
- Inserted email addresses are validated via `regex`.
- The available methods depend on the user's authentication state.

---
## Code Overview
The module `users` is separate into:
- `db_tools.py` - built on `sqlite3` to mediate interactions with the database. Two Classes/Models were created: *Users* and *Logs*, to handle the corresponding tables.
- `encryption.py` - password encryption and verification, using the standard library ([crypt](https://docs.python.org/3/library/crypt.html)) to provide password encryption and verification.
**Note**: this library is only available in Unix.
- `menu.py` - app interface, fully connected to the database. The main features include:
    - User registration/deletion
    - User log in/out
    - email/password alterations
    - User log printing
    - Account locking for 30mins, after 5 failed authentications in 10mins.

---
## Setup

Only standard libraries were used, so a recent Python3 should suffice to run everything.

| Linux |
| --- |
| `git clone https://github.com/devpmac/authentication_backend.git` |
| `cd authentication_backend` |
| `python3 -m venv env` |
| `source env/bin/activate` |
