import requests
from bs4 import BeautifulSoup
import csv
import re
from collections import defaultdict
import time

def get_animals_from_page(url):
    """Получает список животных с одной страницы категории"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        animals = []
        
        # Ищем все ссылки в категории
        category_links = soup.find('div', {'class': 'mw-category-group'})
        if category_links:
            links = category_links.find_all('a')
            for link in links:
                title = link.get('title', '').strip()
                if title:
                    animals.append(title)
        
        # Также ищем в других группах категорий
        category_groups = soup.find_all('div', {'class': 'mw-category-group'})
        for group in category_groups:
            links = group.find_all('a')
            for link in links:
                title = link.get('title', '').strip()
                if title and title not in animals:
                    animals.append(title)
        
        return animals
    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")
        return []

def get_all_animals():
    """Получает полный список всех животных из категории"""
    base_url = "https://ru.wikipedia.org/wiki/Категория:Животные_по_алфавиту"
    all_animals = []
    
    page_url = base_url
    visited_urls = set()
    page_count = 0
    
    while page_url and page_url not in visited_urls:
        page_count += 1
        print(f"Обрабатываем страницу {page_count}: {page_url}")
        visited_urls.add(page_url)
        
        try:
            response = requests.get(page_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Получаем животных с текущей страницы
            animals = get_animals_from_current_page(soup)
            all_animals.extend(animals)
            print(f"Найдено {len(animals)} записей на этой странице")
            
            # Ищем ссылку на следующую страницу
            next_page = None
            
            # Метод 1: Ищем в навигации по страницам
            nav_div = soup.find('div', {'id': 'mw-pages'})
            if nav_div:
                nav_links = nav_div.find_all('a')
                for link in nav_links:
                    href = link.get('href', '')
                    if 'pagefrom=' in href:
                        next_page = "https://ru.wikipedia.org" + href
                        break
            
            # Метод 2: Ищем в категории
            if not next_page:
                category_nav = soup.find('div', {'class': 'mw-category-generated'})
                if category_nav:
                    nav_links = category_nav.find_all('a')
                    for link in nav_links:
                        href = link.get('href', '')
                        if 'pagefrom=' in href:
                            next_page = "https://ru.wikipedia.org" + href
                            break
            
            # Метод 3: Ищем любые ссылки с pagefrom
            if not next_page:
                pagefrom_links = soup.find_all('a', href=re.compile(r'pagefrom='))
                for link in pagefrom_links:
                    href = link.get('href', '')
                    full_url = "https://ru.wikipedia.org" + href
                    if full_url not in visited_urls:
                        next_page = full_url
                        break
            
            page_url = next_page
            time.sleep(1)
            
        except Exception as e:
            print(f"Ошибка при обработке страницы {page_url}: {e}")
            break
    
    print(f"Всего обработано страниц: {page_count}")
    return all_animals

def get_animals_from_current_page(soup):
    """Извлекает животных с текущей страницы"""
    animals = []
    
    # Ищем все группы категорий
    category_groups = soup.find_all('div', {'class': 'mw-category-group'})
    
    for group in category_groups:
        # Находим все ссылки в группе
        links = group.find_all('a')
        for link in links:
            title = link.get('title', '').strip()
            if title:
                animals.append(title)
    
    return animals

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
    # Создаем упорядоченный список русских букв
    russian_alphabet = [
        'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й', 'К', 'Л', 'М',
        'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ',
        'Ы', 'Ь', 'Э', 'Ю', 'Я'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        for letter in russian_alphabet:
            count = letter_counts.get(letter, 0)
            if count > 0:  # Записываем только буквы с животными
                writer.writerow([letter, count])
    
    print(f"Результаты сохранены в файл {filename}")

def main():
    """Основная функция"""
    print("Начинаем сбор данных о животных с Википедии...")
    
    # Получаем список всех животных
    animals = get_all_animals()
    print(f"Всего найдено записей: {len(animals)}")
    
    if not animals:
        print("Не удалось получить данные о животных")
        return
    
    # Подсчитываем по буквам
    letter_counts = count_animals_by_letter(animals)
    
    # Выводим статистику
    print("\nСтатистика по буквам:")
    total_count = 0
    for letter in sorted(letter_counts.keys()):
        count = letter_counts[letter]
        print(f"{letter}: {count}")
        total_count += count
    
    print(f"\nВсего учтено: {total_count} записей")
    
    # Сохраняем в CSV
    save_to_csv(letter_counts)
    
    print("Готово!")

if __name__ == "__main__":
    main()