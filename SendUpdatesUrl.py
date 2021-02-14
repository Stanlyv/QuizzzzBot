import urllib.request
import config

chat_ids = [199610041, 273077469, 308729527, 884721281]
text = """Game Quiz Bot v0.3 has been released!
Changelog:
1. Categories added
2. Buttons for categories added
3. Bugs for buttons for categories added
4. DB reworked
5. Moi nervi ne vuderjivaut"""
text = text.replace(" ", "%20")
text = text.replace("\n", "%0A")

for i in chat_ids:
    urllib.request.urlopen(f"https://api.telegram.org/bot{config.Token}/sendMessage?chat_id={i}&text={text}")