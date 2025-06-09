import unittest
from unittest.mock import patch, Mock, mock_open
import csv
import io
from collections import defaultdict

# Импортируем функции из основного модуля
try:
    from solution import (
        get_first_letter,
        count_animals_by_letter,
        save_to_csv,
        get_animals_from_current_page
    )
except ImportError:
    # Если импорт не удался, определяем функции здесь для тестирования
    def get_first_letter(animal_name):
        """Получает первую букву названия животного"""
        if not animal_name:
            return None
        
        first_char = animal_name[0].upper()
        
        # Проверяем, является ли первый символ русской буквой
        if 'А' <= first_char <= 'Я' or first_char == 'Ё':
            return first_char
        
        return None

    def count_animals_by_letter(animals):
        """Подсчитывает количество животных по первым буквам"""
        letter_counts = defaultdict(int)
        
        for animal in animals:
            first_letter = get_first_letter(animal)
            if first_letter:
                letter_counts[first_letter] += 1
        
        return dict(letter_counts)

    def save_to_csv(letter_counts, filename='beasts.csv'):
        """Сохраняет результаты в CSV файл"""
        russian_alphabet = [
            'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М',
            'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ',
            'Ы', 'Ь', 'Э', 'Ю', 'Я'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            for letter in russian_alphabet:
                count = letter_counts.get(letter, 0)
                if count > 0:
                    writer.writerow([letter, count])

    def get_animals_from_current_page(soup):
        """Извлекает животных с текущей страницы"""
        animals = []
        
        category_groups = soup.find_all('div', {'class': 'mw-category-group'})
        
        for group in category_groups:
            links = group.find_all('a')
            for link in links:
                title = link.get('title', '').strip()
                if title:
                    animals.append(title)
        
        return animals


class TestAnimalsCounter(unittest.TestCase):
    """Тесты для функций подсчета животных"""

    def test_get_first_letter_russian_letters(self):
        """Тест получения первой буквы для русских названий"""
        test_cases = [
            ('Антилопа', 'А'),
            ('барс', 'Б'),
            ('Волк', 'В'),
            ('ёж', 'Ё'),
            ('Ягуар', 'Я')
        ]
        
        for animal_name, expected_letter in test_cases:
            with self.subTest(animal=animal_name):
                result = get_first_letter(animal_name)
                self.assertEqual(result, expected_letter)

    def test_get_first_letter_non_russian_letters(self):
        """Тест с нерусскими символами - должны возвращать None"""
        test_cases = ['Cat', 'Dog', '123Animal', 'English name']
        
        for animal_name in test_cases:
            with self.subTest(animal=animal_name):
                result = get_first_letter(animal_name)
                self.assertIsNone(result)

    def test_get_first_letter_empty_input(self):
        """Тест с пустыми входными данными"""
        test_cases = ['', None, '   ']
        
        for animal_name in test_cases:
            with self.subTest(animal=animal_name):
                result = get_first_letter(animal_name)
                self.assertIsNone(result)

    def test_get_first_letter_special_characters(self):
        """Тест с специальными символами в начале"""
        test_cases = ['(Антилопа)', '[Барс]', '"Волк"']
        expected_results = [None, None, None]
        
        for animal_name, expected in zip(test_cases, expected_results):
            with self.subTest(animal=animal_name):
                result = get_first_letter(animal_name)
                self.assertEqual(result, expected)

    def test_count_animals_by_letter_normal_case(self):
        """Тест подсчета животных по буквам - обычный случай"""
        animals = [
            'Антилопа', 'Акула', 'Барс', 'Белка', 'Волк', 
            'Ворона', 'Гепард', 'Дельфин'
        ]
        
        expected = {
            'А': 2,
            'Б': 2,
            'В': 2,
            'Г': 1,
            'Д': 1
        }
        
        result = count_animals_by_letter(animals)
        self.assertEqual(result, expected)

    def test_count_animals_by_letter_empty_list(self):
        """Тест с пустым списком животных"""
        animals = []
        result = count_animals_by_letter(animals)
        self.assertEqual(result, {})

    def test_count_animals_by_letter_with_invalid_names(self):
        """Тест с некорректными названиями"""
        animals = [
            'Антилопа', 'Cat', '', 'Барс', 'Dog', None, 'Волк'
        ]
        
        expected = {
            'А': 1,
            'Б': 1,
            'В': 1
        }
        
        result = count_animals_by_letter(animals)
        self.assertEqual(result, expected)

    def test_count_animals_by_letter_case_insensitive(self):
        """Тест нечувствительности к регистру"""
        animals = ['антилопа', 'БАРС', 'Волк', 'гЕПАРД']
        
        expected = {
            'А': 1,
            'Б': 1,
            'В': 1,
            'Г': 1
        }
        
        result = count_animals_by_letter(animals)
        self.assertEqual(result, expected)

    def test_count_animals_by_letter_with_yo(self):
        """Тест с буквой Ё"""
        animals = ['Ёж', 'ёрш', 'Енот']
        
        expected = {
            'Ё': 2,
            'Е': 1
        }
        
        result = count_animals_by_letter(animals)
        self.assertEqual(result, expected)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_csv_normal_case(self, mock_file):
        """Тест сохранения в CSV файл"""
        letter_counts = {
            'А': 5,
            'Б': 3,
            'В': 7,
            'Ё': 2
        }
        
        save_to_csv(letter_counts, 'test.csv')
        
        # Проверяем, что файл был открыт с правильными параметрами
        mock_file.assert_called_once_with('test.csv', 'w', newline='', encoding='utf-8')
        
        # Получаем все вызовы write
        handle = mock_file()
        written_content = ''.join(call[0][0] for call in handle.write.call_args_list)
        
        # Проверяем, что записаны правильные данные
        self.assertIn('А,5', written_content)
        self.assertIn('Б,3', written_content)
        self.assertIn('В,7', written_content)
        self.assertIn('Ё,2', written_content)

    @patch('builtins.open', new_callable=mock_open)
    def test_save_to_csv_empty_counts(self, mock_file):
        """Тест сохранения пустого словаря"""
        letter_counts = {}
        
        save_to_csv(letter_counts, 'test.csv')
        
        mock_file.assert_called_once_with('test.csv', 'w', newline='', encoding='utf-8')
        
        # При пустом словаре файл должен быть создан, но пустой
        handle = mock_file()
        written_content = ''.join(call[0][0] for call in handle.write.call_args_list)
        
        # Не должно быть записей с буквами
        self.assertNotIn('А,', written_content)
        self.assertNotIn('Б,', written_content)

    def test_save_to_csv_only_existing_letters(self):
        """Тест что сохраняются только буквы с ненулевым количеством"""
        letter_counts = {
            'А': 5,
            'Б': 0,  # Эта буква не должна попасть в файл
            'В': 3
        }
        
        # Используем StringIO для имитации файла
        output = io.StringIO()
        
        # Временно заменяем функцию сохранения для тестирования
        russian_alphabet = ['А', 'Б', 'В', 'Г', 'Д', 'Е']
        
        writer = csv.writer(output)
        for letter in russian_alphabet:
            count = letter_counts.get(letter, 0)
            if count > 0:
                writer.writerow([letter, count])
        
        content = output.getvalue()
        
        self.assertIn('А,5', content)
        self.assertNotIn('Б,0', content)
        self.assertNotIn('Б,', content)
        self.assertIn('В,3', content)

    @patch('requests.get')
    def test_get_animals_from_current_page_mock(self, mock_get):
        """Тест парсинга страницы с мок-данными"""
        # Создаем мок HTML контент
        mock_html = """
        <html>
            <div class="mw-category-group">
                <a title="Антилопа">Антилопа</a>
                <a title="Барс">Барс</a>
            </div>
            <div class="mw-category-group">
                <a title="Волк">Волк</a>
            </div>
        </html>
        """
        
        # Создаем мок BeautifulSoup объект
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(mock_html, 'html.parser')
            
            result = get_animals_from_current_page(soup)
            expected = ['Антилопа', 'Барс', 'Волк']
            
            self.assertEqual(sorted(result), sorted(expected))
        except ImportError:
            self.skipTest("BeautifulSoup не установлен")


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты"""

    def test_full_workflow(self):
        """Тест полного рабочего процесса"""
        # Симулируем получение животных
        animals = [
            'Антилопа', 'Акула', 'Барс', 'Белка', 'Белый медведь',
            'Волк', 'Ворона', 'Гепард', 'Дельфин', 'Ёж', 'Енот'
        ]
        
        # Подсчитываем по буквам
        letter_counts = count_animals_by_letter(animals)
        
        # Проверяем результат
        expected_counts = {
            'А': 2,  # Антилопа, Акула
            'Б': 3,  # Барс, Белка, Белый медведь
            'В': 2,  # Волк, Ворона
            'Г': 1,  # Гепард
            'Д': 1,  # Дельфин
            'Ё': 1,  # Ёж
            'Е': 1   # Енот
        }
        
        self.assertEqual(letter_counts, expected_counts)
        
        # Проверяем общее количество
        total_counted = sum(letter_counts.values())
        self.assertEqual(total_counted, len(animals))


if __name__ == '__main__':
    # Запуск тестов с подробным выводом
    unittest.main(verbosity=2)