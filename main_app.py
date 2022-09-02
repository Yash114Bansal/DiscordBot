import discord
from json import loads,dumps
from discord.utils import get
from settings import *
from datetime import datetime
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord.ext.commands import has_any_role

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
        print("Logged In as {0.user}".format(client))


# ----------------------------------------------------
slash=SlashCommand(client,sync_commands=True)

@slash.slash(name="send_message",
        description="Send Message to Channel",
        options=[
                create_option(
                        name="channel_name",
                        description="Channel In which Mention",
                        required=True,
                        option_type=7
                        ),
                create_option(
                        name="message_text",
                        description="Message",
                        required=True,
                        option_type=3
                        ),

        ]
)
@has_any_role(*Managers)
async def _Send_Message(ctx:SlashContext,channel_name,message_text):
        await channel_name.send(f"{message_text}")
        await ctx.send("Done")

# ----------------------------------------------------------

@slash.slash(name="send_user_message",
        description="Send Message to User",
        options=[
                create_option(
                        name="user_name",
                        description="User To Mention",
                        required=True,
                        option_type=6
                        ),
                create_option(
                        name="channel_name",
                        description="Channel In which Mention",
                        required=True,
                        option_type=7
                        ),
                create_option(
                        name="message_text",
                        description="Message",
                        required=True,
                        option_type=3
                        ),
                
        ]
)
@has_any_role(*Managers)
async def _Send_User_Message(ctx:SlashContext,user_name,channel_name,message_text):
        await channel_name.send(f"{user_name.mention} {message_text}")
        await ctx.send("Done")

# ----------------------------------------------------


@slash.slash(name="send_message_dm",
        description="Send Message to User",
        options=[
                create_option(
                        name="user_name",
                        description="User To DM",
                        required=True,
                        option_type=6
                        ),
                create_option(
                        name="message_text",
                        description="Message",
                        required=True,
                        option_type=3
                        ),

        ]
)
@has_any_role(*Managers)
async def _Send_Message_dm(ctx:SlashContext,user_name,message_text):
        await user_name.send(f"{message_text}")
        
        guild=client.get_guild(server_id)
        channel_dm= guild.get_channel(dm_logs_channel)
        embed_reply = discord.Embed(title="Successfully DM'ed", description=message_text, color=discord.Color.red())
        embed_reply.set_author(name=user_name.display_name,icon_url=user_name.avatar_url)
        await ctx.send(embeds=[embed_reply])




# ------------------------------------------------------------------------------
@client.event
async def on_member_update(before, after):
        guild = client.get_guild(server_id)
        role_logs = guild.get_channel(role_logs_channel)

        if len(before.roles) < len(after.roles):
                newRole = [role for role in after.roles if role not in before.roles]
                embed_change_role = discord.Embed(title="Roles Changed", description=f'{before.name} Added Role **{newRole[0].name}**', color=discord.Color.green()) 
                embed_change_role.set_author(name=before.display_name,icon_url=before.avatar_url)
                await role_logs.send(embed=embed_change_role)
                return
        elif len(before.roles) > len(after.roles):
                oldRole = [role for role in before.roles if role not in after.roles]
                embed_change_role = discord.Embed(title="Roles Changed", description=f'{before.name} Removed Role **{oldRole[0].name}**', color=discord.Color.red()) 
                embed_change_role.set_author(name=before.display_name,icon_url=before.avatar_url)
                await role_logs.send(embed=embed_change_role)
                return


@client.event
async def on_member_join(member):
        guild = client.get_guild(server_id)
        join_log = guild.get_channel(join_logs_channel)
        embed_join = discord.Embed(title="Joined Server", description=f'{member.name} joined Geek Reborn', color=discord.Color.green()) 
        embed_join.set_author(name=member.display_name,icon_url=member.avatar_url)
        await join_log.send(embed=embed_join)
        if member.id in Managers:
                role = get(member.guild.roles, name=Admin_Role)
                await member.add_roles(role)
                role = get(member.guild.roles, name=Geek_Role)
                await member.add_roles(role)
        else:
                role = get(member.guild.roles, name=New_Member_Role)
                await member.add_roles(role)


@client.event
async def on_member_remove(member):
        guild = client.get_guild(server_id)
        leave_log = guild.get_channel(leave_logs_channel)
        embed_leave = discord.Embed(title="Left Server", description=f'{member.name} Left Geek Reborn', color=discord.Color.red()) 
        embed_leave.set_author(name=member.display_name,icon_url=member.avatar_url)
        await leave_log.send(embed=embed_leave)

