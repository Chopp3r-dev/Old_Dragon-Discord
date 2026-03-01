import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv

# --- CONFIGURAÇÃO DE CAMINHO ---
# Isso garante que o Python ache o .env na mesma pasta do main.py
diretorio_atual = os.path.dirname(os.path.abspath(__file__))
caminho_env = os.path.join(diretorio_atual, '.env')

if os.path.exists(caminho_env):
    load_dotenv(caminho_env)
    TOKEN = os.getenv('DISCORD_TOKEN')
else:
    TOKEN = None
    print("❌ Arquivo .env não encontrado no diretório!")

# --- CONFIGURAÇÃO DO BOT ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='&', intents=intents)

async def carregar_cogs():
    pasta_cogs = os.path.join(diretorio_atual, 'cogs')
    if not os.path.exists(pasta_cogs):
        return
        
    for filename in os.listdir(pasta_cogs):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"📦 Módulo carregado: {filename}")
            except Exception as e:
                print(f"❌ Erro no módulo {filename}: {e}")

@bot.event
async def on_ready():
    print(f"✅ Bot online: {bot.user.name}")

async def iniciar():
    async with bot:
        await carregar_cogs()
        if TOKEN:
            try:
                await bot.start(TOKEN)
            except Exception as e:
                print(f"❌ Erro do Discord: {e}")
        else:
            print("❌ Erro: TOKEN está vazio ou None no .env")

if __name__ == "__main__":
    try:
        asyncio.run(iniciar())
    except KeyboardInterrupt:
        pass
