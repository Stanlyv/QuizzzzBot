import urllib.request
import config

chat_ids = [199610041, 273077469, 308729527, 884721281]
text = """Game%20Quiz%20Bot%20v0.3%20has%20been%20released!%0AChangelog:%0A1.%20Categories%20added%0A2.%20Buttons%20for%20categories%20added%0A3.%20Bugs%20for%20buttons%20for%20categories%20added%0A4.%20DB%20reworked%0A5.%20Moi%20nervi%20ne%20vuderjivaut"""

for i in chat_ids:
    urllib.request.urlopen(f"https://api.telegram.org/bot{config.Token}/sendMessage?chat_id={i}&text={text}")