@client.event
async def on_voice_state_update(member, before, after):
        role = get(member.guild.roles, name=In_VC_Role_name)
        guild=client.get_guild(server_id)
        vc_logs = guild.get_channel(vc_logs_channel)


        # If Someone joins
        if not before.channel and after.channel:
                await member.add_roles(role)
                embed3=discord.Embed(title="Joined VC", description=f'{member.name} joined {after.channel.name} at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', color=discord.Color.green()) 
                embed3.set_author(name=member.display_name,icon_url=member.avatar_url)
                await vc_logs.send(embed=embed3)

        # If Someone Leaves

        if not after.channel and before.channel:
                embed3=discord.Embed(title="Left VC", description=f'{member.name} Left {before.channel.name} at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', color=discord.Color.red())
                embed3.set_author(name=member.display_name,icon_url=member.avatar_url)
                await vc_logs.send(embed=embed3)
                await member.remove_roles(role)

        # Streams

        if after.self_stream and not before.self_stream:

                # If Someone starts Stream

                embed3=discord.Embed(title="Started Stream", description=f'{member.name} started stream in {before.channel.name} at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', color=discord.Color.green())
                embed3.set_author(name=member.display_name,icon_url=member.avatar_url)
                await vc_logs.send(embed=embed3)

        if before.self_stream and not after.self_stream:
                # If Someone Stops stream

                embed3=discord.Embed(title="Stoped Stream", description=f'{member.name} stoped stream in {before.channel.name} at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}', color=discord.Color.red())
                embed3.set_author(name=member.display_name,icon_url=member.avatar_url)
                await vc_logs.send(embed=embed3)

@client.event
async def on_message_delete(message):
        if "logs" in str(message.channel.name):
                return
        guild=client.get_guild(server_id)
        message_logs = guild.get_channel(message_logs_channel)

        embed_delete=discord.Embed(title=f"Message Deleted", description=f'``` {message.content}``` from {message.channel.name}', color=0x7d2500)
        embed_delete.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
        await message_logs.send(embed=embed_delete)

@client.event
async def on_message_edit(before, after):
        guild=client.get_guild(server_id)
        message_logs = guild.get_channel(message_logs_channel)
        warning_logs=guild.get_channel(warning_logs_channel)

        if before.content.lower() == after.content.lower():
                return
        embed_edit=discord.Embed(title=f"Message Edited", description=f'{before.author.name} Edited ``` {before.content}``` to ```{after.content}``` in {after.channel.name}', color=0xa1a106)
        embed_edit.set_author(name=before.author.display_name,icon_url=before.author.avatar_url)
        await message_logs.send(embed=embed_edit)

        #Checking For bad Words
        message=after
        t=str(message.content.lower()).split(" ")
        for i in t:
                if i.strip() in bad_words:
                        try:
                                embed_warning=discord.Embed(title="Warning", description=f'{message.author.name} Warned for using `{message.content}`', color=0x8f0101)
                                embed_warning.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
                                await warning_logs.send(embed=embed_warning)
                                await message.delete()
                                embed_public=discord.Embed(title=f"{message.author.name} Has been warned", description=f'{message.author.name} You have been warned Please Dont use these words', color=0x8f0101)
                                embed_public.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
                                await message.channel.send(f"{message.author.mention}",embed=embed_public)
                                await message.author.send(f"You are Warned For Using `{i}` Please dont use bad words !!")
                                return
                        except Exception as e:
                                print(e)

