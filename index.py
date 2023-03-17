from tkinter import *
from tkinter import ttk
from tkinter.messagebox import showerror, showinfo
import sqlite3
import json
import os
from math import sqrt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

db = sqlite3.connect('data.db')
cur = db.cursor()

# загрузка данный из json файла
def load_data_from_json(x):
    global json_file
    with open(x, 'r', encoding='utf-8') as file:
        json_file = json.load(file)

# загрузка данный в json файл
def load_data_to_json(x):
    with open(x, 'w') as file:
        json.dump(json_file, file, indent=4)

# список компаний из json файла
load_data_from_json('json_data/companies.json')
companies_list = list(i.get('name') for i in json_file)

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
    # поиск по типу самолёта и типу двигателя
    def search():
        main_table.delete(*main_table.get_children())
        for i in planes_list:
            if search_entry.get() in i[0] or search_entry.get() in i[2]:
                main_table.insert('', 0, values=i) 
    
    def analize():
        if main_table.focus():
            analisys()
        else:
            showinfo(message='Выберете самолёт')
    
    def delete():
        selected_item = main_table.item(main_table.focus()).get('values')
        for i in json_file:
            if i['plane_number'] == selected_item[1]:
                json_file.remove(i)
                main_table.delete(main_table.focus())
                load_data_to_json('json_data/planes.json')

    main_window = Tk()
    main_window.geometry('+200+200')

    companies_btn = ttk.Button(main_window, text='Список компаний', command=companies)
    add_plane_btn = ttk.Button(main_window, text='Добавить самолёт', command=planes)
    delete_plane_btn = ttk.Button(main_window, text='Удалить самолёт', command=delete)

    # таблица самолётов
    global main_table
    main_table = ttk.Treeview(main_window, height=30, show='headings')
    headings = ['Тип самолёта', '№ Самолёта', 'Тип двигателя', '№ Двигателя', '№ СУ', 'дата установки', 'Наработка-час\цикл', 'Компания']
    main_table['columns'] = headings

    for header in headings:
        main_table.heading(header, text=header)
        main_table.column(header, anchor=CENTER)
    
    load_data_from_json('json_data/planes.json')
    # список самолётов из json файла
    planes_list = list((i['plane_type'], i['plane_number'], i['engine_type'], i['engine_number'], 
    i['PU_position'], i['installation'], i['time_scince_installed'], i['company']) for i in json_file)

    for i in planes_list:
        main_table.insert('', 0, values=i)
    
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
        load_data_from_json('json_data/companies.json')
        json_file.append({'name': companies_entry.get()})
        companies_list.append(companies_entry.get())
        companies_table.insert('', 0, values=(companies_entry.get(),))
        load_data_to_json('json_data/companies.json')

    # не добавлять числа!!!
    def delete_company():
        selected_item = companies_table.item(companies_table.focus()).get('values')[0]
        load_data_from_json('json_data/companies.json')
        for i in json_file:
            if i['name'] == selected_item:
                json_file.remove(i)
                companies_list.remove(selected_item)
                companies_table.delete(companies_table.focus())
                load_data_to_json('json_data/companies.json')

    companies_window = Toplevel()
    companies_window.title('Список компаний')
    companies_window.geometry('+900+300')

    # список компаний
    companies_table = ttk.Treeview(companies_window, columns=(1,), show='headings')
    companies_table.heading(1, text='Компания')

    # добавить новую компанию
    companies_entry = ttk.Entry(companies_window)
    add_company_btn = ttk.Button(companies_window, text='Добавить', command=add_company)
    delete_company_btn = ttk.Button(companies_window, text='Удалить', command=delete_company)

    for i in companies_list:
        companies_table.insert('', 0, values=(i,))

    companies_table.grid(row=0, column=0, columnspan=6, padx=5, pady=5, sticky='we')
    companies_entry.grid(row=1, column=0, sticky='we', columnspan=3, padx=5, pady=(0, 5))
    add_company_btn.grid(row=1, column=4, sticky='we', padx=(0, 5), pady=(0, 5))
    delete_company_btn.grid(row=1, column=5, sticky='we')

    companies_window.mainloop()

