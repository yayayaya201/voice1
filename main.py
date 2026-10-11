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

# Lấy Token từ biến môi trường của Render (hoặc thay trực tiếp token vào đây nếu muốn)
TOKEN = os.getenv("DISCORD_TOKEN")

# THAY TRỰC TIẾP ID SERVER VÀ ID KÊNH VOICE VÀO ĐÂY (Dạng số nguyên - Integer)
GUILD_ID = 123456789012345678    # <-- Thay ID Server của bạn vào đây
CHANNEL_ID = 123456789012345678  # <-- Thay ID Kênh Voice của bạn vào đây

async def keep_voice_connected():
    """Hàm tự động kết nối và duy trì trạng thái trong phòng Voice 24/7"""
    print(f"[DEBUG] Đang khởi chạy với GUILD_ID: {GUILD_ID}, CHANNEL_ID: {CHANNEL_ID}")
    await bot.wait_until_ready()
    
    while not bot.is_closed():
        try:
            guild = bot.get_guild(GUILD_ID)
            if guild:
                channel = guild.get_channel(CHANNEL_ID)
                if channel and isinstance(channel, discord.VoiceChannel):
                    voice_client = guild.voice_client
                    
                    # Nếu chưa vào phòng -> Thực hiện kết nối
                    if voice_client is None:
                        print(f"[VOICE] Đang kết nối vào kênh: {channel.name}...")
                        await channel.connect(reconnect=True, self_deaf=True)
                        print(f"[VOICE] Kết nối thành công 24/7!")
                    # Nếu bị rớt kết nối -> Kết nối lại
                    elif not voice_client.is_connected():
                        print("[VOICE] Mất kết nối, đang thử kết nối lại...")
                        await voice_client.connect(reconnect=True, self_deaf=True)
                else:
                    print(f"[WARNING] Không tìm thấy kênh voice với ID: {CHANNEL_ID} trong Server!")
            else:
                print(f"[WARNING] Không tìm thấy Server với ID: {GUILD_ID}!")
                        
        except Exception as e:
            print(f"[ERROR] Lỗi khi duy trì Voice: {e}")
            
        # Kiểm tra lại định kỳ mỗi 30 giây
        await asyncio.sleep(30)

@bot.event
async def on_ready():
    print(f"==== Bot đã sẵn sàng: {bot.user.name} ({bot.user.id}) ====")
    # Khởi chạy vòng lặp treo voice ngầm
    bot.loop.create_task(keep_voice_connected())

if __name__ == "__main__":
    # Khởi chạy web server ngầm trước để Render nhận diện port
    keep_alive()
    
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("[CRITICAL] Không tìm thấy DISCORD_TOKEN trong biến môi trường!")
