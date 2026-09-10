import customtkinter as ctk
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import arabic_reshaper as ar
import config
import data_helpers
import db

class Stats(ctk.CTkFrame):
    def __init__(self,master):
        super().__init__(master)
        self.master = master
        self.grid_columnconfigure((0), weight=1)

        # Page Header
        header = ctk.CTkLabel(self, text=config.choosed_lang["statistics"], font=("Arial", 20, "bold"))
        header.grid(row=0, column=0, pady=20)

        # Balance frame
        self.balance_frame = ctk.CTkFrame(self)
        self.balance_frame.grid(row=1, column=0, padx=100)

            # Income Frame
        self.income_frame = ctk.CTkFrame(self.balance_frame)
        self.income_frame.grid(row=0, column=0, padx=20, pady=20)

        self.income_labl = ctk.CTkLabel(self.income_frame, text=config.choosed_lang["total_income"], font=("Roboto", 18, "bold"))
        self.income_labl.grid(row=0, column=0, padx=10)

        total_income = data_helpers.calc_amount(config.get_current_user_id(), 'income', month='all')
        self.income_amount = ctk.CTkLabel(self.income_frame, text=config.choosed_lang["symbols"][config.currency]+" "+str(total_income), font=("Roboto", 18))
        self.income_amount.grid(row=1, column=0, padx=10)
        
            # Expense Frame
        self.expense_frame = ctk.CTkFrame(self.balance_frame)
        self.expense_frame.grid(row=0, column=1, padx=20, pady=20)

        self.expense_labl = ctk.CTkLabel(self.expense_frame, text=config.choosed_lang["total_expense"], font=("Roboto", 18, "bold"))
        self.expense_labl.grid(row=0, column=0, padx=10)

        total_expense = data_helpers.calc_amount(config.get_current_user_id(), 'expense', month='all')
        self.expense_amount = ctk.CTkLabel(self.expense_frame, text=config.choosed_lang["symbols"][config.currency]+" "+str(total_expense), font=("Roboto", 18))
        self.expense_amount.grid(row=1, column=0, padx=10) 

            # Net Balance Frame
        self.net_balance_frame = ctk.CTkFrame(self.balance_frame)
        self.net_balance_frame.grid(row=0, column=2, padx=20, pady=20)

        self.net_balance_labl = ctk.CTkLabel(self.net_balance_frame, text=config.choosed_lang["net_balance"], font=("Roboto", 18, "bold"))
        self.net_balance_labl.grid(row=0, column=0, padx=10)

        net_balance = round(total_income - total_expense, 2)
        self.net_balance_amount = ctk.CTkLabel(self.net_balance_frame, text=config.choosed_lang["symbols"][config.currency]+" "+str(net_balance), font=("Roboto", 18, "bold"))
        if net_balance < 0:
            self.net_balance_amount.configure(text_color='red')
        elif net_balance > 0:
            self.net_balance_amount.configure(text_color='#5bb450')
            
        self.net_balance_amount.grid(row=1, column=0, padx=10)


        # Income VS Expense barchart
        months = db.get_months(config.get_current_user_id())
        x = np.arange(len(db.get_months(config.get_current_user_id())))

        incomes = [data_helpers.calc_amount(config.get_current_user_id(), 'income', month=month) for month in months]
        expenses = [data_helpers.calc_amount(config.get_current_user_id(), 'expense', month=month) for month in months]

        width=0.35

        self.c_idx = 0 if ctk.get_appearance_mode() == "Light" else 1
        self.tex_c = "black" if ctk.get_appearance_mode() == "Light" else "white"

        fig, ax = plt.subplots(figsize=(5, 5), layout='constrained')
        fig.set_facecolor(self.cget('fg_color')[self.c_idx])
        income_bar = ax.bar(x - width/2, incomes, label=config.choosed_lang["bar_chart_labels"]["income"], width=width, edgecolor="white", linewidth=0.7, color="green")
        expense_bar = ax.bar(x + width/2, expenses, label=config.choosed_lang["bar_chart_labels"]["expenses"], width=width, edgecolor="white", linewidth=0.7, color="red")
        ax.bar_label(income_bar, padding=3, color=self.tex_c, labels=[f"{int(v.get_height())}" for v in income_bar])
        ax.bar_label(expense_bar, padding=3, color=self.tex_c, labels=[f"{int(v.get_height())}" for v in expense_bar])
        ax.set_xticks(x, months)
        ax.set_facecolor(self.cget('fg_color')[self.c_idx])
        ax.set_xlabel(config.choosed_lang["months"], color=self.tex_c)
        ax.set_ylabel(config.choosed_lang[config.currency], color=self.tex_c)
        ax.set_title(config.choosed_lang["bar_title"], color=self.tex_c)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.tex_c)
        ax.spines['bottom'].set_color(self.tex_c)
        ax.tick_params(axis='x', colors=self.tex_c)
        ax.tick_params(axis='y', colors=self.tex_c)
        ax.legend()

        fig.tight_layout()
        income_expense = FigureCanvasTkAgg(fig, master=self,)
        income_expense.draw()
        income_expense.get_tk_widget().grid(row=2, sticky="W")
        
        # category Expenses Pie chart
        self.pie_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.pie_frame.grid(row=2, sticky='E')

        if months:
            self.pie_chart_month_menu = ctk.CTkOptionMenu(self.pie_frame, values=months[::-1], command=self.make_category_pie_chart)
            self.pie_chart_month_menu.grid(row=0, pady=5, padx=20, sticky="E")
            self.make_category_pie_chart()


    def make_category_pie_chart(self, value=""):
        month = value if value else self.pie_chart_month_menu.get()
        categories = db.get_expense_categories(config.get_current_user_id(), month)
        amounts = [data_helpers.calc_amount(config.get_current_user_id(), 'expense', category, month) for category in categories]

        fig, ax = plt.subplots()

        if config.lang_name == "ar":
            cat_labels = [ar.reshape(db.get_category_name(category, 'ar')) for category in categories]
        else:
            cat_labels = [db.get_category_name(category, 'en') for category in categories]
        ax.pie(amounts, autopct="%1.1f%%", labels=cat_labels,
                                            textprops={'color':self.tex_c})
        ax.set_title(config.choosed_lang["piechart_categories_title"], {'color':self.tex_c})
        fig.set_facecolor(self.cget('fg_color')[self.c_idx])
        
        fig.tight_layout()
        categories_pie = FigureCanvasTkAgg(fig, master=self.pie_frame)
        categories_pie.draw()
        categories_pie.get_tk_widget().grid(row=1)