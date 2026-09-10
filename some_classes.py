import customtkinter
from tkinter import PhotoImage
import tkinter
from tkcalendar import Calendar
import datetime
import config

class NumEntry(customtkinter.CTkFrame):
    def __init__(self, master, num_type: str="float", minus_val: int=10, plus_val: int=10,
                    placeholder_text: str="", width: int=100, quick_plus_minus: bool=True, align_direction: str="ltr"):
        super().__init__(master)
        self.master = master
        self.placeholder_text = placeholder_text
        self.minus_val =minus_val
        self.plus_val =plus_val
        self.type = num_type

        self.configure(fg_color="transparent")

        valid_command = self.register(self._check_entry)

        self.entry = customtkinter.CTkEntry(self, width=width, placeholder_text=placeholder_text)
        self.entry.configure(validate="key", validatecommand=(valid_command, "%P"))
        self.entry.grid(row=0, column=0)

        if quick_plus_minus:
            self.minus = customtkinter.CTkButton(self, width=28, corner_radius=100, text="-", font=("Arial", 20), command=self._decrease)
            self.plus = customtkinter.CTkButton(self, width=28, corner_radius=100, text="+", font=("Arial", 20), command=self._add)
            if align_direction == "ltr":
                self.minus.grid(row=0, column=1)
                self.plus.grid(row=0, column=2)
            elif align_direction == "rtl":
                self.entry.configure(justify="right")
                self.minus.grid(row=0, column=0)
                self.plus.grid(row=0, column=1)
                self.entry.grid(row=0, column=2)


    def _check_entry(self, text):
        "checks that the entry only takes numbers"
        if text == "":
            return True
        try:
            if self.type == "float":
                float(text)
            elif self.type == "int":
                int(text)
                
            dot_index = text.find(".")
            if dot_index != -1 and len(text) > dot_index + 3:
                return False
            else:
                return True
        except ValueError:
            return False

    def _decrease(self):
        if self.entry.get() == "":
            val: float= 0.0
        else:
            val = float(self.entry.get())
        self.entry.delete(0, customtkinter.END)
        val -= self.minus_val
        if val < 0:
            val: float=0.0
        self.entry.insert(index=0, string=val)

    def _add(self):
        if self.entry.get() == "":
            val: float=0.0
        else:
            val = float(self.entry.get())
        self.entry.delete(0, customtkinter.END)
        val += self.plus_val
        self.entry.insert(index=0, string=val)

    def get(self):
        value = self.entry.get()

        while value.startswith("00"):
            value = value[1:]
        
        return value

    def insert(self, value, index=0):
        self.entry.insert(index, str(value))
    
    def clear(self):
        self.entry.delete(0, "end")

    def bind(self, sequence, method):
        self.entry.bind(sequence, method)

class CurrencyMenu(customtkinter.CTkOptionMenu):
    def __init__(self, master, add_all: bool=False, width: int=80, command=None, label=None):
        super().__init__(master)

        values = [config.choosed_lang["all"], *config.choosed_lang["currency_list"]] if add_all else config.choosed_lang["currency_list"]

        self.configure(
            width = width,
            values = values,
            command=command
            )
        self.set(values[0])


    def get_currency(self):
        if config.lang_name == "en":
            return self.get()

        currencies_en = list(config.LANG["en"]["currency_list"])
        currencies = list(config.choosed_lang["currency_list"])
        try:
            index = currencies.index(self.get())
            return currencies_en[index]
        except:
            return ""

    def set_value(self, value):
        if config.lang_name == "ar":
            value = config.choosed_lang[value]

        self.set(value)

