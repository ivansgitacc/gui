from tkinter import *
from tkinter.ttk import Treeview, Combobox
import sqlite3

db = sqlite3.connect('data.db')
cur = db.cursor()
# список компаний из БД
companies_query = [item[0] for item in cur.execute('SELECT name FROM companies').fetchall()]

def login():
    def login_user():
        if cur.execute('SELECT * FROM users WHERE username = ? AND password = ?', (name_entry.get(), password_entry.get())).fetchone():
            login_window.destroy()
            main()
        else:
            error_label = Label(login_window, text='Пользаватель не найден')
            error_label.pack()

    login_window = Tk()
    login_window.title('Вход')
    login_window.geometry('300x350+800+350')

    name_label = Label(login_window, text='Имя', font='Arial 12')
    name_entry = Entry(login_window, font='Arial 14')
    password_label = Label(login_window, text='Пароль', font='Arial 12')
    password_entry = Entry(login_window, font='Arial 14', show='*')
    login_btn = Button(login_window, text='Вход', font='Arial 12', command=login_user)
    register_btn = Button(login_window, text='Создать аккаунт', border=0, fg='blue', cursor='hand1', command=register)

    name_label.pack(padx=20, pady=(50, 0))
    name_entry.pack(padx=20)
    password_label.pack(padx=20)
    password_entry.pack(padx=20)
    login_btn.pack(padx=20, pady=(30, 0))
    register_btn.pack(pady=(20, 0))

    login_window.mainloop()

def register():
    def create_user():
        if name_entry.get() and password_entry.get():
            if password_entry.get() == password_entry_2.get():
                cur.execute('INSERT INTO users VALUES (?, ?)', (name_entry.get(), password_entry.get()))
                db.commit()
                register_window.destroy()
            else:
                error_label = Label(register_window, text='Пароли не совпадают', fg='red')
                error_label.pack()

    register_window = Toplevel()
    register_window.title('Регистрация')
    register_window.geometry('300x350+800+350')

    name_label = Label(register_window, text='Введите имя', font='Arial 12')
    name_entry = Entry(register_window, font='Arial 12')
    password_label = Label(register_window, text='Введите пароль', font='Arial 12')
    password_entry = Entry(register_window, show='*', font='Arial 12')
    password_label_2 = Label(register_window, text='Подтвердите пароль', font='Arial 12')
    password_entry_2 = Entry(register_window, show='*', font='Arial 12')
    register_btn = Button(register_window, text='Создать', font='Arial 12', command=create_user)

    name_label.pack(pady=(50, 10))
    name_entry.pack(pady=(0, 10))
    password_label.pack()
    password_entry.pack(pady=(0, 10))
    password_label_2.pack()
    password_entry_2.pack(pady=(0, 30))
    register_btn.pack()

    register_window.mainloop()

def main():
    def search():
        value = '%' + search_entry.get() + '%'
        main_table.delete(*main_table.get_children())
        for i in cur.execute(f'SELECT * FROM planes WHERE plane_type LIKE ? OR engine_type LIKE ?', (value, value)):
            main_table.insert('', 0, values=i)

    main_window = Tk()
    main_window.geometry('+200+200')

    companies_btn = Button(main_window, text='Выбрать компанию', command=companies)
    add_plane_btn = Button(main_window, text='Добавить самолёт', command=planes)

    global main_table
    main_table = Treeview(main_window, height=30, show='headings')
    headers = ['Тип самолёта', '№ Самолёта', 'Тип двигателя', '№ Двигателя', '№ СУ', 'Дата установки', 'Наработка-час\цикл', 'Компания']
    main_table['columns'] = headers

    for header in headers:
        main_table.heading(header, text=header)
        main_table.column(header, anchor=CENTER)
    
    for value in cur.execute('SELECT * FROM planes').fetchall():
        main_table.insert('', 0, values=value)
    
    search_entry = Entry(main_window)
    search_btn = Button(main_window, text='Поиск', command=search)

    companies_btn.grid(row=0, column=0)
    add_plane_btn.grid(row=0, column=1)
    search_entry.grid(row=0, column=18)
    search_btn.grid(row=0, column=19)
    main_table.grid(row=1, column=0, columnspan=20, pady=(10, 0))

    main_window.mainloop()

def companies():
    def add_company():
        if companies_entry.get():
            companies_list.insert(0, companies_entry.get())
            companies_query.append(companies_entry.get())
            cur.execute('INSERT INTO companies (name) VALUES (?)', (companies_entry.get(), ))
            db.commit()

    companies_window = Toplevel()
    companies_window.title('Компании')
    companies_window.geometry('+900+300')

    companies_list = Listbox(companies_window, width=50)
    companies_entry = Entry(companies_window)
    add_btn = Button(companies_window, text='Добавить', command=add_company)

    for item in cur.execute('SELECT * FROM companies').fetchall():
        companies_list.insert(0, item)

    companies_list.grid(row=0, column=0, columnspan=5)
    companies_entry.grid(row=1, column=0, sticky='we', columnspan=4)
    add_btn.grid(row=1, column=4, sticky='we')

    companies_window.mainloop()

