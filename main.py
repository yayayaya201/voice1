import os
import asyncio
import discord
from discord.ext import commands
from threading import Thread
from flask import Flask

# 1. Tạo Flask web server giả lập để Render mở port 24/7
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# 2. Khởi tạo Intents cho Discord Bot
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Lấy Token từ biến môi trường của Render
TOKEN = os.getenv("DISCORD_TOKEN")

# THAY TRỰC TIẾP ID SERVER VÀ ID KÊNH VOICE VÀO ĐÂY (Dạng số nguyên - Integer)
GUILD_ID = 1405414026468392983    # <-- Thay ID Server của bạn vào đây
CHANNEL_ID = 1559185122367119410  # <-- Thay ID Kênh Voice của bạn vào đây

@bot.event
async def on_ready():
    print(f"==== Bot đã sẵn sàng: {bot.user.name} ({bot.user.id}) ====", flush=True)
    try:
        guild = bot.get_guild(GUILD_ID)
        if guild:
            print(f"[DEBUG] Đã tìm thấy Server: {guild.name}", flush=True)
            channel = guild.get_channel(CHANNEL_ID)
            if channel and isinstance(channel, discord.VoiceChannel):
                print(f"[VOICE] Đang kết nối vào kênh: {channel.name}...", flush=True)
                await channel.connect(reconnect=True, self_deaf=True)
                print(f"[VOICE] Kết nối thành công vào phòng thoại!", flush=True)
            else:
                print(f"[WARNING] Không tìm thấy kênh voice với ID: {CHANNEL_ID} trong Server!", flush=True)
        else:
            print(f"[WARNING] Không tìm thấy Server với ID: {GUILD_ID}! (Kiểm tra lại bot đã được mời vào server này chưa)", flush=True)
    except Exception as e:
        print(f"[ERROR] Không thể join voice: {e}", flush=True)

if __name__ == "__main__":
    # Khởi chạy web server ngầm trước để Render nhận diện port
    keep_alive()
    
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("[CRITICAL] Không tìm thấy DISCORD_TOKEN trong biến môi trường!", flush=True)
