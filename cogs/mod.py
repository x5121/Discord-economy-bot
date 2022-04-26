import discord
import random
import asyncio
import pymysql
import pymysql.cursors
import time
import datetime
import re

from discord.ext import commands, tasks
from discord.utils import get
import datetime

class moderation(commands.Cog):

	def __init__(self, bot, con):
		self.bot = bot
		self.con = con
	@commands.command()
	@commands.has_any_role(820406448725950515)
	async def clear(self, ctx, amount: int):
		ctx.channel.purge(limit=amount)
		await ctx.send(f"Успешно удалено {amount} сообщ.")

	@commands.command()
	@commands.has_any_role(820406448725950515)
	async def ban(self, ctx, user: discord.Member, *, reason="Причина не указана"):
		await user.ban(reason=reason)
		embed = discord.Embed(
			description=f"Пользователь **{user.name}#{user.discriminator}** был забанен\n"
			f"Администратор: **{ctx.author.mention}**"
			f"Причина: {reason}"
			)
		await ctx.send(embed=embed)

	@commands.command()
	@commands.has_any_role(820406448725950515)
	async def kick(self, ctx, user: discord.Member, *, reason="Причина не указана"):
		await user.ban(reason=reason)
		embed = discord.Embed(
			description=f"Пользователь **{user.name}#{user.discriminator}** был выгнан\n"
			f"Администратор: **{ctx.author.mention}**"
			f"Причина: {reason}"
			)
		await ctx.send(embed=embed)

	@commands.command(name="mute-role")
	@commands.has_permissions(administrator=True)
	async def muterole(self, ctx, role: discord.Role):
		with self.con.cursor() as cursor:
			cursor.execute("UPDATE `ConfigDB` SET `mute_role`=%s WHERE `gid`=%s", (role.id, ctx.guild.id))
			await ctx.message.add_reaction('✅')
		self.con.commit()

	@commands.command(
		usage="mute [пользователь] [время] (причина)",
		description="Можно заглушить пользовтеля на время",
		brief="mute @M1racle 10m Оскорбление\nmute @M1racle 10h Нарушение правил\nmute @M1racle 1d Он сам захотел"
		)
	@commands.has_any_role(820406448725950515,819321566223007744)
	async def mute (self, ctx, user: discord.Member, duration, reason = "Причина не указана"):
		with self.con.cursor() as cursor:
			if user == ctx.author:
				embed = discord.Embed ( 
					description=f"<:error:820689811182583829> Ты не можешь заглушить самого себя!", 
					color = 0xfa4c4d
					)
				await ctx.send (embed=embed)
			elif user == ctx.guild.owner:
				embed = discord.Embed (
					description=f"<:error:820689811182583829> Ты не можешь заглушить владельца сервера!", 
					color = 0xfa4c4d
					)
				await ctx.send (embed=embed)
			elif ctx.author.top_role.position < user.top_role.position:
				embed = discord.Embed (
					description=f"<:error:820689811182583829> Ты не можешь заглушить человека с ролью выше твоей!", 
					color = 0xfa4c4d
					)
				await ctx.send (embed=embed)
			else:
				cursor.execute("SELECT mute_role FROM `ConfigDB` WHERE `gid`=%s", (ctx.guild.id))
				role = ctx.guild.get_role(int(cursor.fetchone()[0]))
				time = None
				type = None
				if duration.endswith("s"):
					duration, type = re.findall(r'(\d+)([a-zA-Z])', duration)[0]
					time = int(duration)
					type = "сек."
				if duration.endswith("m"):
					duration, type = re.findall(r'(\d+)([a-zA-Z])', duration)[0]
					time = int(duration)*60
					type = "мин."
				if duration.endswith("h"):
					duration, type = re.findall(r'(\d+)([a-zA-Z])', duration)[0]
					time = int(duration)*60*60
					type = "ч."
				if duration.endswith("d"):
					duration, type = re.findall(r'(\d+)([a-zA-Z])', duration)[0]
					time = int(duration)*60*60*24
					type = "дн."

				await user.add_roles(role)
				embed = discord.Embed (
					description=f"<:succes:820689811182583829> ***{user}*** заглушен на **{duration}{type}** | {reason}", 
					color = 0x43b581
					)
				await ctx.send(time)
				await ctx.send(duration)
				await ctx.send (embed=embed)
				timestamp = int(datetime.datetime.now().timestamp()) + int(time)
				cursor.execute(f"INSERT INTO `MutesDB` VALUES (NULL, '{ctx.guild.id}', '{user.id}', '{reason}', '{timestamp}')")
		self.con.commit()

	@commands.command()
	@commands.has_any_role(820689811182583829)
	async def unmute(self, ctx, user: discord.Member):
		with self.con.cursor() as cursor:
			cursor.execute("DELETE FROM `MutesDB` WHERE `gid`=%s AND `uid`=%s", (ctx.guild.id, user.id))
			cursor.execute("SELECT mute_role FROM `ConfigDB` WHERE `gid`=%s", (ctx.guild.id))
			role = ctx.guild.get_role(int(cursor.fetchone()[0]))
			await user.remove_roles(role)
			await ctx.message.add_reaction('✅')
		self.con.commit()
