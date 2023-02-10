from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import sqlite3
import math
import matplotlib.pyplot as plt

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
            showerror(message='Пользаватель не найден')

    login_window = Tk()
    login_window.title('Вход')
    login_window.geometry('+800+350')
    login_window.resizable(False, False)

    name_label = ttk.Label(login_window, text='Имя')
    name_entry = ttk.Entry(login_window)
    password_label = ttk.Label(login_window, text='Пароль')
    password_entry = ttk.Entry(login_window, show='*')
    login_btn = ttk.Button(login_window, text='Вход', command=login_user)
    register_btn = Button(login_window, text='Создать аккаунт', border=0, fg='blue', cursor='hand1', command=register)

    name_label.pack(pady=(40, 0))
    name_entry.pack(padx=40, pady=(0, 10))
    password_label.pack()
    password_entry.pack(pady=(0, 20))
    login_btn.pack()
    register_btn.pack(pady=(20))

    login_window.mainloop()

def register():
    def create_user():
        if name_entry.get() and password_entry.get():
            if password_entry.get() == password_entry_2.get():
                cur.execute('INSERT INTO users VALUES (?, ?)', (name_entry.get(), password_entry.get()))
                db.commit()
                register_window.destroy()
            else:
                showerror(message='Пароли не совпадают')

    register_window = Toplevel()
    register_window.title('Регистрация')
    register_window.geometry('+800+350')

    name_label = ttk.Label(register_window, text='Введите имя')
    name_entry = ttk.Entry(register_window)
    password_label = ttk.Label(register_window, text='Введите пароль')
    password_entry = ttk.Entry(register_window, show='*')
    password_label_2 = ttk.Label(register_window, text='Подтвердите пароль')
    password_entry_2 = ttk.Entry(register_window, show='*')
    register_btn = ttk.Button(register_window, text='Создать', command=create_user)

    name_label.pack(pady=(40, 0))
    name_entry.pack(padx=40)
    password_label.pack(pady=(10, 0))
    password_entry.pack()
    password_label_2.pack(pady=(10, 0))
    password_entry_2.pack()
    register_btn.pack(pady=20)

    register_window.mainloop()

def main():
    def search():
        value = '%' + search_entry.get() + '%'
        main_table.delete(*main_table.get_children())
        for i in cur.execute(f'SELECT * FROM planes WHERE plane_type LIKE ? OR engine_type LIKE ?', (value, value)):
            main_table.insert('', 0, values=i)
    
    def analize():
        if main_table.focus():
            analisys()
        else:
            showinfo(message='Выберете самолёт')
    
    def delete():
        items = main_table.item(main_table.focus()).get('values')
        cur.execute('DELETE FROM planes WHERE plane_number = ?', (items[1],))
        selected_item = main_table.selection()
        main_table.delete(selected_item)
        db.commit()

    main_window = Tk()
    main_window.geometry('+200+200')

    companies_btn = ttk.Button(main_window, text='Список компаний', command=companies)
    add_plane_btn = ttk.Button(main_window, text='Добавить самолёт', command=planes)
    delete_plane_btn = ttk.Button(main_window, text='Удалить самолёт', command=delete)

    global main_table
    main_table = ttk.Treeview(main_window, height=30, show='headings')
    headers = ['Тип самолёта', '№ Самолёта', 'Тип двигателя', '№ Двигателя', '№ СУ', 'Дата установки', 'Наработка-час\цикл', 'Компания']
    main_table['columns'] = headers

    for header in headers:
        main_table.heading(header, text=header)
        main_table.column(header, anchor=CENTER)
    
    for value in cur.execute('SELECT * FROM planes').fetchall():
        main_table.insert('', 0, values=value)
    
    search_entry = ttk.Entry(main_window)
    search_btn = ttk.Button(main_window, text='Поиск', command=search)

    analisys_btn = ttk.Button(main_window, text='Анализ', command=analize)

    companies_btn.grid(row=0, column=0)
    add_plane_btn.grid(row=0, column=1)
    delete_plane_btn.grid(row=0, column=16)
    analisys_btn.grid(row=0, column=17)
    search_entry.grid(row=0, column=18)
    search_btn.grid(row=0, column=19)
    main_table.grid(row=1, column=0, columnspan=20, pady=5, padx=5)

    main_window.mainloop()

