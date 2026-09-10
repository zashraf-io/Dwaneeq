import customtkinter
import datetime
import some_classes
import config
import db
import data_helpers
# align = config.direction
# if align == "rtl":
#     self.direction = "right"
#     self.sub_direction = "left"
# else:
#     self.direction = "left"
#     self.sub_direction = "right"
# col_align = config.align["budget"][align]


class TakeBudget(customtkinter.CTkFrame):
    def __init__(self, master, edit: bool=False):
        super().__init__(master)
        self.master = master
        self.edit = edit

        self.align = config.direction
        if self.align == "rtl":
            self.direction = "right"
            self.sub_direction = "left"
        else:
            self.direction = "left"
            self.sub_direction = "right"

        self.open_add_budget_frame()

    def open_add_budget_frame(self):
        "Add a budget Dynamic Frame"
        self.add_budget_frame = customtkinter.CTkFrame(self)
        self.add_budget_frame.grid_columnconfigure(0, weight=1)
        self.add_budget_frame.pack(side=self.direction, fill="x", anchor="n", expand=True, pady=10, padx=20)

        self.add_budget_label = customtkinter.CTkLabel(self.add_budget_frame, text=config.choosed_lang["add_budget_labl"], font=("Arial", 25, "bold"))
        self.add_budget_label.grid(row=0, pady=15)

        self.row1 = customtkinter.CTkFrame(self.add_budget_frame, fg_color="transparent")
        self.row1.grid(row=1)

        self.total_budget_frame = customtkinter.CTkFrame(self.row1, fg_color="transparent")
        self.total_budget_frame.pack(side=self.direction, padx=20)
        self.total_budget_label = customtkinter.CTkLabel(self.total_budget_frame, text=config.choosed_lang["total_budget"])
        self.total_budget_label.pack(side=self.direction)
        self.total_budget_entry = some_classes.NumEntry(self.total_budget_frame, align_direction=self.align, placeholder_text=config.choosed_lang["enter_total_budget"])
        self.total_budget_entry.pack(side=self.sub_direction)

        self.savings_frame = customtkinter.CTkFrame(self.row1, fg_color="transparent")
        self.savings_frame.pack(side=self.sub_direction, padx=100)

        self.savings_label = customtkinter.CTkLabel(self.savings_frame, text=config.choosed_lang["savings"])
        self.savings_label.pack(side=self.direction)
        self.savings_entry = some_classes.NumEntry(self.savings_frame, align_direction=self.align)
        self.savings_entry.pack(side=self.sub_direction)
        
        self.row2 = customtkinter.CTkFrame(self.add_budget_frame, fg_color="transparent")
        self.row2.grid(row=2, pady=5, padx=10)

        self.budget_currency_frame = customtkinter.CTkFrame(self.row2, fg_color="transparent")
        self.budget_currency_frame.pack(side="bottom")

        self.budget_currency_label = customtkinter.CTkLabel(self.budget_currency_frame, text=config.choosed_lang["choose_budget_currency"])
        self.budget_currency_label.pack(side=self.direction, padx=5)

        self.budget_currency_menu = some_classes.CurrencyMenu(self.budget_currency_frame)
        self.budget_currency_menu.set_value(config.currency)
        self.budget_currency_menu.pack(side=self.sub_direction)

        self.row3 = customtkinter.CTkFrame(self.add_budget_frame, fg_color="transparent")
        self.row3.grid(row=3, pady=5, padx=10)

        self.auto_budget_chackvar = customtkinter.BooleanVar(self.row3)
        self.budget_checkbox = customtkinter.CTkCheckBox(self.row3, text=config.choosed_lang["apply_for_coming_months"])
        self.budget_checkbox.pack()

        self.row4 = customtkinter.CTkFrame(self.add_budget_frame, height=2, fg_color="grey50")
        self.row4.grid(row=4, pady=15, sticky="EW")

        self.categories_budget_frame = customtkinter.CTkScrollableFrame(self.add_budget_frame)
        self.categories_budget_frame.grid(row=5, padx=20, pady=10, sticky="EW")

        self.label = customtkinter.CTkLabel(self.categories_budget_frame, text=config.choosed_lang["plan_detail_expenses"], font=("Arial", 25, "bold"))
        self.label.pack(side="top", pady=15)

        self.add_category_btn = customtkinter.CTkButton(self.categories_budget_frame, text=config.choosed_lang["add_category"], command=self.add_category)
        self.add_category_btn.pack(side="bottom", anchor="s", padx=10, pady=10)

        self.buttons_frame = customtkinter.CTkFrame(self.add_budget_frame, fg_color="transparent")
        self.buttons_frame.grid(row=6)


        self.save_btn = customtkinter.CTkButton(self.buttons_frame, text=config.choosed_lang["save"], command=self.save_budget)
        self.save_btn.pack(fill="x", anchor="center")

        self.categories_budget_set = {}

        self.cancel_btn = customtkinter.CTkButton(self.buttons_frame, text=config.choosed_lang["cancel"], command=self.cancel)
        self.cancel_btn.pack(fill="x", anchor="center", pady=10)

        if self.edit:

            budget_id = db.get_latest_budget_info(config.get_current_user_id())[0]

            budget_data, categories_data = db.get_budget(budget_id)
            

            self.total_budget_entry.insert(budget_data[0])
            self.savings_entry.insert(budget_data[1])
            self.budget_currency_menu.set_value(budget_data[2])
            if budget_data[3]:
                self.budget_checkbox.select()
            else:
                self.budget_checkbox.deselect()

            for item in categories_data:
                cat_id = item[0]
                amount = item[2]
                self.add_category(cat_id, amount)


    def add_category(self, category=None, amount=None):
        category_frame = customtkinter.CTkFrame(self.categories_budget_frame)
        category_frame.pack(fill="x", pady=5)

        categ_labl = customtkinter.CTkLabel(category_frame, text=config.choosed_lang["category"])
        categ_labl.pack(side=self.direction, padx=10, anchor="n")

        category_menu = some_classes.CategoryMenu(category_frame, type="expense")
        category_menu.pack(side=self.direction, anchor="s")

        amount_labl = customtkinter.CTkLabel(category_frame, text=config.choosed_lang["amount"])
        amount_labl.pack(side=self.direction, padx=10)

        amount_entry = some_classes.NumEntry(category_frame, align_direction=self.align)
        amount_entry.pack(side=self.direction)

        del_btn = customtkinter.CTkButton(category_frame, text=config.choosed_lang["delete"], width=50,
                                                    command=lambda: self.delete_category_budget(category_frame))
        del_btn.pack(side=self.direction, padx=80)

        self.categories_budget_set.update({category_frame : [category_menu, amount_entry]})
        
        if category:
            category_menu.set_value(category)
        if amount:
            amount_entry.insert(amount)

    def cancel(self):
        self.master.master.set_budget_btn.pack()
        self.destroy()

    def delete_category_budget(self, frame):
        del self.categories_budget_set[frame]
        frame.destroy()

    def save_budget(self):
        
        # checking the repeated categories and excluding the non-specified categories
        choosed_categories = []
        for frame in self.categories_budget_set:
            if self.categories_budget_set[frame][1].get() != "":
                category = self.categories_budget_set[frame][0].get()
                if category in choosed_categories:
                    if hasattr(self, "save_note"):
                        self.save_note.configure(text=config.choosed_lang["save_budget_note_set_two_categories"])
                    else:
                        self.save_note = customtkinter.CTkLabel(self.buttons_frame, text=config.choosed_lang["save_budget_note_set_two_categories"],
                                                        text_color="red")
                    self.save_note.pack(padx=10, pady=10)
                    return
                else:
                    choosed_categories.append(self.categories_budget_set[frame][0].get())
            else:
                if hasattr(self, "save_note"):
                        self.save_note.configure(text=config.choosed_lang["save_budget_note_category_not_specified"])
                else:
                    self.save_note = customtkinter.CTkLabel(self.buttons_frame, text=config.choosed_lang["save_budget_note_category_not_specified"],
                                                        text_color="red")
                self.save_note.pack(padx=10, pady=10)
                return

        total_budget = self.total_budget_entry.get()
        savings = self.savings_entry.get()
        currency = self.get_currency()
        is_auto = self.budget_checkbox.get()

        if total_budget == "":
            if hasattr(self, "save_note"):
                self.save_note.configure(text=config.choosed_lang["save_budget_note_total_budget_not_set"])
            else:
                self.save_note = customtkinter.CTkLabel(self.buttons_frame, text=config.choosed_lang["save_budget_note_total_budget_not_set"],
                                                        text_color="red")
                self.save_note.pack(padx=10, pady=10)
            return

        if savings == "":
            if hasattr(self, "save_note"):
                self.save_note.configure(text=config.choosed_lang["save_budget_note_savings_budget_not_set"])
            else:
                self.save_note = customtkinter.CTkLabel(self.buttons_frame, text=config.choosed_lang["save_budget_note_savings_budget_not_set"],
                                                        text_color="red")
                self.save_note.pack(padx=10, pady=10)
            return

        if not self.edit:
            db.add_budget(config.get_current_user_id(), total_budget, savings, currency, is_auto=is_auto)

        budget_id = db.get_latest_budget_info(config.get_current_user_id())[0]

        if self.edit:
            db.edit_budget(config.get_current_user_id(), budget_id, total_budget, savings, currency, is_auto)
            db.delete_category_budget(budget_id)

        for frame in self.categories_budget_set:
            cat_id = self.categories_budget_set[frame][0].get_category_id()
            if cat_id is not None:
                db.add_category_budget(budget_id, cat_id, float(self.categories_budget_set[frame][1].get()))

        self.master.master.master.clear_frame("destroy")
        self.master.master.master.open_side_bar()
        self.master.master.master.open_budget()

    def get_currency(self):
        return self.budget_currency_menu.get_currency()

