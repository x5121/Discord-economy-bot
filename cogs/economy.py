import discord
import random
from discord.ext import commands, tasks
import datetime

class economy(commands.Cog):

	def __init__(self, bot, con):
		self.bot = bot
		self.con = con

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		if isinstance(error, commands.CommandOnCooldown):
			m, s = divmod(error.retry_after, 60)
			h, m = divmod(m, 60)
			if int(h) is 0 and int(m) is 0:
				await ctx.send(f"Ты сможешь использовать эту команду через **{int(s)}** сек.")
			elif int(h) is 0 and int(m) is not 0:
				await ctx.send(f"Ты сможешь использовать эту команду через **{int(m)}** мин. **{int(s)}** сек.")
			else:
				await ctx.send(f"Ты сможешь использовать эту команду через **{int(h)}** ч. **{int(m)}** мин. **{int(s)}** сек.")

	@commands.command()
	async def balance(self, ctx, user: discord.Member = None):
		user = ctx.author if (user is None) else user
		with self.con.cursor() as cursor:
			cursor.execute("SELECT balance FROM `UsersDB` WHERE `gid`=%s AND `uid`=%s", (ctx.guild.id, user.id))
			bal = cursor.fetchone()[0]
			embed = discord.Embed(title=f"🤑Баланс {user.name}")
			embed.add_field(name=f"{bal}$", value=f"** **")
			await ctx.send(embed=embed)

	@commands.command()
	async def casino(self, ctx, bet: int):
		with self.con.cursor() as cursor:
			cursor.execute("SELECT balance FROM `UsersDB` WHERE `gid`=%s AND `uid`=%s", (ctx.guild.id, ctx.author.id))
			bal = cursor.fetchone()[0]
			if int(bal) < 50:
				await ctx.send("👀Минимальный баланс 50 :[")
				return
			elif int(bal) < bet:
				await ctx.send("😢У вас недостаточно деняк :[")
				return
			rand = random.randint(0, 1)
			if rand == 0:
				cursor.execute("UPDATE `UsersDB` SET `balance`=%s WHERE `gid`=%s AND `uid`=%s", (int(bal)-bet, ctx.guild.id, ctx.author.id))
				await ctx.send(f"🤑Не повезло не повезло, вы проиграли **{bet}$**, ваш баланс: **{int(bal)-bet}$**")
			if rand == 1:
				cursor.execute("UPDATE `UsersDB` SET `balance`=%s WHERE `gid`=%s AND `uid`=%s", (int(bal)+bet, ctx.guild.id, ctx.author.id))
				await ctx.send(f"🙏О повезло повезло, вы выиграли **{bet}$**, ваш баланс: **{int(bal)+bet}$**")
		self.con.commit()

	@commands.cooldown(1, 7200, commands.BucketType.user)
	@commands.command()
	async def work(self, ctx):
		with self.con.cursor() as cursor:
			rand = random.randint(100, 300)
			cursor.execute(f"UPDATE `UsersDB` SET `balance`=balance+{rand} WHERE `gid`=%s AND `uid`=%s", (ctx.guild.id, ctx.author.id))
			await ctx.send(f"💼Вы получили **{rand}$** за работу💼")
		self.con.commit()

	@commands.command()
	async def pay(self, ctx, user: discord.Member, amount: int):
		with self.con.cursor() as cursor:
			cursor.execute("SELECT * FROM `UsersDB` WHERE `gid`=%s AND `uid`=%s", (ctx.guild.id, ctx.author.id))
			row = cursor.fetchone()
			if row is None:
				await ctx.send(f"👺Пользователь не найден")
			else:
				if amount > int(row[3]):
					embed = discord.Embed(description="👺У вас недостаточно денег на балансе")
					await ctx.send(embed=embed)
				else:
					cursor.execute(f"UPDATE `UsersDB` SET `balance`=balance-{amount} WHERE `gid`=%s AND `uid`=%s", (ctx.guild.id, ctx.author.id))
					cursor.execute(f"UPDATE `UsersDB` SET `balance`=balance+{amount} WHERE `gid`=%s AND `uid`=%s", (ctx.guild.id, user.id))
					embed = discord.Embed(description=f"Вы перевели {user.mention} **{amount}$**")
					await ctx.send(embed=embed)

	@commands.command()
	async def shop(self, ctx):
		embed = discord.Embed(title="Магазин ролей")
		embed.set_footer(text=".buy [ID товара]")
		with self.con.cursor() as cursor:
			cursor.execute("SELECT * FROM `ShopDB` WHERE `gid`=%s", (ctx.guild.id))
			rows = cursor.fetchall()
			for row in rows:
				embed.add_field (
					name=f"{row[3]} | ID: {row[0]}", 
					value=f"Цена: **{row[4]}**", 
					inline = False
					)
		await ctx.send(embed=embed)

	@commands.command(name="add-role")
	@commands.has_permissions(administrator=True)
	async def add_shop(self, ctx, role: discord.Role, cost: int, name):
		print("work")
		with self.con.cursor() as cursor:
			cursor.execute("SELECT * FROM `ShopDB` WHERE `gid`=%s AND `name`=%s", (ctx.guild.id, name))
			row = cursor.fetchone()
			if row is not None:
				embed = discord.Embed(description="Данный товар уже находиться в магазине")
				await ctx.send(embed=embed)
			else:
				cursor.execute("SELECT * FROM `ShopDB` WHERE `gid`=%s AND `rid`=%s", (ctx.guild.id, role.id))
				raw = cursor.fetchone()
				if raw is not None:
					embed = discord.Embed(description="Данный товар уже находиться в магазине")
					await ctx.send(embed=embed)
				else:
					cursor.execute(f"INSERT INTO `ShopDB` VALUES (NULL, '{ctx.guild.id}', '{role.id}', '{name}', '{cost}')")
					embed = discord.Embed(
						description=f"Роль {role.mention} успешно добавлена в магазин!\n"
						f"Название товара: **{name}**\n"
						f"Цена товара: **{cost}**"
						)
					await ctx.send(embed=embed)

	@commands.command(name="remove-role")
	@commands.has_permissions(administrator=True)
	async def remove_shop(self, ctx, id_r: int):
		with self.con.cursor() as cursor:
			cursor.execute("SELECT * FROM `ShopDB` WHERE `gid`=%s AND `id`=%s", (ctx.guild.id, id_r))
			row = cursor.fetchone()
			if row is None:
				embed = discord.Embed(description=f"Товар с ID **{id_r}** не найден в базе")
				await ctx.send(embed=embed)
			else:
				cursor.execute("DELETE FROM `ShopDB` WHERE `gid`=%s AND `id`=%s", (ctx.guild.id, id_r))
				embed = discord.Embed(description=f"Товар **{row[0]}** был успешно удалён")
				await ctx.send(embed=embed)

	@commands.command()
	async def buy(self, ctx, role: int):
		with self.con.cursor() as cursor:
			cursor.execute("SELECT * FROM `ShopDB` WHERE `gid`=%s AND `id`=%s", (ctx.guild.id, role))
			row = cursor.fetchone()
			cursor.execute("SELECT balance FROM `UsersDB` WHERE `gid`=%s AND `uid`=%s", (ctx.guild.id, ctx.author.id))
			bal = cursor.fetchone()[0]
			if row is None:
				await ctx.send(f"Роль: **{role}** не найдена!")
				return
			else:
				if int(bal) < int(row[4]):
					embed = discord.Embed(description="У вас недостаточно денег для покупки этой роли")
					await ctx.send(embed=embed)
				else:
					r = ctx.guild.get_role(int(row[2]))
					if r in ctx.author.roles:
						embed = discord.Embed(description="У вас уже есть данная роль")
						await ctx.send(embed=embed)
						return
					else:
						await ctx.author.add_roles(r)
						cursor.execute("UPDATE `UsersDB` SET `balance`=%s WHERE `gid`=%s AND `uid`=%s", (int(bal)-int(row[4]), ctx.guild.id, ctx.author.id))
						embed = discord.Embed(description=f"Вы успешно приобрели роль {r.mention} за **{row[4]}$**")
						await ctx.send(embed=embed)