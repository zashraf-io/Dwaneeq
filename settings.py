import customtkinter
import config; from config import resource_path
from some_classes import *
import db
from arabic_reshaper import arabic_reshaper as ar


class Settings(customtkinter.CTkFrame):
    def __init__(self,master):
        super().__init__(master)
        self.master = master
        self.grid_columnconfigure((0),weight=1)

        self.mode = customtkinter.CTkLabel(self, text=config.choosed_lang["Appearance_mode"], font=("Arial", 22, "bold"))
        self.mode.grid(row=0, column=0, pady=10, sticky="NEW")

        self.mode_btns_frame = customtkinter.CTkFrame(self)
        self.mode_btns_frame.grid(row=1, column=0)

        self.light_mode_btn = customtkinter.CTkButton(self.mode_btns_frame, text=config.choosed_lang["light_mode"],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # hover_color=config.choosed_colors["button_hover_color"],
                                                    # border_color=config.choosed_colors["button_border_color"],
                                                    command=self.light_mode)
        self.light_mode_btn.grid(row=1, column=0, padx=15, pady=10, sticky="NSE")
        self.dark_mode_btn = customtkinter.CTkButton(self.mode_btns_frame, text=config.choosed_lang["dark_mode"],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # hover_color=config.choosed_colors["button_hover_color"],
                                                    # border_color=config.choosed_colors["button_border_color"],
                                                    command=self.dark_mode)
        self.dark_mode_btn.grid(row=1, column=1, padx=15, pady=10, sticky="NSW")
        self.disable_choosed('mode')


        self.separator = customtkinter.CTkFrame(self, height=2, fg_color="grey80")
        self.separator.grid(row=2, column=0, pady=20, columnspan=2, sticky="EW")

        self.theme = customtkinter.CTkLabel(self, text=config.choosed_lang["theme"], font=("Arial", 22, "bold"))
        self.theme.grid(row=3, column=0,  columnspan=2, pady=10, sticky="NEW")

        self.theme_btns_frame  = customtkinter.CTkFrame(self)
        self.theme_btns_frame.grid(row=4, column=0, pady=20)

        self.blue = customtkinter.CTkButton(self.theme_btns_frame, text=config.choosed_lang["blue"],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # hover_color=config.choosed_colors["button_hover_color"],
                                                    # border_color=config.choosed_colors["button_border_color"],
                                                    command=lambda: self.change_theme("blue"))
        self.blue.grid(row=0, column=0, padx=25, pady=20)
        self.yellow = customtkinter.CTkButton(self.theme_btns_frame, text=config.choosed_lang["yellow"],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # hover_color=config.choosed_colors["button_hover_color"],
                                                    # border_color=config.choosed_colors["button_border_color"],
                                                    command=lambda: self.change_theme("yellow"))
        self.yellow.grid(row=0, column=1, padx=25, pady=20)
        self.green = customtkinter.CTkButton(self.theme_btns_frame, text=config.choosed_lang["green"],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # hover_color=config.choosed_colors["button_hover_color"],
                                                    # border_color=config.choosed_colors["button_border_color"],
                                                    command=lambda: self.change_theme("green"))
        self.green.grid(row=0, column=2, padx=25, pady=20)
        self.red = customtkinter.CTkButton(self.theme_btns_frame, text=config.choosed_lang["red"],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # hover_color=config.choosed_colors["button_hover_color"],
                                                    # border_color=config.choosed_colors["button_border_color"],
                                                    command=lambda: self.change_theme("red"))
        self.red.grid(row=0, column=3, padx=25, pady=20)

        self.purple = customtkinter.CTkButton(self.theme_btns_frame, text=config.choosed_lang["purple"],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # hover_color=config.choosed_colors["button_hover_color"],
                                                    # border_color=config.choosed_colors["button_border_color"],
                                                    command=lambda: self.change_theme("purple"))
        self.purple.grid(row=1, column=0, columnspan=2, padx=25, pady=20)

        self.grey = customtkinter.CTkButton(self.theme_btns_frame, text=config.choosed_lang["grey"],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # hover_color=config.choosed_colors["button_hover_color"],
                                                    # border_color=config.choosed_colors["button_border_color"],
                                                    command=lambda: self.change_theme("grey"))
        self.grey.grid(row=1, column=1, columnspan=2, padx=25, pady=20)

        self.black = customtkinter.CTkButton(self.theme_btns_frame, text=config.choosed_lang["black"],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # hover_color=config.choosed_colors["button_hover_color"],
                                                    # border_color=config.choosed_colors["button_border_color"],
                                                    command=lambda: self.change_theme("black"))
        self.black.grid(row=1, column=2, columnspan=2, padx=25, pady=20)


        self.disable_choosed('theme')

        self.separator = customtkinter.CTkFrame(self, height=2, fg_color="grey80")
        self.separator.grid(row=5, column=0, pady=20, columnspan=2, sticky="EW")
        
        self.lang_label = customtkinter.CTkLabel(self, text=config.choosed_lang["lang"], font=("Arial", 22, "bold"))
        self.lang_label.grid(row=6)

        self.english = "English"
        self.arabic = "عـــربــي"
        self.lang_btn = customtkinter.CTkSegmentedButton(self, values=[self.english, self.arabic],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # selected_color=config.choosed_colors["seg_selected_color"],
                                                    # unselected_color=config.choosed_colors["seg_unselected_color"],
                                                    # # selected_hover_color=config.choosed_colors[""],
                                                    # # unselected_hover_color=config.choosed_colors[""],
                                                    command=self.change_lang)
        if config.get_current_lang() == "en":
            self.lang_btn.set(self.english)
        elif config.get_current_lang() == "ar":
            self.lang_btn.set(self.arabic)
        self.lang_btn.grid(row=7, pady=20)
        

        self.separator = customtkinter.CTkFrame(self, height=2, fg_color="grey80")
        self.separator.grid(row=8, column=0, pady=20, columnspan=2, sticky="EW")
        
        if db.isfound_remembered():
            self.remember_var = customtkinter.BooleanVar(self, True)
        else:
            self.remember_var = customtkinter.BooleanVar(self, False)

        self.remember_checkbox = customtkinter.CTkCheckBox(self, variable=self.remember_var, onvalue=True, offvalue=False,
                                                            command=self.remember_checkbox_assign, text=config.choosed_lang["remember_login"])
        self.remember_checkbox.grid(row=8)

        self.account_lbl = customtkinter.CTkLabel(self, text=ar.reshape(config.choosed_lang["account"]) if config.lang_name=="ar" else config.choosed_lang["account"],
        font=("Arial", 22, "bold"))
        self.account_lbl.grid(row=9)

        self.change_pass_btn = customtkinter.CTkButton(self, text=config.choosed_lang["change_password"],
                                                    command=self.open_change_password_frame)
        self.change_pass_btn.grid(row=10, sticky="W", padx=50)

        self.main_currency_frame = customtkinter.CTkFrame(self)
        self.main_currency_frame.grid(row=10, padx=50, pady=10)

        self.main_currency_label = customtkinter.CTkLabel(self.main_currency_frame, text=config.choosed_lang["main_currency_across_app"])
        self.main_currency_label.grid(row=0)

        self.main_currency_menu = CurrencyMenu(self.main_currency_frame, command=self.update_main_currency)
        self.main_currency_menu.set_value(config.currency)
        self.main_currency_menu.grid(row=1)

        self.log_out_btn = customtkinter.CTkButton(self, text=config.choosed_lang["log_out"],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # hover_color=config.choosed_colors["button_hover_color"],
                                                    # border_color=config.choosed_colors["button_border_color"],
                                                    command=self.log_out)
        self.log_out_btn.grid(row=10, sticky="E", padx=50)

        self.delete_account_btn = customtkinter.CTkButton(self, text=config.choosed_lang["delete_account"],
                                                    # fg_color=config.choosed_colors["sidebar_btn"],
                                                    # hover_color=config.choosed_colors["button_hover_color"],
                                                    # border_color=config.choosed_colors["button_border_color"],
                                                    command=self.confirm_delete)
        self.delete_account_btn.grid(row=11, padx=50, sticky="W")

    def update_main_currency(self, value=None):
        main_currency = self.main_currency_menu.get_currency()
        config.currency = main_currency
        db.set_main_currency(config.get_current_user_id(), main_currency)

        self.master.clear_frame("destroy")
        self.master.open_side_bar()
        self.master.open_settings()

    def confirm_delete(self):
        "shows a pop up message to confirm deleteint the account permenantly"
        self.confirm_deleting_message = PopUpMessage(self, config.choosed_lang["confirm_deleting_message"], config.choosed_lang["delete"],
                                                        True, True, self.delete_account)

    def delete_account(self):
        db.delete_user(config.get_current_user_id())
        self.log_out()

    def log_out(self):
        "retrun to the login window"
        self.master.clear_frame("destroy")
        if db.isfound_remembered():
            db.remember_login(config.get_current_user_id(), False)
        config.set_current_user_id("not defined")
        config.set_lang("ar")
        config.set_mode("dark")
        config.set_theme("black")
        customtkinter.set_default_color_theme(resource_path("themes/Black.json"))
        config.currency = "EGP"
        self.master.open_login_window()

    def open_change_password_frame(self):
        "open a frame beside in the place of the button to check the old password, then write the new"
        self.change_pass_btn.grid_remove()
        self.change_frame = customtkinter.CTkFrame(self, fg_color=config.choosed_colors["sidebar_bg"])
        self.change_frame.grid_columnconfigure((0, 1), weight=1)
        self.change_frame.grid(row=9, sticky="W", padx=10)
        self.old_password_entry = customtkinter.CTkEntry(self.change_frame, show="●",fg_color="transparent", width=250,
                                                        placeholder_text=config.choosed_lang["write_old_password"])
    
        self.old_password_entry.grid(row=0, column=0, columnspan=2, pady=10, sticky="EW")
        self.continue_btn = customtkinter.CTkButton(self.change_frame, text=config.choosed_lang["continue"], command=self.continue_changing)
        self.continue_btn.grid(row=3, column=1, padx=10, pady=5, sticky="E")
        self.cancel_btn = customtkinter.CTkButton(self.change_frame, text=config.choosed_lang["cancel"], command=self.finish_changing)
        self.cancel_btn.grid(row=3, column=2, padx=10, pady=5, sticky="E")
        
    def continue_changing(self):
        "check the old password, if true open the new password, else show a message"
        if db.check_password(config.get_current_user_id(), self.old_password_entry.get()):
            self.old_password_entry.destroy()
            self.continue_btn.destroy()
            if hasattr(self, "note"):
                self.note.destroy()

            self.new_password_entry = customtkinter.CTkEntry(self.change_frame, show="●", fg_color="transparent", width=250,
                                                                placeholder_text=config.choosed_lang["enter_the_new_password"])
            self.new_password_entry.grid(row=0, column=0, columnspan=2, pady=10, sticky="EW")
            self.confirm_new_password = customtkinter.CTkEntry(self.change_frame, show="●",fg_color="transparent", width=250,
                                                                placeholder_text=config.choosed_lang["confirm_password"])
            self.confirm_new_password.grid(row=1, column=0, columnspan=2, sticky="EW")
            self.save_btn = customtkinter.CTkButton(self.change_frame, text=config.choosed_lang["save"], command=self.confirm_changing)
            self.save_btn.grid(row=3, column=1, padx=10, pady=5, sticky="E")
        else:
            self.note = customtkinter.CTkLabel(self.change_frame, text=config.choosed_lang["old_password_note"], text_color="red")
            self.note.grid(row=2, column=0, columnspan=3, pady=5, padx=5, sticky="NW")

    def confirm_changing(self) -> None:
        "check the password form first, if valid form show a pop up message to confirm change"
        special_characters = "!@$%^&()/-+_|=<>?,'\" "
        if self.new_password_entry.get().strip() == "":
            self.note = customtkinter.CTkLabel(self.change_frame, text=config.choosed_lang["empty_password"], text_color="red")
            self.note.grid(row=2, column=0, columnspan=3, pady=5, padx=5, sticky="NW")

        elif not self.new_password_entry.get().isascii():
            self.note = self.note = customtkinter.CTkLabel(self.change_frame, text=config.choosed_lang["non_english_characters"], text_color="red")
            self.note.grid(row=2, column=0, columnspan=3, pady=5, padx=5, sticky="NW")

        elif any(char in self.new_password_entry.get() for char in special_characters):
            self.note = customtkinter.CTkLabel(self.change_frame, text=config.choosed_lang["special_character_note"], text_color="red")
            self.note.grid(row=2, column=0, columnspan=3, pady=5, padx=5, sticky="NW")

        elif self.new_password_entry.get() != self.confirm_new_password.get():
            self.note = customtkinter.CTkLabel(self.change_frame, text=config.choosed_lang["wrong_password_confirmation_note"], text_color="red")
            self.note.grid(row=2, column=0, columnspan=3, pady=5, padx=5, sticky="NW")
        else:
            self.confirm_message = PopUpMessage(self, config.choosed_lang["confirm_changing_message"], config.choosed_lang["yes"], True, True,
                                        command=self.save_new_password, cancel_command=self.finish_changing)

    def save_new_password(self) -> None:
        "save the new password and return to normal widgets again"
        db.change_password(config.get_current_user_id(), self.new_password_entry.get())
        self.finish_changing()
        self.notification_message = PopUpMessage(self, config.choosed_lang["password_changed_successfully"], force=True)

    def finish_changing(self):
        "close the change passowrd frame"
        for widget in self.change_frame.winfo_children():
            widget.destroy()
        self.change_frame.destroy()
        self.change_pass_btn.grid()

    def light_mode(self):
        if customtkinter.get_appearance_mode() != "Light":
            self.master.clear_frame("destroy")
            customtkinter.set_appearance_mode("light")
            config.set_mode("light")
            db.set(config.get_current_user_id(), field="mode")
            self.master.open_side_bar()
            self.master.open_settings()

    def dark_mode(self):
        if customtkinter.get_appearance_mode() != "Dark":
            self.master.clear_frame("destroy")
            customtkinter.set_appearance_mode("dark")
            config.set_mode("dark")
            db.set(config.get_current_user_id(), mode="dark",field="mode")
            self.master.open_side_bar()
            self.master.open_settings()

    def change_theme(self, theme):
        if config.choosed_theme != theme:
            self.master.clear_frame("destroy")
            customtkinter.set_default_color_theme(resource_path("themes/"+theme.title()+".json"))
            config.set_theme(theme)
            db.set(config.get_current_user_id(), theme=theme, field="theme")
            self.master.open_side_bar()
            self.master.open_settings()

    def change_lang(self, value):
        if value == self.english:
            config.set_lang("en")
            db.set(config.get_current_user_id(), field="lang")
        elif value == self.arabic:
            config.set_lang("ar")
            db.set(config.get_current_user_id(), lang="ar", field="lang")

        self.master.clear_frame("destroy")
        self.master.open_side_bar()
        self.master.open_settings()

    def disable_choosed(self, field='mode'):
        if field == 'mode':
            if config.choosed_mode == 'light':
                self.light_mode_btn.configure(state='disabled')
                self.light_mode_btn.configure(fg_color=config.choosed_colors["accent"])
            else:
                self.dark_mode_btn.configure(state='disabled')
                self.dark_mode_btn.configure(fg_color=config.choosed_colors["accent"])

        elif field == 'theme':
            if config.choosed_theme == 'blue':
                self.blue.configure(state='disabled')
                self.blue.configure(fg_color=config.choosed_colors["accent"])
            elif config.choosed_theme == 'yellow':
                self.yellow.configure(state='disabled')
                self.yellow.configure(fg_color=config.choosed_colors["accent"])
            elif config.choosed_theme == 'green':
                self.green.configure(state='disabled')
                self.green.configure(fg_color=config.choosed_colors["accent"])
            elif config.choosed_theme == 'red':
                self.red.configure(state='disabled')
                self.red.configure(fg_color=config.choosed_colors["accent"])
            elif config.choosed_theme == 'purple':
                self.purple.configure(state='disabled')
                self.purple.configure(fg_color=config.choosed_colors["accent"])
            elif config.choosed_theme == 'grey':
                self.grey.configure(state='disabled')
                self.grey.configure(fg_color=config.choosed_colors["accent"])
            elif config.choosed_theme == 'black':
                self.black.configure(state='disabled')
                self.black.configure(fg_color=config.choosed_colors["accent"])
            
    def remember_checkbox_assign(self):
        "according to the check box state it remember or forget the login"
        if self.remember_var.get():
            db.remember_login(config.current_user_id)
        else:
            db.remember_login(config.current_user_id, remember=False)