@client.event
async def on_message(message):


        if message.author == client.user:
                return

        # For Private Chat
        if message.channel.type == discord.ChannelType.private:
                guild=client.get_guild(server_id)
                channel_respect = guild.get_channel(respect_logs)
                channel_dm= guild.get_channel(dm_logs_channel)
                warning_logs=guild.get_channel(warning_logs_channel)

                links=""
                for attach in message.attachments:
                        links+=attach.url + " "
                embed_dm=discord.Embed(title="DM", description=f"{message.author.name} DM'ed me `{message.content}` {links}", color=0x5300a1)
                embed_dm.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
                await channel_dm.send(embed=embed_dm)
                t=str(message.content.lower()).split(" ")
                for i in t:
                        if i.strip() in bad_words:
                                try:
                                        embed_warning=discord.Embed(title="Warning", description=f'{message.author.name} Warned for using `{message.content}` In DM', color=0x8f0101)
                                        embed_warning.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
                                        await warning_logs.send(embed=embed_warning)
                                        await message.delete()
                                        embed_public=discord.Embed(title=f"{message.author.name} Has been warned", description=f'{message.author.name} You have been warned for using {i} Please Dont use these words', color=0x8f0101)
                                        embed_public.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
                                        await message.channel.send(f"{message.author.mention}",embed=embed_public)
                                        return
                                except Exception as e:
                                        print(e)


                message_words = [i.strip() for i in message.content.lower().split(" ")]
                if "what" in message_words and "up" in message_words:
                                await message.channel.send(f"Nothing much what about you {message.author.mention} ?")
                                return

                if "welcome" in message_words:
                                await message.reply(f"Thank You so much {message.author.name}")
                                return

                if "hello" in message_words:
                                await message.reply(f"Hey {message.author.name} how are you?")
                                return

                if "fine" in message_words:
                                await message.reply(f"cool")
                                return

                if "hi" in message_words:
                                await message.reply(f"Hi {message.author.name}")
                                return

                if message.content.lower() =="<@914421016766324776>" or message.content.lower()=="<@!914421016766324776>":
                                if message.author.id in Managers:
                                        await message.reply(f"Hello {message.author.name} Sir")
                                else:
                                        await message.reply(f"Hello {message.author.name}")
                return


        #Common information
        guild=client.get_guild(server_id)
        channel_respect = guild.get_channel(respect_logs)
        warning_logs=guild.get_channel(warning_logs_channel)    

        t=str(message.content.lower()).split(" ")
        for i in t:
                if i.strip() in bad_words:
                        try:
                                
                                embed_warning=discord.Embed(title="Warning", description=f'{message.author.name} Warned for using `{message.content}`', color=0x8f0101)
                                embed_warning.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
                                await warning_logs.send(embed=embed_warning)
                                await message.delete()
                                embed_public=discord.Embed(title=f"{message.author.name} Has been warned", description=f'{message.author.name} You have been warned Please Dont use these words', color=0x8f0101)
                                embed_public.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
                                await message.channel.send(f"{message.author.mention}",embed=embed_public)
                                await message.author.send(f"You are Warned For Using `{i}` Please dont use bad words")
                        except Exception as e:
                                print(e)

        # If It is Mentioned in
        if client.user.mentioned_in(message):

                message_words = [i.strip() for i in message.content.lower().split(" ")]
                if ("what" in message_words or "whats" in message_words) and "up" in message_words:
                        await message.channel.send(f"Nothing much what about you {message.author.mention} ?")
                        return

                if "welcome" in message_words:
                        await message.reply(f"Thank You so much {message.author.name}")
                        return

                if "hello" in message_words:
                        await message.reply(f"Hey {message.author.name} how are you?")
                        return

                if "fine" in message_words:
                        await message.reply(f"cool")
                        return

                if "hi" in message_words:
                        await message.reply(f"Hi {message.author.name}")
                        return

                if message.content.lower() =="<@914421016766324776>" or message.content.lower()=="<@!914421016766324776>": #Id of Bot
                        if int(message.author.id) in Managers:
                                await message.reply(f"Hello {message.author.name} Sir")
                        else:
                                await message.reply(f"Hello {message.author.name}")

        if message.mentions and "thank" in message.content.lower():
                for i in message.mentions:
                        with open("respect.json","r") as j:
                                if i == message.author or i == client.user:
                                        continue
                                respect_dict=loads(j.read())
                                if i.name in respect_dict:
                                        c=respect_dict[str(i.name)]
                                        c=str(int(c)+1)
                                        respect_dict[str(i.name)]=c
                                else:
                                        respect_dict[str(i.name)]='1'
                        with open("respect.json","w") as j:
                                j.write(dumps(respect_dict))
                        await message.channel.send(f" Respect ++{i.mention}")

                        #Sending embed

                        embed1=discord.Embed(title="Respect", description=f"{i.name} got 1 respect from {message.author.name}", color=discord.Color.blue()) 
                        embed1.set_author(name=i.display_name,icon_url=i.avatar_url)
                        await channel_respect.send(embed=embed1)
                        return

        #Checking If Message contain -respect
        if message.content.lower().strip()=="-respect":
                for rol in message.author.roles:
                        if rol.name in ["Contributer","Moderator","Representative"]:
                                with open("respect.json") as j:
                                        respect_dict=loads(j.read())

                                embed2=discord.Embed(title="Respect", description=f"", color=0xfc03ca) 
                                embed2.set_author(name=message.author.display_name,icon_url=message.author.avatar_url)
                                for i in respect_dict:
                                        embed2.add_field(name=f"{i} :", value=respect_dict[i], inline=True)

                                await message.channel.send(embed=embed2)
                        else:
                                await message.reply("You Dont Have Permission to use That")

client.run(bot_token)
