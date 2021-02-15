import urllib.request
import config

chat_ids = [199610041, 273077469, 308729527, 884721281]
text = """Game Quiz Bot v0.5 has been released! (Yeah, not 0.4)
Changelog:
1. Categories buttons disappearing added
2. Reset warning added
3. **Feedback feature added** (Only text for now)
4. Nervi uspokoilis' kofeechkom"""
text = text.replace(" ", "%20")
text = text.replace("\n", "%0A")

for i in chat_ids:
    urllib.request.urlopen(f"https://api.telegram.org/bot{config.Token}/sendMessage?chat_id={i}&text={text}")