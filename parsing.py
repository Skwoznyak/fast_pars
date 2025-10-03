from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options as ChromeOptions
import time
import pickle
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


def create_firefox_driver():
    """Создает настроенный Chrome драйвер с опциями для стабильной работы (переименовано для совместимости)"""
    chrome_options = ChromeOptions()

    # Основные опции для headless режима
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-software-rasterizer")

    # User agent
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Для работы в Docker
    chrome_options.add_argument("--disable-setuid-sandbox")
    chrome_options.add_argument("--single-process")

    # Путь к Chromium в Debian
    chrome_options.binary_location = "/usr/bin/chromium"

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ Chrome драйвер успешно создан")
        return driver
    except Exception as e:
        print(f"❌ Ошибка при создании Chrome драйвера: {e}")
        return None


def phone_register_send(phone_num):
    driver = create_firefox_driver()
    if not driver:
        print("Не удалось создать Firefox драйвер")
        return

    driver.get("https://ads.telegram.org")

    pole_phone = driver.find_element(By.CSS_SELECTOR, ".btn.pr-btn.login-link")
    pole_phone.click()

    phone = phone_num
    vvod = driver.find_element(
        By.CSS_SELECTOR, '.form-control.pr-form-control.input-lg')
    vvod.send_keys(phone)

    send_sms = driver.find_element(
        By.XPATH, "//button[@type='submit' and contains(@class, 'btn') and contains(text(), 'Next')]")
    send_sms.click()

    time.sleep(30)

    save_cookies(driver)
    try:
        driver.quit()
    except Exception as e:
        print(f"Ошибка при закрытии браузера: {e}")


def save_cookies(driver, filename="cookies_user.pkl"):
    cookies = driver.get_cookies()

    with open(filename, 'wb') as f:
        pickle.dump(cookies, f)

    print(f"Куки сохранены: {len(cookies)} штук")


def load_cookies(driver, filename="cookies_user.pkl"):
    try:
        with open(filename, 'rb') as f:
            cookies = pickle.load(f)

        for cookie in cookies:
            driver.add_cookie(cookie)

        print(f"Куки загружены: {len(cookies)} штук")
        return True
    except FileNotFoundError:
        print("Файл с куки не найден")
        return False


def is_authorized(driver):
    try:
        driver.find_element(By.CSS_SELECTOR, ".pr-account-button-content")
        return True
    except:
        return False


def login_with_cookies():
    driver = create_firefox_driver()
    if not driver:
        print("Не удалось создать Firefox драйвер")
        return None

    driver.get("https://ads.telegram.org")

    if load_cookies(driver):
        driver.refresh()

        if is_authorized(driver):
            print("Успешный вход через куки!")
            return driver
        else:
            print("Куки устарели, нужна повторная авторизация")
            driver.quit()
            return None
    else:
        print("Файл с куками не найден")
        driver.quit()
        return None


def find_channel_by_name(driver, channel_name):
    try:
        channel_elem = driver.find_element(
            By.XPATH, f"//div[@class='pr-account-button-title' and contains(text(), '{channel_name}')]")
        print(f'канал {channel_name} нашелся!')
        return channel_elem
    except:
        print(f"Канал '{channel_name}' не найден")
        return None


def _safe_text(elem):
    """Возвращает текст элемента, если он есть, иначе пустую строку."""
    try:
        if elem is None:
            return ""
        return elem.text.strip()
    except Exception:
        return ""


def _load_all_rows_by_scrolling(driver, wait):
    """
    🚀 ОПТИМИЗИРОВАННАЯ прокрутка с адаптивным ожиданием
    Устраняет time.sleep() и использует WebDriverWait
    """
    try:
        # Убедимся, что таблица есть
        wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, ".js-ads-table-body")))

        last_height = driver.execute_script(
            "return document.body.scrollHeight")

        scroll_iterations = 0

        while True:
            # Прокручиваем вниз
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")

            # 🚀 ДОБАВЛЕНО: Пауза 1 секунда после каждой прокрутки для загрузки
            print(f"[ПАРСИНГ] ⏳ Пауза 1 сек для загрузки данных...")
            time.sleep(1)

            # 🚀 УВЕЛИЧЕНО ВРЕМЯ: Адаптивное ожидание (теперь до 8 секунд)
            try:
                # Ждем максимум 8 секунд, пока высота страницы не увеличится
                WebDriverWait(driver, 8).until(lambda d: d.execute_script(
                    "return document.body.scrollHeight") > last_height)
                new_height = driver.execute_script(
                    "return document.body.scrollHeight")
                last_height = new_height
                scroll_iterations += 1
                print(
                    f"[ПАРСИНГ] ✅ Итерация скролла {scroll_iterations}, высота: {new_height}")
            except TimeoutException:
                # Если высота не изменилась за 8 секунд, выходим
                print(
                    "[ПАРСИНГ] ✅ Высота страницы не изменилась, прекращаю прокрутку.")
                break

        print(
            f"[ПАРСИНГ] Прокрутка завершена после {scroll_iterations} итераций")

        # 🚀 ДОБАВЛЕНО: Дополнительная задержка для полной загрузки всех элементов
        print("[ПАРСИНГ] ⏳ Ожидаю 5 секунд для полной загрузки всех элементов...")
        time.sleep(5)

    except Exception as e:
        print(f"[ПАРСИНГ] ⚠️ Ошибка при прокрутке: {e}")


