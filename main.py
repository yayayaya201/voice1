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

# THAY TRỰC TIẾP ID SERVER VÀ ID KÊNH VOICE VÀO ĐÂY
GUILD_ID = 1405414026468392983    # Đã lấy đúng ID từ log của bạn
CHANNEL_ID = 1560563821079167036  # Đã lấy đúng ID từ log của bạn

async def keep_voice_connected():
    """Hàm vòng lặp vô hạn tự động kiểm tra và duy trì bot trong phòng Voice 24/7"""
    await bot.wait_until_ready()
    
    while not bot.is_closed():
        try:
            guild = bot.get_guild(GUILD_ID)
            if guild:
                channel = guild.get_channel(CHANNEL_ID)
                if channel and isinstance(channel, discord.VoiceChannel):
                    voice_client = guild.voice_client
                    
                    # Nếu bot chưa vào phòng hoặc mất kết nối -> Thực hiện kết nối lại
                    if voice_client is None or not voice_client.is_connected():
                        print(f"[VOICE] Đang kết nối vào kênh: {channel.name}...", flush=True)
                        if voice_client and voice_client.is_connected():
                            await voice_client.disconnect()
                        await channel.connect(reconnect=True, self_deaf=True)
                        print(f"[VOICE] Kết nối thành công 24/7!", flush=True)
                else:
                    print(f"[WARNING] Không tìm thấy kênh voice với ID: {CHANNEL_ID}!", flush=True)
            else:
                print(f"[WARNING] Không tìm thấy Server với ID: {GUILD_ID}!", flush=True)
                
        except Exception as e:
            print(f"[ERROR] Lỗi khi duy trì Voice: {e}", flush=True)
            
        # Kiểm tra và giữ kết nối định kỳ mỗi 30 giây
        await asyncio.sleep(30)

@bot.event
async def on_ready():
    print(f"==== Bot đã sẵn sàng: {bot.user.name} ({bot.user.id}) ====", flush=True)
    # Khởi chạy vòng lặp treo voice ngầm chạy vĩnh viễn
    bot.loop.create_task(keep_voice_connected())

if __name__ == "__main__":
    # Khởi chạy web server ngầm trước để Render nhận diện port
    keep_alive()
    
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("[CRITICAL] Không tìm thấy DISCORD_TOKEN trong biến môi trường!", flush=True)
