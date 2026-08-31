import discord
from discord.ext import commands


class InviteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="battle_invite", description="Пригласить соперника в игру")
    async def battle_invite(
        self,
        ctx: discord.ApplicationContext,
        opponent: discord.Option(discord.Member, "Кого вы хотите пригласить?"),
    ):
        if ctx.guild is None:
            await ctx.respond("Эта команда не доступна в личке.", ephemeral=True)
            return
        if opponent.id == ctx.author.id:
            await ctx.respond("Нельзя пригласить самого себя...", ephemeral=True)
            return
        if opponent.bot:
            await ctx.respond("Нельзя пригласить бота...", ephemeral=True)
            return
        await ctx.respond(f"{opponent.mention}, вас вызывает {ctx.author.mention} на дуэль!")
