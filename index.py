from tkinter import *
from tkinter import filedialog
import ttkbootstrap as ttk
from tkinter.messagebox import showerror, showinfo
import sqlite3
import json
import os
import matplotlib
from PIL import Image, ImageTk
from math import sqrt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from time import localtime

db = sqlite3.connect('data.db')
cur = db.cursor()

# Загрузка данный из json файла
def load_data_from_json(x):
    global json_file
    with open(x, 'r', encoding='utf-8') as file:
        json_file = json.load(file)

# Загрузка данный в json файл
def load_data_to_json(x):
    with open(x, 'w') as file:
        json.dump(json_file, file, indent=4)

# Список компаний из json файла
load_data_from_json('json_data/companies.json')
companies_list = list(i['name'] for i in json_file)

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
    register_window.geometry('+1200+50')

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
    def show_menu(event):
        if main_table.focus():
            context_menu.tk_popup(event.x_root, event.y_root)

    # Поиск по типу самолёта и типу двигателя
    def search():
        main_table.delete(*main_table.get_children())
        for i in planes_list:
            if search_entry.get() in i[0] or search_entry.get() in i[2]:
                main_table.insert('', 0, values=i) 
    
    def delete():
        selected_item = main_table.item(main_table.focus()).get('values')
        for i in json_file:
            if i['plane_number'] == selected_item[1]:
                json_file.remove(i)
                main_table.delete(main_table.focus())
                load_data_to_json('json_data/planes.json')

    main_window = ttk.Window(themename='simplex')

    companies_btn = ttk.Button(main_window, text='Список компаний', command=companies)
    companies_btn.grid(row=0, column=0, pady=(10, 0))

    add_plane_btn = ttk.Button(main_window, text='Добавить самолёт', command=planes)
    add_plane_btn.grid(row=0, column=1, pady=(10, 0))

    search_entry = ttk.Entry(main_window)
    search_entry.grid(row=0, column=28, pady=(10, 0))

    search_btn = ttk.Button(main_window, text='Поиск', command=search)
    search_btn.grid(row=0, column=29, pady=(10, 0))

    # Контекстное меню
    context_menu = Menu(main_window, tearoff=0)
    context_menu.add_command(label='Сохранённые сплавы', command=saved_results)
    context_menu.add_command(label='Анализ', command=analysis)
    context_menu.add_separator()
    context_menu.add_command(label='Удалить', command=delete)

    # Таблица самолётов
    global main_table
    headings = ['Тип самолёта', '№ Самолёта', 'Тип двигателя', '№ Двигателя', '№ СУ', 'дата установки', 'Наработка-час\цикл', 'Компания']
    main_table = ttk.Treeview(main_window, height=30, show='headings', columns=headings)

    for header in headings:
        main_table.heading(header, text=header)
        main_table.column(header, anchor=CENTER, width=150)
    
    main_table.grid(row=1, column=0, columnspan=30, padx=10, pady=10)
    # Контекстное меню по кнопке
    main_table.bind('<Button-3>', show_menu)

    # Список самолётов из json файла
    load_data_from_json('json_data/planes.json')
    planes_list = [tuple(i.values()) for i in json_file]
    
    for item in planes_list:
        main_table.insert('', 0, values=item)

    main_window.mainloop()

def companies():
    def add_company():
        load_data_from_json('json_data/companies.json')
        json_file.append({'name': add_company_entry.get()})
        companies_list.append(add_company_entry.get())
        companies_table.insert('', 0, values=(add_company_entry.get(),))
        load_data_to_json('json_data/companies.json')
        add_company_entry.delete(0, END)

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
    
    def show_menu(event):
        if companies_table.focus():
            context_menu.tk_popup(event.x_root, event.y_root)

    companies_window = Toplevel()
    companies_window.title('Список компаний')

    # Список компаний
    companies_table = ttk.Treeview(companies_window, columns=(1,), show='headings', height=15)
    companies_table.heading(1, text='Название')
    companies_table.column(1, anchor=CENTER)
    companies_table.grid(row=0, column=0, columnspan=2)
    companies_table.bind('<Button-3>', show_menu)

    # Добавить новую компанию
    add_company_entry = ttk.Entry(companies_window)
    add_company_entry.grid(row=1, column=0, pady=10, padx=(5, 0))

    add_company_btn = ttk.Button(companies_window, text='Добавить', command=add_company)
    add_company_btn.grid(row=1, column=1, padx=(0, 5))
    
    # Контекстное меню
    context_menu = Menu(companies_window, tearoff=0)
    context_menu.add_command(label='Удалить', command=delete_company)

    for i in companies_list:
        companies_table.insert('', 0, values=(i,))


    companies_window.mainloop()

