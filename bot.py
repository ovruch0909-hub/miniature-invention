import requests
import time

TELEGRAM_TOKEN = '8130580024:AAGOjgt2wuDl5LCAQD25I8wRVcgl3xLoNNU'
MISTRAL_API_KEY = "eR5UueMtT8vWsMy15rZTErptGBdHHK0R"

TG_BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
TG_FILE_URL = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}"
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


def analyze_image_and_text(image_url, user_prompt):
    headers = {"Authorization": f"Bearer {MISTRAL_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "pixtral-12b",
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": f"Ты CribMaster 🎓. Реши задачу с фото: {user_prompt}"},
            {"type": "image_url", "image_url": image_url}
        ]}]
    }
    try:
        res = requests.post(MISTRAL_URL, json=data, headers=headers, timeout=60)
        return res.json()['choices'][0]['message']['content']
    except:
        return "❌ Ошибка анализа фото."


def generate_video_url(prompt):
    safe_prompt = requests.utils.quote(prompt)
    return f"https://pollinations.ai/p/{safe_prompt}?width=1024&height=1024&model=flux&video=true"


def generate_image_url(prompt):
    return f"https://pollinations.ai/p/{requests.utils.quote(prompt)}?width=1024&height=1024&model=flux"


def send_message(chat_id, text):
    requests.post(f"{TG_BASE_URL}/sendMessage", json={"chat_id": chat_id, "text": text})


def send_video(chat_id, video_url, caption):
    requests.post(f"{TG_BASE_URL}/sendVideo", json={"chat_id": chat_id, "video": video_url, "caption": caption})


def send_photo(chat_id, photo_url, caption):
    requests.post(f"{TG_BASE_URL}/sendPhoto", json={"chat_id": chat_id, "photo": photo_url, "caption": caption})


def main():
    last_update_id = 0
    print("🚀 CribMaster ULTIMATE started on Fly.io")

    while True:
        try:
            url = f"{TG_BASE_URL}/getUpdates?offset={last_update_id + 1}&timeout=20"
            res = requests.get(url).json()

            if not res.get("result"):
                continue

            for update in res["result"]:
                last_update_id = update["update_id"]

                if "message" not in update:
                    continue

                msg = update["message"]
                chat_id = msg["chat"]["id"]

                if "photo" in msg:
                    file_id = msg["photo"][-1]["file_id"]
                    path_res = requests.get(f"{TG_BASE_URL}/getFile?file_id={file_id}").json()
                    img_url = f"{TG_FILE_URL}/{path_res['result']['file_path']}"
                    send_message(chat_id, "🔍 Читаю фото...")
                    send_message(chat_id, analyze_image_and_text(img_url, msg.get("caption", "Реши это")))

                elif "text" in msg:
                    txt = msg["text"].lower()

                    if txt.startswith(("видео", "/video", "video")):
                        p = txt.replace("/video", "").replace("видео", "").replace("video", "").strip()
                        if not p:
                            send_message(chat_id, "🎬 Напиши описание для видео!")
                            continue
                        send_message(chat_id, f"🎬 Создаю видео: {p}")
                        send_video(chat_id, generate_video_url(p), f"Готово!")

                    elif txt.startswith(("намалюй", "/img")):
                        p = txt.replace("намалюй", "").replace("/img", "").strip()
                        send_message(chat_id, f"🎨 Малюю: {p}")
                        send_photo(chat_id, generate_image_url(p), f"Готово!")

                    elif txt == "/start":
                        send_message(chat_id, "🌟 Я CribMaster. Кидай фото или команды!")

                    else:
                        send_message(chat_id, "⏳ Думаю...")
                        send_message(chat_id, "Готово!")

        except Exception as e:
            print("Error:", e)
            time.sleep(2)


if __name__ == "__main__":
    main()
