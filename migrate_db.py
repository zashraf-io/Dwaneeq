import sqlite3
import shutil
import datetime
import os
import json
import keyring

SERVICE_NAME = "Dwaneeq"
DB_PATH = "myfinance.db"

def backup_database():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. Nothing to backup.")
        return None
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{DB_PATH}.backup_{timestamp}"
    shutil.copy2(DB_PATH, backup_path)
    print(f"Database backed up to: {backup_path}")
    return backup_path

def load_builtins():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    en_path = os.path.join(base_dir, "lang", "en.json")
    ar_path = os.path.join(base_dir, "lang", "ar.json")
    
    with open(en_path, "r", encoding="utf-8") as f:
        en_data = json.load(f)
    with open(ar_path, "r", encoding="utf-8") as f:
        ar_data = json.load(f)
        
    return en_data.get("_builtin_categories", {}), ar_data.get("_builtin_categories", {})

def run_migration():
    print("=== Starting Dwaneeq Database Migration ===")
    if not os.path.exists(DB_PATH):
        print("No existing myfinance.db found to migrate.")
        return

    backup_path = backup_database()
    conn = sqlite3.connect(DB_PATH)
    cr = conn.cursor()

    # 1. Migrate remember_logins table to keyring
    cr.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='remember_logins'")
    if cr.fetchone():
        print("Migrating remember_logins to keyring...")
        cr.execute("SELECT user_id FROM remember_logins LIMIT 1")
        row = cr.fetchone()
        if row and row[0]:
            keyring.set_password(SERVICE_NAME, "remembered_user_id", str(row[0]))
            print(f"Remembered user_id ({row[0]}) stored in OS credential manager (keyring).")
        cr.execute("DROP TABLE remember_logins")
        conn.commit()

    # 2. Create categories and category_translations tables if missing
    cr.execute("""CREATE TABLE IF NOT EXISTS categories(
                    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    type TEXT,
                    is_builtin BOOL,
                    user_id INTEGER)""")

    cr.execute("""CREATE TABLE IF NOT EXISTS category_translations(
                    category_id INTEGER,
                    lang TEXT,
                    name TEXT,
                    FOREIGN KEY(category_id) REFERENCES categories(category_id))""")
    conn.commit()

    # 3. Seed built-in categories
    en_builtins, ar_builtins = load_builtins()
    cr.execute("SELECT COUNT(*) FROM categories WHERE is_builtin=1")
    if cr.fetchone()[0] == 0:
        print("Seeding built-in categories...")
        for cat_type in ["income", "expense"]:
            en_cats = en_builtins.get(cat_type, {})
            ar_cats = ar_builtins.get(cat_type, {})
            for key, en_name in en_cats.items():
                ar_name = ar_cats.get(key, en_name)
                cr.execute("INSERT INTO categories(key, type, is_builtin, user_id) VALUES(?,?,1,NULL)", (key, cat_type))
                cat_id = cr.lastrowid
                cr.execute("INSERT INTO category_translations(category_id, lang, name) VALUES(?,?,?)", (cat_id, "en", en_name))
                cr.execute("INSERT INTO category_translations(category_id, lang, name) VALUES(?,?,?)", (cat_id, "ar", ar_name))
        conn.commit()

    # Build name-to-id mapping
    cr.execute("""SELECT c.category_id, c.key, c.type, ct_en.name, ct_ar.name 
                  FROM categories c
                  LEFT JOIN category_translations ct_en ON c.category_id = ct_en.category_id AND ct_en.lang = 'en'
                  LEFT JOIN category_translations ct_ar ON c.category_id = ct_ar.category_id AND ct_ar.lang = 'ar'""")
    rows = cr.fetchall()
    
    lookup = {} # lowercase string -> category_id
    for cat_id, key, ctype, en_name, ar_name in rows:
        if key: lookup[key.lower()] = cat_id
        if en_name: lookup[en_name.lower()] = cat_id
        if ar_name: lookup[ar_name.lower()] = cat_id

    def get_or_create_category_id(cat_str: str, trans_type: str, user_id: int) -> int:
        if not cat_str:
            # Fallback to Other
            other_key = "other_income" if trans_type == "income" else "other_expense"
            return lookup.get(other_key, 1)
            
        clean_str = cat_str.strip()
        if clean_str.lower() in lookup:
            return lookup[clean_str.lower()]

        # Try to match if it's already an integer ID
        try:
            val_id = int(clean_str)
            cr.execute("SELECT category_id FROM categories WHERE category_id=?", (val_id,))
            if cr.fetchone():
                return val_id
        except ValueError:
            pass

        # Create custom category
        print(f"Creating custom category '{clean_str}' for user {user_id}...")
        cr.execute("INSERT INTO categories(key, type, is_builtin, user_id) VALUES(?,?,0,?)", (clean_str, trans_type, user_id))
        new_id = cr.lastrowid
        cr.execute("INSERT INTO category_translations(category_id, lang, name) VALUES(?,?,?)", (new_id, "en", clean_str))
        cr.execute("INSERT INTO category_translations(category_id, lang, name) VALUES(?,?,?)", (new_id, "ar", clean_str))
        conn.commit()
        lookup[clean_str.lower()] = new_id
        return new_id

    # 4. Migrate transactions table if it has 'category' column
    cr.execute("PRAGMA table_info(transactions)")
    columns = [col[1] for col in cr.fetchall()]
    if "category" in columns and "category_id" not in columns:
        print("Migrating transactions table...")
        cr.execute("SELECT transaction_id, user_id, type, category, amount, currency, date, note FROM transactions")
        old_trans = cr.fetchall()

        cr.execute("""CREATE TABLE transactions_new(
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
                    )""")

        for tid, uid, ttype, cat_str, amount, curr, dt, note in old_trans:
            cid = get_or_create_category_id(cat_str, ttype or "expense", uid)
            cr.execute("""INSERT INTO transactions_new(transaction_id, user_id, type, category_id, amount, currency, date, note)
                          VALUES(?,?,?,?,?,?,?,?)""", (tid, uid, ttype, cid, amount, curr, dt, note))

        cr.execute("DROP TABLE transactions")
        cr.execute("ALTER TABLE transactions_new RENAME TO transactions")
        conn.commit()
        print(f"Migrated {len(old_trans)} transactions successfully.")

    # 5. Migrate category_budget table if it has 'category' column
    cr.execute("PRAGMA table_info(category_budget)")
    cb_columns = [col[1] for col in cr.fetchall()]
    if "category" in cb_columns and "category_id" not in cb_columns:
        print("Migrating category_budget table...")
        cr.execute("SELECT budget_id, category, category_budget FROM category_budget")
        old_cb = cr.fetchall()

        cr.execute("""CREATE TABLE category_budget_new(
                        budget_id INTEGER,
                        category_id INTEGER,
                        category_budget REAL,
                        FOREIGN KEY(budget_id) REFERENCES budget(budget_id),
                        FOREIGN KEY(category_id) REFERENCES categories(category_id)
                    )""")

        for bid, cat_str, cat_budget in old_cb:
            cid = get_or_create_category_id(cat_str, "expense", 0)
            cr.execute("INSERT INTO category_budget_new(budget_id, category_id, category_budget) VALUES(?,?,?)",
                       (bid, cid, cat_budget))

        cr.execute("DROP TABLE category_budget")
        cr.execute("ALTER TABLE category_budget_new RENAME TO category_budget")
        conn.commit()
        print(f"Migrated {len(old_cb)} category budget items successfully.")

    conn.close()
    print("=== Migration Completed Successfully ===")

if __name__ == "__main__":
    run_migration()
