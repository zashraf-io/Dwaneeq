import customtkinter as ctk
import datetime
from history import History
import config
import data_helpers
import db

class Home(ctk.CTkScrollableFrame):
    def __init__(self, master) -> None:
        super().__init__(master)

        self.master = master
        self.grid_columnconfigure(0, weight=1)

        self.header = ctk.CTkLabel(self, text=config.choosed_lang["Home"], font=('Roboto', 20, 'bold'))
        self.header.grid(row=0, column=0, pady=15)

        # overview cards section
        self.balance_frame = ctk.CTkFrame(self, fg_color=config.choosed_colors["sidebar_bg"])
        self.balance_frame.grid(row=1, column=0, padx=100)

        self.balance_header = ctk.CTkLabel(self.balance_frame, text=config.choosed_lang["current_month_balance"], font=("Roboto", 18, "bold"))
        self.balance_header.grid(row=0, column=0, columnspan=4, pady=10)

            # Income Frame
        self.income_frame = ctk.CTkFrame(self.balance_frame)
        self.income_frame.grid(row=1, column=0, padx=20, pady=20)

        self.income_labl = ctk.CTkLabel(self.income_frame, text=config.choosed_lang["income"], font=("Roboto", 18, "bold"))
        self.income_labl.grid(row=0, column=0, padx=10)

        total_income = data_helpers.calc_amount(config.get_current_user_id(), 'income')
        self.income_amount = ctk.CTkLabel(self.income_frame, text=config.choosed_lang["symbols"][config.currency]+" "+str(total_income), font=("Roboto", 18))
        self.income_amount.grid(row=1, column=0, padx=10)
        
            # Expense Frame
        self.expense_frame = ctk.CTkFrame(self.balance_frame)
        self.expense_frame.grid(row=1, column=1, padx=20, pady=20)

        self.expense_labl = ctk.CTkLabel(self.expense_frame, text=config.choosed_lang["expense"], font=("Roboto", 18, "bold"))
        self.expense_labl.grid(row=0, column=0, padx=10)

        total_expense = data_helpers.calc_amount(config.get_current_user_id(), 'expense')
        self.expense_amount = ctk.CTkLabel(self.expense_frame, text=config.choosed_lang["symbols"][config.currency]+" "+str(total_expense), font=("Roboto", 18))
        self.expense_amount.grid(row=1, column=0, padx=10) 

            # Net Balance Frame
        self.net_balance_frame = ctk.CTkFrame(self.balance_frame)
        self.net_balance_frame.grid(row=1, column=2, padx=20, pady=20)

        self.net_balance_labl = ctk.CTkLabel(self.net_balance_frame, text=config.choosed_lang["net_balance"], font=("Roboto", 18, "bold"))
        self.net_balance_labl.grid(row=0, column=0, padx=10)

        net_balance = round(total_income - total_expense, 2)
        self.net_balance_amount = ctk.CTkLabel(self.net_balance_frame, text=config.choosed_lang["symbols"][config.currency]+" "+str(net_balance), font=("Roboto", 18, "bold"))
        if net_balance < 0:
            self.net_balance_amount.configure(text_color='red')
        elif net_balance > 0:
            self.net_balance_amount.configure(text_color='#5bb450')
            
        self.net_balance_amount.grid(row=1, column=0, padx=10)

            # Remaining in Budget
        self.remaining_budget_frame = ctk.CTkFrame(self.balance_frame)
        self.remaining_budget_frame.grid(row=1, column=3, padx=20, pady=20)

        if db.isfound_budget(config.get_current_user_id()):
            self.net_balance_labl = ctk.CTkLabel(self.remaining_budget_frame, text=config.choosed_lang["remaining_budget"], font=("Roboto", 18, "bold"))
            self.net_balance_labl.grid(row=0, column=0, padx=10)

            remaining_in_budget = round(data_helpers.get_total_budget(config.get_current_user_id()) - total_expense, 2)
            self.remaining_in_budget = ctk.CTkLabel(self.remaining_budget_frame, text=config.choosed_lang["symbols"][config.currency]+" "+str(remaining_in_budget), font=("Roboto", 18, "bold"))
            if remaining_in_budget < 0:
                self.remaining_in_budget.configure(text_color='red')
            else:
                self.remaining_in_budget.configure(text_color='#5bb450')
                
            self.remaining_in_budget.grid(row=1, column=0, padx=10)

        else:
            self.net_balance_labl = ctk.CTkLabel(self.remaining_budget_frame, text=config.choosed_lang["not_budget_set"], font=("Roboto", 18, "bold"))
            self.net_balance_labl.grid(row=0, column=0, padx=10)



        # Mini-Stats section
        self.category_budget_overview_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.category_budget_overview_frame.grid(row=2, column=0, pady=15, padx=10)

        self.categories_frame = ctk.CTkFrame(self.category_budget_overview_frame)
        if config.direction == "rtl":
            column = 1 
            sub_column = 0
        else:
            column = 0
            sub_column = 1

        self.categories_frame.grid(row=0, column=column, pady=20, padx=50, sticky="NW")

        categories_frame_label = ctk.CTkLabel(self.categories_frame, text=config.choosed_lang["categories_expenses_current_month"], font=("Roboto", 20, 'bold'))
        categories_frame_label.grid(row=0, column=0, columnspan=3, pady=15)

        current_month = datetime.datetime.now().strftime(r"%Y-%m")
        categories = db.get_expense_categories(config.get_current_user_id(), current_month)
        row=1
        if categories:
            if config.direction == 'rtl':
                col = 2
                sub_col = 0
            else:
                col = 0
                sub_col = 2
            
            for category in categories:
                amount = data_helpers.calc_amount(config.get_current_user_id(), 'expense', category, current_month)
                cat_name = db.get_category_name(category, config.get_current_lang())
                label = ctk.CTkLabel(self.categories_frame, text=cat_name, font=("Roboto", 18))
                label.grid(row=row, column=col)
                amount_label = ctk.CTkLabel(self.categories_frame, text=str(amount), font=("Roboto", 18))
                amount_label.grid(row=row, column=1, padx=10)
                curr = ctk.CTkLabel(self.categories_frame, text=config.choosed_lang['symbols'][config.currency], font=("Roboto", 18))
                curr.grid(row=row, column=sub_col)

                row += 1

            self.pie_frame = ctk.CTkFrame(self.category_budget_overview_frame)
            self.pie_frame.grid(row=0, column=sub_column, sticky="E")

            from stats import Stats
            self.c_idx = 0 if ctk.get_appearance_mode() == "Light" else 1
            self.tex_c = "black" if ctk.get_appearance_mode() == "Light" else "white"
        
            Stats.make_category_pie_chart(self, current_month)

        else:
            note = ctk.CTkLabel(self.categories_frame, text=config.choosed_lang["no_expense_yet"], font=("Roboto", 16, 'italic'))
            note.grid(row=row, pady=10, padx=10)

        #----------------
        self.separator = ctk.CTkFrame(self, height=2, fg_color="grey80")
        self.separator.grid(row=3, column=0, pady=50, columnspan=2, sticky="EW")

        # Recent transactions section
        self.recent_transactions_frame = ctk.CTkFrame(self)
        self.recent_transactions_frame.grid(row=4, padx=100, sticky="EW")
        
        recent_label = ctk.CTkLabel(self.recent_transactions_frame, text=config.choosed_lang["recent_transactions"], font=("Roboto", 18, "bold"))
        recent_label.pack(fill='x', pady=10)

        tree = History(self.recent_transactions_frame, False, 5)
        tree.pack(fill='x')

        view_all_btn = ctk.CTkButton(self.recent_transactions_frame, text=config.choosed_lang["view_all"], command=self.master.open_history)
        view_all_btn.pack(fill="x", pady=10)