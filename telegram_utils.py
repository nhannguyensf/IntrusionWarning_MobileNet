import telegram
from datetime import datetime
import secret

def send_telegram(photo_path="alert.png"):
    try:
        my_token = secret.my_token
        chat_id = secret.chat_id
        bot = telegram.Bot(token=my_token)
        bot.sendPhoto(chat_id=chat_id, photo=open(photo_path, "rb"), caption="Alert!!! Intrusion detected at {}.".format(datetime.now().strftime("%H:%M:%S-%d/%m/%Y")))
    except Exception as ex:
        print("Can not send message telegram at {}".format(datetime.now().strftime("%H:%M:%S-%d/%m/%Y")), ex)

    print("Send success at {}".format(datetime.now().strftime("%H:%M:%S-%d/%m/%Y")))