def parse_table_data_optimized(driver):
    """
    🚀🚀 КРИТИЧЕСКИ ОПТИМИЗИРОВАННЫЙ парсинг с локальным HTML парсингом
    """
    try:
        # Ждем загрузки таблицы (увеличено до 20 секунд)
        wait = WebDriverWait(driver, 20)

        # Пробуем разные селекторы для таблицы
        table_selectors = [
            ".js-ads-table-body",
            ".ads-table",
            ".table-body",
            "[class*='table']",
            "[class*='ads']"
        ]

        table_found = False
        for selector in table_selectors:
            try:
                print(f"[ПАРСИНГ] Пробую селектор: {selector}")
                wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, selector)))
                print(f"[ПАРСИНГ] ✅ Таблица найдена с селектором: {selector}")
                table_found = True
                break
            except Exception as e:
                print(f"[ПАРСИНГ] ❌ Селектор {selector} не найден: {e}")
                continue

        if not table_found:
            print(f"[ПАРСИНГ] ❌ Таблица объявлений не найдена ни с одним селектором")
            return []

        # Перед парсингом загружаем все строки через оптимизированную прокрутку
        try:
            _load_all_rows_by_scrolling(driver, wait)
        except Exception as e:
            print(
                f"[ПАРСИНГ] ⚠️ Не удалось догрузить все строки прокруткой: {e}")

        # 🚀🚀 КРИТИЧЕСКАЯ ОПТИМИЗАЦИЯ: Локальный парсинг HTML
        print("[ПАРСИНГ] 🚀 Переходим к локальному парсингу HTML...")

        # Получаем весь HTML таблицы одной командой
        table_element = driver.find_element(
            By.CSS_SELECTOR, ".js-ads-table-body")
        table_html = table_element.get_attribute('outerHTML')

        # Парсим HTML локально с BeautifulSoup (МНОГОКРАТНО быстрее)
        soup = BeautifulSoup(table_html, 'lxml')
        rows = soup.find_all('tr')

        print(f"[ПАРСИНГ] 📊 Найдено строк в HTML: {len(rows)}")

        # Отладка: выводим структуру первой строки
        if len(rows) > 0:
            first_row = rows[0]
            first_cells = first_row.find_all('td')
            print(
                f"[ПАРСИНГ] 🔍 Первая строка содержит {len(first_cells)} ячеек")
            if len(first_cells) > 0:
                print(
                    f"[ПАРСИНГ] 🔍 Пример первой ячейки: {first_cells[0].get_text(strip=True)[:50]}...")

        parsed_data = []
        skipped_rows = 0

        for i, row in enumerate(rows):
            try:
                cells = row.find_all('td')
                if not cells:
                    skipped_rows += 1
                    continue

                # Пропускаем строки с менее чем 5 ячейками (неполные данные)
                if len(cells) < 5:
                    print(
                        f"[ПАРСИНГ] ⚠️ Строка {i} пропущена: только {len(cells)} ячеек")
                    skipped_rows += 1
                    continue

                # 1) Первая ячейка: заголовок и URL
                title_cell = cells[0]
                title_link = title_cell.find('a', class_='pr-link')

                # 🚀 ИСПРАВЛЕНИЕ: Ищем ссылку с target="_blank" и извлекаем href
                url_link = title_cell.find('a', {'target': '_blank'})

                ad_title = title_link.get_text(
                    strip=True) if title_link else ""

                # 🚀 ИСПРАВЛЕНИЕ: Извлекаем полный URL из атрибута href
                if url_link and url_link.get('href'):
                    ad_url = url_link.get('href')
                else:
                    ad_url = ""

                # 🚀 НОВОЕ: Объединяем Title и URL через перенос строки
                if ad_url:
                    ad_title_with_url = f"{ad_title}\n{ad_url}"
                else:
                    ad_title_with_url = ad_title

                # Далее ячейки идут по порядку как в шапке
                def cell_text(idx):
                    try:
                        if idx >= len(cells):
                            return ""
                        cell = cells[idx]
                        link = cell.find('a', class_='pr-link')
                        if link:
                            return link.get_text(strip=True).replace("\n", " ")
                        else:
                            return cell.get_text(strip=True).replace("\n", " ")
                    except Exception:
                        return ""

                # Индексация: [0] уже использовали под заголовок/URL
                views = cell_text(1)
                opened = cell_text(2)
                clicks = cell_text(3)
                actions = cell_text(4)
                ctr = cell_text(5)
                cvr = cell_text(6)
                cpm = cell_text(7)
                cpc = cell_text(8)
                cpa = cell_text(9)
                spent = cell_text(10)
                budget = cell_text(11)
                target = cell_text(12)
                status = cell_text(13)
                date_added = cell_text(14)

                # 🚀 ОПТИМИЗАЦИЯ: Правильная обработка числовых данных
                try:
                    cpm_clean = cpm.replace('€', '').replace(',', '.')
                    cpm_num = float(
                        cpm_clean) if cpm_clean and cpm_clean != '–' else 0.0
                except ValueError:
                    cpm_num = cpm

                try:
                    budget_clean = budget.replace('€', '').replace(',', '.')
                    budget_num = float(
                        budget_clean) if budget_clean and budget_clean != '–' else 0.0
                except ValueError:
                    budget_num = budget

                row_data = {
                    'Ad Title': ad_title_with_url,  # 🚀 ИЗМЕНЕНО: Title + URL через перенос строки
                    'Views': views,
                    'Actions': actions,
                    'CPM': cpm_num,
                    'Budget': budget_num,
                    'Target': target,
                    'Status': status,
                    'Date Added': date_added
                }
                parsed_data.append(row_data)

                # 🔍 ОТЛАДКА: Выводим первую спарсенную строку
                if len(parsed_data) == 1:
                    print(f"[ПАРСИНГ] 🔍 Пример спарсенной строки:")
                    print(f"  - Title with URL: {ad_title_with_url[:100]}...")
                    print(f"  - Views: {views}, Actions: {actions}")
                    print(f"  - CPM: {cpm_num}, Budget: {budget_num}")

            except Exception as e:
                print(f"[ПАРСИНГ] ❌ Ошибка при парсинге строки {i}: {e}")
                skipped_rows += 1
                continue

        print(f"🚀 Спарсено {len(parsed_data)} строк из таблицы")
        print(f"📊 Всего строк найдено: {len(rows)}")
        print(f"✅ Успешно спарсено: {len(parsed_data)}")
        print(f"⚠️ Пропущено строк: {skipped_rows}")

        return parsed_data

    except Exception as e:
        print(f"Ошибка при парсинге таблицы: {e}")
        return []


