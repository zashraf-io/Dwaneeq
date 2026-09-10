import customtkinter
from tkcalendar import Calendar
import datetime
from arabic_reshaper import arabic_reshaper as ar
from some_classes import *
import db
import config

class CategoryManagerDialog(tkinter.Toplevel):
    def __init__(self, master, trans_type: str="expense", on_update=None):
        super().__init__(master)
        self.master = master
        self.trans_type = trans_type
        self.on_update = on_update

        title_text = ar.reshape(config.choosed_lang.get("manage_categories", "Manage Categories"))
        self.title(title_text)

        self.icon = PhotoImage(file=config.resource_path("images/app_icon.png"))
        self.iconphoto(True, self.icon)

        self.geometry("460x520")
        self.resizable(False, False)
        self.attributes('-topmost', True)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)


        # Background frame
        self.background_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.background_frame.pack(fill="both") 

        # Type selector
        self.type_var = customtkinter.StringVar(value=self.trans_type)
        self.type_frame = customtkinter.CTkFrame(self.background_frame, fg_color="transparent")
        self.type_frame.pack(fill="x", padx=20, pady=(15, 5))

        self.income_rb = customtkinter.CTkRadioButton(
            self.type_frame, text=config.choosed_lang["income"], value="income",
            variable=self.type_var, fg_color="green", command=self.on_type_changed
        )
        self.income_rb.pack(side="left" if config.direction == "ltr" else "right", padx=10)

        self.expense_rb = customtkinter.CTkRadioButton(
            self.type_frame, text=config.choosed_lang["expense"], value="expense",
            variable=self.type_var, fg_color="red", command=self.on_type_changed
        )
        self.expense_rb.pack(side="left" if config.direction == "ltr" else "right", padx=10)

        # Add Category Frame
        self.add_frame = customtkinter.CTkFrame(self.background_frame)
        self.add_frame.pack(fill="x", padx=20, pady=10)

        curr_lang = config.get_current_lang()
        other_lang = "ar" if curr_lang == "en" else "en"
        curr_lang_name = "English" if curr_lang == "en" else "العربية"
        other_lang_name = "العربية" if curr_lang == "en" else "English"

        self.name_entry = customtkinter.CTkEntry(
            self.add_frame, placeholder_text=f"{config.choosed_lang.get('new_category_name', 'Category Name')} ({curr_lang_name})"
        )
        self.name_entry.pack(fill="x", padx=15, pady=(10, 5))

        # Optional translation entry (toggled by small button)
        self.show_translation = False
        self.trans_entry = customtkinter.CTkEntry(
            self.add_frame, placeholder_text=f"{config.choosed_lang.get('new_category_name', 'Category Name')} ({other_lang_name})"
        )

        self.btn_row = customtkinter.CTkFrame(self.add_frame, fg_color="transparent")
        self.btn_row.pack(fill="x", padx=15, pady=(5, 10))

        self.toggle_trans_btn = customtkinter.CTkButton(
            self.btn_row, text=f"+ {config.choosed_lang.get('add_translation', 'Add Translation')}",
            width=120, height=28, fg_color="grey40", hover_color="grey50", command=self.toggle_translation_entry
        )
        self.toggle_trans_btn.pack(side="left" if config.direction == "ltr" else "right")

        self.add_btn = customtkinter.CTkButton(
            self.btn_row, text=config.choosed_lang.get("add_category", "Add Category"),
            width=100, height=28, command=self.save_new_category
        )
        self.add_btn.pack(side="right" if config.direction == "ltr" else "left")

        self.msg_label = customtkinter.CTkLabel(self.add_frame, text="", text_color="red")
        self.msg_label.pack(pady=(0, 5))

        # Categories list scrollable
        self.list_frame = customtkinter.CTkScrollableFrame(self.background_frame, height=240)
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        self.render_categories()

    def toggle_translation_entry(self):
        if not self.show_translation:
            self.trans_entry.pack(after=self.name_entry, fill="x", padx=15, pady=(0, 5))
            self.toggle_trans_btn.configure(text=f"- {config.choosed_lang.get('cancel', 'Cancel')}")
            self.show_translation = True
        else:
            self.trans_entry.delete(0, "end")
            self.trans_entry.pack_forget()
            self.toggle_trans_btn.configure(text=f"+ {config.choosed_lang.get('add_translation', 'Add Translation')}")
            self.show_translation = False

    def on_type_changed(self):
        self.trans_type = self.type_var.get()
        self.msg_label.configure(text="")
        self.render_categories()

    def save_new_category(self):
        name = self.name_entry.get().strip()
        if not name:
            self.msg_label.configure(text=config.choosed_lang.get("category_name_empty", "Category name cannot be empty"))
            return

        curr_lang = config.get_current_lang()
        other_lang = "ar" if curr_lang == "en" else "en"
        trans_name = self.trans_entry.get().strip() if self.show_translation else name

        translations = {
            curr_lang: name,
            other_lang: trans_name if trans_name else name
        }

        user_id = config.get_current_user_id()
        db.add_category(key=name, type=self.trans_type, is_builtin=False, user_id=user_id, translations=translations)

        self.name_entry.delete(0, "end")
        if self.show_translation:
            self.toggle_translation_entry()

        self.msg_label.configure(text="")
        self.render_categories()
        if self.on_update:
            self.on_update()

    def render_categories(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        lang = config.get_current_lang()
        user_id = config.get_current_user_id()
        categories = db.get_categories(self.trans_type, lang, user_id)

        for cat_id, name in categories:
            row = customtkinter.CTkFrame(self.list_frame, fg_color="grey20")
            row.pack(fill="x", pady=4, padx=2)

            name_lbl = customtkinter.CTkLabel(row, text=name, anchor="w" if config.direction == "ltr" else "e", font=("Arial", 14))
            name_lbl.pack(side="left" if config.direction == "ltr" else "right", padx=10, pady=6, fill="x", expand=True)

            del_btn = customtkinter.CTkButton(
                row, text="✕", width=28, height=28, fg_color="transparent", hover_color="#dc2626",
                command=lambda cid=cat_id: self.confirm_delete(cid)
            )
            del_btn.pack(side="right" if config.direction == "ltr" else "left", padx=4)

            rename_btn = customtkinter.CTkButton(
                row, text="✎", width=28, height=28, fg_color="transparent", hover_color="grey40",
                command=lambda cid=cat_id, cname=name: self.prompt_rename(cid, cname)
            )
            rename_btn.pack(side="right" if config.direction == "ltr" else "left", padx=4)

    def prompt_rename(self, cat_id: int, current_name: str):
        prompt = customtkinter.CTkInputDialog(
            text=f"{config.choosed_lang.get('rename', 'Rename')}:",
            title=config.choosed_lang.get("rename", "Rename")
        )
        new_val = prompt.get_input()
        if new_val and new_val.strip():
            lang = config.get_current_lang()
            other_lang = "ar" if lang == "en" else "en"
            # Keep both translations updated
            db.rename_category(cat_id, {lang: new_val.strip(), other_lang: new_val.strip()})
            self.render_categories()
            if self.on_update:
                self.on_update()

    def confirm_delete(self, cat_id: int):
        confirm_msg = config.choosed_lang.get("confirm_delete_category", "Are you sure you want to delete this category?")
        PopUpMessage(
            self, message=confirm_msg, button_name=config.choosed_lang.get("delete", "Delete"),
            cancel_btn=True, command=lambda: self.do_delete(cat_id)
        )

    def do_delete(self, cat_id: int):
        db.delete_category(cat_id)
        self.render_categories()
        if self.on_update:
            self.on_update()


class Transaction(customtkinter.CTkFrame):
    def __init__(self, master, edit_data=None):
        super().__init__(master)
        self.master = master
        self.edit_data = edit_data
        
        direction = config.direction
        align = config.align["add_transaction"][direction]

        self.grid_columnconfigure((0, 1), weight=1)

        title_text = config.choosed_lang.get("edit_transaction", "Edit Transaction") if self.edit_data else config.choosed_lang["add_transaction"]
        self.title = customtkinter.CTkLabel(self, text=title_text, font=("Arial", 30, "bold"))
        self.title.grid(row=0, column=0, columnspan=2, pady=10, sticky="EW")

        # transaction type taken
        self.type_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.type_frame.grid_columnconfigure((0, 1), weight=1)
        self.type_frame.grid(row=1, column=0, columnspan=2)

        self.type_var = customtkinter.StringVar(self, value=self.edit_data[2] if self.edit_data else "")
        self.income = customtkinter.CTkRadioButton(
            self.type_frame, text=config.choosed_lang["income"], fg_color="green",
            value='income', variable=self.type_var, command=self.choose_type
        )
        self.income.grid(row=0, column=0, pady=20, sticky="E")
        self.expense = customtkinter.CTkRadioButton(
            self.type_frame, text=config.choosed_lang["expense"], fg_color="red",
            value='expense', variable=self.type_var, command=self.choose_type
        )
        self.expense.grid(row=0, column=1, pady=20, sticky="W")

        # taking amount along with currency
        self.amount_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.amount_frame.grid(row=2, column=align["amount_labl"]["column"], padx=20, pady=20, sticky="EW")
        self.amount_frame.grid_columnconfigure((0, 1), weight=1)

        self.amount_label = customtkinter.CTkLabel(self.amount_frame, text=config.choosed_lang["amount"])
        self.amount_label.grid(row=0, column=align["amount_labl"]["column"], padx=20, pady=10, sticky=align["amount_labl"]["sticky"])

        self.amount_entry = NumEntry(
            self.amount_frame, placeholder_text=config.choosed_lang["enter_amount"], width=200,
            quick_plus_minus=True, align_direction=config.direction
        )
        if self.edit_data:
            self.amount_entry.insert(self.edit_data[4])
        self.amount_entry.grid(row=0, padx=40, column=align["amount_entry"]["column"])

        self.amount_currency_menu = CurrencyMenu(self.amount_frame, width=80)
        curr_val = self.edit_data[5] if self.edit_data else config.currency
        self.amount_currency_menu.set_value(curr_val)
        self.amount_currency_menu.grid(row=0, padx=15, column=align["currency"]["column"], sticky=align["currency"]["sticky"])

        # taking the category according to the type income/expense
        self.category_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.category_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.category_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=15, sticky="EW")

        self.cat_header = customtkinter.CTkFrame(self.category_frame, fg_color="transparent")
        self.cat_header.grid(row=0, column=0, columnspan=4, pady=5)

        self.cate_labl = customtkinter.CTkLabel(self.cat_header, text=config.choosed_lang["category"], font=("Roboto", 20, "bold"))
        self.cate_labl.pack(side="left" if direction == "ltr" else "right", padx=10)

        self.manage_cat_btn = customtkinter.CTkButton(
            self.cat_header, text="⚙ " + config.choosed_lang.get("manage_categories", "Manage"),
            width=70, height=26, font=("Arial", 12), fg_color="grey30", hover_color="grey40",
            command=self.open_category_manager
        )
        self.manage_cat_btn.pack(side="left" if direction == "ltr" else "right", padx=10)

        initial_cat_id = str(self.edit_data[8]) if (self.edit_data and len(self.edit_data) > 8 and self.edit_data[8]) else ""
        self.category_var = customtkinter.StringVar(self.category_frame, value=initial_cat_id)

        # taking note
        self.note_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.note_frame.grid(row=4, column=align["note_labl"]["column"], padx=20, pady=10, sticky=align["note_labl"]["sticky"])

        self.note_labl = customtkinter.CTkLabel(self.note_frame, text=config.choosed_lang["add_note"])
        self.note_labl.grid(row=0, padx=20, column=align["note_labl"]["column"], sticky=align["note_labl"]["sticky"])

        self.note_text_box = customtkinter.CTkTextbox(self.note_frame, width=200, height=60)
        if self.edit_data and self.edit_data[7]:
            self.note_text_box.insert("0.0", str(self.edit_data[7]))
        self.note_text_box.grid(row=0, padx=15, column=align["note_text_box"]["column"])

        # taking date
        self.date_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.date_frame.grid(row=5, column=align["date_frame"]["column"], padx=20, pady=10, sticky=align["date_frame"]["sticky"])

        self.date_labl = customtkinter.CTkLabel(self.date_frame, text=config.choosed_lang["date"])
        self.date_labl.grid(row=0, padx=10, column=align["date_labl"]["column"])

        self.date_entry = customtkinter.CTkEntry(self.date_frame)
        initial_date = self.edit_data[6] if self.edit_data else datetime.datetime.now().strftime(r"%Y-%m-%d")
        self.date_entry.insert(0, initial_date)
        self.date_entry.configure(state="disabled")
        self.date_entry.grid(row=0, column=1)

        self.open_cal_btn = customtkinter.CTkButton(self.date_frame, text=config.choosed_lang["open_cal"], command=self.open_cal)
        self.open_cal_btn.grid(row=0, column=align["open_cal_btn"]["column"])

        # save button
        self.btns_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.btns_frame.grid(row=6, pady=20, column=0, columnspan=2)

        btn_text = config.choosed_lang.get("update_btn", "Update") if self.edit_data else config.choosed_lang["save"]
        self.save_btn = customtkinter.CTkButton(self.btns_frame, text=btn_text, command=self.save_transaction)
        self.save_btn.grid(row=0, padx=10, column=0)

        self.cancel_btn = customtkinter.CTkButton(self.btns_frame, text=config.choosed_lang["cancel"], command=self.cancel)
        self.cancel_btn.grid(row=0, padx=10, column=1)

        if self.edit_data:
            self.choose_type()

    def open_category_manager(self):
        t = self.type_var.get() or "expense"
        CategoryManagerDialog(self, trans_type=t, on_update=self.choose_type)

    def choose_type(self):
        # Clear existing category radio buttons (keep header)
        for w in self.category_frame.winfo_children():
            if w != self.cat_header:
                w.destroy()

        t = self.type_var.get()
        if not t:
            return

        hover_c = "green" if t == "income" else "red"
        self.save_btn.configure(hover_color=hover_c)

        lang = config.get_current_lang()
        user_id = config.get_current_user_id()
        categories = db.get_categories(t, lang, user_id)

        row = 1
        col = 0
        for cat_id, cat_name in categories:
            rb = customtkinter.CTkRadioButton(
                self.category_frame, text=cat_name, value=str(cat_id),
                variable=self.category_var, fg_color=hover_c
            )
            rb.grid(row=row, column=col, padx=10, pady=8, sticky="W" if config.direction == "ltr" else "E")
            col += 1
            if col > 3:
                col = 0
                row += 1

    def open_cal(self):
        cal = DateCalender(self, self.date_entry)

    def cancel(self):
        if self.edit_data:
            self.master.clear_frame("destroy")
            self.master.open_side_bar()
            self.master.open_history()
            return

        self.type_var.set("")
        self.amount_entry.entry.delete(0, "end")
        self.category_var.set("")
        self.note_text_box.delete("0.0", "end")
        self.date_entry.configure(state="normal")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, datetime.datetime.now().strftime(r"%Y-%m-%d"))
        self.date_entry.configure(state="readonly")
        self.save_btn.configure(hover_color="grey")

        for w in self.category_frame.winfo_children():
            if w != self.cat_header:
                w.destroy()

        if hasattr(self, "message") and self.message:
            self.message.destroy()
            self.message = None

    def save_transaction(self):
        transaction_type = self.type_var.get()
        amount = self.amount_entry.get()
        currency = self.amount_currency_menu.get_currency()
        category_id_str = self.category_var.get()
        note = self.note_text_box.get("0.0", "end").strip()
        date = self.date_entry.get()

        show_message = ""
        if transaction_type == "":
            show_message = "transaction_type_error"
        elif amount == "":
            show_message = "amount_error"
        elif category_id_str == "":
            show_message = "category_error"

        if show_message:
            if hasattr(self, "message") and self.message:
                self.message.configure(text=config.choosed_lang[show_message])
            else:
                self.message = customtkinter.CTkLabel(self, text=config.choosed_lang[show_message], text_color="red")
            self.message.grid(row=7, column=0, columnspan=2)
        else:
            category_id = int(category_id_str)
            if self.edit_data:
                trans_id = self.edit_data[0]
                db.update_transaction(trans_id, float(amount), currency, transaction_type, category_id, date, note)
                self.master.clear_frame("destroy")
                self.master.open_side_bar()
                self.master.open_history()
            else:
                db.add_transaction(config.get_current_user_id(), float(amount), currency, transaction_type, category_id, date, note)
                self.cancel()
                self.master.clear_frame("destroy")
                self.master.open_side_bar()
                self.master.open_expense()