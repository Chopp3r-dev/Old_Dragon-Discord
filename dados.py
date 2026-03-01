import discord
from discord.ext import commands
import random

class Dados(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="r")
    async def rolar(self, ctx, *, formula: str):
        """Rola dados no formato &r 1d20+5 ou &r 3d6"""
        try:
            # Tratamento da fórmula (ex: 1d20+5)
            formula = formula.replace(" ", "").lower()
            
            if "+" in formula:
                dice_part, bonus_part = formula.split("+")
                bonus = int(bonus_part)
            elif "-" in formula:
                dice_part, bonus_part = formula.split("-")
                bonus = -int(bonus_part)
            else:
                dice_part = formula
                bonus = 0

            qtd, faces = map(int, dice_part.split("d"))
            
            # Rolagem dos dados
            resultados = [random.randint(1, faces) for _ in range(qtd)]
            soma_dados = sum(resultados)
            total = soma_dados + bonus

            # Criando o Embed bonitão
            embed = discord.Embed(
                title="🎲 Resultado da Rolagem",
                color=discord.Color.gold() if total >= 20 else discord.Color.dark_red()
            )
            
            embed.set_author(name=f"Mestre {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            
            # Formatação do bônus para exibição
            str_bonus = f" + {bonus}" if bonus > 0 else (f" - {abs(bonus)}" if bonus < 0 else "")
            
            embed.add_field(name="🔢 Fórmula", value=f"`{formula}`", inline=True)
            embed.add_field(name="💥 Total", value=f"**{total}**", inline=True)
            
            # Se for apenas 1 dado, não precisa listar "Detalhes" para não poluir
            detalhes = f"Detalhes: `{resultados}`{str_bonus}" if qtd > 1 or bonus != 0 else "Dado puro"
            embed.set_footer(text=detalhes)

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send("❌ Formato inválido! Tente algo como `&r 1d20+2` ou `&r 3d6`.")

async def setup(bot):
    await bot.add_cog(Dados(bot))
