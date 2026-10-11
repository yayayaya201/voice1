import os
import asyncio
import discord
from discord.ext import commands

# Khởi tạo Intents
intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Lấy thông tin cấu hình từ biến môi trường (Secrets)
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", 0))
CHANNEL_ID = int(os.getenv("CHANNEL_ID", 0))

async def keep_voice_connected():
    """Hàm tự động kết nối và duy trì trạng thái trong phòng Voice 24/7"""
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
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("[CRITICAL] Không tìm thấy DISCORD_TOKEN trong biến môi trường!")
