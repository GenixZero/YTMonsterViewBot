# YT Monster API/Bot
Lightweight Python YTMonster Client Wrapper. Get view exchanges on https://ytmonster.net without actually watching any videos. Run multiple clients & accounts easily in the same process.
## Demo
```
from ytmonsterclient import YTMonsterClient
import time

client = YTMonsterClient(username, password)
client.startAsync()
time.sleep(25)
client.stop()
```