class CategoryMenu(customtkinter.CTkOptionMenu):
    def __init__(self, master, width=80, add_all: bool=False, type: str="all"):
        super().__init__(master)
        self.type = type
        self.add_all = add_all
        self.category_map = {}
        self.configure(width=width)
        self.refresh()

    def refresh(self):
        import db
        values = []
        self.category_map = {}
        if self.add_all:
            all_text = config.choosed_lang.get("all", "All")
            values.append(all_text)
            self.category_map[all_text] = None

        lang = config.get_current_lang()
        user_id = config.get_current_user_id()
        if self.type in ["income", "expense"]:
            cats = db.get_categories(self.type, lang, user_id)
        else:
            cats = db.get_categories("income", lang, user_id) + db.get_categories("expense", lang, user_id)

        for cat_id, name in cats:
            values.append(name)
            self.category_map[name] = cat_id

        if not values:
            values = [""]

        self.configure(values=values)
        self.set(values[0])

    def get_category_id(self):
        return self.category_map.get(self.get(), None)

    def get_category(self):
        cid = self.get_category_id()
        return "" if cid is None else cid

    def set_value(self, value):
        for name, cid in self.category_map.items():
            if str(cid) == str(value) or name == str(value):
                self.set(name)
                return

class PopUpMessage(tkinter.Toplevel):
    def __init__(self, master, message: str, button_name: str="OK", cancel_btn: bool=False, force=False, command=None, cancel_command=None):
        super().__init__(master)
        self.title("Note")

        self.attributes('-topmost', True)          # Appears always above all windows, to avoid disappearing behind them
        self.resizable(False, False)

        self.background_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.background_frame.pack(fill="both")

        self.message = customtkinter.CTkLabel(self.background_frame, text=message, width=270)
        self.message.grid(row=0, column=0, padx=10, pady=10, sticky="NESW")
        self.btnok = customtkinter.CTkButton(self.background_frame, text=button_name,
                                                    command=lambda: self.run_and_close(command))
        self.btnok.grid(row=1, column=0, pady=10)

        if cancel_btn:
            self.message.grid_configure(columnspan=2)
            self.btnok.grid_configure(padx=10)
            self.cancel_btn = customtkinter.CTkButton(self.background_frame, text=config.choosed_lang["cancel"],
                                                    command=lambda: self.run_and_close(cancel_command))
            self.cancel_btn.grid(row=1, column=1, pady=10, padx=10)

        if force:
            self.grab_set()

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        
        toplevel_width = self.winfo_width()
        toplevel_height = self.winfo_height()

        x = (screen_width - toplevel_width) // 2 - 180
        y = (screen_height - toplevel_height) // 2

        self.grid_propagate(True)
        self.geometry(f"+{x}+{y}")


    def run_and_close(self, command) -> None:
        if command:
            command()
        self.destroy()

class DateCalender(tkinter.Toplevel):
    def __init__(self, master, date_entry):
        super().__init__(master)
        
        self.background_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.background_frame.pack(fill="both")

        self.date_entry = date_entry
        
        self.title("Date")
        self.attributes('-topmost', True)
        self.resizable(False, False)
        self.grab_set()

        self.cal = Calendar(self.background_frame, selectmode='day', year=datetime.datetime.now().year,
                   month=datetime.datetime.now().month, day=datetime.datetime.now().day,
                   date_pattern="yyyy-mm-dd")
        self.cal.grid(row=0, pady=20, padx=10)

        select_btn = customtkinter.CTkButton(self.background_frame, text=config.choosed_lang["select"], command=self.pick_date)
        select_btn.grid(row=1, pady=5, padx=10)

        clear_btn = customtkinter.CTkButton(self.background_frame, text=config.choosed_lang["clear"], command=self.clear_date)
        clear_btn.grid(row=2, pady=5, padx=10)

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        
        toplevel_width = self.winfo_width()
        toplevel_height = self.winfo_height()

        x = (screen_width - toplevel_width) // 2 - 100
        y = (screen_height - toplevel_height) // 2 - 100

        self.grid_propagate(True)
        self.geometry(f"+{x}+{y}")


    def pick_date(self):
        "get the date from the calender and put it into the date entry"
        self.date_entry.configure(state="normal")
        self.date_entry.delete(0, customtkinter.END)
        self.date_entry.insert(0, self.cal.get_date())
        self.date_entry.configure(state="disabled")
        self.destroy()

    def clear_date(self):
        "clear the date entry so seatch within the whole data"
        self.date_entry.configure(state="normal")
        self.date_entry.delete(0, customtkinter.END)
        self.date_entry.configure(state="disabled")
        self.destroy()