def planes():
    def add_plane():
        types = table.item(table.focus()).get('values') # тип самолёта и двигателя из таблицы
        if types and plane_number_entry.get() and engine_number_entry.get() and pu_position_entry.get() and \
        installation_entry.get() and time_scince_installed_entry.get() and company_enter.get():
            main_table.insert('', 0, values=(
                types[0], 
                plane_number_entry.get(), 
                types[1], 
                engine_number_entry.get(), 
                pu_position_entry.get(), 
                installation_entry.get(), 
                time_scince_installed_entry.get(), 
                company_enter.get()
            ))
            # PU_position = № СУ, installation = дата установки, time_scince_installed = наработка
            cur.execute('''INSERT INTO planes (plane_type, plane_number, engine_type, engine_number, 
                PU_position, installation, time_scince_installed, company) VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (
                types[0], 
                plane_number_entry.get(), 
                types[1], 
                engine_number_entry.get(), 
                pu_position_entry.get(), 
                installation_entry.get(), 
                time_scince_installed_entry.get(), 
                company_enter.get()
            ))
            db.commit()

    planes_window = Toplevel()
    planes_window.title('Главная')
    planes_window.geometry('+700+300')

    global table
    table = Treeview(planes_window, show='headings')
    headers = ['Тип самолёта', 'Тип двигателя']
    table['columns'] = headers

    for header in headers:
        table.heading(header, text=header)
        table.column(header, anchor=CENTER)
    
    for item in cur.execute('SELECT * FROM types').fetchall():
        table.insert('', 0, values=item)  

    plane_number_label = Label(planes_window, text='№ Самолёта')
    plane_number_entry = Entry(planes_window)
    engine_number_label = Label(planes_window, text='№ Двигателя')
    engine_number_entry = Entry(planes_window)
    company_label = Label(planes_window, text='Компания')
    company_enter = Combobox(planes_window, values=companies_query)
    pu_position_label = Label(planes_window, text='№ СУ')
    pu_position_entry = Combobox(planes_window, values=(1, 2))
    installation_label = Label(planes_window, text='Дата установки')
    installation_entry = Entry(planes_window)
    time_scince_installed_label = Label(planes_window, text='Наработка')
    time_scince_installed_entry = Entry(planes_window)
    
    add_type_btn = Button(planes_window, text='Новый тип', command=plane_types)
    add_plane_btn = Button(planes_window, text='Добавить', command=add_plane)

    table.grid(row=0, column=0, columnspan=3)
    plane_number_label.grid(row=1, column=0)
    plane_number_entry.grid(row=2, column=0)
    engine_number_label.grid(row=1, column=1)
    engine_number_entry.grid(row=2, column=1)
    company_label.grid(row=1, column=2)
    company_enter.grid(row=2, column=2)
    pu_position_label.grid(row=3, column=0)
    pu_position_entry.grid(row=4, column=0)
    installation_label.grid(row=3, column=1)
    installation_entry.grid(row=4, column=1)
    time_scince_installed_label.grid(row=3, column=2)
    time_scince_installed_entry.grid(row=4, column=2)
    add_type_btn.grid(row=5, column=0)
    add_plane_btn.grid(row=5, column=1)

    planes_window.mainloop()

def plane_types():
    def add_type(): # добавить тип самолёта и двигателя
        if plane_type_entry.get() and engine_type_entry.get():
            cur.execute('INSERT INTO types (plane_type, engine_type) VALUES (?, ?)', (plane_type_entry.get(), engine_type_entry.get()))
            db.commit()
            table.insert('', 0, values=(plane_type_entry.get(), engine_type_entry.get()))
            plane_type_entry.delete(0, END)
            engine_type_entry.delete(0, END)

    plane_types_window = Toplevel()
    plane_types_window.title('Добавить новый тип')
    plane_types_window.geometry('+800+450')

    plane_type_label = Label(plane_types_window, text='Тип самолёта')
    plane_type_entry = Entry(plane_types_window)
    engine_type_label = Label(plane_types_window, text='Тип двигателя')
    engine_type_entry = Entry(plane_types_window)
    add_type_btn = Button(plane_types_window, text='Добавить', command=add_type)

    plane_type_label.grid(row=0, column=0)
    plane_type_entry.grid(row=1, column=0, padx=(5, 0))
    engine_type_label.grid(row=0, column=1)
    engine_type_entry.grid(row=1, column=1, padx=(0, 5))
    add_type_btn.grid(row=2, column=0, columnspan=2, pady=5)

    plane_types_window.mainloop()

if __name__ == '__main__':
    login()