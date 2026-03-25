import discord
from discord.ext import commands
from discord import File
from easy_pil import Editor, load_image_async, Font
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# --- 1. KEEP ALIVE WEB SERVER (Required for Render) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    # Render uses port 8080 by default for many setups
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_web)
    t.daemon = True
    t.start()

# --- 2. BOT CONFIGURATION ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="the server"
        )
    )
    print(f'✅ {bot.user} is online and connected to Discord!')

@bot.event
async def on_member_join(member):
    # REPLACE THIS ID with your actual Welcome Channel ID
    WELCOME_CHANNEL_ID = 1485781231491743885 
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    
    # Path handling for Linux/Windows compatibility
    base_path = os.path.dirname(__file__)
    BG_PATH = os.path.join(base_path, "background.jpg")
    
    try:
        # Check if channel exists
        if not channel:
            print(f"❌ Error: Could not find channel with ID {WELCOME_CHANNEL_ID}")
            return

        # --- IMAGE GENERATION ---
        if os.path.exists(BG_PATH):
            # Load and process image
            background = Editor(BG_PATH).resize((800, 450))
            
            # Get avatar - fallback to default if user has no avatar
            avatar_url = member.display_avatar.url
            avatar_data = await load_image_async(str(avatar_url))
            profile = Editor(avatar_data).resize((160, 160)).circle_image()
            
            background.paste(profile, (320, 80))
            
            # Fonts
            font_big = Font.poppins(size=50, variant="bold")
            font_small = Font.poppins(size=30, variant="regular")
            
            background.text((400, 270), "WELCOME", color="white", font=font_big, align="center")
            background.text((400, 325), f"{member.name}", color="white", font=font_small, align="center")
            
            file = File(fp=background.image_bytes, filename="welcome.png")
            await channel.send(f"Welcome to the server, {member.mention}! ✨", file=file)
        else:
            # Fallback if image file is missing
            await channel.send(f"Welcome to the server, {member.mention}! ✨ (Background image missing)")

        # --- SEND RULES DM ---
        rules_embed = discord.Embed(
            title=f"Welcome to {member.guild.name}!",
            description="Please follow our community guidelines:",
            color=discord.Color.gold()
        )
        rules_embed.add_field(name="📜 Rules", value="1. Be respectful\n2. No spam\n3. No unauthorized links", inline=False)
        rules_embed.set_footer(text="Enjoy your stay!")
        
        try:
            await member.send(embed=rules_embed)
        except discord.Forbidden:
            print(f"⚠️ Could not DM {member.name} (DMs are closed).")

    except Exception as e:
        print(f"⚠️ System Error: {e}")

# --- 3. START BOT ---
if __name__ == "__main__":
    if TOKEN:
        keep_alive() # Start web server
        bot.run(TOKEN)
    else:
        print("❌ CRITICAL ERROR: DISCORD_TOKEN not found in environment variables!")
