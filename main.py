import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk
import psycopg2
import datetime
import webbrowser

conn = psycopg2.connect("postgresql://lox:8PLDXx6f7pTY5lfcIn0WrpsCWx7Jeezc@dpg-cvokl215pdvs73a0l5tg-a.frankfurt-postgres.render.com/lox")
cursor = conn.cursor()

conn.commit()

def open_link():
    webbrowser.open("https://boosty.to/mrgastrit")

def create_styled_button(parent, text, command=None):
    return tk.Button(
        parent,
        text=text,
        command=command,
        highlightbackground="blue",
        highlightcolor="blue",
        highlightthickness=2,
        bd=2,
        relief="ridge"
    )

def open_main_window():
    main_window = tk.Tk()
    main_window.title("Добро пожаловать")
    main_window.geometry("300x250")

    bg_image = Image.open("background.png")
    bg_photo = ImageTk.PhotoImage(bg_image)
    bg_label = tk.Label(main_window, image=bg_photo)
    bg_label.place(relwidth=1, relheight=1)
    bg_label.image = bg_photo

    frame = tk.Frame(main_window, bg='white')
    frame.place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(frame, text="Выберите действие:", bg='white').pack(pady=10)

    create_styled_button(frame, "Войти", lambda: [main_window.destroy(), open_login_window()])\
        .pack(fill=tk.X, padx=20, pady=5)

    create_styled_button(frame, "Зарегистрироваться", lambda: [main_window.destroy(), open_register_window()])\
        .pack(fill=tk.X, padx=20, pady=5)

    create_styled_button(frame, "Поддержать разработчика", open_link)\
        .pack(fill=tk.X, padx=20, pady=5)

    main_window.mainloop()

def open_login_window():
    login_window = tk.Tk()
    login_window.title("Вход")
    login_window.geometry("300x200")

    for i in range(4):
        login_window.rowconfigure(i, weight=1)
    login_window.columnconfigure(0, weight=1)

    tk.Label(login_window, text="Логин:").grid(row=0, column=0, sticky="w", padx=10, pady=2)
    login_entry = tk.Entry(login_window)
    login_entry.grid(row=0, column=0, sticky="e", padx=10, pady=2)

    tk.Label(login_window, text="Пароль:").grid(row=1, column=0, sticky="w", padx=10, pady=2)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.grid(row=1, column=0, sticky="e", padx=10, pady=2)

    def login_action():
        login = login_entry.get()
        password_input = password_entry.get()

        cursor.execute("SELECT password, is_banned, ban_reason FROM users WHERE username = %s", (login,))
        result = cursor.fetchone()

        if result:
            password_db, is_banned, ban_reason = result
            if is_banned:
                reason = ban_reason if ban_reason else "Не указана"
                messagebox.showerror("Заблокирован", f"Пользователь заблокирован!\nПричина: {reason}")
            elif password_input == password_db:
                messagebox.showinfo("Успех", "Вы успешно вошли в аккаунт!")
                login_window.destroy()
                open_users_window(login)
            else:
                messagebox.showerror("Ошибка", "Неверный пароль")
        else:
            messagebox.showerror("Ошибка", "Пользователь не найден")

    create_styled_button(login_window, "Войти", login_action)\
        .grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

    login_window.bind("<Return>", lambda event: login_action())
    login_window.mainloop()

def open_register_window():
    reg_window = tk.Tk()
    reg_window.title("Регистрация")
    reg_window.geometry("300x250")

    for i in range(5):
        reg_window.rowconfigure(i, weight=1)
    reg_window.columnconfigure(0, weight=1)

    tk.Label(reg_window, text="Логин:").grid(row=0, column=0, sticky="w", padx=10, pady=2)
    login_entry = tk.Entry(reg_window)
    login_entry.grid(row=0, column=0, sticky="e", padx=10, pady=2)

    tk.Label(reg_window, text="Пароль:").grid(row=1, column=0, sticky="w", padx=10, pady=2)
    password_entry = tk.Entry(reg_window, show="*")
    password_entry.grid(row=1, column=0, sticky="e", padx=10, pady=2)

    tk.Label(reg_window, text="Повторите пароль:").grid(row=2, column=0, sticky="w", padx=10, pady=2)
    confirm_entry = tk.Entry(reg_window, show="*")
    confirm_entry.grid(row=2, column=0, sticky="e", padx=10, pady=2)

    def register_action():
        login = login_entry.get()
        password = password_entry.get()
        confirm = confirm_entry.get()

        cursor.execute("SELECT username FROM users WHERE username = %s", (login,))
        if cursor.fetchone():
            messagebox.showerror("Ошибка", "Такой пользователь уже существует!")
        elif password != confirm:
            messagebox.showerror("Ошибка", "Пароли не совпадают!")
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (login, password))
            conn.commit()
            messagebox.showinfo("Успех", "Вы успешно зарегистрированы!")
            reg_window.destroy()
            open_users_window(login)

    create_styled_button(reg_window, "Зарегистрироваться", register_action)\
        .grid(row=4, column=0, sticky="nsew", padx=20, pady=10)

    reg_window.bind("<Return>", lambda event: register_action())
    reg_window.mainloop()

def open_users_window(current_user):
    users_window = tk.Tk()
    users_window.title("Доступные контакты")
    users_window.geometry("300x500")

    tk.Label(users_window, text="Пользователи:").pack(pady=5)
    users_listbox = tk.Listbox(users_window, width=30, height=20)
    users_listbox.pack(padx=10, pady=5)

    cursor.execute("SELECT username FROM users WHERE username != %s", (current_user,))
    users = cursor.fetchall()

    for user in users:
        users_listbox.insert(tk.END, user[0])

    def on_user_select(event):
        selected_index = users_listbox.curselection()
        if selected_index:
            selected_user = users_listbox.get(selected_index[0])
            open_chat_window(current_user, selected_user)

    users_listbox.bind("<<ListboxSelect>>", on_user_select)

    users_window.mainloop()

def open_chat_window(sender, receiver):
    chat_window = tk.Toplevel()
    chat_window.title(f"Чат с {receiver}")
    chat_window.geometry("400x500")

    chat_display = scrolledtext.ScrolledText(chat_window, state='disabled', wrap=tk.WORD)
    chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    message_entry = tk.Entry(chat_window)
    message_entry.pack(padx=10, pady=5, fill=tk.X)

    def load_messages():
        cursor.execute("""
            SELECT sender, content, timestamp FROM messages
            WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s)
            ORDER BY timestamp ASC
        """, (sender, receiver, receiver, sender))
        messages = cursor.fetchall()

        chat_display.config(state='normal')
        chat_display.delete('1.0', tk.END)
        for msg_sender, content, timestamp in messages:
            chat_display.insert(tk.END, f"[{timestamp.strftime('%H:%M')}] {msg_sender}: {content}\n")
        chat_display.config(state='disabled')

    def send_message():
        content = message_entry.get()
        if content.strip():
            try:
                cursor.execute(
                    "INSERT INTO messages (sender, receiver, content, timestamp) VALUES (%s, %s, %s, %s)",
                    (sender, receiver, content, datetime.datetime.now())
                )
                conn.commit()
                message_entry.delete(0, tk.END)
                load_messages()
            except Exception as e:
                conn.rollback()
                messagebox.showerror("Ошибка отправки", str(e))

    chat_window.after(2000, load_messages)
    chat_window.bind("<Return>", lambda event: send_message())

    send_button = create_styled_button(chat_window, "Отправить", send_message)
    send_button.pack(padx=10, pady=5)

    load_messages()

try:
    open_main_window()
finally:
    cursor.close()
    conn.close()

