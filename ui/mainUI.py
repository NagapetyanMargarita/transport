import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from xml.etree.ElementTree import tostring
from sqlScripts import rcScripts
from tkcalendar import DateEntry  # Для календаря нужно установить: pip install tkcalendar
from documents import documentCreator
from documents import ObjectStorage




class DatabaseApp:
    def __init__(self, root):
        self.date_entry = None
        self.root = root
        self.root.title("База данных - Просмотр информации")
        self.root.geometry("800x600")

        # Инициализация базы данных

        # Создание интерфейса
        self.create_widgets()

        # Загрузка данных РЦ
        self.rcData()

    def object_storage(file_path):
        # Прямая передача ключей в конструктор
        storage = ObjectStorage.YandexStaticKeyStorage(
            key_id='YCAJE8gyPb9rAuyGYYKicSuvS',
            secret_key='YCMmulTnsXttMXesYJLDTGxOToQ1gVELqj58cgGh',
            bucket_name='trucking-documents'
        )

        # Тестируем подключение
        if storage.test_connection():
            # Просматриваем файлы
            # storage.list_files()

            # Загружаем документ
            storage.upload_docx_file(file_path)

    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Фрейм для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        # Поле выбора даты
        ttk.Label(filter_frame, text="Дата:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.date_entry = DateEntry(
            filter_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            mindate=date(2020, 1, 1)
        )
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        # Поле выбора РЦ
        ttk.Label(filter_frame, text="РЦ:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.rc_var = tk.StringVar()
        self.rc_combobox = ttk.Combobox(filter_frame, textvariable=self.rc_var, width=20, state="readonly")
        self.rc_combobox.grid(row=0, column=3, padx=5, pady=5)
        self.rc_combobox.bind('<<ComboboxSelected>>', self.on_rc_select)

        # Кнопки управления
        button_frame = ttk.Frame(filter_frame)
        button_frame.grid(row=0, column=4, padx=10, pady=5)

        ttk.Button(button_frame, text="Обновить", command=self.load_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(button_frame, text="Только действующие", command=self.onActiveMl).pack(side=tk.LEFT, padx=2)
        # ttk.Button(button_frame, text="Показать все", command=self.show_all_data).pack(side=tk.LEFT, padx=2)

        # Главное поле для отображения данных (Treeview)
        data_frame = ttk.LabelFrame(self.root, text="Данные из базы", padding=10)
        data_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Создание Treeview с прокруткой
        tree_scroll = ttk.Scrollbar(data_frame)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = ttk.Treeview(
            data_frame,
            yscrollcommand=tree_scroll.set,
            selectmode="extended",  # Возможность выбора нескольких строк
            columns=('ID маршрута', 'РЦ', 'Дата', 'Путевой лист', 'ТС', 'Прицеп', 'Статус маршрута', 'ВЭ на маршруте')
        )
        self.tree.pack(fill=tk.BOTH, expand=True)

        tree_scroll.config(command=self.tree.yview)

        # Настройка колонок
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('ID маршрута', width=50, anchor=tk.CENTER)
        self.tree.column('РЦ', width=100, anchor=tk.CENTER)
        self.tree.column('Дата', width=100, anchor=tk.CENTER)
        self.tree.column('Путевой лист', width=100, anchor=tk.W)
        self.tree.column('ТС', width=80, anchor=tk.CENTER)
        self.tree.column('Прицеп', width=80, anchor=tk.E)
        self.tree.column('Статус маршрута', width=100, anchor=tk.E)
        self.tree.column('ВЭ на маршруте', width=100, anchor=tk.E)

        # Заголовки колонок
        self.tree.heading('ID маршрута', text='ID маршрута')
        self.tree.heading('РЦ', text='РЦ')
        self.tree.heading('Дата', text='Дата')
        self.tree.heading('Путевой лист', text='Путевой лист')
        self.tree.heading('ТС', text='ТС')
        self.tree.heading('Прицеп', text='Прицеп')
        self.tree.heading('Статус маршрута', text='Статус маршрута')
        self.tree.heading('ВЭ на маршруте', text='ВЭ на маршруте')


        # Фрейм для кнопок управления данными
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(action_frame, text="Открыть маршрут", command=self.openRoute).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Экспорт в файл", command=self.export_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Информация о выбранном", command=self.show_selected_info).pack(side=tk.LEFT,
                                                                                                      padx=5)

        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готово")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Загрузка всех данных при запуске
        # self.show_all_data()

    def rcData(self):
        """Загрузка данных РЦ из базы данных"""
        rc_names = rcScripts.returnRC()
        rcList = list()
        if rc_names:
            for row in rc_names:
                rcList.append(row['name'])
            self.rc_combobox["values"] = rcList

    def load_data(self):
        """Загрузка данных по выбранным фильтрам"""


        try:
            # Очистка Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Получение значений фильтров

            selected_rc = self.rc_var.get()

            # Построение запроса
            rows = rcScripts.returnMldata(selected_rc)

            # Заполнение Treeview
            for row in rows:
                values = [value for value in row.values()]
                values[-3:] = [' '.join(values[-3:])]
                values[2] =  datetime.fromtimestamp(values[2] / 1000000.0)
                self.tree.insert('', tk.END, values=values)

            self.status_var.set(f"Загружено {len(rows)} записей")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {str(e)}")

    # def show_all_data(self):
    #     """Показать все данные"""
    #     try:
    #         # Очистка Treeview
    #         for item in self.tree.get_children():
    #             self.tree.delete(item)
    #
    #         query = """
    #             SELECT md.id, rl.name, md.date, md.product_name, md.quantity, md.price
    #             FROM main_data md
    #             JOIN rc_list rl ON md.rc_id = rl.id
    #             ORDER BY md.id
    #         """
    #
    #         self.cursor.execute(query)
    #         rows = self.cursor.fetchall()
    #
    #         # Заполнение Treeview
    #         for row in rows:
    #             self.tree.insert('', tk.END, values=row)
    #
    #         self.status_var.set(f"Загружено всех записей: {len(rows)}")
    #
    #     except Exception as e:
    #         messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def onActiveMl(self):
        """Очистка фильтров"""
        try:
            # Очистка Treeview
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Получение значений фильтров

            selected_rc = self.rc_var.get()

            # Построение запроса
            rows = rcScripts.returnMldataActive(selected_rc)

            # Заполнение Treeview
            for row in rows:
                values = [value for value in row.values()]
                values[-3:] = [' '.join(values[-3:])]
                values[2] = datetime.fromtimestamp(values[2] / 1000000.0)
                self.tree.insert('', tk.END, values=values)

            self.status_var.set(f"Загружено {len(rows)} записей")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def on_rc_select(self, event):
        """Обработчик выбора РЦ"""
        selected_rc = self.rc_var.get()
        self.status_var.set(f"Выбран РЦ: {selected_rc}")

    def openRoute(self):
        """Удаление выбранных записей"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Предупреждение", "Не выбрано ни одной записи для удаления")
            return


        try:
            for item in selected_items:
                item_id = self.tree.item(item)['values'][0]
                if self.tree.item(item)['values'][6] == 'не открыт':
                    if messagebox.askyesno("Подтверждение",
                                       f"Вы уверены, что хотите открыть маршрут" + str(item_id) + "?"):
                        print(item_id)
                        print(rcScripts.openRouteWithRouteId(int(item_id)))
                        self.onActiveMl()
                        file_path = "documents/route_sheet.docx"
                        documentCreator.generate_document(item_id, self.tree.item(item)['values'][3],
                                                          self.tree.item(item)['values'][7], seal_path="documents/seal.jpg",
                      output_file=file_path)
                        documentCreator.object_storage(file_path)
                        # Удаление файла
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            print(f"Файл удален: {file_path}")
                        else:
                            print(f"Файл не найден: {file_path}")
                else:
                    messagebox.showwarning("Предупреждение", "Данный маршрут уже открыт")
            #     self.cursor.execute("DELETE FROM main_data WHERE id = ?", (item_id,))
            #
            # self.conn.commit()
            # self.show_all_data()  # Обновляем отображение


        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка удаления: {str(e)}")

    def export_data(self):
        """Экспорт данных в файл (упрощенная версия)"""
        try:
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showwarning("Предупреждение", "Не выбрано ни одной записи для экспорта")
                return

            with open("exported_data.txt", "w", encoding="utf-8") as f:
                f.write("ID\tРЦ\tДата\tНаименование\tКоличество\tЦена\n")
                for item in selected_items:
                    values = self.tree.item(item)['values']
                    f.write("\t".join(map(str, values)) + "\n")

            messagebox.showinfo("Успех", f"Данные экспортированы в файл: exported_data.txt")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка экспорта: {str(e)}")

    def show_selected_info(self):
        """Показать информацию о выбранных записях"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Предупреждение", "Не выбрано ни одной записи")
            return

        info = f"Выбрано записей: {len(selected_items)}\n\n"
        total_quantity = 0
        total_value = 0

        for item in selected_items:
            values = self.tree.item(item)['values']
            info += f"ID: {values[0]}, Товар: {values[3]}, Кол-во: {values[4]}, Цена: {values[5]}\n"
            total_quantity += values[4]
            total_value += values[4] * values[5]

        info += f"\nИтого количество: {total_quantity}"
        info += f"\nОбщая стоимость: {total_value:.2f}"

        messagebox.showinfo("Информация о выбранных записях", info)


def main():
    root = tk.Tk()
    app = DatabaseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