def planes():
    def add_plane():
        types = planes_table.item(planes_table.focus()).get('values') # тип самолёта и двигателя из таблицы
        if types and plane_number_entry.get() and engine_number_entry.get() and pu_position_entry.get() and \
        installation_entry.get() and time_scince_installed_entry.get() and company_combobox.get():
            main_table.insert('', 0, values=(
                types[0], 
                plane_number_entry.get(), 
                types[1], 
                engine_number_entry.get(), 
                pu_position_entry.get(), 
                installation_entry.get(), 
                time_scince_installed_entry.get(), 
                company_combobox.get()
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
                    'company': company_combobox.get()
                }
            )
            load_data_to_json('json_data/planes.json')
        else:
            showerror(message='Вы не выбрали тип самолёта')
    
    def delete_plane_type():
        selected_item = planes_table.item(planes_table.focus()).get('values')
        for plane_type in json_file:
            if plane_type['plane_type'] == selected_item[0] and plane_type['engine_type'] == selected_item[1]:
                json_file.remove(plane_type)
                planes_table.delete(planes_table.focus())
                load_data_to_json('json_data/plane_types.json')
    
    def show_menu(event):
        if planes_table.focus():
            context_menu.tk_popup(event.x_root, event.y_root)

    planes_window = Toplevel()
    planes_window.title('Главная')

    # Контекстное меню
    context_menu = Menu(planes_window, tearoff=0)
    context_menu.add_command(label='Удалить', command=delete_plane_type)

    global planes_table
    headings = ['Тип самолёта', 'Тип двигателя']
    planes_table = ttk.Treeview(planes_window, show='headings', columns=headings)
    planes_table.grid(row=0, column=0, columnspan=3, padx=5, pady=5)
    planes_table.bind('<Button-3>', show_menu)

    for heading in headings:
        planes_table.heading(heading, text=heading)
        planes_table.column(heading, anchor=CENTER)
    
    # Список типов самолёта из json файла
    load_data_from_json('json_data/plane_types.json')

    for item in json_file:
        planes_table.insert('', 0, values=(item['plane_type'], item['engine_type']))

    plane_number_label = ttk.Label(planes_window, text='№ Самолёта')
    plane_number_label.grid(row=1, column=0)

    plane_number_entry = ttk.Entry(planes_window)
    plane_number_entry.grid(row=2, column=0)

    engine_number_label = ttk.Label(planes_window, text='№ Двигателя')
    engine_number_label.grid(row=1, column=1)

    engine_number_entry = ttk.Entry(planes_window)
    engine_number_entry.grid(row=2, column=1)

    company_label = ttk.Label(planes_window, text='Компания')
    company_label.grid(row=1, column=2)

    company_combobox = ttk.Combobox(planes_window, values=companies_list, width=17, state='readonly')
    company_combobox.grid(row=2, column=2)

    pu_position_label = ttk.Label(planes_window, text='№ СУ')
    pu_position_label.grid(row=3, column=0)

    pu_position_entry = ttk.Combobox(planes_window, values=(1, 2), width=17, state='readonly')
    pu_position_entry.grid(row=4, column=0)

    installation_label = ttk.Label(planes_window, text='Дата установки')
    installation_label.grid(row=3, column=1)

    installation_entry = ttk.Entry(planes_window)
    installation_entry.grid(row=4, column=1)

    time_scince_installed_label = ttk.Label(planes_window, text='Наработка')
    time_scince_installed_label.grid(row=3, column=2)

    time_scince_installed_entry = ttk.Entry(planes_window)
    time_scince_installed_entry.grid(row=4, column=2)
    
    add_plane_btn = ttk.Button(planes_window, text='Добавить', command=add_plane)
    add_plane_btn.grid(row=5, column=0, columnspan=3, pady=10)

    add_type_btn = ttk.Button(planes_window, text='Новый тип', command=plane_types)
    add_type_btn.grid(row=6, column=0, columnspan=3, pady=(0, 10))

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


