import imaplib
import email
import re
import time

def get_confirmation_code(login, password, max_attempts=5, delay=10):
    try:
        mail = imaplib.IMAP4_SSL("imap.mail.ru")
        mail.login(login, password)  # 🔥 УБРАЛ encode('utf-8') для пароля
        mail.select("inbox")

        last_code = None  

        for attempt in range(max_attempts):
            print(f"📩 Попытка {attempt + 1} из {max_attempts}...")

            result, data = mail.search(None, "ALL")
            mail_ids = data[0].split()
            if not mail_ids:
                print("📭 Новых писем нет, ждём...")
                time.sleep(delay)
                continue

            latest_email_id = mail_ids[-1]
            result, message_data = mail.fetch(latest_email_id, "(RFC822)")
            raw_email = message_data[0][1]

            msg = email.message_from_bytes(raw_email)
            email_body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        email_body = part.get_payload(decode=True)
                        if isinstance(email_body, bytes):
                            email_body = email_body.decode('utf-8', errors='ignore')
                        break
            else:
                email_body = msg.get_payload(decode=True)
                if isinstance(email_body, bytes):
                    email_body = email_body.decode('utf-8', errors='ignore')

            code_match = re.search(r"\b\d{6}\b", email_body)
            if code_match:
                new_code = code_match.group(0)
                if new_code == last_code:
                    print("⚠️ Код не изменился, ждём новое письмо...")
                    time.sleep(delay)
                    continue  

                last_code = new_code
                return new_code

            print("⚠️ Код в письме не найден, ждём новое письмо...")
            time.sleep(delay)

        print("❌ Код подтверждения не получен.")
        return None

    except Exception as e:
        print(f"❌ Ошибка при работе с почтой: {e}")
        return None

    finally:
        mail.logout()
