import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from email_reader import get_confirmation_code

# Настройки
REGISTER_URL = "https://axieinfinity.com/pre-register/?ref=ieiuaxzl"
EMAILS = [
    "example1@mail.ru:password1",
    "example2@mail.ru:password2"
]
MAX_ATTEMPTS = 5  # Количество попыток
DELAY_BETWEEN_ACTIONS = 3  # Задержка между действиями

# Инициализация браузера
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

registered_accounts = 0  # Счётчик зарегистрированных аккаунтов

for email_data in EMAILS:
    email, password = email_data.split(":")
    driver.get(REGISTER_URL)
    
    try:
        # Ввод почты
        email_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email")))
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)
        print(f"📧 Регистрируем почту: {email}")
        time.sleep(DELAY_BETWEEN_ACTIONS)

        # Ждём новый код (убедимся, что это свежий код)
        confirmation_code = get_confirmation_code(email, password, MAX_ATTEMPTS)
        if not confirmation_code:
            print("❌ Не удалось получить код подтверждения, пропускаем аккаунт.")
            continue

        # Вводим код
        code_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "code")))
        code_input.send_keys(confirmation_code)
        code_input.send_keys(Keys.RETURN)
        print(f"✅ Код введён!")

        # Нажимаем кнопку подтверждения капчи
        confirm_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "axie-captcha-confirm-button")))
        confirm_button.click()
        print("✅ Капча подтверждена!")

        # Проверяем, прошла ли капча (ждём перехода на success-страницу)
        time.sleep(DELAY_BETWEEN_ACTIONS)
        if "registration-successful" in driver.current_url:
            print("🎉 Регистрация успешна!")
            registered_accounts += 1
        else:
            print("❌ Капча не прошла, пробуем снова с той же почтой.")
            continue  # Повторяем попытку с этим же email

        # Выход из аккаунта
        try:
            menu_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "sub-menu-group_itemContent__KXOWI")))
            menu_button.click()
            logout_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, "sub-menu-group_itemLabel__ZbaJg")))
            logout_button.click()
            print("🔄 Выходим из аккаунта...")
        except:
            print("❌ Не удалось выйти из аккаунта.")

    except Exception as e:
        print(f"❌ Ошибка: {e}")

print(f"✅ Всего зарегистрировано аккаунтов: {registered_accounts}")
driver.quit()
