import discord
import random
from discord.ext import commands, tasks
import datetime, pymysql

def sql_connect(command):
    con = pymysql.connect(			 host='141.8.192.169',
                                     user= 'a0569226_xela1337',
                                     password='kravik228',
                                     db='a0569226_xela1337'
                                    )
    with con.cursor() as cursor:
        data = command.split('\n')
        if data[0] == '':
            del(data[0])
        for i in range(0, len(data)):
            cursor.execute(data[i])
        l = []
        for row in cursor:
            l.append(row)
        con.commit()
        con.close()
        return l

class other(commands.Cog):

	def __init__(self, bot, con):
		self.bot = bot
		self.con = con

	@commands.Cog.listener()
	async def on_member_join(self, member):
		roles = [819319460137533510,819319460137533510,819319460137533510]
		with self.con.cursor() as cursor:
			cursor.execute("SELECT * FROM `UsersDB` WHERE `gid`=%s AND `uid`=%s", (member.guild.id, member.id))
			if cursor.fetchone() is None:
				cursor.execute(f"INSERT INTO `UsersDB` VALUES (NULL, '{member.guild.id}', '{member.id}', '0')")
			for role in roles:
				await member.add_roles(member.guild.get_role(role))

	@commands.command()
	async def avatar(self, ctx, user: discord.Member = None):
		user = ctx.author if (user is None) else user
		embed = discord.Embed(title=f"Аватар {user.name}")
		embed.set_image(url=str(user.avatar_url))
		await ctx.send(embed=embed)

	@commands.command(
	aliases=['server', 'сервер', 'серверинфо'],
	description="Информация о сервере"
	)
	async def serverinfo(self, ctx):
		regions = {
			"russia": ":flag_ru: Россия",
			"europe": ":flag_eu: Европа"
			}
		region = regions[str(ctx.guild.region)]

		months = {
			"Jan": "Янв.",
			"Feb": "Февр.",
			"Mar": "Мар.",
			"Apr": "Апр.",
			"May": "Май",
			"June": "Июн.",
			"July": "Июл.",
			"Aug": "Авг.",
			"Sep": "Сент.",
			"Oct": "Октя.",
			"Nov": "Нояб.",
			"Dec": "Дек."
		}
		month = months[str(ctx.guild.created_at.strftime('%b'))]
		day = ctx.guild.created_at.strftime('%#d')
		year = ctx.guild.created_at.strftime('%Y')
		time = ctx.guild.created_at.strftime('%X')

		members = ctx.guild.members
		allusers = len(members)
		bots = len([m for m in members if m.bot])
		users = len(members) - bots
		online = len(list(filter(lambda x: x.status == discord.Status.online, members)))
		offline = len(list(filter(lambda x: x.status == discord.Status.offline, members)))
		idle = len(list(filter(lambda x: x.status == discord.Status.idle, members)))
		dnd = len(list(filter(lambda x: x.status == discord.Status.dnd, members)))
		allvoice = len(ctx.guild.voice_channels)
		alltext = len(ctx.guild.text_channels)
		allchannels = allvoice + alltext
		allroles = len(ctx.guild.roles)
	 
		embed = discord.Embed(title=f"{ctx.guild.name}", color=ctx.author.color, timestamp=ctx.message.created_at)
		embed.set_thumbnail(url=ctx.guild.icon_url)
	 
		embed.add_field(name=f"Пользователи", value=f"<:allusers:781849067524587540> Всего: **{allusers}**\n"
												f"<:users:781849067080253470> Участников: **{users}**\n"
												f"<:BOT:781849066790715393> Ботов: **{bots}**")

		embed.add_field(name=f"Статусы", value=f"<:online:781849066891247617> Онлайн: **{online}**\n"
												f"<:idle:781849067294031912> Отошёл: **{idle}**\n"
												f"<:dnd:781849067067932672> Не Беспокоить: **{dnd}**\n"
												f"<:offline:781849067029528586> Оффлайн: **{offline}**")
	 
		embed.add_field(name=f"Каналов", value=f"<:channels:781849066983129119> Всего: **{allchannels}**\n"
												f"<:voice:781849067059675146> Голосовые: **{allvoice}**\n"
												f"<:text:781849067294031882> Текстовые: **{alltext}**\n", inline=False)
	 
		embed.add_field(name=f"Создатель сервера", value=f"{ctx.guild.owner.mention}")
		embed.add_field(name=f"Регион сервера", value=region)
		embed.add_field(name=f"Дата создания сервера", value=f"{day} {month} {year}г. {time}")
		await ctx.send(embed=embed)

	@commands.command()
	async def user (self, ctx, user: discord.Member = None):
		user = ctx.author if (user is None) else user

		statuses = {
			"online": "<:online:781849066891247617> Онлайн",
			"idle": "<:idle:781849067294031912> Не активен",
			"dnd": "<:dnd:781849067067932672> Не беспокоить",
			"offline": "<:offline:781849067029528586> Не в cети",
		}

		j_month = user.joined_at.strftime('%b')
		j_day = user.joined_at.strftime('%#d')
		j_year = user.joined_at.strftime('%Y')
		j_time = user.joined_at.strftime('%X')

		c_month = user.created_at.strftime('%b')
		c_day = user.created_at.strftime('%#d')
		c_year = user.created_at.strftime('%Y')
		c_time = user.created_at.strftime('%X')

		status = statuses[str(user.status)]
		try:
			time_vc = str(sql_connect(f"""SELECT TimeVC FROM UsersDB WHERE uid = '{user.id}' """)[0][0])
			print(time_vc)
			embed = discord.Embed (
				title=f"Информация о {user.display_name}"
							"**Основная информация**\n"
							f"**Статус:** {status}\n"
							f"**Пользовательский статус:**\n"
							f"**Присоединился:** {j_day} {j_month} {j_year}г. {j_time}\n"
							f"**Дата регистрации:** {c_day} {c_month} {c_year}г. {c_time}\n"
							f"**Время VoiceChat:** {time_vc} секунд")
			embed.set_thumbnail(url = str(user.avatar_url))
			embed.set_footer(text = f"ID: {user.id}")
			await ctx.send (embed=embed)
		except Exception as e:
			print(e)