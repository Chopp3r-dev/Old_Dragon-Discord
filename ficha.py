import discord
from discord.ext import commands
import sqlite3
import os

class Ficha(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = './data/database.db'
        self._criar_tabela()

    def _criar_tabela(self):
        # Garante que a pasta data existe
        if not os.path.exists('./data'):
            os.makedirs('./data')
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fichas (
                user_id INTEGER PRIMARY KEY,
                nome TEXT, raca TEXT, classe TEXT, nivel INTEGER,
                alinhamento TEXT, vida_max INTEGER, vida_atual INTEGER,
                ca INTEGER, forca INTEGER, des INTEGER, con INTEGER,
                int INTEGER, sab INTEGER, car INTEGER, cor TEXT
            )
        ''')
        conn.commit()
        conn.close()

    @commands.command(name="criar_ficha")
    async def criar(self, ctx, *, informacoes: str):
        """Uso: &criar_ficha Nome Sobrenome, Raça, Classe, Alinhamento"""
        try:
            partes = [p.strip() for p in informacoes.split(',')]
            if len(partes) < 4:
                await ctx.send("❌ Use: `&criar_ficha Nome Completo, Raça, Classe, Alinhamento`")
                return

            nome, raca, classe, alinhamento = partes[0], partes[1], partes[2], partes[3]

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO fichas 
                (user_id, nome, raca, classe, nivel, alinhamento, vida_max, vida_atual, ca, cor)
                VALUES (?, ?, ?, ?, 1, ?, 10, 10, 10, '0xFFFFFF')
            ''', (ctx.author.id, nome, raca, classe, alinhamento))
            conn.commit()
            conn.close()
            await ctx.send(f"✅ Ficha de **{nome}** criada! Use `&set_atributos` para os pontos.")
        except Exception as e:
            await ctx.send(f"❌ Erro ao criar: {e}")

    @commands.command(name="set_atributos")
    async def set_atribs(self, ctx, forca: int, des: int, con: int, intel: int, sab: int, car: int):
        """Define os 6 atributos: &set_atributos 10 10 11 15 15 17"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE fichas 
            SET forca = ?, des = ?, con = ?, int = ?, sab = ?, car = ?
            WHERE user_id = ?
        ''', (forca, des, con, intel, sab, car, ctx.author.id))
        conn.commit()
        conn.close()
        await ctx.send(f"📊 Atributos de **{ctx.author.display_name}** atualizados!")

    @commands.command(name="ficha")
    async def mostrar(self, ctx, membro: discord.Member = None):
        """Mostra a ficha: &ficha ou &ficha @membro"""
        target = membro or ctx.author
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fichas WHERE user_id = ?", (target.id,))
        f = cursor.fetchone()
        conn.close()

        if not f:
            await ctx.send("❌ Ficha não encontrada.")
            return

        embed = discord.Embed(title=f"📜 Personagem: {f[1]}", color=int(f[15], 16))
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="🧬 Raça/Classe", value=f"{f[2]} {f[3]} (Lvl {f[4]})", inline=True)
        embed.add_field(name="❤️ Vida", value=f"{f[7]}/{f[6]}", inline=True)
        embed.add_field(name="🛡️ CA", value=str(f[8]), inline=True)
        
        attrs = (f"STR: {f[9] or 0} | DEX: {f[10] or 0} | CON: {f[11] or 0}\n"
                 f"INT: {f[12] or 0} | WIS: {f[13] or 0} | CHA: {f[14] or 0}")
        embed.add_field(name="📊 Atributos", value=f"```\n{attrs}\n```", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="dano")
    async def dano(self, ctx, quantidade: int, membro: discord.Member = None):
        """Tira vida: &dano 5 ou &dano 5 @membro"""
        target = membro or ctx.author
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE fichas SET vida_atual = vida_atual - ? WHERE user_id = ?", (quantidade, target.id))
        conn.commit()
        conn.close()
        await ctx.send(f"💥 **{target.display_name}** recebeu {quantidade} de dano!")

    @commands.command(name="cura")
    async def cura(self, ctx, quantidade: int, membro: discord.Member = None):
        """Cura vida: &cura 5 ou &cura 5 @membro"""
        target = membro or ctx.author
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # Cura mas não deixa passar do máximo
        cursor.execute("UPDATE fichas SET vida_atual = MIN(vida_max, vida_atual + ?) WHERE user_id = ?", (quantidade, target.id))
        conn.commit()
        conn.close()
        await ctx.send(f"✨ **{target.display_name}** foi curado em {quantidade} PV!")

async def setup(bot):
    await bot.add_cog(Ficha(bot))