def planes():
    def add_plane():
        types = planes_table.item(planes_table.focus()).get('values') # тип самолёта и двигателя из таблицы
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
            load_data_from_json('json_data/planes.json')
            json_file.append(
                {
                    'plane_type': types[0], 
                    'plane_number': plane_number_entry.get(), 
                    'engine_type': types[1],
                    'engine_number': engine_number_entry.get(),
                    'PU_position': pu_position_entry.get(),
                    'installation': installation_entry.get(),
                    'time_scince_installed': time_scince_installed_entry.get(),
                    'company': company_enter.get()
                }
            )
            load_data_to_json('json_data/planes.json')
        else:
            showerror(message='Вы не выбрали тип самолёта')
    
    def delete_plane_type():
        if planes_table.item(planes_table.focus()).get('values'):
            pass
        else:
            showerror(message='Вы не выбрали тип самолёта')

    planes_window = Toplevel()
    planes_window.title('Главная')
    planes_window.geometry('+700+300')

    global planes_table
    planes_table = ttk.Treeview(planes_window, show='headings')
    headers = ['Тип самолёта', 'Тип двигателя']
    planes_table['columns'] = headers

    for header in headers:
        planes_table.heading(header, text=header)
        planes_table.column(header, anchor=CENTER)
    
    load_data_from_json('json_data/plane_types.json')
    for i in json_file:
        planes_table.insert('', 0, values=(i.get('plane_type'), i.get('engine_type')))

    plane_number_label = ttk.Label(planes_window, text='№ Самолёта')
    plane_number_entry = ttk.Entry(planes_window)
    engine_number_label = ttk.Label(planes_window, text='№ Двигателя')
    engine_number_entry = ttk.Entry(planes_window)
    company_label = ttk.Label(planes_window, text='Компания')
    company_enter = ttk.Combobox(planes_window, values=companies_list, width=17)
    pu_position_label = ttk.Label(planes_window, text='№ СУ')
    pu_position_entry = ttk.Combobox(planes_window, values=(1, 2), width=17)
    installation_label = ttk.Label(planes_window, text='Дата установки')
    installation_entry = ttk.Entry(planes_window)
    time_scince_installed_label = ttk.Label(planes_window, text='Наработка')
    time_scince_installed_entry = ttk.Entry(planes_window)
    
    add_type_btn = ttk.Button(planes_window, text='Новый тип', command=plane_types)
    add_plane_btn = ttk.Button(planes_window, text='Добавить', command=add_plane)
    delete_type_btn = ttk.Button(planes_window, text='Удалить', command=delete_plane_type)

    planes_table.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
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

    add_type_btn.grid(row=5, column=0, pady=20)
    add_plane_btn.grid(row=5, column=1)
    delete_type_btn.grid(row=5, column=2)

    planes_window.mainloop()