def save_to_excel_optimized(data, channel_name, filename=None):
    """
    🚀 ОПТИМИЗИРОВАННОЕ сохранение в Excel с правильными типами данных
    """
    if not filename:
        # Очищаем имя канала от недопустимых символов для имени файла
        safe_channel_name = "".join(
            c for c in channel_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_channel_name}_{timestamp}.xlsx"

    try:
        # Создаем DataFrame из данных
        df = pd.DataFrame(data)

        # 🚀 ОБНОВЛЕНО: Ad Title теперь содержит Title + URL через перенос строки
        columns_order = ['Ad Title', 'Views', 'Actions',
                         'CPM', 'Budget', 'Target', 'Status', 'Date Added']
        df = df.reindex(columns=columns_order)

        # 🚀 ОПТИМИЗАЦИЯ: Правильные типы данных для числовых колонок
        numeric_columns = ['CPM', 'Budget']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Сохраняем в Excel
        df.to_excel(filename, index=False, engine='openpyxl')

        print(f"🚀 Данные канала '{channel_name}' сохранены в файл: {filename}")
        return filename

    except Exception as e:
        print(f"Ошибка при сохранении в Excel: {e}")
        return None


def parse_channel_data_optimized(driver, channel_name, save_excel=True):
    """
    🚀 ОПТИМИЗИРОВАННЫЙ поиск канала и парсинг данных
    """
    try:
        # Находим канал
        channel_element = find_channel_by_name(driver, channel_name)

        if not channel_element:
            return {'error': f'Канал "{channel_name}" не найден'}

        # Кликаем по каналу
        channel_element.click()

        # 🚀 ОПТИМИЗАЦИЯ: Ждем загрузки специфического элемента вместо time.sleep()
        wait = WebDriverWait(driver, 15)  # Увеличено до 15 секунд
        try:
            # Ждем появления таблицы или заголовка страницы канала
            wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".js-ads-table-body")))
            print("[ПАРСИНГ] ✅ Таблица найдена, ожидаю дополнительно 2 сек...")
            time.sleep(2)  # Дополнительная пауза после появления таблицы
        except TimeoutException:
            print("⚠️ Таблица не загрузилась за 15 секунд, продолжаем...")

        # Парсим данные таблицы с критическими оптимизациями
        table_data = parse_table_data_optimized(driver)

        result = {
            'channel_name': channel_name,
            'table_data': table_data,
            'status': 'success'
        }

        # Сохраняем в Excel если нужно
        if save_excel and table_data:
            excel_file = save_to_excel_optimized(table_data, channel_name)
            if excel_file:
                result['excel_file'] = excel_file

        return result

    except Exception as e:
        return {'error': f'Ошибка при парсинге канала: {e}'}
