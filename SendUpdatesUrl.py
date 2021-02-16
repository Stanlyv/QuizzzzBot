import urllib.request
import config

chat_ids = [199610041, 273077469, 308729527, 884721281]
text = """Game Quiz Bot v0.6 has been released!
Changelog:
1. All message type are supporting in feedback now
2. Keyboard button disappearing added
3. DB changes
4. Ya vse eshe ne znau, kak otpravlyat' etot tekst na russkom"""
text = text.replace(" ", "%20")
text = text.replace("\n", "%0A")

for i in chat_ids:
    urllib.request.urlopen(f"https://api.telegram.org/bot{config.Token}/sendMessage?chat_id={i}&text={text}")