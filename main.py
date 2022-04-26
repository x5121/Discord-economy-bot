import discord
from discord.ext import commands, tasks
from discord_components import DiscordComponents, Button, ButtonStyle

import pymysql
import pymysql.cursors

#ИМПОРТ МОДУЛЕЙ
from cogs.mod import *
from cogs.economy import *
from cogs.other import *

# def get_prefix(bot, message):
# 	guild_id = message.guild.id
# 	with con.cursor() as cursor:
# 		cursor.execute("SELECT prefix FROM `ConfigDB` WHERE `gid`=%s", (guild_id))
# 		prefix = cursor.fetchone()
# 	con.commit()
# 	return prefix
bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

bot.remove_command("help")

overwrites = {}
sl = []

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

con = pymysql.connect(				 host='141.8.192.169',
                                     user= 'a0569226_xela1337',
                                     password='kravik228',
                                     db='a0569226_xela1337'
                                    )
@bot.event
async def on_ready():
	DiscordComponents(bot)
	with con.cursor() as cursor:
		guild = bot.get_guild(874960692392919090)
		for member in guild.members:
			cursor.execute("SELECT uid FROM `UsersDB` WHERE `uid`=%s AND `gid`=%s", (member.id, guild.id))
			if cursor.fetchone() is None:
				cursor.execute(f"INSERT INTO `UsersDB` VALUES (NULL, '{guild.id}', '{member.id}', '0')")
	con.commit()
	m_check.start()
	bot.add_cog(moderation(bot, con))
	bot.add_cog(economy(bot, con))
	bot.add_cog(other(bot, con))
	print("Xela Bot Ready")

@bot.command()
async def prefix (ctx, prefix):
	with con.cursor() as cursor:
		cursor.execute("UPDATE `ConfigDB` SET `prefix`=%s WHERE `gid`=%s", (prefix, ctx.guild.id))
	con.commit()
	embed = discord.Embed (description=f"Префикс сервера успешно изменён на: **`{prefix}`**")
	await ctx.send (embed=embed)

@tasks.loop(seconds=10)
async def m_check():
	date_now = int(datetime.datetime.now().timestamp())
	print(date_now)
	with con.cursor() as cursor:
		cursor.execute("SELECT * FROM `MutesDB`")
		mutes = cursor.fetchall()
		for row in mutes:
			cursor.execute("SELECT mute_role FROM `ConfigDB` WHERE `gid`=%s", (row[1]))
			role=cursor.fetchone()[0]
			print(role)
			guild = bot.get_guild (int(row[1]))
			mute_role = 	guild.get_role(int(role))
			un_time = int(row[4])
			if date_now >= un_time:
				try:
					await guild.get_member(int(row[2])).remove_roles(mute_role)
				except:
					pass
				cursor.execute("DELETE FROM `MutesDB` WHERE `id`=%s AND `gid`=%s", (row[0], row[1]))
		con.commit()
@bot.command()
async def createclan(ctx):
	global overwrites
	name_clan = ctx.message.content.replace('!createclan ', '')
	author_id = str(ctx.message.author.id)
	try:
		with con.cursor() as cursor:
			information_clan_uid = cursor.execute(f"""SELECT UserID FROM UsersClansDB WHERE UserID = '{author_id}'""")
			con.commit()
		if information_clan_uid == 0:
			with con.cursor() as cursor:
				cursor.execute((f"""INSERT INTO UsersClansDB VALUES ('{name_clan}', '{author_id}', True) """))
				con.commit()
			overwrites[ctx.guild.default_role] = discord.PermissionOverwrite(read_messages=False)
			guild = ctx.guild
			await guild.create_role(name=name_clan)
			role = discord.utils.get(guild.roles, name=name_clan)
			await ctx.author.add_roles(role)
			overwrites[role] = discord.PermissionOverwrite(read_messages=True)
			await ctx.guild.create_text_channel('Чат ' + name_clan, overwrites=overwrites)
			await ctx.guild.create_voice_channel('Канал для ' + name_clan, overwrites=overwrites)
			await ctx.send('Клан успешно был создан!')
		else:
			await ctx.send(f'Ты уже состоишь в клане!')
	except Exception as Error:
		print(Error)
@bot.command()
async def inviteclan(ctx):
	try:
		global overwrites
		new_member = ctx.message.content.replace('!inviteclan ', '').replace('<@', '').replace('>', '').replace('!', '')
		author_id = str(ctx.message.author.id)
		with con.cursor() as cursor:
			information_new_member = cursor.execute(f"""SELECT uid FROM UsersDB WHERE uid = '{new_member}' """)
			information_clan = cursor.execute(f"""SELECT admin FROM UsersClansDB WHERE UserID = '{new_member}'""")
			con.commit()
		if information_new_member == any(([], 0, None)):
			await ctx.send('Пользователь не найден!')
			return 0
		if information_clan == 0:
			await ctx.send(f'Вам поступило приглашение, об вступлении в клан <@{new_member}>')
			await ctx.send(
				embed=discord.Embed(title=f"Тебя пригласил в клан {ctx.message.author.name}"),
				components=[[
					Button(style=ButtonStyle.green, label='Вступить', emoji='✅'),
					Button(style=ButtonStyle.red, label='Отказаться', emoji='❌')
				]]
			)
			
			response = await bot.wait_for("button_click")
			if response.channel == ctx.channel:
				if int(response.author.id) == int(new_member):
					if response.component.label == 'Вступить':
						await response.respond(content="Вы успешно вступили в клан ✅")
						with con.cursor() as cursor:
							name_clan = sql_connect(f"""SELECT ClanName FROM UsersClansDB WHERE UserID = '{author_id}'""")[0][0]
							role = discord.utils.get(ctx.guild.roles, name=name_clan)
							user = get(bot.get_all_members(), id=int(new_member))
							await user.add_roles(role)
							cursor.execute((f"""INSERT INTO UsersClansDB VALUES ('{name_clan}', '{new_member}', False); """))
							con.commit()
							return
					if response.component.label == 'Отказаться':
						await response.respond(content="👺Вы отказались от вступления в клан.")
						return
		else:
			await ctx.send('Вы не являетесь создателем какого-либо клана.')
	except Exception as E:
		print(E)
@bot.event
async def on_voice_state_update(member, before, after):
    global start_time, sl
    try:
        if member.bot:
            return
        if before.channel is None and after.channel is not None:
            if after.channel.id:
                user_dict = {member.id : time.time()}
                sl.append(user_dict)
                await member.guild.system_channel.send(f'{member.name} зашёл на канал {after.channel.name}')
        if before.channel and not after.channel:
            ttotal_time=0
            for i in range(len(sl)):
                for id_user, t in sl[i].items():
                        if id_user == member.id:
                            end_time = time.time()
                            total_time = end_time - sl[i].get(member.id)
                            del(sl[i])
                            print(member.id)
                            a = sql_connect(f"""SELECT TimeVC FROM UsersDB where uid = '{member.id}'""")[0][0]
                            if a == None:
                                a = 0
                            ttotal_time = total_time + a
                            sql_connect((f"""UPDATE UsersDB SET TimeVC = {ttotal_time} where uid = {member.id};"""))
    except Exception as e:
        print(e)
bot.run ('ODc0OTYxNjI5MzkyMDE1NDAw.YROlhA.c6SwYRvGdk7xIZNzEUaw8fWVnX8')