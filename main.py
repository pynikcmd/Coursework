import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from tkinter import messagebox
import sqlite3


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Аутентификация")

        # Установка размеров окна во весь экран
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}")

        # Создание фонового изображения для окна
        self.bg_image = tk.PhotoImage(file="1.png")
        self.bg_label = tk.Label(root, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)

        # Центрирование элементов на экране
        self.center_window()

        # Создание рамки для фона вокруг полей ввода
        self.login_frame = tk.Frame(root, bg="#FFEBCD")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.2, relheight=0.32)

        # Создание рамки для группировки элементов
        self.input_frame = tk.Frame(self.login_frame, bg="#FFEBCD")
        self.input_frame.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.6)

        # Создание текстовых меток и полей ввода
        self.login_label = tk.Label(self.input_frame, text="Логин:", font=("Georgia", 18), bg="#FFEBCD")
        self.login_label.grid(row=0, column=0, pady=(1, 5), sticky="w")

        self.login_entry = tk.Entry(self.input_frame, font=("Arial", 18))
        self.login_entry.grid(row=1, column=0, pady=5, sticky="ew")

        self.password_label = tk.Label(self.input_frame, text="Пароль:", font=("Georgia", 18), bg="#FFEBCD")
        self.password_label.grid(row=2, column=0, pady=(5, 5), sticky="w")

        self.password_entry = tk.Entry(self.input_frame, show="*", font=("Arial", 18))
        self.password_entry.grid(row=3, column=0, pady=5, sticky="ew")

        # Привязка события нажатия клавиши Enter к методу login
        self.password_entry.bind("<Return>", lambda event: self.login())

        # Кнопка для входа
        self.login_button = tk.Button(self.login_frame, text="Войти", command=self.login, font=("Georgia", 16),
                                      bg="#CDB38B", fg="#000000")
        self.login_button.place(relx=0.5, rely=0.8, anchor="center")

    def center_window(self):
        # Определение центра экрана
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.root.winfo_reqwidth()) / 2
        y = (screen_height - self.root.winfo_reqheight()) / 2
        self.root.geometry("+%d+%d" % (x, y))

    def login(self):
        login = self.login_entry.get()
        password = self.password_entry.get()

        if login == "Nika" and password == "12345":
            self.root.destroy()  # Закрываем окно аутентификации
            self.open_main_app()
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def open_main_app(self):
        root = tk.Tk()
        app = HotelApp(root)
        root.mainloop()


class HotelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Отель")

        # Установка фона приложения
        self.bg_image = tk.PhotoImage(file="1.png")
        self.bg_label = tk.Label(root, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)

        # Инициализация базы данных
        self.conn = sqlite3.connect("hotel.db")
        self.create_table()

        # Переменные для хранения введенных данных
        self.last_name_vars = []
        self.first_name_vars = []
        self.middle_name_vars = []
        self.checkin_date_var = tk.StringVar()
        self.checkout_date_var = tk.StringVar()
        self.room_type_var = tk.StringVar()
        self.room_number_var = tk.StringVar()

        # Создание и размещение элементов управления
        self.create_widgets()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS guests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                last_name TEXT CHECK(length(last_name) <= 25) NOT NULL,
                first_name TEXT CHECK(length(first_name) <= 25) NOT NULL,
                middle_name TEXT CHECK(length(middle_name) <= 25) NOT NULL,
                checkin_date TEXT CHECK(length(checkin_date) = 10) NOT NULL,
                checkout_date TEXT CHECK(length(checkout_date) = 10) NOT NULL,
                room_type TEXT CHECK(length(room_type) > 0) NOT NULL,
                room_number INTEGER CHECK(room_number > 0) NOT NULL
            )
        ''')
        self.conn.commit()

    def is_room_available(self, room_type, room_number, checkin_date, checkout_date):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM guests
            WHERE room_type = ? AND room_number = ? AND (
                (checkin_date BETWEEN ? AND ?) OR
                (checkout_date BETWEEN ? AND ?) OR
                (checkin_date <= ? AND checkout_date >= ?)
            )
        ''', (room_type, room_number, checkin_date, checkout_date, checkin_date, checkout_date, checkin_date, checkout_date))

        # Если есть записи для данного номера в выбранный период, номер не доступен
        return not cursor.fetchall()

    def insert_data(self):
        last_names = [var.get() for var in self.last_name_vars if var.get()]
        first_names = [var.get() for var in self.first_name_vars if var.get()]
        middle_names = [var.get() for var in self.middle_name_vars if var.get()]
        checkin_date = self.checkin_date_var.get()
        checkout_date = self.checkout_date_var.get()
        room_type = self.room_type_var.get()
        room_number = self.room_number_var.get()

        # Проверка заполнения хотя бы одного поля ФИО
        if not any(self.last_name_vars) and not any(self.first_name_vars) and not any(self.middle_name_vars):
            messagebox.showerror("Ошибка", "Введите хотя бы одно поле ФИО")
            return

        if not self.checkin_date_var.get() or not self.checkout_date_var.get():
            messagebox.showerror("Ошибка", "Введите дату заселения и выселения")
            return

        if not self.room_number_var.get():
            messagebox.showerror("Ошибка", "Выберите номер комнаты")
            return

        # Проверка доступности номера
        if not self.is_room_available(room_type, room_number, checkin_date, checkout_date):
            messagebox.showerror("Ошибка", "Номер занят в выбранный период")
            return

        # Проверка количества вносимых гостей
        num_guests = len(last_names)
        if num_guests < 1 or num_guests > 4:
            messagebox.showerror("Ошибка", "Введите все данные в поле ФИО.")
            return

        # Ограничение на количество гостей в зависимости от типа номера
        if num_guests > 1 and room_type == "Одноместные":
            messagebox.showerror("Ошибка", "В одноместный номер можно внести только одного гостя.")
            return
        elif num_guests > 2 and room_type == "Двуместные":
            messagebox.showerror("Ошибка", "В двуместный номер можно внести не более двух гостей.")
            return
        elif num_guests > 3 and room_type == "Трёхместные":
            messagebox.showerror("Ошибка", "В трёхместный номер можно внести не более трёх гостей.")
            return
        elif num_guests > 4 and room_type == "Четырёхместные":
            messagebox.showerror("Ошибка", "В четырёхместный номер можно внести не более четырёх гостей.")
            return

        last_names = last_names[:num_guests]
        first_names = first_names[:num_guests]
        middle_names = middle_names[:num_guests]

        # Вставка данных в базу данных
        cursor = self.conn.cursor()
        for last_name, first_name, middle_name in zip(last_names, first_names, middle_names):
            # Проверка наличия данных перед вставкой
            if last_name or first_name or middle_name:
                cursor.execute('''
                    INSERT INTO guests (last_name, first_name, middle_name, checkin_date, checkout_date, room_type, room_number)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (last_name, first_name, middle_name, checkin_date, checkout_date, room_type, room_number))

        # Фиксация изменений в базе данных
        self.conn.commit()

        # Очистка введенных данных и обновление таблицы
        self.clear_entries()
        self.update_table()

    def delete_data(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Ошибка", "Выберите запись для удаления")
            return

        item_id = self.tree.item(selected_item)['values'][0]

        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM guests WHERE id = ?', (item_id,))
        self.conn.commit()

        self.update_table()

    def clear_entries(self):
        for var in self.last_name_vars:
            var.set("")
        for var in self.first_name_vars:
            var.set("")
        for var in self.middle_name_vars:
            var.set("")
        self.checkin_date_var.set("")
        self.checkout_date_var.set("")
        self.room_number_var.set("")

    def update_table(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM guests')
        data = cursor.fetchall()

        # Очистка текущего содержимого таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Заполнение таблицы новыми данными
        for row in data:
            self.tree.insert("", "end", values=row)

    def sort_table(self, col, reverse):
        data_list = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        data_list.sort(reverse=reverse)

        for index, (val, k) in enumerate(data_list):
            self.tree.move(k, '', index)

        self.tree.heading(col, command=lambda: self.sort_table(col, not reverse))


    def create_widgets(self):
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Создаем input_frame заранее
        input_frame = ttk.LabelFrame(self.root, text="Ввод данных")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Применяем стиль к input_frame для установки цвета фона
        input_frame_style = ttk.Style()
        input_frame_style.configure("LightBrown.TLabelframe", background="#f4ede6")
        input_frame.configure(style="LightBrown.TLabelframe")

        input_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)
        input_frame.columnconfigure(1, weight=1)
        input_frame.columnconfigure(2, weight=1)

        # Создаем name_frame заранее
        name_frame = ttk.LabelFrame(input_frame, text="ФИО")
        name_frame.grid(row=0, column=0, rowspan=4, padx=5, pady=5, sticky="nsew")

        for i in range(4):
            name_frame.rowconfigure(i, weight=1)
            name_frame.columnconfigure(0, weight=1)
            name_frame.columnconfigure(1, weight=1)
            name_frame.columnconfigure(2, weight=1)
            name_frame.columnconfigure(3, weight=1)
            name_frame.columnconfigure(4, weight=1)
            name_frame.columnconfigure(5, weight=1)

            last_name_var = tk.StringVar()
            first_name_var = tk.StringVar()
            middle_name_var = tk.StringVar()

            self.last_name_vars.append(last_name_var)
            self.first_name_vars.append(first_name_var)
            self.middle_name_vars.append(middle_name_var)

            ttk.Label(name_frame, text=f"Фамилия {i + 1}:").grid(row=i, column=0, padx=5, pady=5, sticky="e")
            ttk.Entry(name_frame, textvariable=last_name_var).grid(row=i, column=1, padx=5, pady=5, sticky="w")

            ttk.Label(name_frame, text=f"Имя {i + 1}:").grid(row=i, column=2, padx=5, pady=5, sticky="e")
            ttk.Entry(name_frame, textvariable=first_name_var).grid(row=i, column=3, padx=5, pady=5, sticky="w")

            ttk.Label(name_frame, text=f"Отчество {i + 1}:").grid(row=i, column=4, padx=5, pady=5, sticky="e")
            ttk.Entry(name_frame, textvariable=middle_name_var).grid(row=i, column=5, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="Дата заселения:").grid(row=0, column=1, padx=5, pady=5, sticky="e")
        DateEntry(input_frame, textvariable=self.checkin_date_var, date_pattern="dd.MM.yyyy", width=12).grid(row=0,
                                                                                                             column=2,
                                                                                                             padx=5,
                                                                                                             pady=5,
                                                                                                             sticky="w")

        ttk.Label(input_frame, text="Дата выселения:").grid(row=1, column=1, padx=5, pady=5, sticky="e")
        DateEntry(input_frame, textvariable=self.checkout_date_var, date_pattern="dd.MM.yyyy", width=12).grid(row=1,
                                                                                                              column=2,
                                                                                                              padx=5,
                                                                                                              pady=5,
                                                                                                              sticky="w")

        ttk.Label(input_frame, text="Тип комнаты:").grid(row=2, column=1, padx=5, pady=5, sticky="e")
        room_types = ["Одноместные", "Двуместные", "Трёхместные", "Четырёхместные"]
        self.room_type_combobox = ttk.Combobox(input_frame, textvariable=self.room_type_var, values=room_types)
        self.room_type_combobox.grid(row=2, column=2, padx=5, pady=5, sticky="w")
        # Установка значения по умолчанию
        self.room_type_var.set(room_types[0])

        ttk.Label(input_frame, text="Номер комнаты:").grid(row=3, column=1, padx=5, pady=5, sticky="e")
        self.room_number_combobox = ttk.Combobox(input_frame, textvariable=self.room_number_var)
        self.room_number_combobox.grid(row=3, column=2, padx=5, pady=5, sticky="w")
        # Установка значения по умолчанию
        self.room_number_var.set(self.get_room_numbers("Одноместные")[0])

        # Заполнение номеров комнат в зависимости от типа
        self.room_type_combobox.bind("<<ComboboxSelected>>", self.update_room_numbers)
        self.update_room_numbers(None)  # Обновление номеров при запуске приложения

        ttk.Button(input_frame, text="Добавить", command=self.insert_data).grid(row=4, column=3, rowspan=2, pady=10,
                                                                                padx=(0, 10))
        ttk.Button(input_frame, text="Удалить", command=self.delete_data).grid(row=6, column=3, rowspan=2, pady=10,
                                                                               padx=(0, 10))

        display_frame = ttk.LabelFrame(self.root, text="База данных")
        display_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Применяем стиль к display_frame для установки цвета фона
        display_frame_style = ttk.Style()
        display_frame_style.configure("LightBrown.TLabelframe", background="#f4ede6")
        display_frame.configure(style="LightBrown.TLabelframe")

        columns = (
            "ID", "Фамилия", "Имя", "Отчество", "Дата заселения", "Дата выселения", "Тип комнаты", "Номер комнаты"
        )
        self.tree = ttk.Treeview(display_frame, columns=columns, show="headings", height=20)

        for col in columns:
            self.tree.heading(col, text=col, command=lambda _col=col: self.sort_table(_col, False))
            self.tree.column(col, width=170)
        self.tree.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        y_scrollbar = ttk.Scrollbar(display_frame, orient="vertical", command=self.tree.yview)
        y_scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=y_scrollbar.set)

        x_scrollbar = ttk.Scrollbar(display_frame, orient="horizontal", command=self.tree.xview)
        x_scrollbar.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=x_scrollbar.set)

        self.update_table()

        # Разрешение изменения размеров окна
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)

    def get_room_numbers(self, room_type):
        start, end = 1, 100
        if room_type == "Двуместные":
            start, end = 101, 200
        elif room_type == "Трёхместные":
            start, end = 201, 300
        elif room_type == "Четырёхместные":
            start, end = 301, 400

        return [str(number) for number in range(start, end + 1)]

    def update_room_numbers(self, event):
        room_type = self.room_type_var.get()
        room_numbers = self.get_room_numbers(room_type)
        self.room_number_combobox["values"] = room_numbers
        # Установка значения по умолчанию, чтобы избежать ошибок при смене типа комнаты
        self.room_number_var.set(room_numbers[0])

if __name__ == "__main__":
    login_root = tk.Tk()
    login_window = LoginWindow(login_root)
    login_root.mainloop()