def analysis():
    def measure():
        fe_differences = ((float(measure_fe_entry.get()) - float(fon_fe_entry.get())) / (float(intensity_fe_entry.get()) - float(fon_fe_entry.get()))) * 100
        w_differences = ((float(measure_w_entry.get()) - float(fon_w_entry.get())) / (float(intensity_w_entry.get()) - float(fon_w_entry.get()))) * 100
        ni_differences = ((float(measure_ni_entry.get()) - float(fon_ni_entry.get())) / (float(intensity_ni_entry.get()) - float(fon_ni_entry.get()))) * 100
        cr_differences = ((float(measure_cr_entry.get()) - float(fon_cr_entry.get())) / (float(intensity_cr_entry.get()) - float(fon_cr_entry.get()))) * 100
        mo_differences = ((float(measure_mo_entry.get()) - float(fon_mo_entry.get())) / (float(intensity_mo_entry.get()) - float(fon_mo_entry.get()))) * 100
        v_differences = ((float(measure_v_entry.get()) - float(fon_v_entry.get())) / (float(intensity_v_entry.get()) - float(fon_v_entry.get()))) * 100

        differences_sum = sum([fe_differences, w_differences, ni_differences, cr_differences, mo_differences, v_differences])
        a = 100 / differences_sum

        fe_rounded = round(fe_differences * a, 2)
        w_rounded = round(w_differences * a, 2)
        ni_rounded = round(ni_differences * a, 2)
        cr_rounded = round(cr_differences * a, 2)
        mo_rounded = round(mo_differences * a, 2)
        v_rounded = round(v_differences * a, 2)

        result_fe_entry.delete(0, END)
        result_w_entry.delete(0, END)
        result_ni_entry.delete(0, END)
        result_cr_entry.delete(0, END)
        result_mo_entry.delete(0, END)
        result_v_entry.delete(0, END)

        result_fe_entry.insert(0, fe_rounded)
        result_w_entry.insert(0, w_rounded)
        result_ni_entry.insert(0, ni_rounded)
        result_cr_entry.insert(0, cr_rounded)
        result_mo_entry.insert(0, mo_rounded)
        result_v_entry.insert(0, v_rounded)

        least_squares = []

        for alloy in alloys_list:
            least_square = \
            (pow((float(result_w_entry.get()) - alloy[2]), 2)) / (1 + sqrt(alloy[2])) + \
            (pow((float(result_ni_entry.get()) - alloy[3]), 2)) / (1 + sqrt(alloy[3])) + \
            (pow((float(result_cr_entry.get()) - alloy[4]), 2)) / (1 + sqrt(alloy[4])) + \
            (pow((float(result_mo_entry.get()) - alloy[5]), 2)) / (1 + sqrt(alloy[5])) + \
            (pow((float(result_v_entry.get()) - alloy[6]), 2)) / (1 + sqrt(alloy[6]))

            least_squares.append(least_square)
                
        percent = list(1 / x for x in least_squares)
        x = 100 / sum(percent)
        result = list(item * x for item in percent)

        names = [alloy[0] for alloy in alloys_list]
        alloys_items = sorted(list(zip(names, result)), key=lambda x: x[1], reverse=True)
        
        for item in alloys_list:
            if item[0] == alloys_items[0][0]:
                selected_alloy_table.insert('', 0, values=item)

        # График
        font = {'size': 6}
        matplotlib.rc('font', **font)

        figure = Figure(figsize=(7, 3), dpi=100)
        global figure_canvas
        figure_canvas = FigureCanvasTkAgg(figure, analysis_window)
        axes = figure.add_subplot()
        axes.barh(names, result, color='red')

        chosen_alloy_label_frame = LabelFrame(analysis_window, text='Выбран сплав')
        chosen_alloy_label_frame.grid(row=17, column=2, columnspan=7, sticky='wens', padx=10, pady=10)

        figure_canvas.get_tk_widget().grid(row=8, column=2, columnspan=7)

        save_btn['state'] = 'enabled'

    def load_photo():
        nonlocal selected_photo
        selected_photo = filedialog.askopenfilename()
        img = Image.open(selected_photo)
        img = img.resize((384, 216))
        img = ImageTk.PhotoImage(img)
        photo_canvas.create_image(0, 0, anchor=NW, image=img)
        description.insert(1, selected_photo)

    def save_result():
        load_data_from_json('json_data/saved_results.json')
        json_file.append({
            'date': f'{localtime()[2]}/{localtime()[1]}/{localtime()[0]} {localtime()[3]}:{localtime()[4]}:{localtime()[5]}',
            'description': description.get(1.0, END),
            'photo': selected_photo,
            'alloy_result': {
                'fe': result_fe_entry.get(),
                'w': result_w_entry.get(),
                'ni': result_ni_entry.get(),
                'cr': result_cr_entry.get(),
                'mo': result_mo_entry.get(),
                'v': result_v_entry.get()
            },
            'plane_number': plane_number_entry.get(),
            'su_number': su_number_entry.get(),
            'engine_number': engine_number_entry.get(),
            'engine_type': engine_type_entry.get(),
            'selected_alloy': selected_alloy_table.item(selected_alloy_table.get_children())['values'][0]
        })

        load_data_to_json('json_data/saved_results.json')

        photo_canvas.delete('all')
        description.delete('1.0', END)
        figure_canvas.get_tk_widget().grid_forget()
        save_btn['state'] = 'disabled'

    def open_file():
        for file in os.listdir('files'):
            if file[:-4] in selected_alloy_table.item(selected_alloy_table.focus())['values'][0]:
                os.startfile(f'files\{file}', 'edit')
    
    def show_menu(event):
        if selected_alloy_table.focus():
            context_menu.tk_popup(event.x_root, event.y_root)

    analysis_window = Toplevel()

    save_btn = ttk.Button(analysis_window, text='Сохранить', command=save_result, state='disabled')
    save_btn.grid(row=0, column=8, pady=(10, 0))

    measure_btn = ttk.Button(analysis_window, text='Измерить', command=measure)
    measure_btn.grid(row=0, column=7, pady=(10, 0))

    # Информация о самолёте
    plane_df = ttk.LabelFrame(analysis_window, text='Данные двигателя')
    plane_df.grid(row=1, column=0, rowspan=5, columnspan=2, sticky='wens', padx=10, pady=10)

    plane_number_label = ttk.Label(plane_df, text='Номер самолёта')
    plane_number_label.grid(row=1, column=0, pady=5)

    plane_number_entry = ttk.Entry(plane_df, width=15)
    plane_number_entry.grid(row=1, column=1, pady=5)

    su_number_label = ttk.Label(plane_df, text='Номер СУ')
    su_number_label.grid(row=2, column=0, pady=5)

    su_number_entry = ttk.Entry(plane_df, width=15)
    su_number_entry.grid(row=2, column=1, pady=5)

    engine_number_label = ttk.Label(plane_df, text='Номер двигателя')
    engine_number_label.grid(row=3, column=0, pady=(5, 0))

    engine_number_entry = ttk.Entry(plane_df, width=15)
    engine_number_entry.grid(row=3, column=1, pady=(5, 0))

    engine_type_label = ttk.Label(plane_df, text='Тип двигателя')
    engine_type_label.grid(row=4, column=0, pady=5)

    engine_type_entry = ttk.Entry(plane_df, width=15)
    engine_type_entry.grid(row=4, column=1, pady=5)

    # Информация из основной таблицы
    main_table_items = main_table.item(main_table.focus())['values']

    plane_number_entry.insert(0, main_table_items[1])
    su_number_entry.insert(0, main_table_items[4])
    engine_number_entry.insert(0, main_table_items[3])
    engine_type_entry.insert(0, main_table_items[2])

    # Материалы основы
    base_df = ttk.LabelFrame(analysis_window, text='Материалы основы')
    base_df.grid(row=1, column=2, rowspan=5, columnspan=7, padx=10, pady=10, sticky='we')

    fe_label = ttk.Label(base_df, text='Fe')
    fe_label.grid(row=1, column=3)

    w_label = ttk.Label(base_df, text='W')
    w_label.grid(row=1, column=4)

    ni_label = ttk.Label(base_df, text='Ni')
    ni_label.grid(row=1, column=5)

    cr_label = ttk.Label(base_df, text='Cr')
    cr_label.grid(row=1, column=6)

    mo_label = ttk.Label(base_df, text='Mo')
    mo_label.grid(row=1, column=7)

    v_label = ttk.Label(base_df, text='V')
    v_label.grid(row=1, column=8)

    # Интенсивность
    intensity_label = ttk.Label(base_df, text='Интенсивность')
    intensity_label.grid(row=2, column=2)

    intensity_fe_entry = ttk.Entry(base_df, width=14)
    intensity_fe_entry.grid(row=2, column=3, padx=(10, 0))

    intensity_w_entry = ttk.Entry(base_df, width=14)
    intensity_w_entry.grid(row=2, column=4, padx=(5, 0))

    intensity_ni_entry = ttk.Entry(base_df, width=14)
    intensity_ni_entry.grid(row=2, column=5, padx=(5, 0))

    intensity_cr_entry = ttk.Entry(base_df, width=14)
    intensity_cr_entry.grid(row=2, column=6, padx=(5, 0))

    intensity_mo_entry = ttk.Entry(base_df, width=14)
    intensity_mo_entry.grid(row=2, column=7, padx=5)

    intensity_v_entry = ttk.Entry(base_df, width=14)
    intensity_v_entry.grid(row=2, column=8, padx=(0, 10))

    # Фон
    fon_label = ttk.Label(base_df, text='Фон')
    fon_label.grid(row=3, column=2, pady=(5, 0))

    fon_fe_entry = ttk.Entry(base_df, width=14)
    fon_fe_entry.grid(row=3, column=3, padx=(10, 0), pady=(5, 0))

    fon_w_entry = ttk.Entry(base_df, width=14)
    fon_w_entry.grid(row=3, column=4, padx=(5, 0), pady=(5, 0))

    fon_ni_entry = ttk.Entry(base_df, width=14)
    fon_ni_entry.grid(row=3, column=5, padx=(5, 0), pady=(5, 0))

    fon_cr_entry = ttk.Entry(base_df, width=14)
    fon_cr_entry.grid(row=3, column=6, padx=(5, 0), pady=(5, 0))

    fon_mo_entry = ttk.Entry(base_df, width=14)
    fon_mo_entry.grid(row=3, column=7, padx=5, pady=(5, 0))

    fon_v_entry = ttk.Entry(base_df, width=14)
    fon_v_entry.grid(row=3, column=8, padx=(0, 10), pady=(5, 0))

    # Измерения
    measure_label = ttk.Label(base_df, text='Измерения')
    measure_label.grid(row=4, column=2)

    measure_fe_entry = ttk.Entry(base_df, width=14)
    measure_fe_entry.grid(row=4, column=3, padx=(10, 0), pady=5)

    measure_w_entry = ttk.Entry(base_df, width=14)
    measure_w_entry.grid(row=4, column=4, padx=(5, 0), pady=5)

    measure_ni_entry = ttk.Entry(base_df, width=14)
    measure_ni_entry.grid(row=4, column=5, padx=(5, 0), pady=5)

    measure_cr_entry = ttk.Entry(base_df, width=14)
    measure_cr_entry.grid(row=4, column=6, padx=(5, 0), pady=5)

    measure_mo_entry = ttk.Entry(base_df, width=14)
    measure_mo_entry.grid(row=4, column=7, padx=5, pady=5)

    measure_v_entry = ttk.Entry(base_df, width=14)
    measure_v_entry.grid(row=4, column=8, padx=(0, 10), pady=5)

    intensity_fe_entry.insert(0, 532134)
    intensity_w_entry.insert(0, 153148)
    intensity_ni_entry.insert(0, 377087)
    intensity_cr_entry.insert(0, 556578)
    intensity_mo_entry.insert(0, 76710)
    intensity_v_entry.insert(0, 335563)

    fon_fe_entry.insert(0, 67)
    fon_w_entry.insert(0, 189)
    fon_ni_entry.insert(0, 122)
    fon_cr_entry.insert(0, 31)
    fon_mo_entry.insert(0, 20)
    fon_v_entry.insert(0, 33)

    measure_fe_entry.insert(0, 28213)
    measure_w_entry.insert(0, 202)
    measure_ni_entry.insert(0, 367)
    measure_cr_entry.insert(0, 1500)
    measure_mo_entry.insert(0, 250)
    measure_v_entry.insert(0, 400)

    # Результат
    result_entry = ttk.Label(base_df, text='Результат')
    result_entry.grid(row=5, column=2, pady=(0, 10))

    result_fe_entry = ttk.Entry(base_df, width=14)
    result_fe_entry.grid(row=5, column=3, padx=(10, 0), pady=(0, 10))

    result_w_entry = ttk.Entry(base_df, width=14)
    result_w_entry.grid(row=5, column=4, padx=(5, 0), pady=(0, 10))

    result_ni_entry = ttk.Entry(base_df, width=14)
    result_ni_entry.grid(row=5, column=5, padx=(5, 0), pady=(0, 10))

    result_cr_entry = ttk.Entry(base_df, width=14)
    result_cr_entry.grid(row=5, column=6, padx=(5, 0), pady=(0, 10))

    result_mo_entry = ttk.Entry(base_df, width=14)
    result_mo_entry.grid(row=5, column=7, padx=5, pady=(0, 10))

    result_v_entry = ttk.Entry(base_df, width=14)
    result_v_entry.grid(row=5, column=8, padx=(0, 10), pady=(0, 10))

    # Фото
    photo_frame = ttk.Frame(analysis_window)
    photo_frame.grid(row=6, column=0, columnspan=2)

    photo_canvas = Canvas(photo_frame)
    photo_canvas.grid(row=6, column=0, columnspan=2)

    # Таблица сплавов
    table_df = ttk.LabelFrame(analysis_window, text='Перечень')
    table_df.grid(row=6, column=2, columnspan=7, sticky='wens', padx=10, pady=10)

    names = ['Название', 'Fe', 'W', 'Ni', 'Cr', 'Mo', 'V']
    alloys_table = ttk.Treeview(table_df, show='headings', columns=names, height=15, bootstyle='primary')
    alloys_table.grid(row=6, column=2, columnspan=7, padx=5, pady=5)

    for name in names:
        alloys_table.heading(name, text=name)
        alloys_table.column(name, anchor=CENTER, width=100)

    load_data_from_json('json_data/alloys.json')

    alloys_list = [(i['name'], i['fe'], i['w'], i['ni'], i['cr'], i['mo'], i['v']) for i in json_file]

    for alloy in alloys_list:
        alloys_table.insert('', 0, values=alloy)
    
    # Выбор фото
    selected_photo = None
    select_photo_btn = ttk.Button(analysis_window, text='Выбрать фото', command=load_photo)
    select_photo_btn.grid(row=7, column=0, columnspan=2)

    # Выбранный сплав
    selected_alloy_df = ttk.LabelFrame(analysis_window, text='Выбран сплав')
    selected_alloy_df.grid(row=7, column=2, columnspan=7, sticky='wens', padx=10, pady=10)

    selected_alloy_table = ttk.Treeview(selected_alloy_df, columns=names, show='headings', height=1, bootstyle='primary')
    selected_alloy_table.grid(row=7, column=2, columnspan=7, padx=5, pady=5)

    for name in names:
        selected_alloy_table.heading(name, text=name)
        selected_alloy_table.column(name, anchor=CENTER, width=100)
    
    selected_alloy_table.bind('<Button-3>', show_menu)

    # Контекстное меню
    context_menu = Menu(analysis_window, tearoff=0)
    context_menu.add_command(label='Открыть файл', command=open_file)
    
    # Описание
    description_df = ttk.LabelFrame(analysis_window, text='Описание')
    description_df.grid(row=8, column=0, columnspan=2, sticky='wens', padx=10, pady=10)

    description = Text(description_df, width=58, height=17)
    description.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    analysis_window.mainloop()