def companies():
    def add_company():
        if companies_entry.get():
            companies_list.insert(0, companies_entry.get())
            companies_query.append(companies_entry.get())
            cur.execute('INSERT INTO companies (name) VALUES (?)', (companies_entry.get(), ))
            db.commit()
            companies_entry.delete(0, END)

    companies_window = Toplevel()
    companies_window.title('Компании')
    companies_window.geometry('+900+300')

    companies_list = Listbox(companies_window, width=50)
    companies_entry = ttk.Entry(companies_window)
    add_btn = ttk.Button(companies_window, text='Добавить', command=add_company)

    for item in cur.execute('SELECT * FROM companies').fetchall():
        companies_list.insert(0, item)

    companies_list.grid(row=0, column=0, columnspan=5, padx=5, pady=5)
    companies_entry.grid(row=1, column=0, sticky='we', columnspan=4, padx=5, pady=(0, 5))
    add_btn.grid(row=1, column=4, sticky='we', padx=(0, 5), pady=(0, 5))

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
    table = ttk.Treeview(planes_window, show='headings')
    headers = ['Тип самолёта', 'Тип двигателя']
    table['columns'] = headers

    for header in headers:
        table.heading(header, text=header)
        table.column(header, anchor=CENTER)
    
    for item in cur.execute('SELECT * FROM types').fetchall():
        table.insert('', 0, values=item)  

    plane_number_label = ttk.Label(planes_window, text='№ Самолёта')
    plane_number_entry = ttk.Entry(planes_window)
    engine_number_label = ttk.Label(planes_window, text='№ Двигателя')
    engine_number_entry = ttk.Entry(planes_window)
    company_label = ttk.Label(planes_window, text='Компания')
    company_enter = ttk.Combobox(planes_window, values=companies_query, width=17)
    pu_position_label = ttk.Label(planes_window, text='№ СУ')
    pu_position_entry = ttk.Combobox(planes_window, values=(1, 2), width=17)
    installation_label = ttk.Label(planes_window, text='Дата установки')
    installation_entry = ttk.Entry(planes_window)
    time_scince_installed_label = ttk.Label(planes_window, text='Наработка')
    time_scince_installed_entry = ttk.Entry(planes_window)
    
    add_type_btn = ttk.Button(planes_window, text='Новый тип', command=plane_types)
    add_plane_btn = ttk.Button(planes_window, text='Добавить', command=add_plane)

    table.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
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
    add_type_btn.grid(row=5, column=1, pady=10)
    add_plane_btn.grid(row=5, column=2, pady=10)

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

    plane_type_label = ttk.Label(plane_types_window, text='Тип самолёта')
    plane_type_entry = ttk.Entry(plane_types_window)
    engine_type_label = ttk.Label(plane_types_window, text='Тип двигателя')
    engine_type_entry = ttk.Entry(plane_types_window)
    add_type_btn = ttk.Button(plane_types_window, text='Добавить', command=add_type)

    plane_type_label.pack(pady=(20, 0))
    plane_type_entry.pack(padx=20)
    engine_type_label.pack(pady=(10, 0))
    engine_type_entry.pack()
    add_type_btn.pack(pady=20)

    plane_types_window.mainloop()

