import asyncio
import json
import os
import requests
import websockets
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# --- 1. WEB SERVER GIA LẬP CHO UPTIMEROBOT ---
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"[HTTP] Web server started on port {port}")
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

# --- 2. CẤU HÌNH LẤY TỪ RENDER ---
TOKEN = os.environ.get("DISCORD_TOKEN")
GUILD_ID = os.environ.get("GUILD_ID")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

if not TOKEN or not GUILD_ID or not CHANNEL_ID:
    print("[LỖI] Thiếu biến môi trường (DISCORD_TOKEN, GUILD_ID hoặc CHANNEL_ID) trên Render!")
    exit(1)

STATUS = "online" # online / dnd / idle
SELF_MUTE = True
SELF_DEAF = False

API = "https://discord.com/api/v10"

res = requests.get(f"{API}/users/@me", headers={"Authorization": TOKEN})
if res.status_code != 200:
    print("Invalid token!")
    exit()

user = res.json()
print(f"Logged in as {user['username']} ({user['id']})!")

async def heartbeat(ws, interval):
    while True:
        await asyncio.sleep(interval / 1000)
        await ws.send(json.dumps({"op": 1, "d": None}))

async def main():
    uri = "wss://gateway.discord.gg/?v=10&encoding=json"

    async with websockets.connect(uri, max_size=10 * 1024 * 1024) as ws:
        hello = json.loads(await ws.recv())
        heartbeat_interval = hello["d"]["heartbeat_interval"]

        asyncio.create_task(heartbeat(ws, heartbeat_interval))

        await ws.send(json.dumps({
            "op": 2,
            "d": {
                "token": TOKEN,
                "properties": {
                    "$os": "windows",
                    "$browser": "chrome",
                    "$device": "pc"
                },
                "presence": {
                    "status": STATUS,
                    "afk": False
                }
            }
        }))

        while True:
            event = json.loads(await ws.recv())
            if event.get("t") == "READY":
                break

        await ws.send(json.dumps({
            "op": 4,
            "d": {
                "guild_id": GUILD_ID,
                "channel_id": CHANNEL_ID,
                "self_mute": SELF_MUTE,
                "self_deaf": SELF_DEAF
            }
        }))

        print("Joined the voice channel!")

        while True:
            try:
                msg = await ws.recv()
            except:
                print("Disconnected, reconnecting...")
                break

async def run():
    while True:
        try:
            await main()
        except Exception as e:
            print("Error: ", e)
            await asyncio.sleep(5)

asyncio.run(run())
