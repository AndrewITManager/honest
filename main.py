from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
import re
from datetime import datetime

class ЧестныйЗнакAPI:
    @staticmethod
    def parse_qr_code(qr_data):
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
    def compare_qr_codes(qr1_data, qr2_data):
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
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)
        
        # Заголовок
        title = Label(text="Проверка QR кода", font_size=24, size_hint_y=0.1)
        self.add_widget(title)
        
        # Поле ввода
        self.qr_input = TextInput(
            hint_text="Введите QR код",
            size_hint_y=0.15,
            multiline=False,
            font_size=18
        )
        self.add_widget(self.qr_input)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        
        check_btn = Button(text="Проверить", on_press=self.check_qr)
        btn_layout.add_widget(check_btn)
        
        clear_btn = Button(text="Очистить", on_press=self.clear_fields)
        btn_layout.add_widget(clear_btn)
        
        self.add_widget(btn_layout)
        
        # Результат
        self.result_label = Label(text="", size_hint_y=0.1, font_size=16)
        self.add_widget(self.result_label)
        
        # Детали
        scroll = ScrollView(size_hint_y=0.6)
        self.details_label = Label(
            text="",
            size_hint_y=None,
            text_size=(None, None),
            markup=True,
            halign='left',
            valign='top'
        )
        self.details_label.bind(texture_size=self.details_label.setter('size'))
        scroll.add_widget(self.details_label)
        self.add_widget(scroll)
    
    def check_qr(self, instance):
        qr_data = self.qr_input.text.strip()
        if not qr_data:
            self.result_label.text = "[color=ff0000]Введите QR код[/color]"
            return
        
        parsed = ЧестныйЗнакAPI.parse_qr_code(qr_data)
        
        if parsed["parsed_successfully"]:
            self.result_label.text = "[color=00ff00]✓ QR код распознан[/color]"
        else:
            self.result_label.text = "[color=ff0000]✗ Не удалось распознать[/color]"
        
        details = f"[b]Результат анализа:[/b]\n\n"
        details += f"GTIN: [b]{parsed['gtin'] or 'Не найден'}[/b]\n"
        details += f"Серийный номер: [b]{parsed['serial'] or 'Не найден'}[/b]\n"
        details += f"Криптохвост: [b]{parsed['crypto'] or 'Не найден'}[/b]\n"
        details += f"\n[i]Время: {datetime.now().strftime('%H:%M:%S')}[/i]"
        
        self.details_label.text = details
    
    def clear_fields(self, instance):
        self.qr_input.text = ""
        self.result_label.text = ""
        self.details_label.text = ""

class ComparisonTab(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)
        
        # Заголовок
        title = Label(text="Сравнение QR кодов", font_size=24, size_hint_y=0.1)
        self.add_widget(title)
        
        # Поля ввода
        input_layout = BoxLayout(orientation='vertical', spacing=5, size_hint_y=0.3)
        
        self.qr1_input = TextInput(
            hint_text="Первый QR код",
            size_hint_y=0.45,
            multiline=False,
            font_size=18
        )
        input_layout.add_widget(self.qr1_input)
        
        self.qr2_input = TextInput(
            hint_text="Второй QR код",
            size_hint_y=0.45,
            multiline=False,
            font_size=18
        )
        input_layout.add_widget(self.qr2_input)
        
        self.add_widget(input_layout)
        
        # Кнопки
        btn_layout = BoxLayout(size_hint_y=0.15, spacing=10)
        
        compare_btn = Button(text="Сравнить", on_press=self.compare_qr)
        btn_layout.add_widget(compare_btn)
        
        swap_btn = Button(text="Поменять", on_press=self.swap_qr)
        btn_layout.add_widget(swap_btn)
        
        clear_btn = Button(text="Очистить", on_press=self.clear_fields)
        btn_layout.add_widget(clear_btn)
        
        self.add_widget(btn_layout)
        
        # Результат
        self.result_label = Label(
            text="",
            size_hint_y=0.1,
            font_size=20,
            bold=True
        )
        self.add_widget(self.result_label)
        
        # Детали
        scroll = ScrollView(size_hint_y=0.35)
        self.details_label = Label(
            text="",
            size_hint_y=None,
            text_size=(None, None),
            markup=True,
            halign='left',
            valign='top'
        )
        self.details_label.bind(texture_size=self.details_label.setter('size'))
        scroll.add_widget(self.details_label)
        self.add_widget(scroll)

class ЧестныйЗнакApp(App):
    def build(self):
        self.title = "Честный Знак"
        
        # Создаем панель с вкладками
        tab_panel = TabbedPanel(do_default_tab=False)
        
        # Первая вкладка
        tab1 = TabbedPanelItem(text='Проверка QR')
        tab1.add_widget(SingleCheckTab())
        tab_panel.add_widget(tab1)
        
        # Вторая вкладка
        tab2 = TabbedPanelItem(text='Сравнение QR')
        tab2.add_widget(ComparisonTab())
        tab_panel.add_widget(tab2)
        
        return tab_panel

if __name__ == '__main__':
    ЧестныйЗнакApp().run()
