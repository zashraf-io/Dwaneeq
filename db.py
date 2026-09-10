import sqlite3
import hashlib
import datetime
from dateutil.relativedelta import relativedelta
import os, sys
from bs4 import BeautifulSoup
import requests
import config
import json
import keyring

SERVICE_NAME = "Dwaneeq"

def open_database(table: str = None) -> None:
    """coonects to the data base and opens the required table ['users', 'settings', 'remember_logins', 'transactions',
    'budget', 'category_budget', 'currency_rate']"""
    global db, cr

    db = sqlite3.connect("myfinance.db", timeout=20.0)


    if table == "users":
        db.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, username TEXT, 
        password BLOB, salt BLOB, iterations INTEGER, last_login TEXT, signup_date TEXT)""")
    elif table == "settings":
        db.execute("""CREATE TABLE IF NOT EXISTS settings(
            user_id INTEGER PRIMARY KEY,
            mode TEXT, theme TEXT, lang TEXT, remember_login BOOLEN, main_currency TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id))""")
    elif table == "categories":
        db.execute("""CREATE TABLE IF NOT EXISTS categories(
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    type TEXT,
                    is_builtin BOOL,
                    user_id INTEGER)""")
    elif table == "category_translations":
        db.execute("""CREATE TABLE IF NOT EXISTS category_translations(
                    category_id INTEGER,
                    lang TEXT,
                    name TEXT,
                    FOREIGN KEY(category_id) REFERENCES categories(category_id))""")
    elif table == "transactions":
        db.execute("""CREATE TABLE IF NOT EXISTS transactions(
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    category_id INTEGER,
                    amount REAL,
                    currency TEXT,
                    date TEXT,
                    note TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id),
                    FOREIGN KEY(category_id) REFERENCES categories(category_id)
                    )
                    """)
    elif table == "budget":
        db.execute("""CREATE TABLE IF NOT EXISTS budget(
                    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    month TEXT,
                    total_budget REAL,
                    savings_goal REAL,
                    currency TEXT,
                    is_auto BOOL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                    )""")
    elif table == "category_budget":
        db.execute("""CREATE TABLE IF NOT EXISTS category_budget(
            budget_id INTEGER,
            category_id INTEGER,
            category_budget REAL,
            FOREIGN KEY (budget_id) REFERENCES budget(budget_id),
            FOREIGN KEY (category_id) REFERENCES categories(category_id))""")
    elif table == "currency_rate":
        db.execute("CREATE TABLE IF NOT EXISTS currency_rate(currency STRING, rate REAL, last_update STRING)")
    elif table == "all":
        db.execute("""CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, username TEXT, 
        password BLOB, salt BLOB, iterations INTEGER, last_login TEXT, signup_date TEXT)""")
        db.execute("""CREATE TABLE IF NOT EXISTS settings(
            user_id INTEGER PRIMARY KEY,
            mode TEXT, theme TEXT, lang TEXT, remember_login BOOLEN, main_currency TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id))""")
        db.execute("""CREATE TABLE IF NOT EXISTS categories(
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    type TEXT,
                    is_builtin BOOL,
                    user_id INTEGER)""")
        db.execute("""CREATE TABLE IF NOT EXISTS category_translations(
                    category_id INTEGER,
                    lang TEXT,
                    name TEXT,
                    FOREIGN KEY(category_id) REFERENCES categories(category_id))""")
        db.execute("""CREATE TABLE IF NOT EXISTS transactions(
                    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    type TEXT,
                    category_id INTEGER,
                    amount REAL,
                    currency TEXT,
                    date TEXT,
                    note TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(user_id),
                    FOREIGN KEY(category_id) REFERENCES categories(category_id)
                    )
                    """)
        db.execute("""CREATE TABLE IF NOT EXISTS budget(
                    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    month TEXT,
                    total_budget REAL,
                    savings_goal REAL,
                    currency TEXT,
                    is_auto BOOL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                    )""")
        db.execute("""CREATE TABLE IF NOT EXISTS category_budget(
            budget_id INTEGER,
            category_id INTEGER,
            category_budget REAL,
            FOREIGN KEY (budget_id) REFERENCES budget(budget_id),
            FOREIGN KEY (category_id) REFERENCES categories(category_id))""")
        db.execute("CREATE TABLE IF NOT EXISTS currency_rate(currency STRING, rate REAL, last_update STRING)")
        save()
        seed_builtin_categories()
        return

    cr = db.cursor()

def seed_builtin_categories():
    try:
        lang_en_path = os.path.join(os.path.dirname(__file__), "lang", "en.json")
        lang_ar_path = os.path.join(os.path.dirname(__file__), "lang", "ar.json")
        with open(lang_en_path, "r", encoding="utf-8") as f:
            en_data = json.load(f)
        with open(lang_ar_path, "r", encoding="utf-8") as f:
            ar_data = json.load(f)

        en_builtins = en_data.get("_builtin_categories", {})
        ar_builtins = ar_data.get("_builtin_categories", {})

        open_database("categories")
        cr.execute("SELECT COUNT(*) FROM categories WHERE is_builtin=1")
        if cr.fetchone()[0] == 0:
            for cat_type in ["income", "expense"]:
                en_cats = en_builtins.get(cat_type, {})
                ar_cats = ar_builtins.get(cat_type, {})
                for key, en_name in en_cats.items():
                    ar_name = ar_cats.get(key, en_name)
                    cr.execute("INSERT INTO categories(key, type, is_builtin, user_id) VALUES(?,?,1,NULL)", (key, cat_type))
                    cat_id = cr.lastrowid
                    cr.execute("INSERT INTO category_translations(category_id, lang, name) VALUES(?,?,?)", (cat_id, "en", en_name))
                    cr.execute("INSERT INTO category_translations(category_id, lang, name) VALUES(?,?,?)", (cat_id, "ar", ar_name))
            save()
        else:
            db.close()
    except Exception as e:
        print(f"Error seeding categories: {e}")

def save() -> None:
    """save changes after insertion or updating or deleting then close the database"""
    db.commit()
    db.close()


# Log in and Sign up functions
def isreserved(username: str) -> bool:
    """checks if username is reserved by another user, to ensure that usernames are unique"""
    open_database("users")

    cr.execute("SELECT username FROM users")
    usernames_list = cr.fetchall()
    db.close()


    if (username,) in usernames_list:
        return True
    else:
        return False

def add_user(username: str, password:str) -> None:
    """add a user to the data base, used with sign up"""
    
    open_database("users")

    salt = os.urandom(16)
    iterations = 100000
    password = password.encode("utf-8")
    encoded_password = hashlib.pbkdf2_hmac("sha256", password, salt, iterations)

    signup_date = datetime.datetime.now().strftime(r"%Y-%m-%d %H:%M")
    last_login = signup_date

    cr.execute("INSERT INTO users(username, password, salt, iterations, last_login, signup_date) VALUES(?, ?, ?, ?, ?, ?)", 
                (username, encoded_password, salt, iterations, last_login, signup_date))
    save()

    open_database("settings")
    cr.execute("INSERT INTO settings (mode, theme, lang, remember_login, main_currency) VALUES('Dark', 'black', 'ar', 'False', 'EGP')")

    save()

def update_login_date(user_id: int) -> None:
    "update the last_login date into now"
    
    open_database()

    cr.execute("UPDATE users SET last_login=? WHERE user_id=?", (datetime.datetime.now().strftime(r"%Y-%m-%d %H:%M"), user_id))
    
    save()

def get_login_date(user_id: int) -> str:
    "returns the last login date"
    open_database()

    cr.execute("SELECT last_login FROM users WHERE user_id=?", (user_id,))
    return cr.fetchone()[0]

def isvalid_user(username: str, password: str) -> str:
    """Checks that a given username and password are valid,
    if valid return user_id, if NOT valid return 'not valid', if username does not exists return 'not found'
    used with log in"""

    open_database()

    cr.execute("SELECT user_id, username, password, salt, iterations FROM users")
    users = cr.fetchall()
    db.close()

    found = False
    for user in users:
        if username in user:
            user_id = user[0]
            true_password = user[2]
            salt = user[3]
            iterations = user[4]
            found = True
            break
    
    if not found:
        return 'not found'

    password = password.encode("utf-8")
    encoded_password = hashlib.pbkdf2_hmac("sha256", password, salt, iterations)
    if encoded_password == true_password:
        return user_id
    else:
        return 'not valid'

# Settings functions
def check_password(user_id: int, password: str) -> bool:
    "check the password using user id"

    open_database()

    cr.execute("SELECT password, salt, iterations FROM users WHERE user_id=?", (user_id,))
    user = cr.fetchone()
    db.close()

    true_password = user[0]
    salt = user[1]
    iterations = user[2]

    password = password.encode("utf-8")
    encoded_password = hashlib.pbkdf2_hmac("sha256", password, salt, iterations)
    if encoded_password == true_password:
        return True
    else:
        return False

def set(user_id: int, mode: str="light", theme="", lang="en", remember_login=False, command="update", field="all") -> None:
    """insert and update data in settings table in the database, takes data in addition to command[create, update]"""
    open_database("settings")
    if command == "update":
        if field == "all":
            cr.execute("UPDATE settings SET mode=?, theme=?, lang=?, remember_login=? WHERE user_id=?", (mode, theme, lang, remember_login, user_id))
        elif field == "mode":
            cr.execute("UPDATE settings SET mode=? WHERE user_id=?", (mode, user_id))
        elif field == "theme":
            cr.execute("UPDATE settings SET theme=? WHERE user_id=?", (theme, user_id))
        elif field == "lang":
            cr.execute("UPDATE settings SET lang=? WHERE user_id=? ", (lang, user_id))
        elif field == "remember_login":
            cr.execute("UPDATE settings SET remember_login=? WHERE user_id=?", (remember_login, user_id))
    elif command == "create":
        cr.execute("INSERT INTO settings(user_id, mode, theme, lang, remember_login) VALUES(?,?,?,?,?)", (user_id, mode, theme, lang, remember_login))

    save()

def change_password(user_id, new_password):
    """change the password of the required user"""
    open_database()

    new_password = new_password.encode("utf-8")
    new_salt = os.urandom(16)
    encoded_password = hashlib.pbkdf2_hmac("sha256", new_password, new_salt, 100000)

    cr.execute("UPDATE users SET password=?, salt=? WHERE user_id=?", (encoded_password, new_salt, user_id))

    save()

def delete_user(user_id):
    """delete the user permenantly from the data base"""
    category_budget_ids = get_user_budgets_id(user_id)
    open_database()

    cr.execute("DELETE FROM settings WHERE user_id=?", (user_id,))
    cr.execute("DELETE FROM transactions WHERE user_id=?", (user_id,))

    for id in category_budget_ids:
        cr.execute("DELETE FROM category_budget WHERE budget_id=?", (id[0],))

    cr.execute("DELETE FROM budget WHERE user_id=?", (user_id,))
    cr.execute("DELETE FROM users WHERE user_id=?", (user_id,))

    save()

def get_setting(user_id: int, req: str) -> str:
    "returns the saved mode for the user from the data base"
    open_database()

    if req == 'mode':
        cr.execute("SELECT mode FROM settings WHERE user_id=?", (user_id,))
    elif req == 'theme':
        cr.execute("SELECT theme FROM settings WHERE user_id=?", (user_id,))
    elif req == 'lang':
        cr.execute("SELECT lang FROM settings WHERE user_id=?", (user_id,))
    elif req == 'main_currency':
        cr.execute("SELECT main_currency FROM settings WHERE user_id=?", (user_id,))

    
    mode = cr.fetchone()[0]
    db.close()
    return mode

def set_main_currency(user_id, currency):
    open_database()

    cr.execute("UPDATE settings SET main_currency=? WHERE user_id=?", (currency, user_id))

    save()

def remember_login(user_id, remember=True) -> None:
    "add to the data base the user id to remember his login"
    if remember:
        keyring.set_password(SERVICE_NAME, "remembered_user_id", str(user_id))
    else:
        try:
            keyring.delete_password(SERVICE_NAME, "remembered_user_id")
        except keyring.errors.PasswordDeleteError:
            pass

def isfound_remembered(close_after: bool =True) -> int:
    "see if there is a saved user id, return id if found, else return 0"
    cred = keyring.get_password(SERVICE_NAME, "remembered_user_id")
    if cred:
        return int(cred)
    return 0

# Category functions
def add_category(key: str, type: str, is_builtin: bool=False, user_id=None, translations: dict={}):
    open_database("categories")
    cr.execute("INSERT INTO categories(key, type, is_builtin, user_id) VALUES(?,?,?,?)", (key, type, is_builtin, user_id))
    category_id = cr.lastrowid
    
    for lang, name in translations.items():
        cr.execute("INSERT INTO category_translations(category_id, lang, name) VALUES(?,?,?)", (category_id, lang, name))
    
    save()
    return category_id

def rename_category(category_id: int, new_names: dict):
    open_database("category_translations")
    for lang, name in new_names.items():
        cr.execute("SELECT 1 FROM category_translations WHERE category_id=? AND lang=?", (category_id, lang))
        if cr.fetchone():
            cr.execute("UPDATE category_translations SET name=? WHERE category_id=? AND lang=?", (name, category_id, lang))
        else:
            cr.execute("INSERT INTO category_translations(category_id, lang, name) VALUES(?,?,?)", (category_id, lang, name))
    save()

def delete_category(category_id: int):
    open_database("categories")
    cr.execute("DELETE FROM category_translations WHERE category_id=?", (category_id,))
    cr.execute("DELETE FROM categories WHERE category_id=?", (category_id,))
    save()

def get_categories(type: str, lang: str, user_id: int=None) -> list:
    open_database()
    query = """SELECT c.category_id, COALESCE(ct.name, c.key) FROM categories c 
               LEFT JOIN category_translations ct ON c.category_id = ct.category_id AND ct.lang = ?
               WHERE c.type = ? AND (c.is_builtin = 1 OR c.user_id = ?)"""
    cr.execute(query, (lang, type, user_id))
    records = cr.fetchall()
    db.close()
    return records

def get_category_name(category_id: int, lang: str) -> str:
    open_database()
    cr.execute("""SELECT COALESCE(ct.name, c.key) FROM categories c
                  LEFT JOIN category_translations ct ON c.category_id = ct.category_id AND ct.lang = ?
                  WHERE c.category_id = ?""", (lang, category_id))
    record = cr.fetchone()
    db.close()
    if record:
        return record[0]
    return config.choosed_lang.get("deleted", "Deleted")

# Transactions functions
def add_transaction(user_id: int, amount: float, Currency="EGP", type: str="", category_id: int=0, date: str="now", note: str=""):
    "append date to the transaction table in the database"
    open_database("transactions")

    cr.execute("""INSERT INTO transactions(user_id, type, category_id, amount, currency, date, note)
                VALUES(?,?,?,?,?,?,?)""", (user_id, type, category_id, amount, Currency, date, note))
            
    save()

def update_transaction(transaction_id: int, amount: float, Currency="EGP", type: str="", category_id: int=0, date: str="now", note: str=""):
    open_database("transactions")
    cr.execute("""UPDATE transactions 
                  SET type=?, category_id=?, amount=?, currency=?, date=?, note=? 
                  WHERE transaction_id=?""", 
               (type, category_id, amount, Currency, date, note, transaction_id))
    save()


# History functions
def get_transactions(user_id, search: str="", type: str="all", category_id: int=None, currnecy: str="all", date_from: str="", date_to: str="", limit=None):
    "get the transactions from the data base, if filters are given it search by them"
    open_database()

    lang = config.get_current_lang()
    query = """SELECT t.transaction_id, t.user_id, t.type, COALESCE(ct.name, c.key) as category_name, 
                      t.amount, t.currency, t.date, t.note, t.category_id 
               FROM transactions t
               LEFT JOIN categories c ON t.category_id = c.category_id
               LEFT JOIN category_translations ct ON c.category_id = ct.category_id AND ct.lang = ?
               WHERE t.user_id=?"""
    variables = [lang, user_id]

    if type != "all" and type:
        query += " AND t.type = ?"
        variables.append(type)

    if category_id:
        query += " AND t.category_id = ?"
        variables.append(category_id)

    if currnecy != "all" and currnecy != "":
        query += " AND t.currency = ?"
        variables.append(currnecy)

    if date_from != "":
        query += " AND t.date BETWEEN ? AND ?"
        variables.extend([date_from, date_to])

    if search != "":
        query += " AND t.note LIKE ?"
        variables.append(f"%{search}%")
    
    query += " ORDER BY t.date DESC"

    if limit:
        query += " LIMIT ?"
        variables.append(limit)

    try:
        cr.execute(query, variables)
        records = cr.fetchall()
        db.close()

        return records
    except Exception as e:
        print("Error in get_transactions:", e)
        return []

def delete_transactions(user_id, ids: tuple):
    open_database()

    for trans_id in ids:
        cr.execute("DELETE FROM transactions WHERE user_id=? and transaction_id=?", (user_id, trans_id))

    save()    

# Budget functions
def isfound_budget(user_id, month: str="now") -> int:
    "search if there is a budget already set for the specific month, default search for the current month"
    try:
        open_database("budget")

        if month == "now":
            month = datetime.datetime.now().strftime(r"%Y-%m")

        cr.execute("SELECT budget_id, month FROM budget WHERE user_id=? AND month=?", (user_id, month))
        record = cr.fetchone()
        db.close()

        if record == None:
            return False
        
        if record[1] == month:
            return record[0]

        return False

    except:
        raise ConnectionError

def add_budget(user_id, total_budget, savings_goal: float=0, currency: str='EGP',  month: str='now', is_auto: bool=False):
    "add a total budget for a month"
    open_database("budget")

    if month == 'now':
        month = datetime.datetime.now().strftime(r"%Y-%m")

    cr.execute("""INSERT INTO budget(user_id, month, total_budget, savings_goal, currency, is_auto)
                VALUES(?,?,?,?,?,?)""", (user_id, month, total_budget, savings_goal, currency, is_auto))

    save()

def add_category_budget(budget_id: int, category_id: int, category_budget: float):
    "add a specific budget for each category"
    open_database("category_budget")

    cr.execute("INSERT INTO category_budget(budget_id, category_id, category_budget) VALUES(?,?,?)", (budget_id, category_id, category_budget))

    save()

def edit_budget(user_id, budget_id, total_budget, savings_goal: float=0, currency: str='EGP', is_auto: bool=False):
    "edit a specific budget by budget_id"
    open_database()

    cr.execute("UPDATE budget SET total_budget=?, savings_goal=?, currency=?, is_auto=? WHERE user_id=? AND budget_id=?",
                (total_budget, savings_goal, currency, is_auto, user_id, budget_id))

    save()

def delete_category_budget(budget_id: int):
    "edit a categories budget of specific budget by deleting old categories and adding the new"
    open_database()

    cr.execute("DELETE FROM category_budget WHERE budget_id=?", (budget_id,))

    save()

def get_latest_budget_info(user_id):
    "return the latest month has a budget set, returns: (budget_id, month, is_auto)"
    open_database()

    cr.execute("SELECT budget_id, month, is_auto FROM budget WHERE user_id=? ORDER BY month DESC LIMIT 1", (user_id,))
    records = cr.fetchone()
    
    if records == None:
        return "no budget"

    return records

def get_budget(budget_id):
    "return the budget data --> [tuple(budget_data), [categories_data]]"
    open_database()
    
    lang = config.get_current_lang()

    cr.execute("SELECT total_budget, savings_goal, currency, is_auto FROM budget WHERE budget_id=?", (budget_id,))
    budget_data = cr.fetchone()

    query = """SELECT cb.category_id, COALESCE(ct.name, c.key) as category_name, cb.category_budget 
               FROM category_budget cb
               LEFT JOIN categories c ON cb.category_id = c.category_id
               LEFT JOIN category_translations ct ON c.category_id = ct.category_id AND ct.lang = ?
               WHERE cb.budget_id = ?"""

    cr.execute(query, (lang, budget_id))
    categories_data = cr.fetchall()

    return [budget_data, categories_data]

def update_auto_budget(user_id, budget_id="latest", new_month: str="now"):
    """take a budget_id and new_month to copy a new budget from the given budget
    budget_id default is set for the latest budget set
    new_month is month formated YYYY-mm or ['now', 'next'], default is set for the current month"""
    open_database()
    
    if not get_latest_budget_info(user_id):
        return

    if get_latest_budget_info(user_id)[1] == datetime.datetime.now().strftime(r"%Y-%m"):
        return

    if budget_id == "latest":
        budget_id = get_latest_budget_info(user_id)[0]

    cr.execute("SELECT total_budget, savings_goal, currency, is_auto FROM budget WHERE budget_id=? AND user_id=? AND is_auto=1",
                    (budget_id, user_id,))

    records = cr.fetchone()

    if records == None:
        return "no auto"

    total_budget = records[0]
    savings = records[1]
    currency = records[2]
    is_auto = records[3]

    if new_month == "now":
        new_month = datetime.datetime.now().strftime(r"%Y-%m")
    elif new_month == "next":
        new_month = datetime.datetime.now() + relativedelta(months=1)
        new_month = new_month.strftime(r"%Y-%m")


    add_budget(user_id, total_budget, savings, currency, new_month, is_auto)


    open_database()

    cr.execute("SELECT category_id, category_budget FROM category_budget WHERE budget_id=?",
                    (budget_id,))

    records = cr.fetchall()
    new_budget_id = get_latest_budget_info(user_id)[0]

    for category in records:
        add_category_budget(new_budget_id, category[0], category[1])

def cancel_last_auto(user_id: int):
    "cancels the auto of last budget"
    budget_id = get_latest_budget_info(user_id)[0]
    open_database()
    cr.execute("UPDATE budget SET is_auto=? WHERE user_id=? and budget_id=?", (False, user_id, budget_id))

    save()

def get_user_budgets_id(user_id):
    open_database()

    cr.execute("SELECT budget_id FROM budget WHERE user_id=?", (user_id,))
    ids = cr.fetchall()

    db.close()

    return ids

# Currency rates, based on 'EGP' is the main currency
def update_currencies_rates() -> int:
    """updates the currencies rates in the database using a thread-local SQLite connection.
    if not all are updated, nothing updated and old rates are kept."""
    from_currency = "EGP"
    currencies = config.LANG["en"]["currency_list"]
    len_currencies = len(currencies)

    start_date = (datetime.datetime.now() - relativedelta(days=1)).strftime(r"%Y-%m-%d")
    end_date = datetime.datetime.now().astimezone().strftime(r"%Y-%m-%d")

    # 1. Thread-safe check if already updated today
    try:
        check_conn = sqlite3.connect("myfinance.db", timeout=20.0)
        check_cr = check_conn.cursor()
        check_cr.execute("CREATE TABLE IF NOT EXISTS currency_rate(currency STRING, rate REAL, last_update STRING)")
        row = check_cr.execute("SELECT last_update FROM currency_rate LIMIT 1").fetchone()
        check_conn.close()
        if row and end_date == row[0]:
            return 0
    except Exception:
        pass

    # 2. Fetch exchange rates over network BEFORE opening any write transaction
    fetched_rates = []
    for to_currency in currencies:
        url = f"https://fxds-public-exchange-rates-api.oanda.com/cc-api/currencies?base={from_currency}&quote={to_currency}&data_type=general_currency_pair&start_date={start_date}&end_date={end_date}"
        try:
            r = requests.get(url, timeout=10)
        except requests.exceptions.ConnectionError:
            return 1
        except Exception:
            return 1

        try:
            soup = BeautifulSoup(r.content, "lxml")
            data = json.loads(soup.find("p").text)
            if 'response' in data:
                rate = 1 / ((float(data['response'][0]["average_bid"]) + float(data['response'][0]["average_ask"])) / 2)
                fetched_rates.append((to_currency, float(f"{rate:.5f}"), end_date))
            elif "error" in data:
                return 2
        except Exception:
            return 3

    # 3. Fast atomic write with thread-local connection
    if len(fetched_rates) == len_currencies:
        try:
            conn = sqlite3.connect("myfinance.db", timeout=20.0)
            cr_local = conn.cursor()
            cr_local.execute("DELETE FROM currency_rate")
            cr_local.executemany("INSERT INTO currency_rate(currency, rate, last_update) VALUES(?,?,?)", fetched_rates)
            conn.commit()
            conn.close()
            return 0
        except Exception as e:
            print(f"Error saving currency rates: {e}")
            return 3
    else:
        return 3

def get_currency_rate(currency) -> float:
    open_database()
    rate = cr.execute("SELECT rate FROM currency_rate WHERE currency=?",(currency,)).fetchone()[0]
    db.close()
    return rate

def get_update_date() -> str:
    open_database()
    
    cr.execute("SELECT last_update FROM currency_rate LIMIT 1")
    date = cr.fetchone()[0]

    db.close()

    return date

# Stats needs

def get_amount(user_id, type, category_id: int=None, month: str="all") -> list:
    """return the summation of 'EGP' and other amounts with their currencies
    retrun --> ['EGP summation', [(amount, currency), (amount, currency)]]"""
    sum = 0
    open_database()
    vars = [user_id, type]
    query = "SELECT SUM(amount) FROM transactions WHERE user_id=? and currency='EGP' and type=?"

    if category_id is not None:
        query += " and category_id=?"
        vars.append(category_id)

    if month != "all":
        query += " and date LIKE ?"
        vars.append(month+"%")

    sum = cr.execute(query, vars).fetchone()[0]
    query = "SELECT amount, currency FROM transactions WHERE user_id=? and type=? and currency != 'EGP'"
    vars = [user_id, type]


    if category_id is not None:
        query += " and category_id=?"
        vars.append(category_id)

    if month != "all":
        query += " and date LIKE ?"
        vars.append(f"{month}%")

    records = cr.execute(query, vars).fetchall()

    db.close()

    return [sum, records]

def get_months(user_id):
    open_database()

    cr.execute("SELECT date FROM transactions WHERE user_id=? ORDER BY date ASC", (user_id,))
    dates = cr.fetchall()
    db.close()

    months = []
    for month in dates:
        if month[0][:7] not in months:
            months.append(month[0][:7])

    return months

def get_expense_categories(user_id, month="all"):
    open_database()

    query = "SELECT category_id FROM transactions WHERE user_id=? AND type='expense'"
    vals = [user_id]

    if month != "all":
        query += " AND date LIKE ?"
        vals.append(month+"%")

    records = cr.execute(query, vals).fetchall()
    categories = []
    [categories.append(category[0]) for category in records if category[0] not in categories]
    
    db.close() 

    return categories