def plane_types():
    def add_type(): # добавить тип самолёта и двигателя
        if plane_type_entry.get() and engine_type_entry.get():
            load_data_from_json('json_data/plane_types.json')
            json_file.append({'plane_type': plane_type_entry.get(), 'engine_type': engine_type_entry.get()})
            planes_table.insert('', 0, values=(plane_type_entry.get(), engine_type_entry.get()))
            load_data_to_json('json_data/plane_types.json')

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
    def calculate():
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

        analize()

    def analize():
        names = [row[0] for row in alloys_list]
        lstsqrt = [((float(w_result.get())) - row[2]**2) / (1 + sqrt(row[2])) + 
                   ((float(w_result.get())) - row[3]**2) / (1 + sqrt(row[3])) + 
                   ((float(w_result.get())) - row[4]**2) / (1 + sqrt(row[4])) +
                   ((float(w_result.get())) - row[5]**2) / (1 + sqrt(row[5])) +
                   ((float(w_result.get())) - row[6]**2) / (1 + sqrt(row[6])) for row in alloys_list]

        percent = list(1 / x for x in lstsqrt)
        s = 100 / sum(percent)
        res = list(item * s for item in percent)
        alloys_items = zip(names, res)
        
        alloys_items_sorted = sorted(alloys_items, key=lambda tup: tup[1])
        global chosen_alloy
        chosen_alloy = alloys_items_sorted[-1][0]
        
        font = {'size': 5}

        matplotlib.rc('font', **font)
        figure = Figure(figsize=(8, 3), dpi=100)
        figure_canvas = FigureCanvasTkAgg(figure, analisys_window)
        axes = figure.add_subplot()
        axes.bar(names, res)
        alloy_result_label = Label(analisys_window, text=f'Вероятный сплав: {chosen_alloy}: {alloys_items_sorted[-1][1]}%', 
        font='Arial 10', fg='red')

        alloy_result_label.grid(row=17, column=2, columnspan=7)
        figure_canvas.get_tk_widget().grid(row=18, column=2, columnspan=7)
    
    # def open_file():
    #     for file in os.listdir('files'):
    #         if 'M50' in file:
    #             os.startfile(f'files\{file}', 'edit')

    analisys_window = Toplevel()
    analisys_window.title('Анализ стружки')
    analisys_window.geometry('+500+50')

    
    load_data_from_json('json_data/analysis.json')
    measures_list = list((x['fe'], x['w'], x['ni'], x['cr'], x['mo'], x['v']) for x in json_file)
    load_data_from_json('json_data/alloys.json')
    alloys_list = list([(x['name'], x['fe'], x['w'], x['ni'], x['cr'], x['mo'], x['v']) for x in json_file])

    submit_btn = ttk.Button(analisys_window, text='Измерить')
    open_btn = ttk.Button(analisys_window, text='Открыть')

    submit_btn.grid(row=0, column=7, pady=10)
    open_btn.grid(row=0, column=8)

    # информация об самолёте

    plane_number_label = ttk.Label(analisys_window, text='Номер самолёта')
    plane_number_entry = ttk.Entry(analisys_window, width=10)
    su_number_label = ttk.Label(analisys_window, text='Номер СУ')
    su_number_entry = ttk.Entry(analisys_window, width=10)
    engine_number_label = ttk.Label(analisys_window, text='Номер двигателя')
    engine_number_entry = ttk.Entry(analisys_window, width=10)
    engine_type_label = ttk.Label(analisys_window, text='Тип двигателя')
    engine_type_entry = ttk.Entry(analisys_window, width=10)

    plane_number_label.grid(row=3, column=0)
    plane_number_entry.grid(row=3, column=1)
    su_number_label.grid(row=4, column=0)
    su_number_entry.grid(row=4, column=1)
    engine_number_label.grid(row=5, column=0)
    engine_number_entry.grid(row=5, column=1)
    engine_type_label.grid(row=6, column=0)
    engine_type_entry.grid(row=6, column=1)

    # информация об операторе

    operator_label = ttk.Label(analisys_window, text='имя')
    operator_entry = ttk.Entry(analisys_window)
    date_label = ttk.Label(analisys_window, text='дата')
    date_entry = ttk.Entry(analisys_window)

    operator_label.grid(row=13, column=0)
    operator_entry.grid(row=13, column=1)
    date_label.grid(row=14, column=0)
    date_entry.grid(row=14, column=1)

    # описание

    description = Text(analisys_window, width=30, height=10, border=2)
    description.grid(row=18, column=0, columnspan=2, padx=10)

    # Интенсивность

    fe_label = ttk.Label(analisys_window, text='Fe')
    w_label = ttk.Label(analisys_window, text='W')
    ni_label = ttk.Label(analisys_window, text='Ni')
    cr_label = ttk.Label(analisys_window, text='Cr')
    mo_label = ttk.Label(analisys_window, text='Mo')
    v_label = ttk.Label(analisys_window, text='V')

    fe_label.grid(row=2, column=3)
    w_label.grid(row=2, column=4)
    ni_label.grid(row=2, column=5)
    cr_label.grid(row=2, column=6)
    mo_label.grid(row=2, column=7)
    v_label.grid(row=2, column=8)

    intensity_label = ttk.Label(analisys_window, text='Интенсивность')
    intensity_fe_entry = ttk.Entry(analisys_window, width=10)
    intensity_w_entry = ttk.Entry(analisys_window, width=10)
    intensity_ni_entry = ttk.Entry(analisys_window, width=10)
    intensity_cr_entry = ttk.Entry(analisys_window, width=10)
    intensity_mo_entry = ttk.Entry(analisys_window, width=10)
    intensity_v_entry = ttk.Entry(analisys_window, width=10)

    intensity_label.grid(row=3, column=2)
    intensity_fe_entry.grid(row=3, column=3, pady=5)
    intensity_w_entry.grid(row=3, column=4)
    intensity_ni_entry.grid(row=3, column=5)
    intensity_cr_entry.grid(row=3, column=6)
    intensity_mo_entry.grid(row=3, column=7)
    intensity_v_entry.grid(row=3, column=8)

    intensity_fe_entry.insert(0, 532134)
    intensity_w_entry.insert(0, 153148)
    intensity_ni_entry.insert(0, 377087)
    intensity_cr_entry.insert(0, 556578)
    intensity_mo_entry.insert(0, 76710)
    intensity_v_entry.insert(0, 335563)

    #Фон

    fon_label = Label(analisys_window, text='Фон')
    fon_fe_entry = ttk.Entry(analisys_window, width=10)
    fon_w_entry = ttk.Entry(analisys_window, width=10)
    fon_ni_entry = ttk.Entry(analisys_window, width=10)
    fon_cr_entry = ttk.Entry(analisys_window, width=10)
    fon_mo_entry = ttk.Entry(analisys_window, width=10)
    fon_v_entry = ttk.Entry(analisys_window, width=10)

    fon_label.grid(row=4, column=2)
    fon_fe_entry.grid(row=4, column=3, pady=5)
    fon_w_entry.grid(row=4, column=4)
    fon_ni_entry.grid(row=4, column=5)
    fon_cr_entry.grid(row=4, column=6)
    fon_mo_entry.grid(row=4, column=7)
    fon_v_entry.grid(row=4, column=8)

    fon_fe_entry.insert(0, 67)
    fon_w_entry.insert(0, 189)
    fon_ni_entry.insert(0, 122)
    fon_cr_entry.insert(0, 31)
    fon_mo_entry.insert(0, 20)
    fon_v_entry.insert(0, 33)

    # измерения

    measure_label = ttk.Label(analisys_window, text='Измерения')
    measure_fe_entry = ttk.Entry(analisys_window, width=10)
    measure_w_entry = ttk.Entry(analisys_window, width=10)
    measure_ni_entry = ttk.Entry(analisys_window, width=10)
    measure_cr_entry = ttk.Entry(analisys_window, width=10)
    measure_mo_entry = ttk.Entry(analisys_window, width=10)
    measure_v_entry = ttk.Entry(analisys_window, width=10)

    measure_label.grid(row=5, column=2)
    measure_fe_entry.grid(row=5, column=3, pady=5)
    measure_w_entry.grid(row=5, column=4)
    measure_ni_entry.grid(row=5, column=5)
    measure_cr_entry.grid(row=5, column=6)
    measure_mo_entry.grid(row=5, column=7)
    measure_v_entry.grid(row=5, column=8)

    measure_fe_entry.insert(0, measures_list[-1][0])
    measure_w_entry.insert(0, measures_list[-1][1])
    measure_ni_entry.insert(0, measures_list[-1][2])
    measure_cr_entry.insert(0, measures_list[-1][3])
    measure_mo_entry.insert(0, measures_list[-1][4])
    measure_v_entry.insert(0, measures_list[-1][5])

    # результат

    result_label = ttk.Label(analisys_window, text='Результат')
    fe_result = ttk.Entry(analisys_window, width=10)
    w_result = ttk.Entry(analisys_window, width=10)
    ni_result = ttk.Entry(analisys_window, width=10)
    cr_result = ttk.Entry(analisys_window, width=10)
    mo_result = ttk.Entry(analisys_window, width=10)
    v_result = ttk.Entry(analisys_window, width=10)

    result_label.grid(row=6, column=2)
    fe_result.grid(row=6, column=3, pady=5)
    w_result.grid(row=6, column=4)
    ni_result.grid(row=6, column=5)
    cr_result.grid(row=6, column=6)
    mo_result.grid(row=6, column=7)
    v_result.grid(row=6, column=8)

    calculate()

    analisys_table = ttk.Treeview(analisys_window, show='headings')
    headings = ['Название', 'Fe', 'W', 'Ni', 'Cr', 'M', 'V']
    analisys_table['columns'] = headings

    for heading in headings:
        analisys_table.column(heading, width=100, anchor=CENTER)
        analisys_table.heading(heading, text=heading)
    
    for i in alloys_list:
        analisys_table.insert('', 0, values=i)

    analisys_table.grid(row=12, column=2, columnspan=7, rowspan=4, padx=10, pady=10)

    main_table_items = main_table.item(main_table.focus()).get('values')

    plane_number_entry.insert(0, main_table_items[1])
    su_number_entry.insert(0, main_table_items[4])
    engine_number_entry.insert(0, main_table_items[3])
    engine_type_entry.insert(0, main_table_items[2])

    analisys_window.mainloop()


if __name__ == '__main__':
    main()