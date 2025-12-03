# main.py
import kivy
kivy.require('2.1.0')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
import re
from datetime import datetime

class ЧестныйЗнакAPI:
    @staticmethod
    def parse_qr_code(qr_data: str):
        """Парсит данные QR кода"""
        result = {
            "raw": qr_data,
            "gtin": "",
            "serial": "",
            "crypto": "",
            "parsed_successfully": False
        }
        
        patterns = [
            r"01(\d{14})21(.+?)92(.+)",
            r"gtin=(\d{14});serial=(.+?);crypto=(.+)",
            r"(\d{14})(.+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, qr_data)
            if match:
                if len(match.groups()) >= 2:
                    result["gtin"] = match.group(1)
                    result["serial"] = match.group(2)
                    if len(match.groups()) >= 3:
                        result["crypto"] = match.group(3)
                    result["parsed_successfully"] = True
                break
        
        if not result["parsed_successfully"]:
            gtin_match = re.search(r'(\d{14})', qr_data)
            if gtin_match:
                result["gtin"] = gtin_match.group(1)
                result["parsed_successfully"] = True
                serial_part = qr_data.replace(gtin_match.group(1), '').strip()
                if serial_part:
                    result["serial"] = serial_part
        
        return result
    
    @staticmethod
    def compare_qr_codes(qr1_data: str, qr2_data: str):
        """Сравнивает два QR кода"""
        qr1 = ЧестныйЗнакAPI.parse_qr_code(qr1_data)
        qr2 = ЧестныйЗнакAPI.parse_qr_code(qr2_data)
        
        match = qr1["gtin"] == qr2["gtin"] and qr1["serial"] == qr2["serial"]
        
        return {
            "match": match,
            "qr1": qr1,
            "qr2": qr2
        }

class SingleCheckTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=20, **kwargs)
        
        self.add_widget(Label(text="Проверка QR кода", font_size=24, size_hint_y=0.1))
        
        self.qr_input = TextInput(
            hint_text="Введите QR код",
            size_hint_y=0.15,
            multiline=False
        )
        self.add_widget(self.qr_input)
        
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        
        check_btn = Button(text="Проверить", on_press=self.check_qr)
        btn_layout.add_widget(check_btn)
        
        clear_btn = Button(text="Очистить", on_press=self.clear_fields)
        btn_layout.add_widget(clear_btn)
        
        self.add_widget(btn_layout)
        
        self.result_label = Label(text="", size_hint_y=0.1)
        self.add_widget(self.result_label)
        
        self.details_label = Label(text="", size_hint_y=0.5)
        self.add_widget(self.details_label)
    
    def check_qr(self, instance):
        qr_data = self.qr_input.text.strip()
        if not qr_data:
            self.result_label.text = "Введите QR код"
            return
        
        parsed = ЧестныйЗнакAPI.parse_qr_code(qr_data)
        
        details = f"GTIN: {parsed['gtin'] or 'Не найден'}\n"
        details += f"Серийный: {parsed['serial'] or 'Не найден'}\n"
        details += f"Криптохвост: {parsed['crypto'] or 'Не найден'}\n"
        details += f"Распознан: {'Да' if parsed['parsed_successfully'] else 'Нет'}"
        
        self.details_label.text = details
        self.result_label.text = "Результат проверки"
    
    def clear_fields(self, instance):
        self.qr_input.text = ""
        self.result_label.text = ""
        self.details_label.text = ""

class ComparisonTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=20, **kwargs)
        
        self.add_widget(Label(text="Сравнение QR кодов", font_size=24, size_hint_y=0.1))
        
        # Первый QR
        self.qr1_input = TextInput(
            hint_text="Первый QR код",
            size_hint_y=0.1,
            multiline=False
        )
        self.add_widget(self.qr1_input)
        
        # Второй QR
        self.qr2_input = TextInput(
            hint_text="Второй QR код",
            size_hint_y=0.1,
            multiline=False
        )
        self.add_widget(self.qr2_input)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        
        compare_btn = Button(text="Сравнить", on_press=self.compare_qr)
        btn_layout.add_widget(compare_btn)
        
        swap_btn = Button(text="Поменять", on_press=self.swap_qr)
        btn_layout.add_widget(swap_btn)
        
        clear_btn = Button(text="Очистить", on_press=self.clear_fields)
        btn_layout.add_widget(clear_btn)
        
        self.add_widget(btn_layout)
        
        self.result_label = Label(
            text="",
            size_hint_y=0.1,
            font_size=20,
            bold=True
        )
        self.add_widget(self.result_label)
        
        self.details_label = Label(text="", size_hint_y=0.45)
        self.add_widget(self.details_label)
    
    def compare_qr(self, instance):
        qr1 = self.qr1_input.text.strip()
        qr2 = self.qr2_input.text.strip()
        
        if not qr1 or not qr2:
            self.result_label.text = "Введите оба QR кода"
            return
        
        result = ЧестныйЗнакAPI.compare_qr_codes(qr1, qr2)
        
        if result["match"]:
            self.result_label.text = "✅ СООТВЕТСТВУЕТ"
            self.result_label.color = (0, 1, 0, 1)  # Зеленый
        else:
            self.result_label.text = "❌ НЕ СООТВЕТСТВУЕТ"
            self.result_label.color = (1, 0, 0, 1)  # Красный
        
        details = "Первый QR:\n"
        details += f"GTIN: {result['qr1']['gtin']}\n"
        details += f"Серийный: {result['qr1']['serial']}\n\n"
        
        details += "Второй QR:\n"
        details += f"GTIN: {result['qr2']['gtin']}\n"
        details += f"Серийный: {result['qr2']['serial']}"
        
        self.details_label.text = details
    
    def swap_qr(self, instance):
        qr1 = self.qr1_input.text
        qr2 = self.qr2_input.text
        self.qr1_input.text = qr2
        self.qr2_input.text = qr1
    
    def clear_fields(self, instance):
        self.qr1_input.text = ""
        self.qr2_input.text = ""
        self.result_label.text = ""
        self.details_label.text = ""

class ЧестныйЗнакApp(App):
    def build(self):
        self.title = "Честный Знак Проверка"
        
        # Создаем панель с вкладками
        tab_panel = TabbedPanel()
        tab_panel.do_default_tab = False
        
        # Первая вкладка
        tab1 = TabbedPanelItem(text='Проверка QR')
        tab1.content = SingleCheckTab()
        tab_panel.add_widget(tab1)
        
        # Вторая вкладка
        tab2 = TabbedPanelItem(text='Сравнение QR')
        tab2.content = ComparisonTab()
        tab_panel.add_widget(tab2)
        
        return tab_panel

if __name__ == '__main__':
    ЧестныйЗнакApp().run()