def analisys():
    def add_values():
        cur.execute('INSERT INTO analisys (intensity_fe, intensity_w, intensity_ni, intensity_cr, intensity_mo, intensity_v, intensity_mn, \
        fon_fe, fon_w, fon_ni, fon_cr, fon_mo, fon_v, engine_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', 
        (intensity_fe_entry.get(), intensity_w_entry.get(), intensity_ni_entry.get(), intensity_cr_entry.get(), intensity_mo_entry.get(),
        intensity_v_entry.get(), fon_fe_entry.get(), fon_w_entry.get(), fon_ni_entry.get(), fon_cr_entry.get(), 
        fon_mo_entry.get(), fon_v_entry.get(), engine_number))
        db.commit()

    def calculate():
        if intensity_fe_entry.get() and intensity_w_entry.get() and intensity_ni_entry.get() and intensity_cr_entry.get() and intensity_mo_entry.get() and \
        intensity_v_entry.get() and fon_fe_entry.get() and fon_w_entry.get() and fon_ni_entry.get() and fon_cr_entry.get() and fon_mo_entry.get() and \
        fon_v_entry.get() and measure_fe_entry.get() and measure_w_entry.get() and measure_ni_entry.get() and measure_cr_entry.get() and measure_mo_entry.get() and \
        measure_v_entry.get():
            fe_differences = ((float(measure_fe_entry.get()) - float(fon_fe_entry.get())) / (float(intensity_fe_entry.get()) - float(fon_fe_entry.get()))) * 100
            w_differences = ((float(measure_w_entry.get()) - float(fon_w_entry.get())) / (float(intensity_w_entry.get()) - float(fon_w_entry.get()))) * 100
            ni_differences = ((float(measure_ni_entry.get()) - float(fon_ni_entry.get())) / (float(intensity_ni_entry.get()) - float(fon_ni_entry.get()))) * 100
            cr_differences = ((float(measure_cr_entry.get()) - float(fon_cr_entry.get())) / (float(intensity_cr_entry.get()) - float(fon_cr_entry.get()))) * 100
            mo_differences = ((float(measure_mo_entry.get()) - float(fon_mo_entry.get())) / (float(intensity_mo_entry.get()) - float(fon_mo_entry.get()))) * 100
            v_differences = ((float(measure_v_entry.get()) - float(fon_v_entry.get())) / (float(intensity_v_entry.get()) - float(fon_v_entry.get()))) * 100

            differences_sum = sum([fe_differences, w_differences, ni_differences, cr_differences, mo_differences, v_differences])
            a = 100 / differences_sum

            fe = round(fe_differences * a, 2)
            w = round(w_differences * a, 2)
            ni = round(ni_differences * a, 2)
            cr = round(cr_differences * a, 2)
            mo = round(mo_differences * a, 2)
            v = round(v_differences * a, 2)

            fe_result.insert(0, fe)
            w_result.insert(0, w)
            ni_result.insert(0, ni)
            cr_result.insert(0, cr)
            mo_result.insert(0, mo)
            v_result.insert (0, v)

    def analize():
        query = cur.execute('SELECT * FROM alloy').fetchall()
        lstsqrt = []
        names = []

        for row in query:
            names.append(row[0])
            lstsqrt.append(
                ((float(w_result.get()) - float(row[2]))**2) / (1 + math.sqrt(float(row[2]))) +
                ((float(ni_result.get()) - float(row[3]))**2) / (1 + math.sqrt(float(row[3]))) +
                ((float(cr_result.get()) - float(row[4]))**2) / (1 + math.sqrt(float(row[4]))) +
                ((float(mo_result.get()) - float(row[5]))**2) / (1 + math.sqrt(float(row[5]))) +
                ((float(v_result.get()) - float(row[6]))**2) / (1 + math.sqrt(float(row[6])))
            )

        percent = list(1 / x for x in lstsqrt)
        s = 100 / sum(percent)
        res = list(item * s for item in percent)

        plt.bar(names, res)
        plt.show()

    analisys_window = Toplevel()
    analisys_window.title('Анализ стружки')

    engine_number = main_table.item(main_table.focus()).get('values')[3]
    values = cur.execute('SELECT * FROM analisys WHERE engine_number = ?', (engine_number, )).fetchall()

    base_label = ttk.Label(analisys_window, text='Основа')
    base_menu = ttk.Combobox(analisys_window, values=['Fe', 'Ni', 'Mo', 'V', 'W'], width=2)
    submit_btn = ttk.Button(analisys_window, text='Измерить', command=calculate)
    save_btn = ttk.Button(analisys_window, text='Сохранить', command=add_values)
    analize_btn = ttk.Button(analisys_window, text='Анализ', command=analize)

    analize_btn.grid(row=0, column=0)
    submit_btn.grid(row=0, column=5)
    save_btn.grid(row=0, column=3, columnspan=5)

    # Интенсивность

    fe_label = ttk.Label(analisys_window, text='Fe')
    w_label = ttk.Label(analisys_window, text='W')
    ni_label = ttk.Label(analisys_window, text='Ni')
    cr_label = ttk.Label(analisys_window, text='Cr')
    mo_label = ttk.Label(analisys_window, text='Mo')
    v_label = ttk.Label(analisys_window, text='V')

    fe_label.grid(row=2, column=0)
    w_label.grid(row=2, column=1)
    ni_label.grid(row=2, column=2)
    cr_label.grid(row=2, column=3)
    mo_label.grid(row=2, column=4)
    v_label.grid(row=2, column=5)

    intensity_label = ttk.Label(analisys_window, text='Интенсивность')
    intensity_fe_entry = ttk.Entry(analisys_window, width=10)
    intensity_w_entry = ttk.Entry(analisys_window, width=10)
    intensity_ni_entry = ttk.Entry(analisys_window, width=10)
    intensity_cr_entry = ttk.Entry(analisys_window, width=10,)
    intensity_mo_entry = ttk.Entry(analisys_window, width=10)
    intensity_v_entry = ttk.Entry(analisys_window, width=10)

    intensity_label.grid(row=1, column=0, columnspan=7, pady=(20, 10))
    intensity_fe_entry.grid(row=3, column=0, padx=(10, 2))
    intensity_w_entry.grid(row=3, column=1, padx=2)
    intensity_ni_entry.grid(row=3, column=2, padx=2)
    intensity_cr_entry.grid(row=3, column=3, padx=2)
    intensity_mo_entry.grid(row=3, column=4, padx=2)
    intensity_v_entry.grid(row=3, column=5, padx=2)

    #Фон

    fon_label = Label(analisys_window, text='Фон')
    fon_fe_entry = ttk.Entry(analisys_window, width=10)
    fon_w_entry = ttk.Entry(analisys_window, width=10)
    fon_ni_entry = ttk.Entry(analisys_window, width=10)
    fon_cr_entry = ttk.Entry(analisys_window, width=10)
    fon_mo_entry = ttk.Entry(analisys_window, width=10)
    fon_v_entry = ttk.Entry(analisys_window, width=10)

    fon_label.grid(row=4, column=0, columnspan=7, pady=(20, 10))
    fon_fe_entry.grid(row=5, column=0, padx=(10, 2))
    fon_w_entry.grid(row=5, column=1, padx=2)
    fon_ni_entry.grid(row=5, column=2, padx=2)
    fon_cr_entry.grid(row=5, column=3, padx=2)
    fon_mo_entry.grid(row=5, column=4, padx=2)
    fon_v_entry.grid(row=5, column=5, padx=2)

    if values:
        intensity_fe_entry.insert(0, values[0][0])
        intensity_w_entry.insert(0, values[0][1])
        intensity_ni_entry.insert(0, values[0][2])
        intensity_cr_entry.insert(0, values[0][3])
        intensity_mo_entry.insert(0, values[0][4])
        intensity_v_entry.insert(0, values[0][5])
        fon_fe_entry.insert(0, values[0][7])
        fon_w_entry.insert(0, values[0][8])
        fon_ni_entry.insert(0, values[0][9])
        fon_cr_entry.insert(0, values[0][10])
        fon_mo_entry.insert(0, values[0][11])
        fon_v_entry.insert(0, values[0][12])


    measure_label = ttk.Label(analisys_window, text='Измерения')
    measure_fe_entry = ttk.Entry(analisys_window, width=10)
    measure_w_entry = ttk.Entry(analisys_window, width=10)
    measure_ni_entry = ttk.Entry(analisys_window, width=10)
    measure_cr_entry = ttk.Entry(analisys_window, width=10)
    measure_mo_entry = ttk.Entry(analisys_window, width=10)
    measure_v_entry = ttk.Entry(analisys_window, width=10)

    measure_label.grid(row=6, columnspan=7, pady=(20, 10))
    measure_fe_entry.grid(row=7, column=0, padx=(10, 2))
    measure_w_entry.grid(row=7, column=1, padx=2)
    measure_ni_entry.grid(row=7, column=2, padx=2)
    measure_cr_entry.grid(row=7, column=3, padx=2)
    measure_mo_entry.grid(row=7, column=4, padx=2)
    measure_v_entry.grid(row=7, column=5, padx=2)


    result_label = ttk.Label(analisys_window, text='Результат')
    fe_result = ttk.Entry(analisys_window, width=10)
    w_result = ttk.Entry(analisys_window, width=10)
    ni_result = ttk.Entry(analisys_window, width=10)
    cr_result = ttk.Entry(analisys_window, width=10)
    mo_result = ttk.Entry(analisys_window, width=10)
    v_result = ttk.Entry(analisys_window, width=10)

    result_label.grid(row=8, columnspan=7, pady=(20, 10))
    fe_result.grid(row=9, column=0, padx=(10, 2))
    w_result.grid(row=9, column=1, padx=2)
    ni_result.grid(row=9, column=2, padx=2)
    cr_result.grid(row=9, column=3, padx=2)
    mo_result.grid(row=9, column=4, padx=2)
    v_result.grid(row=9, column=5, padx=2)

    analisys_table = ttk.Treeview(analisys_window, show='headings')
    headings = [1, 2, 3, 4, 5, 6, 7]
    analisys_table['columns'] = headings

    for heading in headings:
        analisys_table.column(heading, width=75, anchor=CENTER)
    
    alloys = cur.execute('SELECT * FROM alloy').fetchall()


    for row in alloys:
        analisys_table.insert('', 0, values=row)

    analisys_table.grid(row=12, column=0, columnspan=6, pady=(20, 10), padx=10)

    analisys_window.mainloop()

if __name__ == '__main__':
    main()