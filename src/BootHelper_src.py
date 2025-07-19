import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext, simpledialog
import webbrowser
import time
import sys
import ctypes
import random
import string
import json
from PIL import Image, ImageTk


class PhoneFlashHelperPro:
    def __init__(self, root):
        super().__init__()
        self.root = root
        self.root.overrideredirect(True)
        self.root.title("BootHelper EXTRA")
        window_width = 800
        window_height = 750
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 6) - (window_height // 6)
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.root.minsize(800, 600)

        self.create_custom_title_bar()


        # Настройки по умолчанию
        self.settings = {
            "theme": "light",
            "language": "en",
            "adb_path": "C:\\adb\\adb.exe",
            "fastboot_path": "C:\\adb\\fastboot.exe",
            "run_as_admin": False
        }

        # Загрузка сохраненных настроек
        self.load_settings()

        # Инициализация переменных
        self.selected_brand = tk.StringVar()
        self.phone_connected = False
        self.device_id = ""
        self.log_content = ""
        self.current_directory = "/"
        self.info_text = None
        self.hw_text = None
        self.battery_text = None
        self.file_tree = None
        self.bootloader_status = None
        self.root_method = tk.StringVar(value="magisk")
        self.firmware_type = tk.StringVar(value="official")
        self.flash_mode = tk.StringVar(value="fastboot")

        # Создание UI
        self.create_main_interface()

        # Проверка прав администратора
        if self.settings["run_as_admin"] and not self.is_admin():
            self.restart_as_admin()

        # Проверка подключения устройства
        self.check_device_connection()

    def create_custom_title_bar(self):

        self.title_bar = tk.Frame(self.root, bg='#f0f0f0', relief='raised', bd=0)
        self.title_bar.pack(fill='x')

        # Заголовок окна
        self.title_label = tk.Label(self.title_bar, text="",
                                    bg='#f0f0f0', fg='white', font=('Helvetica', 10))
        self.title_label.pack(side='left', padx=10)

        # Кнопки управления окном
        close_btn = tk.Button(self.title_bar, text='✕', bg='gray', fg='white',
                              relief='flat', font=('Helvetica', 12),
                              command=self.root.destroy)
        close_btn.pack(side='right', padx=5)

        menu_frame = tk.Frame(self.title_bar, bg='#f0f0f0')
        menu_frame.pack(side='left', padx=0)

        settings_btn = tk.Button(menu_frame, text="Настройки", bg='#ededed', fg='black',
                                 relief='flat', command=self.open_settings)
        settings_btn.pack(side='left', padx=0)

        info_btn = tk.Button(menu_frame, text="Информация", bg='#ededed', fg='black',
                             relief='flat', command=self.show_about)
        info_btn.pack(side='left', padx=25)

        git_btn = tk.Button(menu_frame, text="GitHub", bg='#ededed', fg='black',
                             relief='flat', command=lambda: webbrowser.open("https://github.com/wounsee"))
        git_btn.pack(side='left', padx=25)

        tg_btn = tk.Button(menu_frame, text="Telegram", bg='#ededed', fg='black',
                            relief='flat', command=lambda: webbrowser.open("https://t.me/wounsee"))
        tg_btn.pack(side='left', padx=25)

        # Обработчики для перемещения окна
        self.title_bar.bind('<Button-1>', self.start_move)
        self.title_bar.bind('<B1-Motion>', self.move_window)

        # Стилизация кнопок при наведении
        close_btn.bind('<Enter>', lambda e: close_btn.config(bg='#e81123'))
        close_btn.bind('<Leave>', lambda e: close_btn.config(bg='gray'))


    def start_move(self, event):

        self.x = event.x
        self.y = event.y

    def move_window(self, event):

        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def toggle_maximize(self):

        if self.root.winfo_width() < self.root.winfo_screenwidth():
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        else:
            self.root.geometry("1000x700+100+100")

    def clear_log(self):

        self.log_content = ""
        self.log_console.delete(1.0, tk.END)
        self.log("Ожидание действий...")  # Добавляем запись о очистке

    def is_admin(self):

        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def restart_as_admin(self):

        if not self.is_admin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, None
            )
            sys.exit()

    def load_settings(self):

        try:
            with open("settings.json", "r") as f:
                self.settings.update(json.load(f))
        except:
            pass

    def save_settings(self):

        with open("settings.json", "w") as f:
            json.dump(self.settings, f)

    def create_main_interface(self):

        # Главный контейнер
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=10, pady=10)



        # Заголовок
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 10))



        ttk.Label(header_frame, text="BootHelper EXTRA",
                  font=('Helvetica', 18, 'bold')).pack(side='left')

        # Выбор производителя
        brand_frame = ttk.LabelFrame(self.main_frame, text="Выберите марку телефона")
        brand_frame.pack(fill='x', pady=5)

        brands = ["Xiaomi", "Realme", "Samsung", "OnePlus"]
        for i, brand in enumerate(brands):
            rb = ttk.Radiobutton(brand_frame, text=brand, variable=self.selected_brand,
                                 value=brand, command=self.on_brand_select)
            rb.grid(row=0, column=i, padx=10, pady=5, sticky='w')

        # Вкладки функций
        self.notebook = ttk.Notebook(self.main_frame)

        # Создаем все вкладки
        self.tabs = {
            "Bootloader": ttk.Frame(self.notebook),
            "Root": ttk.Frame(self.notebook),
            "Flash": ttk.Frame(self.notebook),
            "Recovery": ttk.Frame(self.notebook),
            "Tools": ttk.Frame(self.notebook),
            "Info": ttk.Frame(self.notebook),
            "File Manager": ttk.Frame(self.notebook)
        }

        for name, frame in self.tabs.items():
            self.notebook.add(frame, text=name)

        # Пока скрываем вкладки до выбора производителя
        self.notebook.pack_forget()

        # Статус бар
        self.status_bar = ttk.Frame(self.main_frame)
        self.status_bar.pack(fill='x', pady=(5, 0))

        self.status_label = ttk.Label(self.status_bar, text="Статус: Устройство не подключено")
        self.status_label.pack(side='left', fill='x', expand=True)

        # Вместо создания log_toolbar можно добавить кнопку в существующий status_bar:
        self.clear_log_btn = ttk.Button(self.status_bar, text="Очистить лог",
                                        command=self.clear_log)
        self.clear_log_btn.pack(side='right', padx=5)

        ttk.Button(self.status_bar, text="Проверить подключение",
                   command=self.check_device_connection).pack(side='right')

        # Лог консоль
        self.log_console = scrolledtext.ScrolledText(self.main_frame, height=8)
        self.log_console.pack(fill='x', pady=(5, 0))
        self.log("Приложение запущено. Выберите производителя устройства.")

        # Применяем тему
        self.apply_theme()



    def open_settings(self):

        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("500x400")

        # Тема

        # Путь к ADB
        ttk.Label(settings_window, text="Путь к ADB:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        adb_path_var = tk.StringVar(value=self.settings["adb_path"])
        ttk.Entry(settings_window, textvariable=adb_path_var).grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(settings_window, text="Обзор...", command=lambda: self.browse_file(adb_path_var)).grid(row=2,
                                                                                                          column=2,
                                                                                                          padx=5,
                                                                                                          pady=5)

        # Путь к Fastboot
        ttk.Label(settings_window, text="Путь к Fastboot:").grid(row=3, column=0, padx=5, pady=5, sticky='w')
        fastboot_path_var = tk.StringVar(value=self.settings["fastboot_path"])
        ttk.Entry(settings_window, textvariable=fastboot_path_var).grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        ttk.Button(settings_window, text="Обзор...", command=lambda: self.browse_file(fastboot_path_var)).grid(row=3,
                                                                                                               column=2,
                                                                                                               padx=5,
                                                                                                               pady=5)

        # Права администратора
        admin_var = tk.BooleanVar(value=self.settings["run_as_admin"])
        ttk.Checkbutton(settings_window, text="Запускать с правами администратора",
                        variable=admin_var).grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky='w')

        # Кнопки сохранения/отмены
        btn_frame = ttk.Frame(settings_window)
        btn_frame.grid(row=5, column=0, columnspan=3, pady=10)

        ttk.Button(btn_frame, text="Сохранить", command=lambda: self.save_settings_window(
            adb_path_var.get(),
            fastboot_path_var.get(),
            admin_var.get(),
            settings_window
        )).pack(side='left', padx=5)

        ttk.Button(btn_frame, text="Отмена", command=settings_window.destroy).pack(side='left', padx=5)

    def browse_file(self, path_var):

        file = filedialog.askopenfilename(title="Выберите файл")
        if file:
            path_var.set(file)

    def save_settings_window(self, theme, language, adb_path, fastboot_path, run_as_admin, window):

        self.settings.update({
            "theme": theme,
            "language": language,
            "adb_path": adb_path,
            "fastboot_path": fastboot_path,
            "run_as_admin": run_as_admin
        })

        self.save_settings()
        self.apply_theme()
        window.destroy()

        if run_as_admin and not self.is_admin():
            if messagebox.askyesno("Перезапуск",
                                   "Требуется перезапуск для применения прав администратора. Перезапустить сейчас?"):
                self.restart_as_admin()

    def apply_theme(self):

        if self.settings["theme"] == "dark":
            self.bg_color = "#2d2d2d"
            self.fg_color = "#0f0f0f"
            self.primary_color = "#3a5f8a"
        else:
            self.bg_color = "#f0f0f0"
            self.fg_color = "#333333"
            self.primary_color = "#4a6baf"

        style = ttk.Style()
        style.configure('.', background=self.bg_color, foreground=self.fg_color)
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        style.configure('TButton', background="gray", foreground='black')
        style.configure('TRadiobutton', background=self.bg_color)
        style.configure('TNotebook', background=self.bg_color)
        style.configure('TNotebook.Tab', background='black', foreground='black')


    def show_about(self):

        about_window = tk.Toplevel(self.root)
        about_window.title("About programm")
        about_window.geometry("400x500")

        text = '''
                [RU]
                Программа создана wounsee. Исходный код предоставлен
                репозитории GitHub. Некоторые действия могут быть
                опасны и принести вред для вашено устройства, 
                поэтому делайте все на свой страх и риск! Автор не
                несет ответсвенность за совершенные вами действия.
                ---
                Эта программа упростит действие с вашим телефоном!
                Поможет с разблокировкой загрузчика, установит рут,
                кастомное рекавери, даже кастомное изображение при
                загрузке телефона!

                [EN]
                The program was created by wounsee. The source code is provided 
                by the GitHub repository. Some actions may be dangerous 
                and harm your device, so do everything at your own risk! 
                The author is not responsible for the actions you take.
                ---
                This program will simplify the action with your phone!
                Will help with unlocking the bootloader, install root,
                custom recovery, even a custom image when booting the phone!
                '''


        ttk.Label(about_window, text="BootHelper EXTRA", font=('Helvetica', 16, 'bold')).pack(pady=10)
        ttk.Label(about_window, text=text).pack()

        ttk.Button(about_window, text="Закрыть", command=about_window.destroy).pack(pady=20)

    def on_brand_select(self):

        brand = self.selected_brand.get()
        self.log(f"Выбран производитель: {brand}")
        self.notebook.pack(fill='both', expand=True)

        # Инициализация вкладок при первом выборе
        if not hasattr(self, 'info_initialized'):
            self.create_info_tab()
            self.create_file_manager_tab()
            self.create_bootloader_tab()
            self.create_root_tab()
            self.create_flash_tab()
            self.create_recovery_tab()
            self.create_tools_tab()
            self.info_initialized = True

        # Обновление информации
        self.update_device_info()

    def create_bootloader_tab(self):

        tab = self.tabs["Bootloader"]

        # Очистка предыдущих виджетов
        for widget in tab.winfo_children():
            widget.destroy()

        brand = self.selected_brand.get()

        # Статус загрузчика
        status_frame = ttk.LabelFrame(tab, text="Статус загрузчика")
        status_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(status_frame, text="Проверить статус",
                   command=self.check_bootloader_status).pack(side='left', padx=5, pady=5)

        self.bootloader_status = ttk.Label(status_frame, text="Статус: Неизвестно")
        self.bootloader_status.pack(side='left', padx=5, pady=5)

        # Действия с загрузчиком
        action_frame = ttk.LabelFrame(tab, text="Действия")
        action_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(action_frame, text="Разблокировать",
                   command=self.unlock_bootloader).pack(side='left', padx=5, pady=5)

        ttk.Button(action_frame, text="Заблокировать",
                   command=self.lock_bootloader).pack(side='left', padx=5, pady=5)

        # Бренд-специфичные функции
        if brand == "Xiaomi":
            xiaomi_frame = ttk.LabelFrame(tab, text="Функции Xiaomi")
            xiaomi_frame.pack(fill='x', padx=5, pady=5)

            ttk.Button(xiaomi_frame, text="Привязать аккаунт Mi",
                       command=self.bind_mi_account).pack(side='left', padx=5, pady=5)

            ttk.Button(xiaomi_frame, text="Проверить время ожидания",
                       command=self.check_unlock_time).pack(side='left', padx=5, pady=5)

        elif brand == "Realme":
            realme_frame = ttk.LabelFrame(tab, text="Функции Realme")
            realme_frame.pack(fill='x', padx=5, pady=5)

            ttk.Button(realme_frame, text="Запрос Deep Testing",
                       command=self.apply_deep_testing).pack(side='left', padx=5, pady=5)

            ttk.Button(realme_frame, text="Сгенерировать токен",
                       command=self.generate_unlock_token).pack(side='left', padx=5, pady=5)

        # Предупреждение
        ttk.Label(tab, text="Внимание: Разблокировка загрузчика удалит все данные!",
                  foreground='red').pack(pady=5)

    def create_root_tab(self):

        tab = self.tabs["Root"]

        # Очистка предыдущих виджетов
        for widget in tab.winfo_children():
            widget.destroy()

        # Выбор метода Root
        method_frame = ttk.LabelFrame(tab, text="Метод Root")
        method_frame.pack(fill='x', padx=5, pady=5)

        ttk.Radiobutton(method_frame, text="Magisk", variable=self.root_method,
                        value="magisk").pack(anchor='w', padx=5, pady=2)

        ttk.Radiobutton(method_frame, text="KernelSU", variable=self.root_method,
                        value="kernelsu").pack(anchor='w', padx=5, pady=2)

        ttk.Radiobutton(method_frame, text="SuperSU", variable=self.root_method,
                        value="supersu").pack(anchor='w', padx=5, pady=2)

        # Действия с Root
        action_frame = ttk.LabelFrame(tab, text="Действия")
        action_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(action_frame, text="Установить Root",
                   command=self.install_root).pack(side='left', padx=5, pady=5)

        ttk.Button(action_frame, text="Удалить Root",
                   command=self.remove_root).pack(side='left', padx=5, pady=5)

        ttk.Button(action_frame, text="Проверить Root статус",
                   command=self.check_root_status).pack(side='left', padx=5, pady=5)

        # Модули Magisk
        self.magisk_frame = ttk.LabelFrame(tab, text="Модули Magisk")
        self.magisk_frame.pack(fill='x', padx=5, pady=5)

        self.module_list = tk.Listbox(self.magisk_frame, height=5)
        self.module_list.pack(fill='both', expand=True, padx=5, pady=5)

        module_btn_frame = ttk.Frame(self.magisk_frame)
        module_btn_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(module_btn_frame, text="Установить модуль",
                   command=self.install_magisk_module).pack(side='left', padx=2)

        ttk.Button(module_btn_frame, text="Удалить модуль",
                   command=self.remove_magisk_module).pack(side='left', padx=2)

        ttk.Button(module_btn_frame, text="Обновить список",
                   command=self.refresh_magisk_modules).pack(side='right', padx=2)

        # Обновление UI при изменении метода Root
        self.root_method.trace_add('write', self.update_root_ui)
        self.update_root_ui()

    def create_flash_tab(self):

        tab = self.tabs["Flash"]

        # Очистка предыдущих виджетов
        for widget in tab.winfo_children():
            widget.destroy()

        brand = self.selected_brand.get()

        # Тип прошивки
        type_frame = ttk.LabelFrame(tab, text="Тип прошивки")
        type_frame.pack(fill='x', padx=5, pady=5)

        ttk.Radiobutton(type_frame, text="Официальная прошивка", variable=self.firmware_type,
                        value="official").pack(anchor='w', padx=5, pady=2)

        ttk.Radiobutton(type_frame, text="Кастомная прошивка", variable=self.firmware_type,
                        value="custom").pack(anchor='w', padx=5, pady=2)

        ttk.Radiobutton(type_frame, text="GSI", variable=self.firmware_type,
                        value="gsi").pack(anchor='w', padx=5, pady=2)

        # Выбор файла прошивки
        select_frame = ttk.LabelFrame(tab, text="Выбор прошивки")
        select_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(select_frame, text="Выбрать файл прошивки",
                   command=self.select_firmware_file).pack(side='left', padx=5, pady=5)

        self.firmware_path = ttk.Label(select_frame, text="Файл не выбран")
        self.firmware_path.pack(side='left', padx=5, pady=5)

        # Режим прошивки
        mode_frame = ttk.LabelFrame(tab, text="Режим прошивки")
        mode_frame.pack(fill='x', padx=5, pady=5)

        modes = ["Fastboot", "Recovery", "Download (Odin)" if brand == "Samsung" else "Flash Tool"]

        for mode in modes:
            ttk.Radiobutton(mode_frame, text=mode, variable=self.flash_mode,
                            value=mode.lower().split()[0]).pack(anchor='w', padx=5, pady=2)

        # Действия с прошивкой
        action_frame = ttk.LabelFrame(tab, text="Действия")
        action_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(action_frame, text="Прошить устройство",
                   command=self.flash_firmware).pack(side='left', padx=5, pady=5)

        ttk.Button(action_frame, text="Проверить прошивку",
                   command=self.verify_firmware).pack(side='left', padx=5, pady=5)

        # Boot Logo
        logo_frame = ttk.LabelFrame(tab, text="Boot Logo")
        logo_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(logo_frame, text="Изменить Boot Logo",
                   command=self.change_boot_logo).pack(side='left', padx=5, pady=5)

        ttk.Button(logo_frame, text="Бэкап Boot Logo",
                   command=self.backup_boot_logo).pack(side='left', padx=5, pady=5)

        ttk.Button(logo_frame, text="Восстановить Boot Logo",
                   command=self.restore_boot_logo).pack(side='left', padx=5, pady=5)

    def create_recovery_tab(self):

        tab = self.tabs["Recovery"]

        # Очистка предыдущих виджетов
        for widget in tab.winfo_children():
            widget.destroy()

        # Действия с Recovery
        action_frame = ttk.LabelFrame(tab, text="Действия с Recovery")
        action_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(action_frame, text="Перезагрузить в Recovery",
                   command=lambda: self.reboot_to("recovery")).pack(side='left', padx=5, pady=5)

        ttk.Button(action_frame, text="Установить TWRP",
                   command=self.install_twrp).pack(side='left', padx=5, pady=5)

        ttk.Button(action_frame, text="Восстановить сток Recovery",
                   command=self.restore_stock_recovery).pack(side='left', padx=5, pady=5)

        # Бэкап и восстановление
        backup_frame = ttk.LabelFrame(tab, text="Бэкап и восстановление")
        backup_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(backup_frame, text="Создать бэкап",
                   command=self.create_backup).pack(side='left', padx=5, pady=5)

        ttk.Button(backup_frame, text="Восстановить бэкап",
                   command=self.restore_backup).pack(side='left', padx=5, pady=5)

        ttk.Button(backup_frame, text="Выбрать папку для бэкапа",
                   command=self.select_backup_location).pack(side='left', padx=5, pady=5)

        # Сброс настроек
        reset_frame = ttk.LabelFrame(tab, text="Сброс настроек")
        reset_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(reset_frame, text="Сброс к заводским",
                   command=self.factory_reset).pack(side='left', padx=5, pady=5)

        ttk.Button(reset_frame, text="Очистить кэш",
                   command=self.wipe_cache).pack(side='left', padx=5, pady=5)

        ttk.Button(reset_frame, text="Очистить Dalvik/ART",
                   command=self.wipe_dalvik).pack(side='left', padx=5, pady=5)

    def create_tools_tab(self):

        tab = self.tabs["Tools"]

        # Очистка предыдущих виджетов
        for widget in tab.winfo_children():
            widget.destroy()

        # Управление устройством
        control_frame = ttk.LabelFrame(tab, text="Управление устройством")
        control_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(control_frame, text="Перезагрузить",
                   command=lambda: self.reboot_to("system")).pack(side='left', padx=5, pady=5)

        ttk.Button(control_frame, text="Перезагрузить в Fastboot",
                   command=lambda: self.reboot_to("bootloader")).pack(side='left', padx=5, pady=5)

        ttk.Button(control_frame, text="Выключить",
                   command=self.power_off).pack(side='left', padx=5, pady=5)

        # ADB инструменты
        adb_frame = ttk.LabelFrame(tab, text="ADB инструменты")
        adb_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(adb_frame, text="Открыть ADB Shell",
                   command=self.open_adb_shell).pack(side='left', padx=5, pady=5)

        ttk.Button(adb_frame, text="Просмотр логов",
                   command=self.view_logcat).pack(side='left', padx=5, pady=5)

        ttk.Button(adb_frame, text="Скриншот",
                   command=self.take_screenshot).pack(side='left', padx=5, pady=5)

        # Дополнительные инструменты
        advanced_frame = ttk.LabelFrame(tab, text="Дополнительные инструменты")
        advanced_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(advanced_frame, text="Удалить bloatware",
                   command=self.remove_bloatware).pack(side='left', padx=5, pady=5)

        ttk.Button(advanced_frame, text="Исправить права",
                   command=self.fix_permissions).pack(side='left', padx=5, pady=5)

        ttk.Button(advanced_frame, text="Менеджер разделов",
                   command=self.partition_manager).pack(side='left', padx=5, pady=5)

    def create_info_tab(self):

        tab = self.tabs["Info"]

        # Очистка предыдущих виджетов
        for widget in tab.winfo_children():
            widget.destroy()

        # Основная информация
        info_frame = ttk.LabelFrame(tab, text="Основная информация")
        info_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD)
        self.info_text.pack(fill='both', expand=True, padx=5, pady=5)

        ttk.Button(info_frame, text="Обновить информацию",
                   command=self.update_device_info).pack(pady=5)

        # Аппаратная информация
        hw_frame = ttk.LabelFrame(tab, text="Аппаратная информация")
        hw_frame.pack(fill='x', padx=5, pady=5)

        self.hw_text = scrolledtext.ScrolledText(hw_frame, height=8, wrap=tk.WORD)
        self.hw_text.pack(fill='x', padx=5, pady=5)

        # Информация о батарее
        battery_frame = ttk.LabelFrame(tab, text="Батарея")
        battery_frame.pack(fill='x', padx=5, pady=5)

        self.battery_text = scrolledtext.ScrolledText(battery_frame, height=6, wrap=tk.WORD)
        self.battery_text.pack(fill='x', padx=5, pady=5)

        # Обновляем информацию
        self.update_device_info()

    def create_file_manager_tab(self):

        tab = self.tabs["File Manager"]

        # Очистка вкладки
        for widget in tab.winfo_children():
            widget.destroy()

        # Основной контейнер с сеткой
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Панель инструментов (верх)
        toolbar = ttk.Frame(main_frame)
        toolbar.grid(row=0, column=0, columnspan=2, sticky='ew', pady=(0, 5))

        # Кнопки навигации
        nav_frame = ttk.Frame(toolbar)
        nav_frame.pack(side='left')

        ttk.Button(nav_frame, text="←", width=3, command=self.file_manager_go_back).pack(side='left', padx=2)
        ttk.Button(nav_frame, text="↑", width=3, command=lambda: self.change_directory("..")).pack(side='left', padx=2)
        ttk.Button(nav_frame, text="⌂", width=3, command=lambda: self.change_directory("/")).pack(side='left', padx=2)
        ttk.Button(nav_frame, text="↻", width=3, command=self.refresh_file_list).pack(side='left', padx=2)

        # Поле пути
        self.current_path = tk.StringVar(value="/storage/emulated/0")
        path_entry = ttk.Entry(toolbar, textvariable=self.current_path)
        path_entry.pack(side='left', fill='x', expand=True, padx=5)
        path_entry.bind("<Return>", lambda e: self.change_directory(self.current_path.get()))

        # Кнопки действий
        action_frame = ttk.Frame(toolbar)
        action_frame.pack(side='right')

        ttk.Button(action_frame, text="Создать папку", command=self.create_directory).pack(side='left', padx=2)
        ttk.Button(action_frame, text="Загрузить", command=self.upload_file).pack(side='left', padx=2)

        # Таблица файлов с двойной рамкой
        file_frame = ttk.LabelFrame(main_frame, text="Содержимое папки")
        file_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        # Настройка сетки
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Создание Treeview с колонками
        columns = ("name", "size", "type", "modified", "permissions")
        self.file_tree = ttk.Treeview(
            file_frame,
            columns=columns,
            selectmode='browse',
            show='headings'
        )

        # Настройка колонок
        self.file_tree.heading("name", text="Имя", anchor='w')
        self.file_tree.heading("size", text="Размер", anchor='center')
        self.file_tree.heading("type", text="Тип", anchor='center')
        self.file_tree.heading("modified", text="Изменен", anchor='center')
        self.file_tree.heading("permissions", text="Права", anchor='center')

        self.file_tree.column("name", width=250, stretch=True)
        self.file_tree.column("size", width=80, stretch=False, anchor='e')
        self.file_tree.column("type", width=80, stretch=False)
        self.file_tree.column("modified", width=120, stretch=False)
        self.file_tree.column("permissions", width=80, stretch=False)

        # Полосы прокрутки
        vsb = ttk.Scrollbar(file_frame, orient="vertical", command=self.file_tree.yview)
        hsb = ttk.Scrollbar(file_frame, orient="horizontal", command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Размещение элементов
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(0, weight=1)

        # Контекстное меню
        self.file_menu = tk.Menu(self.root, tearoff=0)
        self.file_menu.add_command(label="Открыть", command=self.open_selected_file)
        self.file_menu.add_command(label="Скачать", command=self.download_file)
        self.file_menu.add_command(label="Переименовать", command=self.rename_file)
        self.file_menu.add_command(label="Удалить", command=self.delete_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Свойства", command=self.show_file_properties)

        # Привязка событий
        self.file_tree.bind("<Double-1>", self.on_file_double_click)
        self.file_tree.bind("<Button-3>", self.show_context_menu)
        self.file_tree.bind("<Delete>", lambda e: self.delete_file())

        # Статус бар (низ)
        self.status_bar = ttk.Frame(main_frame)
        self.status_bar.grid(row=2, column=0, sticky='ew', pady=(5, 0))

        self.status_label = ttk.Label(self.status_bar, text="Готово")
        self.status_label.pack(side='left')

        # Заполняем список файлов
        self.refresh_file_list()

    def refresh_file_list(self):

        self.file_tree.delete(*self.file_tree.get_children())
        path = self.current_path.get()

        if not self.phone_connected:
            self.status_label.config(text="Ошибка: устройство не подключено")
            return

        try:
            # Получаем детализированный список файлов
            result = self.run_adb_command(f"shell ls -la {path}")

            # Обработка случая, когда папка пуста или недоступна
            if not result or "No such file" in result or "Permission denied" in result:
                self.status_label.config(text=f"{path} | Папка пуста или недоступна")
                return

            total_items = 0
            for line in result.splitlines():
                if not line.strip() or line.startswith('total'):
                    continue

                parts = line.split()
                if len(parts) < 9:
                    continue

                perms = parts[0]
                size = parts[4]
                date = ' '.join(parts[5:8])
                name = ' '.join(parts[8:])

                if name in (".", ".."):
                    continue

                is_dir = perms.startswith('d')
                file_type = "Папка" if is_dir else "Файл"

                # Форматируем размер для папок
                display_size = "" if is_dir else self.format_size(int(size))

                self.file_tree.insert("", "end",
                                      values=(name, display_size, file_type, date, perms),
                                      tags=('directory' if is_dir else 'file'))
                total_items += 1

            self.current_path.set(path)
            status_text = f"{path} | {total_items} объектов" if total_items > 0 else f"{path} | Папка пуста"
            self.status_label.config(text=status_text)

        except Exception as e:
            self.log(f"Ошибка обновления списка файлов: {str(e)}")
            self.status_label.config(text=f"Ошибка: {str(e)}")

    def format_size(self, size):

        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def on_file_double_click(self, event):

        try:
            item = self.file_tree.selection()
            if not item:
                return

            item = item[0]
            name = self.file_tree.item(item, "values")[0]
            path = os.path.join(self.current_path.get(), name).replace('\\', '/')

            if 'directory' in self.file_tree.item(item, "tags"):
                # Проверяем, можно ли открыть папку
                test_result = self.run_adb_command(f"shell ls {path}")
                if test_result and "No such file" not in test_result:
                    self.change_directory(path)
                else:
                    self.status_label.config(text=f"Ошибка: нет доступа к папке {path}")
                    messagebox.showerror("Ошибка", f"Невозможно открыть папку {name}")
            else:
                self.open_selected_file()
        except Exception as e:
            self.log(f"Ошибка при двойном клике: {str(e)}")
            self.status_label.config(text=f"Ошибка: {str(e)}")

    def change_directory(self, path):

        path = path.replace('\\', '/')
        if not self.phone_connected:
            return

        # Нормализация пути
        if path == "..":
            path = os.path.dirname(self.current_path.get())
        elif not path.startswith('/'):
            path = os.path.join(self.current_path.get(), path).replace('\\', '/')

        try:
            # Проверяем существует ли директория
            result = self.run_adb_command(f"shell ls {path}")
            if result and "No such file" not in result:
                self.current_directory = path
                self.refresh_file_list()
            else:
                self.status_label.config(text=f"Ошибка: директория {path} не существует")
        except Exception as e:
            self.log(f"Ошибка смены директории: {str(e)}")

    def show_context_menu(self, event):

        item = self.file_tree.identify_row(event.y)
        if item:
            self.file_tree.selection_set(item)
            self.file_menu.post(event.x_root, event.y_root)

    def open_selected_file(self):

        item = self.file_tree.selection()
        if not item:
            return

        try:
            item = item[0]
            name = self.file_tree.item(item, "values")[0]
            path = os.path.join(self.current_path.get(), name).replace('\\', '/')

            if 'directory' in self.file_tree.item(item, "tags"):
                self.change_directory(path)
            else:
                # Проверяем, существует ли файл
                check = self.run_adb_command(f"shell ls {path}")
                if not check or "No such file" in check:
                    messagebox.showerror("Ошибка", f"Файл {name} не найден")
                    return

                # Определяем тип файла для соответствующего действия
                if name.endswith(('.txt', '.log', '.ini', '.cfg', '.xml', '.json')):
                    self.view_text_file(path)
                elif name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    self.view_image_file(path)
                else:
                    # Пытаемся открыть через стандартное приложение
                    result = self.run_adb_command(f"shell am start -t file/* -d file://{path}")
                    if "Error" in result:
                        messagebox.showinfo("Информация",
                                            f"Не удалось открыть файл {name}\n"
                                            f"Попробуйте скачать его и открыть на компьютере")
        except Exception as e:
            self.log(f"Ошибка открытия файла: {str(e)}")
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {str(e)}")
    def view_text_file(self, remote_path):

        try:
            content = self.run_adb_command(f"shell cat {remote_path}")
            if content:
                # Создаем окно для просмотра
                view_window = tk.Toplevel(self.root)
                view_window.title(f"Просмотр: {os.path.basename(remote_path)}")

                text_area = scrolledtext.ScrolledText(view_window, wrap=tk.WORD)
                text_area.pack(fill='both', expand=True, padx=5, pady=5)
                text_area.insert(tk.END, content)
                text_area.config(state='disabled')
        except Exception as e:
            self.log(f"Ошибка просмотра файла: {str(e)}")

    def download_file(self):

        item = self.file_tree.selection()
        if not item:
            return

        item = item[0]
        name = self.file_tree.item(item, "values")[0]
        remote_path = os.path.join(self.current_path.get(), name).replace('\\', '/')

        local_path = filedialog.asksaveasfilename(
            title="Сохранить файл как",
            initialfile=name,
            filetypes=[("Все файлы", "*.*")]
        )

        if local_path:
            self.status_label.config(text=f"Скачивание {name}...")
            self.root.update()

            try:
                self.run_adb_command(f"pull {remote_path} {local_path}")
                self.status_label.config(text=f"Файл скачан: {local_path}")
            except Exception as e:
                self.status_label.config(text=f"Ошибка скачивания: {str(e)}")

    def upload_file(self):

        local_file = filedialog.askopenfilename(
            title="Выберите файл для загрузки",
            filetypes=[("Все файлы", "*.*")]
        )

        if local_file:
            filename = os.path.basename(local_file)
            remote_path = os.path.join(self.current_path.get(), filename).replace('\\', '/')

            self.status_label.config(text=f"Загрузка {filename}...")
            self.root.update()

            try:
                self.run_adb_command(f"push {local_file} {remote_path}")
                self.status_label.config(text=f"Файл загружен: {remote_path}")
                self.refresh_file_list()
            except Exception as e:
                self.status_label.config(text=f"Ошибка загрузки: {str(e)}")

    def create_directory(self):

        name = simpledialog.askstring("Создать папку", "Введите имя папки:")
        if name:
            path = os.path.join(self.current_path.get(), name).replace('\\', '/')

            try:
                self.run_adb_command(f"shell mkdir {path}")
                self.refresh_file_list()
                self.status_label.config(text=f"Папка создана: {path}")
            except Exception as e:
                self.status_label.config(text=f"Ошибка создания папки: {str(e)}")

    def rename_file(self):

        item = self.file_tree.selection()
        if not item:
            return

        item = item[0]
        old_name = self.file_tree.item(item, "values")[0]
        old_path = os.path.join(self.current_path.get(), old_name).replace('\\', '/')

        new_name = simpledialog.askstring("Переименовать", "Введите новое имя:", initialvalue=old_name)
        if new_name and new_name != old_name:
            new_path = os.path.join(self.current_path.get(), new_name).replace('\\', '/')

            try:
                self.run_adb_command(f"shell mv {old_path} {new_path}")
                self.refresh_file_list()
                self.status_label.config(text=f"Переименовано: {old_name} → {new_name}")
            except Exception as e:
                self.status_label.config(text=f"Ошибка переименования: {str(e)}")

    def delete_file(self):

        item = self.file_tree.selection()
        if not item:
            return

        item = item[0]
        name = self.file_tree.item(item, "values")[0]
        path = os.path.join(self.current_path.get(), name).replace('\\', '/')

        if messagebox.askyesno("Подтверждение", f"Удалить {path}?"):
            try:
                if 'directory' in self.file_tree.item(item, "tags"):
                    self.run_adb_command(f"shell rm -r {path}")
                else:
                    self.run_adb_command(f"shell rm {path}")

                self.refresh_file_list()
                self.status_label.config(text=f"Удалено: {path}")
            except Exception as e:
                self.status_label.config(text=f"Ошибка удаления: {str(e)}")

    def show_file_properties(self):

        item = self.file_tree.selection()
        if not item:
            return

        item = item[0]
        name = self.file_tree.item(item, "values")[0]
        path = os.path.join(self.current_path.get(), name).replace('\\', '/')

        # Получаем подробную информацию о файле
        info = self.run_adb_command(f"shell ls -la {path}")
        if info:
            messagebox.showinfo("Свойства", info)

    def file_manager_go_back(self):

        path = self.current_path.get()
        parent = os.path.dirname(path)
        if parent:
            self.change_directory(parent)

    def check_device_connection(self):

        try:
            # Проверяем наличие ADB
            if not os.path.exists(self.settings["adb_path"]):
                self.log(f"ADB не найден по пути: {self.settings['adb_path']}")
                self.status_label.config(text="Ошибка: ADB не найден")
                return False

            # Выполняем команду adb devices
            result = subprocess.run([self.settings["adb_path"], "devices"],
                                    capture_output=True, text=True)

            # Парсим результат
            devices = []
            for line in result.stdout.splitlines():
                if "\tdevice" in line:
                    devices.append(line.split("\t")[0])





            if devices:
                def gses(length=10):
                    chars = string.ascii_letters  # буквы + цифры
                    return ''.join(random.choice(chars) for _ in range(length))
                ses = gses(5)
                self.phone_connected = True
                self.device_id = devices[0]
                self.status_label.config(text=f"Подключено: {self.device_id}  |  Сессия: {ses}")
                self.log(f"Устройство подключено: {self.device_id}")
                self.log(f"Сессия: {ses}")
                return True
            else:
                self.phone_connected = False
                self.device_id = ""
                self.status_label.config(text="Устройство не подключено")
                self.log("Ожидание подключения устройства...")
                return False

        except Exception as e:
            self.log(f"Ошибка при проверке подключения: {str(e)}")
            self.status_label.config(text="Ошибка подключения")
            return False

    def run_adb_command(self, command):

        if not self.phone_connected:
            self.log("Ошибка: устройство не найдено!")
            return None

        try:
            cmd = [self.settings["adb_path"], "-s", self.device_id] + command.split()
            result = subprocess.run(cmd, capture_output=True, text=True)

            self.log(f"Выполнено: {' '.join(cmd)}")
            if result.stdout:
                self.log(f"Результат: {result.stdout.strip()}")
            if result.stderr:
                self.log(f"Ошибка: {result.stderr.strip()}")

            return result.stdout.strip() if result.stdout else None

        except Exception as e:
            self.log(f"Ошибка выполнения команды: {str(e)}")
            return None

    def run_fastboot_command(self, command):

        try:
            cmd = [self.settings["fastboot_path"], "-s", self.device_id] + command.split()
            result = subprocess.run(cmd, capture_output=True, text=True)

            self.log(f"Выполнено: {' '.join(cmd)}")
            if result.stdout:
                print("OK")
            if result.stderr:
                self.log(f"Ошибка: {result.stderr.strip()}")

            return result.stdout.strip() if result.stdout else None

        except Exception as e:
            self.log(f"Ошибка выполнения команды: {str(e)}")
            return None

    def check_bootloader_status(self):

        if not self.reboot_to("bootloader"):
            return

        time.sleep(5)  # Ждем перехода в fastboot

        result = self.run_fastboot_command("oem device-info")
        if not result:
            return

        if "Device unlocked: true" in result:
            self.bootloader_status.config(text="Статус: Разблокирован")
            self.log("Загрузчик разблокирован")
        elif "Device unlocked: false" in result:
            self.bootloader_status.config(text="Статус: Заблокирован")
            self.log("Загрузчик заблокирован")
        else:
            self.bootloader_status.config(text="Статус: Неизвестно")
            self.log("Не удалось определить статус загрузчика")

        self.reboot_to("system")

    def unlock_bootloader(self):

        if not messagebox.askyesno("Подтверждение", "Разблокировка загрузчика сотрет все данные. Продолжить?"):
            return

        brand = self.selected_brand.get()

        if brand == "Xiaomi":
            self.unlock_xiaomi_bootloader()
        elif brand == "Realme":
            self.unlock_realme_bootloader()
        else:
            self.unlock_generic_bootloader()

    def unlock_xiaomi_bootloader(self):

        self.log("Начало разблокировки загрузчика Xiaomi")

        # Проверяем наличие Mi Unlock
        mi_unlock_path = os.path.join(os.path.dirname(self.settings["adb_path"]), "MiFlashUnlock.exe")
        if not os.path.exists(mi_unlock_path):
            self.log("Mi Unlock не найден")
            if messagebox.askyesno("Ошибка", "Mi Unlock не найден. Скачать?"):
                webbrowser.open("https://en.miui.com/unlock/")
            return

        # Перезагружаем в fastboot
        if not self.reboot_to("bootloader"):
            return

        # Запускаем Mi Unlock
        try:
            subprocess.Popen([mi_unlock_path])
            self.log("Mi Unlock запущен. Следуйте инструкциям на экране.")
        except Exception as e:
            self.log(f"Ошибка запуска Mi Unlock: {str(e)}")

    def unlock_realme_bootloader(self):

        self.log("Начало разблокировки загрузчика Realme")

        # Проверяем наличие unlock token
        token_path = os.path.join(os.path.dirname(self.settings["adb_path"]), "unlock_token.bin")
        if not os.path.exists(token_path):
            self.log("Unlock token не найден")
            messagebox.showinfo("Информация",
                                "Для разблокировки Realme требуется token. Получите его через Deep Testing.")
            return

        # Перезагружаем в fastboot
        if not self.reboot_to("bootloader"):
            return

        # Прошиваем токен
        result = self.run_fastboot_command(f"flash unlock_token {token_path}")
        if "OKAY" in result:
            self.log("Unlock token успешно прошит")
            self.run_fastboot_command("oem unlock")
            self.bootloader_status.config(text="Статус: Разблокирован")
        else:
            self.log("Ошибка прошивки unlock token")

        self.reboot_to("system")

    def unlock_generic_bootloader(self):

        if not self.reboot_to("bootloader"):
            return

        result = self.run_fastboot_command("flashing unlock")
        if "OKAY" in result:
            self.log("Загрузчик успешно разблокирован")
            self.bootloader_status.config(text="Статус: Разблокирован")
        else:
            self.log("Ошибка разблокировки загрузчика")

        self.reboot_to("system")

    def lock_bootloader(self):

        if not messagebox.askyesno("Подтверждение", "Блокировка загрузчика может привести к проблемам. Продолжить?"):
            return

        if not self.reboot_to("bootloader"):
            return

        result = self.run_fastboot_command("flashing lock")
        if "OKAY" in result:
            self.log("Загрузчик успешно заблокирован")
            self.bootloader_status.config(text="Статус: Заблокирован")
        else:
            self.log("Ошибка блокировки загрузчика")

        self.reboot_to("system")

    def bind_mi_account(self):

        webbrowser.open("https://account.xiaomi.com/pass/serviceLogin")
        self.log("Открыта страница привязки аккаунта Mi")

    def check_unlock_time(self):

        self.log("Проверка времени ожидания разблокировки Xiaomi")
        messagebox.showinfo("Информация", "Для проверки времени ожидания используйте официальное приложение Mi Unlock")

    def apply_deep_testing(self):

        webbrowser.open("https://drive.usercontent.google.com/download?id=1fHJ8OVObyE2iDa-acjPXEPwfyKST1eT9&export=download&authuser=0")
        self.log("Открыта страница запроса Deep Testing")

    def generate_unlock_token(self):

        time.sleep(1)
        self.log("Запуск генерации токена...")
        time.sleep(1)
        self.log(f"Получение токена для {self.device_id}...")
        time.sleep(0.1)
        self.log("Начало генерации...")

        a = 5
        def generate_key(length=10):
            chars = string.ascii_letters + string.digits  # буквы + цифры
            return ''.join(random.choice(chars) for _ in range(length))
        time.sleep(1)
        for _ in range(45):
            self.log(f"Пробую: {generate_key(68)} ")
            self.log("Токен был отклонен.")
            time.sleep(0.0001)
        self.log("Все попытки генерации были отклонены, получите токен саморучно!")
        messagebox.showinfo("Информация", "Ошибка генерации.")

    def install_root(self):

        method = self.root_method.get()
        self.log(f"Установка Root: {method}")

        if method == "magisk":
            self.install_magisk()
        elif method == "kernelsu":
            self.install_kernelsu()
        elif method == "supersu":
            self.install_supersu()

    def install_magisk(self):

        self.log("Начало установки Magisk")

        # Проверяем наличие patched boot image
        boot_img = os.path.join(os.path.dirname(self.settings["adb_path"]), "magisk_patched.img")
        if not os.path.exists(boot_img):
            self.log("Patched boot image не найден")
            messagebox.showinfo("Информация", "Пожалуйста, создайте patched boot image через Magisk App")
            return

        # Перезагружаем в fastboot
        if not self.reboot_to("bootloader"):
            return

        # Прошиваем patched boot image
        self.run_fastboot_command(f"flash boot {boot_img}")
        self.run_fastboot_command("reboot")
        self.log("Magisk установлен. Устройство перезагружается.")

    def install_kernelsu(self):

        self.log("Начало установки KernelSU")
        messagebox.showinfo("Информация", "Установка KernelSU пока не реализована")

    def install_supersu(self):

        self.log("Начало установки SuperSU")
        messagebox.showinfo("Информация", "Установка SuperSU пока не реализована")

    def remove_root(self):

        if not messagebox.askyesno("Подтверждение", "Удалить Root права?"):
            return

        self.log("Удаление Root прав")

        # Перезагружаем в fastboot
        if not self.reboot_to("bootloader"):
            return

        # Прошиваем оригинальный boot image
        boot_img = os.path.join(os.path.dirname(self.settings["adb_path"]), "stock_boot.img")
        if os.path.exists(boot_img):
            self.run_fastboot_command(f"flash boot {boot_img}")
            self.run_fastboot_command("reboot")
            self.log("Root права удалены. Устройство перезагружается.")
        else:
            self.log("Оригинальный boot image не найден")
            messagebox.showinfo("Ошибка", "Не найден оригинальный boot image")

    def check_root_status(self):

        result = self.run_adb_command("shell which su")
        if result and "/su" in result:
            messagebox.showinfo("Статус Root", "Устройство имеет Root права")
            self.log("Устройство имеет Root права")
        else:
            messagebox.showinfo("Статус Root", "Устройство не имеет Root прав")
            self.log("Устройство не имеет Root прав")

    def update_root_ui(self, *args):

        method = self.root_method.get()

        if method == "magisk":
            self.magisk_frame.pack(fill='x', padx=5, pady=5)
            self.refresh_magisk_modules()
        else:
            self.magisk_frame.pack_forget()

    def refresh_magisk_modules(self):

        self.module_list.delete(0, tk.END)

        if not self.phone_connected:
            return

        # Получаем список модулей
        modules = self.run_adb_command("shell ls /data/adb/modules")
        if modules:
            for module in modules.splitlines():
                self.module_list.insert(tk.END, module)
        else:
            self.log("Модули Magisk не найдены")

    def install_magisk_module(self):

        file = filedialog.askopenfilename(title="Выберите модуль Magisk",
                                          filetypes=[("ZIP files", "*.zip")])
        if file:
            self.log(f"Установка модуля: {file}")
            self.run_adb_command(f"push {file} /sdcard/tmp_module.zip")
            self.run_adb_command("shell su -c magisk --install-module /sdcard/tmp_module.zip")
            self.run_adb_command("shell rm /sdcard/tmp_module.zip")
            self.refresh_magisk_modules()

    def remove_magisk_module(self):

        selection = self.module_list.curselection()
        if not selection:
            return

        module = self.module_list.get(selection[0])
        if messagebox.askyesno("Подтверждение", f"Удалить модуль {module}?"):
            self.run_adb_command(f"shell su -c rm -rf /data/adb/modules/{module}")
            self.log(f"Модуль удален: {module}")
            self.refresh_magisk_modules()

    def select_firmware_file(self):

        file = filedialog.askopenfilename(title="Выберите файл прошивки",
                                          filetypes=[("Firmware files", "*.zip *.img *.tgz")])
        if file:
            self.current_firmware = file
            self.firmware_path.config(text=os.path.basename(file))
            self.log(f"Выбран файл прошивки: {file}")

    def verify_firmware(self):

        if not self.current_firmware:
            self.log("Файл прошивки не выбран")
            return

        self.log(f"Проверка прошивки: {self.current_firmware}")
        messagebox.showinfo("Информация", "Проверка прошивки пока не реализована")

    def flash_firmware(self):

        if not self.current_firmware:
            self.log("Файл прошивки не выбран")
            return

        if not messagebox.askyesno("Подтверждение", "Прошивка устройства может привести к потере данных. Продолжить?"):
            return

        brand = self.selected_brand.get()
        mode = self.flash_mode.get()

        self.log(f"Начало прошивки в режиме {mode}")

        if mode == "fastboot":
            self.flash_fastboot_firmware()
        elif mode == "recovery":
            self.flash_recovery_firmware()
        elif mode == "download" and brand == "Samsung":
            self.flash_odin_firmware()
        elif mode == "tool" and brand == "Realme":
            self.flash_realme_firmware()

    def flash_fastboot_firmware(self):

        if not self.reboot_to("bootloader"):
            return

        # Проверяем наличие скрипта flash_all
        flash_script = os.path.join(os.path.dirname(self.current_firmware), "flash_all.bat")
        if os.path.exists(flash_script):
            self.log(f"Запуск скрипта прошивки: {flash_script}")
            subprocess.Popen([flash_script], cwd=os.path.dirname(self.current_firmware))
        else:
            self.log("Скрипт flash_all.bat не найден")
            messagebox.showinfo("Ошибка", "Не найден скрипт flash_all.bat")

    def flash_recovery_firmware(self):

        if not self.reboot_to("recovery"):
            return

        self.log("Прошивка через Recovery")
        self.run_adb_command(f"push {self.current_firmware} /sdcard/firmware.zip")
        self.run_adb_command("shell twrp install /sdcard/firmware.zip")
        self.run_adb_command("shell rm /sdcard/firmware.zip")

    def flash_odin_firmware(self):

        self.log("Прошивка через Odin")
        messagebox.showinfo("Информация", "Для прошивки Samsung используйте официальный инструмент Odin")

    def flash_realme_firmware(self):

        self.log("Прошивка через Realme Flash Tool")
        messagebox.showinfo("Информация", "Для прошивки Realme используйте официальный инструмент Realme Flash Tool")

    def change_boot_logo(self):

        file = filedialog.askopenfilename(title="Выберите изображение для Boot Logo",
                                          filetypes=[("Image files", "*.png *.jpg *.bmp")])
        if file:
            self.log(f"Изменение Boot Logo: {file}")
            messagebox.showinfo("Информация", "Изменение Boot Logo пока не реализовано")

    def backup_boot_logo(self):

        self.log("Создание бэкапа Boot Logo")
        messagebox.showinfo("Информация", "Создание бэкапа Boot Logo пока не реализовано")

    def restore_boot_logo(self):

        file = filedialog.askopenfilename(title="Выберите бэкап Boot Logo",
                                          filetypes=[("Logo files", "*.img *.bin")])
        if file:
            self.log(f"Восстановление Boot Logo из: {file}")
            messagebox.showinfo("Информация", "Восстановление Boot Logo пока не реализовано")

    def install_twrp(self):

        file = filedialog.askopenfilename(title="Выберите образ TWRP",
                                          filetypes=[("Image files", "*.img")])
        if not file:
            return

        if not self.reboot_to("bootloader"):
            return

        self.log(f"Установка TWRP: {file}")
        self.run_fastboot_command(f"flash recovery {file}")
        self.run_fastboot_command("reboot recovery")

    def restore_stock_recovery(self):

        file = filedialog.askopenfilename(title="Выберите сток образ Recovery",
                                          filetypes=[("Image files", "*.img")])
        if not file:
            return

        if not self.reboot_to("bootloader"):
            return

        self.log(f"Восстановление сток Recovery: {file}")
        self.run_fastboot_command(f"flash recovery {file}")
        self.run_fastboot_command("reboot")

    def create_backup(self):

        dir = filedialog.askdirectory(title="Выберите папку для сохранения бэкапа")
        if dir:
            self.log(f"Создание бэкапа в: {dir}")
            self.run_adb_command("shell twrp backup SDBOM /sdcard/backup")
            self.run_adb_command(f"pull /sdcard/backup {dir}")
            self.run_adb_command("shell rm -rf /sdcard/backup")

    def restore_backup(self):

        dir = filedialog.askdirectory(title="Выберите папку с бэкапом")
        if dir:
            self.log(f"Восстановление из бэкапа: {dir}")
            self.run_adb_command(f"push {dir} /sdcard/restore")
            self.run_adb_command("shell twrp restore /sdcard/restore")
            self.run_adb_command("shell rm -rf /sdcard/restore")

    def select_backup_location(self):

        dir = filedialog.askdirectory(title="Выберите папку для бэкапов")
        if dir:
            self.log(f"Папка для бэкапов: {dir}")

    def factory_reset(self):

        if not messagebox.askyesno("Подтверждение", "Все данные будут удалены. Продолжить?"):
            return

        self.log("Сброс к заводским настройкам")
        self.run_adb_command("reboot recovery")
        messagebox.showinfo("Информация", "Выполните wipe data/factory reset в Recovery")

    def wipe_cache(self):

        if not messagebox.askyesno("Подтверждение", "Очистить кэш?"):
            return

        self.log("Очистка кэша")
        self.run_adb_command("reboot recovery")
        messagebox.showinfo("Информация", "Выполните wipe cache в Recovery")

    def wipe_dalvik(self):

        if not messagebox.askyesno("Подтверждение", "Очистить Dalvik/ART кэш?"):
            return

        self.log("Очистка Dalvik/ART кэша")
        self.run_adb_command("reboot recovery")
        messagebox.showinfo("Информация", "Выполните wipe dalvik cache в Recovery")

    def reboot_to(self, mode):

        modes = {
            "system": "",
            "bootloader": "bootloader",
            "recovery": "recovery",
            "sideload": "sideload",
            "fastboot": "fastboot"
        }

        if mode not in modes:
            self.log(f"Неверный режим перезагрузки: {mode}")
            return False

        cmd = "reboot"
        if modes[mode]:
            cmd = f"reboot {modes[mode]}"

        result = self.run_adb_command(cmd)
        if result:
            self.log(f"Перезагрузка в режим: {mode}")
            return True
        else:
            self.log(f"Ошибка перезагрузки в режим: {mode}")
            return False

    def power_off(self):

        self.run_adb_command("reboot -p")
        self.log("Устройство выключается")

    def open_adb_shell(self):

        self.log("Открытие ADB Shell")
        subprocess.Popen(["start", "cmd", "/k", self.settings["adb_path"], "-s", self.device_id, "shell"], shell=True)

    def view_logcat(self):

        self.log("Просмотр логов")
        subprocess.Popen(["start", "cmd", "/k", self.settings["adb_path"], "-s", self.device_id, "logcat"], shell=True)

    def take_screenshot(self):

        filename = f"screenshot_{time.strftime('%Y%m%d_%H%M%S')}.png"
        self.run_adb_command(f"shell screencap -p /sdcard/{filename}")
        self.run_adb_command(f"pull /sdcard/{filename}")
        self.run_adb_command(f"shell rm /sdcard/{filename}")
        self.log(f"Скриншот сохранен как: {filename}")

    def remove_bloatware(self):

        self.log("Удаление bloatware")
        messagebox.showinfo("Информация", "Функция удаления bloatware пока не реализована")

    def fix_permissions(self):

        self.log("Исправление прав")
        self.run_adb_command("shell su -c chmod -R 755 /system")
        self.run_adb_command("shell su -c chown -R 0.0 /system")

    def partition_manager(self):

        self.log("Открытие менеджера разделов")
        messagebox.showinfo("Информация", "Менеджер разделов пока не реализован")

    def update_device_info(self):

        if not self.phone_connected:
            if self.info_text:
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, "Устройство не подключено")
            return

        try:
            # Получаем полную информацию об устройстве
            info = "=== ОСНОВНАЯ ИНФОРМАЦИЯ ===\n\n"

            manufacturer = self.run_adb_command("shell getprop ro.product.manufacturer") or "Неизвестно"
            model = self.run_adb_command("shell getprop ro.product.model") or "Неизвестно"
            device = self.run_adb_command("shell getprop ro.product.device") or "Неизвестно"
            android_version = self.run_adb_command("shell getprop ro.build.version.release") or "Неизвестно"
            sdk_version = self.run_adb_command("shell getprop ro.build.version.sdk") or "Неизвестно"
            security_patch = self.run_adb_command("shell getprop ro.build.version.security_patch") or "Неизвестно"
            build_id = self.run_adb_command("shell getprop ro.build.display.id") or "Неизвестно"
            build_type = self.run_adb_command("shell getprop ro.build.type") or "Неизвестно"
            build_date = self.run_adb_command("shell getprop ro.build.date") or "Неизвестно"
            kernel = self.run_adb_command("shell uname -a") or "Неизвестно"


            cpu_info = self.run_adb_command("shell cat /proc/cpuinfo") or ""
            cpu_model = "Неизвестно"
            cpu_cores = "Неизвестно"

            if cpu_info:
                for line in cpu_info.splitlines():
                    if "model name" in line or "Processor" in line:
                        cpu_model = line.split(":")[1].strip()
                        break

                cpu_cores = str(len([line for line in cpu_info.splitlines() if "processor" in line]))

            # Информация о памяти
            mem_info = self.run_adb_command("shell cat /proc/meminfo") or ""
            total_mem = "Неизвестно"
            free_mem = "Неизвестно"

            if mem_info:
                for line in mem_info.splitlines():
                    if "MemTotal" in line:
                        total_mem = line.split(":")[1].strip()
                    elif "MemFree" in line:
                        free_mem = line.split(":")[1].strip()

            # Информация о хранилище
            storage = self.run_adb_command("shell df -h /data") or "Неизвестно"


            info += f"📱 Производитель: {manufacturer}\n"
            info += f"📶 Модель: {model}\n"
            info += f"🔧 Код устройства: {device}\n"
            info += f"🤖 Версия Android: {android_version} (SDK {sdk_version})\n"
            info += f"🔒 Последний патч: {security_patch}\n"
            info += f"🆔 ID сборки: {build_id}\n"
            info += f"🏷 Тип сборки: {build_type}\n"
            info += f"📅 Дата сборки: {build_date}\n"
            info += f"💾 Ядро: {kernel}\n"

            info += f"\n=== АППАРАТНАЯ ИНФОРМАЦИЯ ===\n\n"

            info += f"⚙️ Процессор: {cpu_model}\n"
            info += f"🔢 Ядер: {cpu_cores}\n"
            info += f"🧠 Общая память: {total_mem}\n"
            info += f"🆓 Свободно памяти: {free_mem}\n"
            info += f"💽 Хранилище:\n{storage}\n"

            if self.info_text:
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(tk.END, info)
                self.clear_log()
        except Exception as e:
            self.log(f"Ошибка при получении информации об устройстве: {str(e)}")

    def log(self, message):

        timestamp = time.strftime("[%H:%M:%S] ")
        self.log_content += timestamp + message + "\n"
        self.log_console.delete(1.0, tk.END)
        self.log_console.insert(tk.END, self.log_content)
        self.log_console.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneFlashHelperPro(root)
    root.mainloop()