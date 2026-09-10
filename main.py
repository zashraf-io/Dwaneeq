import customtkinter
from tkinter import PhotoImage
import datetime; from dateutil.relativedelta import relativedelta
from settings import Settings; from login_signup import Login_Sinup; from addtransaction import Transaction; from home import Home
from history import History; from stats import Stats; from budget import Budget; from currency_calculator import CurrencyCalculator
import config; from config import resource_path; import db; import some_classes
import os, sys, threading

# setting the current working directory to the script directory to use relative paths safely
app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)


class NavigationBar(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.master = master
        self.grid_columnconfigure((0,1), weight=1)
        self.configure(fg_color=config.choosed_colors["sidebar_bg"], bg_color=config.choosed_colors["sidebar_bg"])

        self.home_btn = customtkinter.CTkButton(self, text=config.choosed_lang["Home"],
                                                    command=self.master.open_home)
        self.home_btn.pack(padx=20, pady=30)

        self.expense_btn = customtkinter.CTkButton(self, text=config.choosed_lang["add_transaction"],
                                                    command=self.master.open_expense)
        self.expense_btn.pack(padx=20, pady=30)

        self.history_btn = customtkinter.CTkButton(self, text=config.choosed_lang["History"],
                                                    command=self.master.open_history)
        self.history_btn.pack(padx=20, pady=30)

        self.budget_btn = customtkinter.CTkButton(self, text=config.choosed_lang["Budget"],
                                                    command=self.master.open_budget)
        self.budget_btn.pack(padx=20, pady=30)

        self.stats_btn = customtkinter.CTkButton(self, text=config.choosed_lang["Stats"],
                                                    command=self.master.open_stats)
        self.stats_btn.pack(padx=20, pady=30)

        self.settings_btn = customtkinter.CTkButton(self, text=config.choosed_lang["Settings"],
                                                    command=self.master.open_settings)
        self.settings_btn.pack(padx=20, pady=30)

        self.separator = customtkinter.CTkFrame(self, height=2, fg_color="grey80")
        self.separator.pack(pady=30, fill="x")

        self.currency_calculator_btn = customtkinter.CTkButton(self, text=config.choosed_lang["currency_calculator"],
                                                    command=self.master.open_currency_calculator)
        self.currency_calculator_btn.pack(padx=20, pady=30)

    def wrap_open(self, btn, command):
        self.disable_choosed(btn)
        command()

    def disable_choosed(self, btn):
        for button in self.winfo_children():
            try:
                if button.cget('state') == "disabled":
                    button.configure(state="normal", fg_color=config.choosed_colors["sidebar_btn"])
            except: pass

        btn.configure(state='disabled')
        btn.configure(fg_color=config.choosed_colors["accent"])
   
class App(customtkinter.CTk):
    def __init__(self) -> None:
        super().__init__()
 
        self.title("Dwaneeq")
        self.iconbitmap(resource_path("images/app_icon.ico"))

        self.icon = PhotoImage(file=resource_path("images/app_icon.png"))
        self.iconphoto(True, self.icon)


        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()
        self.width = 900
        self.height = 550

        self.geometry("%dx%d+0+0" % (self.width, self.height))


        customtkinter.set_default_color_theme(resource_path("themes/Black.json"))
        customtkinter.set_appearance_mode("dark")
        self.grid_columnconfigure((0), weight=1)
        self.grid_rowconfigure((0), weight=1)
        self.loaded_windows = {}


        # Background currency update once a day when app opens
        threading.Thread(target=self.background_currency_update, daemon=True).start()

        if db.isfound_remembered():
            user_id = db.isfound_remembered()
            self.load_app(user_id)
        else:
            self.open_login_window()

    def background_currency_update(self):
        try:
            db.update_currencies_rates()
        except Exception as e:
            print(f"Background currency update error: {e}")

    def load_app(self, user_id):
        config.set_current_user_id(user_id)
        try:
            self.get_saved_settings(user_id)
            self.update_auto_budget()               
            self.open_side_bar()
            self.open_home()
        except:
            db.open_database("all")
            self.get_saved_settings(user_id)
            self.update_auto_budget()               
            self.open_side_bar()
            self.open_home()


    def update_currencies(self):
        def retry():
            self.update_currencies()

        r = db.update_currencies_rates()
        if not r:
            return

        if r == 1:
            message = config.choosed_lang["check_connection_message"]
        elif r == 2:
            message = config.choosed_lang["api_responce_error_message"]
        elif r == 3:
            message = config.choosed_lang["unkown_error_message"]
        
        note = some_classes.PopUpMessage(self, message, button_name=config.choosed_lang['retry'], cancel_btn=True, command=retry, force=True)

    def update_auto_budget(self):
        """see the latest login date if more than one month passed without login, cancel all auto budget and alert the user
        else it updates the auto budget of the last month to the current month"""
        if not self.is_consistant_user():
            db.cancel_last_auto(config.get_current_user_id())
            note = some_classes.PopUpMessage(self, config.choosed_lang["not_consistant_user"])
            db.update_login_date(config.get_current_user_id())
            return

        db.update_login_date(config.get_current_user_id())
        db.update_auto_budget(config.get_current_user_id())
           
    def is_consistant_user(self) -> bool:
        """check if the user did not use the program for more than one month or no
        days are not considered, 1 month and 30 days is only one month
        THIS FUNCTION MUST BE CALLED BEFORE UPDATING THE USER LOGIN DATE"""
        login_date = db.get_login_date(config.get_current_user_id())
        login_date = datetime.datetime(int(login_date[:4]), int(login_date[5:7]), 1)
        now = datetime.datetime.now()
        delta = relativedelta(now, login_date)
        if delta.years:
            return False

        if delta.months > 1:
            return False
        
        return True

    def clear_frame(self, command="grid_remove", frames: tuple=()):
        """take command ['destroy', 'grid_remove'], default is 'grid_remove'
        take names of windows as a tuple to deal with ['home', 'expense', 'history', 'budget', 'stats', 'settings'], default is all windows"""
        windows = self.loaded_windows.values()

        if command == "grid_remove":
            for window in windows:
                window.grid_remove()
        elif command == "destroy":
            for window in self.winfo_children():
                window.destroy()

            self.loaded_windows = {}
            self.sidebar.destroy()

    def get_saved_settings(self, user_id) -> None:
        config.choosed_mode = db.get_setting(user_id, 'mode')
        if config.choosed_mode == 'light':
            customtkinter.set_appearance_mode("light")
            config.set_mode("light")
        else:
            customtkinter.set_appearance_mode("dark")
            config.set_mode("dark")

        config.choosed_theme = db.get_setting(user_id, 'theme')
        customtkinter.set_default_color_theme(resource_path("themes/"+config.choosed_theme.title()+".json"))
        config.set_theme(config.choosed_theme)
        
        if db.get_setting(user_id, 'lang') == 'en':
            config.lang_name = "en"
            config.direction = "ltr"
        elif db.get_setting(user_id, 'lang') == 'ar':
            config.lang_name = "ar"
            config.direction = "rtl"

        config.choosed_lang = config.LANG[config.lang_name]

        main_currency = db.get_setting(user_id, "main_currency")
        config.currency = main_currency

    def open_login_window(self, event=None) -> None:
        """opens the login window"""
        if hasattr(self, "login_window"):
            self.login_window.destroy()
        config.set_lang("ar")
        customtkinter.set_appearance_mode(config.choosed_mode)
        self.login_window = Login_Sinup(self)
        self.login_window.pack(fill="both", expand=True)

    def open_side_bar(self):
        """opens the navigation bar a the right of all windows"""
        self.sidebar = NavigationBar(self)
        self.sidebar.grid(row=0, column=1, sticky="NSE")

    def open_home(self):
        """opens the main app at the home window"""
        self.clear_frame()

        self.sidebar.disable_choosed(self.sidebar.home_btn)

        if "home" in self.loaded_windows.keys():
            self.loaded_windows["home"].grid(row=0, column=0, sticky="NSEW")
        else:
            self.home = Home(self)
            self.loaded_windows.update({"home" : self.home})

            self.home.grid(row=0, column=0, sticky="NSEW")
        
    def open_expense(self, edit_data=None):
        """"""
        self.clear_frame()

        if edit_data is not None:
            if "expense" in self.loaded_windows.keys():
                self.loaded_windows["expense"].destroy()
                del self.loaded_windows["expense"]
            self.expense = Transaction(self, edit_data=edit_data)
            self.loaded_windows["expense"] = self.expense
            self.expense.grid(row=0, column=0, sticky="NSEW")
        elif "expense" in self.loaded_windows.keys():
            self.loaded_windows["expense"].grid(row=0, column=0, sticky="NSEW")
        else:
            self.expense = Transaction(self)
            self.loaded_windows.update({"expense" : self.expense})
            self.expense.grid(row=0, column=0, sticky="NSEW")
        
        self.sidebar.disable_choosed(self.sidebar.expense_btn)

    def open_history(self):
        """"""
        self.clear_frame()

        if "history" in self.loaded_windows.keys():
            self.loaded_windows["history"].grid(row=0, column=0, sticky="NSEW")
        else:
            self.history = History(self)
            self.loaded_windows.update({"history" : self.history})

            self.history.grid(row=0, column=0,sticky="NSEW")
        
        self.sidebar.disable_choosed(self.sidebar.history_btn)

    def open_budget(self):
        """"""
        self.clear_frame()

        if "budget" in self.loaded_windows.keys():
            self.loaded_windows["budget"].grid(row=0, column=0, sticky="NSEW")
        else:
            self.budegt = Budget(self)
            self.loaded_windows.update({"budget" : self.budegt})
            
            self.budegt.grid(row=0, column=0,sticky="NSEW")
        
        self.sidebar.disable_choosed(self.sidebar.budget_btn)

    def open_stats(self):
        """"""
        self.clear_frame()

        if "stats" in self.loaded_windows.keys():
            self.loaded_windows["stats"].grid(row=0, column=0, sticky="NSEW")
        else:
            self.stats = Stats(self)
            self.loaded_windows.update({"stats" : self.stats})

            self.stats.grid(row=0, column=0, sticky="NSEW")
        
        self.sidebar.disable_choosed(self.sidebar.stats_btn)

    def open_settings(self):
        """opens the settings window"""
        self.clear_frame()

        if "settings" in self.loaded_windows.keys():
            self.loaded_windows["settings"].grid(row=0, column=0, sticky="NSEW")
        else:
            self.settings = Settings(self)
            self.loaded_windows.update({"settings" : self.settings})

            self.settings.grid(row=0, column=0,sticky="NSEW")
        
        self.sidebar.disable_choosed(self.sidebar.settings_btn)

    def open_currency_calculator(self):
        """"""
        self.clear_frame()

        if "currency_calculator" in self.loaded_windows.keys():
            self.loaded_windows["currency_calculator"].grid(row=0, column=0, sticky="NSEW")
        else:
            self.currency_calculator = CurrencyCalculator(self)
            self.loaded_windows.update({"currency_calculator" : self.currency_calculator})

            self.currency_calculator.grid(row=0, column=0,sticky="NSEW")
        
        self.sidebar.disable_choosed(self.sidebar.currency_calculator_btn)



# splash screen when using pyinstaller
try:
    import pyi_splash
    pyi_splash.update_text("Loading main window...")
    pyi_splash.close()
except ImportError:
    pass

app = App()
app.after_idle(lambda: app.state("zoomed"))     # Maximize the window
app.mainloop()