class Budget(customtkinter.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.align = config.direction
        if self.align == "rtl":
            self.direction = "right"
            self.sub_direction = "left"
        else:
            self.direction = "left"
            self.sub_direction = "right"

        col_align = config.align["budget"][self.align]


        heading = customtkinter.CTkLabel(self, text=config.choosed_lang["budget_heading"], font=("Arial", 30))
        heading.pack(anchor="center", pady=20)

        date = datetime.datetime.now().strftime(r"%Y-%m")

        self.budget_overview_frame = customtkinter.CTkFrame(self, border_width=1)
        self.budget_overview_frame.pack(fill="x", padx=50, pady=20, expand=True)
        if config.direction == "rtl":
            self.budget_overview_frame.grid_columnconfigure((0), weight=1)
        else:
            self.budget_overview_frame.grid_columnconfigure((2), weight=1)

        currency = config.choosed_lang[config.currency]

        self.label = customtkinter.CTkLabel(self.budget_overview_frame, text=date+config.choosed_lang["budget_over_view"], font=("Arial", 20))
        self.label.grid(row=0, column=0, pady=5, columnspan=3)

        # Total Budget
        self.total_budget_label = customtkinter.CTkLabel(self.budget_overview_frame, text=config.choosed_lang["total_budget"], font=("Arial", 16, "bold"))
        self.total_budget_label.grid(row=1, column=col_align["total_budget_lbl"]["column"], sticky=col_align["total_budget_lbl"]["sticky"], padx=10)
        
        total_budget = data_helpers.get_total_budget(config.get_current_user_id())
        self.total_budget_amount = customtkinter.CTkLabel(self.budget_overview_frame, text=total_budget, font=("arial", 16))
        self.total_budget_amount.grid(row=1, column=col_align["total_budget_amount"]["column"], sticky=col_align["total_budget_amount"]["sticky"])

        self.budget_currency = customtkinter.CTkLabel(self.budget_overview_frame, text=currency, font=("Arial", 16))
        self.budget_currency.grid(row=1, padx=10, column=col_align["currency"]["column"], sticky=col_align["currency"]["sticky"])
        
        # Spent
        self.spent_label = customtkinter.CTkLabel(self.budget_overview_frame, text=config.choosed_lang["spent_so_far"], font=("Arial", 16, "bold"))
        self.spent_label.grid(row=2, column=col_align["spent_lbl"]["column"], sticky=col_align["spent_lbl"]["sticky"], padx=10)

        spent_amount = data_helpers.calc_amount(config.get_current_user_id(), "expense")
        self.spent_amount = customtkinter.CTkLabel(self.budget_overview_frame, text=spent_amount, font=("arial", 16))
        self.spent_amount.grid(row=2, column=col_align["spent_amount"]["column"], sticky=col_align["spent_amount"]["sticky"])

        spent_currency = customtkinter.CTkLabel(self.budget_overview_frame, text=currency, font=("Arial", 16))
        spent_currency.grid(row=2, padx=10, column=col_align["currency"]["column"], sticky=col_align["currency"]["sticky"])

        # Remaining
        self.remaining_label = customtkinter.CTkLabel(self.budget_overview_frame, text=config.choosed_lang["remaining"], font=("Arial", 16, "bold"))
        self.remaining_label.grid(row=3, column=col_align["remaining_lbl"]["column"], sticky=col_align["remaining_lbl"]["sticky"], padx=10)

        remaining_amount = config.choosed_lang["not_set"] if total_budget==config.choosed_lang["not_set"] else round(total_budget - spent_amount, 2)
        self.remaining_amount = customtkinter.CTkLabel(self.budget_overview_frame, text=remaining_amount, font=("arial", 16))
        if remaining_amount != config.choosed_lang["not_set"] and remaining_amount < 0:
            self.remaining_amount.configure(text_color="red", font=("arial", 16, "bold"))
        self.remaining_amount.grid(row=3, pady=1, column=col_align["remaining_amount"]["column"], sticky=col_align["remaining_amount"]["sticky"])

        remaining_currency = customtkinter.CTkLabel(self.budget_overview_frame, text=currency, font=("Arial", 16))
        remaining_currency.grid(row=3, padx=10, column=col_align["currency"]["column"], sticky=col_align["currency"]["sticky"])

        # Category Budget table
        self.category_budget_overview_label = customtkinter.CTkLabel(self.budget_overview_frame, font=("Arial", 18, "bold"), text=config.choosed_lang["category_budget_overview_label"])
        self.category_budget_overview_label.grid(row=4, column=0, columnspan=3)

        budget_info = db.get_latest_budget_info(config.get_current_user_id())
        if budget_info != "no budget":
            budget = db.get_budget(budget_info[0])
            category_budgets = budget[1]
            budget_currency = budget[0][2]

            row = 5
            if not category_budgets:
                self.category_budget_not_set_note = customtkinter.CTkLabel(self.budget_overview_frame, text=config.choosed_lang["category_budget_not_set_note"])
                self.category_budget_not_set_note.grid(row=row, column=0, columnspan=2)
            else:
                for item in category_budgets:
                    cat_id = item[0]
                    cat_name = item[1]
                    b_amount = item[2]
                    self.category = customtkinter.CTkLabel(self.budget_overview_frame, font=("Arial", 16, "bold"), text=cat_name)
                    self.category.grid(row=row, column=col_align["total_budget_lbl"]["column"])

                    self.category_budget = customtkinter.CTkLabel(self.budget_overview_frame, font=("Arial", 16), text=data_helpers.from_to(b_amount, budget_currency, config.currency))
                    self.category_budget.grid(row=row, column=col_align["total_budget_amount"]["column"], sticky=col_align["currency"]["sticky"])

                    self.currency = customtkinter.CTkLabel(self.budget_overview_frame, font=("Arial", 16), text=currency)
                    self.currency.grid(row=row, padx=10, pady=1,column=col_align["currency"]["column"], sticky=col_align["currency"]["sticky"])

                    row += 1

        separator = customtkinter.CTkFrame(self, height=2, fg_color="grey60")
        separator.pack(fill="x", pady=20)

        self.budget_setting_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.budget_setting_frame.pack(fill="x")

        if db.isfound_budget(config.get_current_user_id()):
            def open_edit_budget_frame():
                self.set_budget_btn.pack_forget()
                edit_budget = TakeBudget(self.budget_setting_frame, edit=True,)
                edit_budget.pack()

            self.set_budget_btn = customtkinter.CTkButton(self.budget_setting_frame, font=("Arial", 16), text=config.choosed_lang["edit_budget"], command=open_edit_budget_frame)
            self.set_budget_btn.pack()

        else:
            def open_add_budget_frame():
                self.set_budget_btn.pack_forget()
                add_budget = TakeBudget(self.budget_setting_frame)
                add_budget.pack()

            self.set_budget_btn = customtkinter.CTkButton(self.budget_setting_frame, font=("Arial", 16), text=config.choosed_lang["add_budget"], command=open_add_budget_frame)
            self.set_budget_btn.pack()

        separator = customtkinter.CTkFrame(self, height=2, fg_color="grey60")
        separator.pack(fill="x", pady=20)


        # Mini stats for budget in the current month
        self.mini_stats_frame = customtkinter.CTkFrame(self, border_width=1)
        self.mini_stats_frame.pack(fill='x')

        if config.direction == "rtl":
            self.mini_stats_frame.grid_columnconfigure((0), weight=1)
        else:
            self.mini_stats_frame.grid_columnconfigure((2), weight=1)

        if budget_info != "no budget":
            if category_budgets:
                row = 0
                for item in category_budgets:
                    cat_id = item[0]
                    cat_name = item[1]
                    cat_budget = item[2]
                    spent = data_helpers.calc_amount(config.get_current_user_id(), 'expense', cat_id)
                    budget_in_curr = data_helpers.from_to(cat_budget, budget_currency, config.currency)
                    spent_percent = spent / budget_in_curr if budget_in_curr > 0 else 0

                    self.category = customtkinter.CTkLabel(self.mini_stats_frame, font=("Arial", 16, "bold"), text=cat_name)
                    self.category.grid(row=row, padx=10, column=col_align["total_budget_lbl"]["column"])

                    self.category_progress_bar = customtkinter.CTkProgressBar(self.mini_stats_frame)
                    self.category_progress_bar.set(min(1.0, spent_percent))

                    self.category_progress_bar.grid(row=row, column=col_align["total_budget_amount"]["column"], sticky=col_align["currency"]["sticky"])

                    self.percent = customtkinter.CTkLabel(self.mini_stats_frame, font=("Arial", 16), text=f"({round(spent_percent*100, 2)}%)")
                    self.percent.grid(row=row, padx=10, pady=1,column=col_align["currency"]["column"], sticky=col_align["currency"]["sticky"])
                    
                    if spent_percent > 1:
                        self.percent.configure(font=("Arial", 16, "bold"), text_color="red")



                    row += 1