def saved_results():
    def alloy_details():
        alloy_details_window = Toplevel()

        plane_number_label = ttk.Label(alloy_details_window, text='№ Самолёта')
        plane_number_label.grid(row=0, column=0, pady=(5, 0))

        plane_number_entry = ttk.Entry(alloy_details_window)
        plane_number_entry.grid(row=0, column=1, pady=(5, 0))

        su_number_label = ttk.Label(alloy_details_window, text='№ СУ')
        su_number_label.grid(row=0, column=2, pady=(5, 0))

        su_number_entry = ttk.Entry(alloy_details_window)
        su_number_entry.grid(row=0, column=3, pady=(5, 0))

        engine_number_label = ttk.Label(alloy_details_window, text='№ Двигателя')
        engine_number_label.grid(row=1, column=0, pady=(5, 0))

        engine_number_entry = ttk.Entry(alloy_details_window)
        engine_number_entry.grid(row=1, column=1, pady=(5, 0))

        engine_type_label = ttk.Label(alloy_details_window, text='Тип')
        engine_type_label.grid(row=1, column=2, pady=(5, 0))

        engine_type_entry = ttk.Entry(alloy_details_window)
        engine_type_entry.grid(row=1, column=3, pady=(5, 0))
        
        photo_canvas = Canvas(alloy_details_window, bd=2, relief=RAISED)
        photo_canvas.grid(row=2, column=0, columnspan=4, rowspan=3, padx=10, pady=10)

        description = Text(alloy_details_window, width=73, height=11)
        description.grid(row=2, column=5, columnspan=2, padx=10, pady=10)

        headings = ('fe', 'w', 'ni', 'cr', 'mo', 'v')
        result_table = ttk.Treeview(alloy_details_window, show='headings', height=1, columns=headings)
        
        for heading in headings:
            result_table.heading(heading, text=heading)
            result_table.column(heading, width=75, anchor=CENTER)

        result_table.grid(row=3, column=5, columnspan=2)

        alloy_match_label = ttk.Label(alloy_details_window, text='Определён сплав')
        alloy_match_entry = ttk.Entry(alloy_details_window)

        alloy_match_label.grid(row=4, column=5, pady=10)
        alloy_match_entry.grid(row=4, column=6, pady=10)

        for item in json_file:
            if item['date'] == saved_alloys_table.item(saved_alloys_table.focus())['values'][0]:
                plane_number_entry.insert(0, item['plane_number'])
                su_number_entry.insert(0, item['su_number'])
                engine_number_entry.insert(0, item['engine_number'])
                engine_type_entry.insert(0, item['engine_type'])
                description.insert(1.0, item['description'])
                result_table.insert('', 0, values=tuple(item['alloy_result'].values()))
                alloy_match_entry.insert(0, item['selected_alloy'])
                
                if item['photo']:
                    img = Image.open(item['photo'])
                    img = img.resize((384, 216))
                    img = ImageTk.PhotoImage(img)
                    photo_canvas.create_image(0, 0, anchor=NW, image=img)
                    description.insert(1, item['photo'])

        alloy_details_window.mainloop()

    saved_alloys_window = Toplevel()

    saved_alloys_table = ttk.Treeview(saved_alloys_window, show='headings', columns=(1,))
    saved_alloys_table.heading(1, text='Дата')
    saved_alloys_table.column(1, anchor=CENTER)

    load_data_from_json('json_data/saved_results.json')

    for item in json_file:
        saved_alloys_table.insert('', 0, values=(item['date'],))

    saved_alloys_table.pack()

    open_btn = ttk.Button(saved_alloys_window, text='Открыть', command=alloy_details)
    open_btn.pack()

    saved_alloys_window.mainloop()

if __name__ == '__main__':
    main()