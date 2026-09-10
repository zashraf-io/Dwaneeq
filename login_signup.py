import customtkinter
import db
import config

class Login_Sinup(customtkinter.CTkFrame):
    def __init__(self, master) -> None:
        super().__init__(master)

        self.master = master       # The App() instance
        self.is_signup = False

        # Setting the position in the box relative to the size of the main window
        self.login_frame_height = master.screen_height / 1.65
        self.login_frame_width = master.screen_width / 2.2
        self.login_frame = customtkinter.CTkFrame(self, width=self.login_frame_width, height=self.login_frame_height)
        self.login_frame.pack(anchor="center", pady=(master.screen_height - self.login_frame_height) / 2.2)
        self.login_frame.propagate(True)
        self.login_frame.columnconfigure((0, 1, 2, 3), weight=1)

        # 1. Language segmented button (Arabic default)
        self.lang_segmented = customtkinter.CTkSegmentedButton(
            self.login_frame, values=["العربية", "English"], command=self.switch_language,
            selected_color="#2563eb", selected_hover_color="#1d4ed8"
        )
        self.lang_segmented.set("العربية" if config.get_current_lang() == "ar" else "English")
        self.lang_segmented.grid(row=0, pady=(15, 5))

        # Title Label
        self.lbl1 = customtkinter.CTkLabel(self.login_frame, text=config.choosed_lang["login_label"], font=("arial", 30, "bold"))
        self.lbl1.grid(row=1, sticky="NSEW", pady=(10, 15))

        # Username and password entries
        self.user_name_entry = customtkinter.CTkEntry(
            self.login_frame, width=300, placeholder_text=config.choosed_lang["username"], fg_color="transparent"
        )
        self.user_name_entry.grid(row=2, sticky="NSEW", pady=8, padx=30)

        self.password_entry = customtkinter.CTkEntry(
            self.login_frame, show="●", font=("Arial", 12), width=300,
            placeholder_text=config.choosed_lang["password"], fg_color="transparent"
        )
        self.password_entry.grid(row=3, sticky="NSEW", pady=8, padx=30)

        # Confirm password entry (hidden initially, used for sign up)
        self.confirm_password_entry = None

        # Checkboxes frame (show password + remember me)
        self.checkboxes_frame = customtkinter.CTkFrame(self.login_frame, fg_color="transparent")
        self.checkboxes_frame.grid(row=4, padx=30, pady=5, sticky="EW")
        self.checkboxes_frame.columnconfigure((0, 1), weight=1)

        self.show_password = customtkinter.BooleanVar(value=False)
        self.show_password_checkbox = customtkinter.CTkCheckBox(
            self.checkboxes_frame, text=config.choosed_lang["show_password_checkbox"],
            variable=self.show_password, onvalue=True, offvalue=False,
            checkbox_width=17, checkbox_height=17, font=("Arial", 11.5),
            command=self.hide_password
        )
        self.show_password_checkbox.grid(row=0, column=0, sticky="W", pady=2)

        self.remember_var = customtkinter.BooleanVar(value=True)
        self.remember_checkbox = customtkinter.CTkCheckBox(
            self.checkboxes_frame, text=config.choosed_lang.get("remember_login", "Remember me"),
            variable=self.remember_var, onvalue=True, offvalue=False,
            checkbox_width=17, checkbox_height=17, font=("Arial", 11.5)
        )
        self.remember_checkbox.grid(row=0, column=1, sticky="E", pady=2)

        # Note label for error messages
        self.note_label = customtkinter.CTkLabel(self.login_frame, font=("arial", 11), text_color="red")

        # Action Button (Login / Sign Up)
        self.login_btn = customtkinter.CTkButton(
            self.login_frame, width=120, height=32, text=config.choosed_lang["login_button"],
            command=self.log_in
        )
        self.login_btn.grid(row=6, pady=15)

        # Toggle between Login and Sign Up
        self.signup_link_note = customtkinter.CTkLabel(
            self.login_frame, text=config.choosed_lang["signup_link_note"],
            font=("Arial", 12, "underline"), text_color="#3b82f6", cursor="hand2"
        )
        self.signup_link_note.bind("<Button-1>", self.open_signup_frame)
        self.signup_link_note.grid(row=7, pady=(0, 15))

        # Enter key binding
        self.master.bind("<Return>", self.on_enter)

    def on_enter(self, event=None):
        if self.is_signup:
            self.sign_up()
        else:
            self.log_in()

    def destroy(self):
        try:
            self.master.unbind("<Return>")
        except:
            pass
        super().destroy()

    def switch_language(self, selected_lang):
        new_lang = "ar" if selected_lang == "العربية" else "en"
        config.set_lang(new_lang)

        # Update texts
        if not self.is_signup:
            self.lbl1.configure(text=config.choosed_lang["login_label"])
            self.login_btn.configure(text=config.choosed_lang["login_button"])
            self.signup_link_note.configure(text=config.choosed_lang["signup_link_note"])
        else:
            self.lbl1.configure(text=config.choosed_lang["signup_label"])
            self.login_btn.configure(text=config.choosed_lang["signup_button"])
            self.signup_link_note.configure(text=config.choosed_lang["login_link_note"])
            if self.confirm_password_entry:
                self.confirm_password_entry.configure(placeholder_text=config.choosed_lang["confirm_password"])

        self.user_name_entry.configure(placeholder_text=config.choosed_lang["username"])
        self.password_entry.configure(placeholder_text=config.choosed_lang["password"])
        self.show_password_checkbox.configure(text=config.choosed_lang["show_password_checkbox"])
        self.remember_checkbox.configure(text=config.choosed_lang.get("remember_login", "Remember me"))

    def log_in(self) -> None:
        """If the user is valid, opens the Home frame, else show a note for the user to check its user name and password"""
        username = self.user_name_entry.get().lower().strip()
        password = self.password_entry.get().strip()

        try:
            user_id_request = db.isvalid_user(username, password)
        except:
            db.open_database("all")
            user_id_request = db.isvalid_user(username, password)

        if user_id_request not in ['not valid', 'not found']:
            remember = self.remember_var.get()
            db.remember_login(user_id_request, remember=remember)
            db.set(user_id_request, remember_login=remember, field="remember_login")
            self.destroy()
            self.master.load_app(user_id_request)
        else:
            self.note_label.configure(text=config.choosed_lang["invalid_user_note"])
            self.note_label.grid(row=5, sticky="NSEW")

    def sign_up(self) -> None:
        """checks if the user name is used before and check the validity of password, if all true add to the database"""
        special_characters = "!@$%^&()/-+_|=<>?,'\" "
        username = self.user_name_entry.get().lower().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_password_entry.get().strip() if self.confirm_password_entry else ""

        try:
            if db.isreserved(username):
                self.note_label.configure(text=config.choosed_lang["reserved_username_note"])
                self.note_label.grid(row=5)
                return
        except:
            db.open_database("all")
            if db.isreserved(username):
                self.note_label.configure(text=config.choosed_lang["reserved_username_note"])
                self.note_label.grid(row=5)
                return

        if password == "":
            self.note_label.configure(text=config.choosed_lang["empty_password"])
            self.note_label.grid(row=5)
            return

        if password != confirm:
            self.note_label.configure(text=config.choosed_lang["wrong_password_confirmation_note"])
            self.note_label.grid(row=5)
            return

        if not password.isascii():
            self.note_label.configure(text=config.choosed_lang["non_english_characters"])
            self.note_label.grid(row=5)
            return

        if any(char in password for char in special_characters):
            self.note_label.configure(text=config.choosed_lang["special_character_note"])
            self.note_label.grid(row=5)
            return

        db.add_user(username, password.lower())
        user_id = db.isvalid_user(username, password.lower())
        
        remember = self.remember_var.get()
        db.remember_login(user_id, remember=remember)
        db.set(user_id, remember_login=remember, field="remember_login")
        
        self.destroy()
        self.master.load_app(user_id)

    def open_signup_frame(self, event=None) -> None:
        self.is_signup = True
        self.lbl1.configure(text=config.choosed_lang["signup_label"])

        saved_u = self.user_name_entry.get()
        saved_p = self.password_entry.get()

        self.user_name_entry.destroy()
        self.password_entry.destroy()
        self.note_label.grid_forget()

        self.user_name_entry = customtkinter.CTkEntry(
            self.login_frame, width=300, placeholder_text=config.choosed_lang["username"], fg_color="transparent"
        )
        self.user_name_entry.insert(0, saved_u)
        self.user_name_entry.grid(row=2, sticky="NSEW", pady=8, padx=30)

        self.password_entry = customtkinter.CTkEntry(
            self.login_frame, show="●", font=("Arial", 12), width=300,
            placeholder_text=config.choosed_lang["password"], fg_color="transparent"
        )
        self.password_entry.insert(0, saved_p)
        self.password_entry.grid(row=3, sticky="NSEW", pady=8, padx=30)

        self.confirm_password_entry = customtkinter.CTkEntry(
            self.login_frame, show="●", font=("Arial", 12), width=300,
            placeholder_text=config.choosed_lang["confirm_password"], fg_color="transparent"
        )
        self.confirm_password_entry.grid(row=4, sticky="NSEW", pady=8, padx=30)

        self.checkboxes_frame.grid(row=5, padx=30, pady=5, sticky="EW")

        self.login_btn.configure(text=config.choosed_lang["signup_button"], command=self.sign_up)
        self.login_btn.grid(row=6)

        self.signup_link_note.configure(text=config.choosed_lang["login_link_note"])
        self.signup_link_note.bind("<Button-1>", self.open_login_frame)
        self.signup_link_note.grid(row=7)

    def open_login_frame(self, event=None) -> None:
        self.is_signup = False
        self.lbl1.configure(text=config.choosed_lang["login_label"])

        if self.confirm_password_entry:
            self.confirm_password_entry.destroy()
            self.confirm_password_entry = None

        self.checkboxes_frame.grid(row=4, padx=30, pady=5, sticky="EW")

        self.login_btn.configure(text=config.choosed_lang["login_button"], command=self.log_in)
        self.login_btn.grid(row=6)

        self.signup_link_note.configure(text=config.choosed_lang["signup_link_note"])
        self.signup_link_note.bind("<Button-1>", self.open_signup_frame)
        self.signup_link_note.grid(row=7)

    def hide_password(self) -> None:
        """hides characters of password while typing unless 'show password' check box is checked"""
        if self.show_password.get():
            self.password_entry.configure(show="", font=("Arial", 13))
            if self.confirm_password_entry:
                self.confirm_password_entry.configure(show="", font=("Arial", 13))
        else:
            self.password_entry.configure(show="●", font=("Arial", 12))
            if self.confirm_password_entry:
                self.confirm_password_entry.configure(show="●", font=("Arial", 12))
