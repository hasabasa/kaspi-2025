import base64
import json
import logging
import os
import time
import platform
import uuid

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import shutil
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('kaspi_auth.log'), logging.StreamHandler()]
)


class KaspiAuthenticator:
    def __init__(self, user_id):
        self.user_id = user_id
        self.accounts_file = 'accounts.json'
        self.chrome_options = Options()

        self.service = Service(ChromeDriverManager().install())
        self.driver = None
        self.current_state = None
        self.current_email = None
        self.accounts = self.load_accounts()

    def load_accounts(self):
        if os.path.exists(self.accounts_file):
            try:
                with open(self.accounts_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Error loading accounts: {e}")
        return {}

    def save_accounts(self):
        with open(self.accounts_file, 'w') as f:
            json.dump(self.accounts, f)

    def get_user_account(self):
        return self.accounts.get(str(self.user_id))

    def save_user_account(self, email, password):
        self.accounts[str(self.user_id)] = {
            'email': email,
            'password': password,
            'timestamp': int(time.time())
        }
        self.save_accounts()

    def take_screenshot(self, stage_name=None):
        try:
            screenshot = self.driver.get_screenshot_as_png()
            encoded = base64.b64encode(screenshot).decode('utf-8')

            # Сохраняем файл
            if stage_name:
                os.makedirs("screenshots", exist_ok=True)
                filename = f"screenshots/{int(time.time())}_{self.user_id}_{stage_name}.png"
                with open(filename, "wb") as f:
                    f.write(base64.b64decode(encoded))
                logging.info(f"Скриншот сохранён: {filename}")

            return encoded
        except Exception as e:
            logging.error(f"Ошибка при создании скриншота: {e}")
            return None


    def init_driver(self):
        if self.driver is not None:
            self.driver.quit()

        # Очистка и создание новой директории профиля
        import tempfile
        if hasattr(self, 'profile_dir') and os.path.exists(self.profile_dir):
            shutil.rmtree(self.profile_dir, ignore_errors=True)

        self.profile_dir = tempfile.mkdtemp(prefix=f"kaspi_profile_{self.user_id}_{uuid.uuid4().hex[:8]}_")

        # Обновляем chrome_options сразу, один раз
        self.chrome_options = Options()
        self.chrome_options.add_argument(f"--user-data-dir={self.profile_dir}")

        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--window-size=1200,800")
        self.chrome_options.add_argument(f"--user-data-dir={self.profile_dir}")
        if platform.system() == "Linux":
            self.chrome_options.add_argument("--headless=chrome")  # или просто "--headless"
            self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            self.chrome_options.add_argument("--disable-gpu")
            self.chrome_options.add_argument("--disable-infobars")
            self.chrome_options.add_argument("--disable-extensions")
            self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            self.chrome_options.add_experimental_option("useAutomationExtension", False)
            self.chrome_options.add_argument(
                "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            self.chrome_options.binary_location = "/usr/bin/google-chrome"

        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.driver.get("https://idmc.shop.kaspi.kz/login")
        time.sleep(2)
        return self.take_screenshot("init_login_page")



    def enter_email(self, email):
        try:
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "user_email_field"))
            )
            email_field.clear()
            email_field.send_keys(email)

            continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.button.is-primary"))
            )
            continue_button.click()

            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: driver.find_element(By.ID, "password_field").is_displayed() or
                                   driver.find_elements(By.CSS_SELECTOR, ".notification.is-danger")
                )
            except TimeoutException:
                screenshot = self.take_screenshot()
                return False, "Не удалось перейти на страницу ввода пароля", screenshot

            screenshot = self.take_screenshot("email_input_success")
            return True, "Email введен успешно", screenshot
        except Exception as e:
            logging.error(f"Ошибка при вводе email: {e}")
            screenshot = self.take_screenshot("email_input_fail")
            return False, f"Ошибка при вводе email: {str(e)}", screenshot

    def enter_password(self, password):
        try:
            logging.info(f"Перед вводом пароля: URL={self.driver.current_url}, TITLE={self.driver.title}")
            screenshot = self.take_screenshot("before_password_input")

            # Ждем появления поля пароля и немного ждём после
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "password_field"))
            )
            time.sleep(1)
            password_field = self.driver.find_element(By.ID, "password_field")

            password_field.clear()
            password_field.send_keys(password)

            screenshot = self.take_screenshot("after_password_filled")

            continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.button.is-primary"))
            )
            continue_button.click()

            screenshot = self.take_screenshot("after_continue_click")

            try:
                WebDriverWait(self.driver, 30).until(
                    lambda driver: any([
                        self._is_authorized(driver),
                        driver.find_elements(By.CSS_SELECTOR, ".notification.is-danger")
                    ])
                )
            except TimeoutException:
                screenshot = self.take_screenshot("timeout_after_password")
                return False, "Таймаут ожидания авторизации", screenshot

            if self._is_authorized(self.driver):
                self.save_user_account(self.current_email, password)
                screenshot = self.take_screenshot("password_input_success")
                return True, "Авторизация успешна", screenshot
            else:
                error_msg = self._get_error_message()
                screenshot = self.take_screenshot("password_input_fail")
                return False, error_msg or "Не удалось подтвердить авторизацию", screenshot

        except Exception as e:
            logging.error(f"Ошибка при вводе пароля: {str(e)}")
            screenshot = self.take_screenshot("exception_in_password")
            return False, f"Ошибка: {str(e)}", screenshot

    def _is_authorized(self, driver):
        try:
            return "Кабинет продавца" in driver.title
        except:
            return False

    # def _is_authorized(self, driver):
    #     try:
    #         current_url = driver.current_url
    #         if current_url != "https://kaspi.kz/mc/#/orders?status=NEW":
    #             return False
    #
    #         menu_element = driver.find_element(By.CSS_SELECTOR, 'div.menu')
    #         menu_html = menu_element.get_attribute('outerHTML')
    #
    #         required_elements = [
    #             '<p data-v-466f4a84="" class="menu-label"> Заказы </p>',
    #             '<a href="#/orders?status=NEW" class="router-link-exact-active router-link-active is-active"',
    #             '<div data-v-466f4a84="" class="menu__item order__items"><img data-v-466f4a84="" src="/mc/img/new.97c3cf73.svg"'
    #         ]
    #
    #         if not all(element in menu_html for element in required_elements):
    #             return False
    #
    #         return True
    #
    #     except Exception as e:
    #         logging.error(f"Ошибка проверки авторизации: {e}")
    #         return False

    def _get_error_message(self):
        try:
            error_element = self.driver.find_element(By.CSS_SELECTOR, ".notification.is-danger, .error-message")
            return error_element.text.strip()
        except:
            return None

    def login(self, email, password):
        self.current_email = email
        result = {
            "success": False,
            "error": None,
            "merchant_id": None,
            "store_name": None,
            "screenshot": None
        }

        try:
            # Инициализация драйвера
            self.init_driver()

            # Ввод email
            success, message, screenshot = self.enter_email(email)
            if not success:
                result["error"] = message
                result["screenshot"] = screenshot
                return result

            # Ввод пароля
            success, message, screenshot = self.enter_password(password)
            if success:
                merchant_info = self._get_merchant_info()
                result.update({
                    "success": True,
                    "merchant_id": merchant_info["merchant_id"],
                    "store_name": merchant_info["store_name"],
                    "screenshot": screenshot
                })
            else:
                result["error"] = message
                result["screenshot"] = screenshot

            return result

        except Exception as e:
            logging.error(f"Ошибка в процессе аутентификации: {e}")
            result["error"] = f"Ошибка аутентификации: {str(e)}"
            result["screenshot"] = self.take_screenshot("auth_exception")
            return result
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
            if hasattr(self, 'profile_dir') and os.path.exists(self.profile_dir):
                shutil.rmtree(self.profile_dir, ignore_errors=True)


    def _get_merchant_info(self):
        """Получение информации о магазине с новыми селекторами"""
        try:
            # Ожидаем загрузки навигационной панели
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "navbar-end"))
            )
            # Получаем название магазина из элемента <a class="navbar-link is-arrowless">
            name_element = self.driver.find_element(
                By.CSS_SELECTOR, "a.navbar-link.is-arrowless")
            store_name = name_element.text.strip()

            # Получаем merchant_id из элемента с ID (формат "ID - 30355555")
            id_element = self.driver.find_element(
                By.XPATH, "//div[contains(@class, 'navbar-item') and contains(text(), 'ID - ')]")
            merchant_id = id_element.text.split("ID - ")[1].strip()

            return {
                "merchant_id": merchant_id,
                "store_name": store_name
            }

        except Exception as e:
            logging.error(f"Error getting merchant info: {e}")
            return {
                "merchant_id": "demo-123",
                "store_name": "Мой магазин Kaspi"
            }

    def check_existing_account(self):
        return str(self.user_id) in self.accounts

    def __del__(self):
        if hasattr(self, 'driver') and self.driver:
            try:
                self.driver.quit()
            except:
                pass
