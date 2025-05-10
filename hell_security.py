
from discord.ext import commands
from collections import defaultdict
from datetime import timedelta
from datetime import datetime
import discord
import asyncio
import time
import asyncio

intents = discord.Intents.default()
intents.message_content = True  
intents.members = True
bot = commands.Bot(command_prefix="!" , intents=intents)

token = "MTE1MzIzODcyNDg1MTgxMDMxNA.G4BkRT.0SoA_CB2idGKz1ePutrmg4WmOyJdrpjvWbtJHo"

last_checked = {}

async def get_log_channel(guild):
    """Get or create the logging channel"""
    category = discord.utils.get(guild.categories, name="L O G ⛩  H E L L")
    if not category:
        try:
            category = await guild.create_category("L O G ⛩  H E L L")
        except discord.Forbidden:
            return None
    
    channel = discord.utils.get(guild.text_channels, name="all_logs", category=category)
    if not channel:
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True)
            }
            channel = await guild.create_text_channel(
                "all_logs",
                category=category,
                overwrites=overwrites
            )
        except discord.Forbidden:
            return None
    
    return channel

async def get_audit_log_entry(guild, action, target=None):
    try:
        async for entry in guild.audit_logs(limit=5, action=action):
            if target is None or entry.target.id == target.id:
                return entry
        return None
    except:
        return None

async def setup_log_system():
    for guild in bot.guilds:
        await get_log_channel(guild)
        last_checked[guild.id] = datetime.utcnow()

@bot.event
async def on_member_ban(guild, user):
    entry = None
    async for log in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        entry = log
        break
    if entry and entry.user and entry.user != bot.user:
        if entry.user.name != 1137024054411407442:
            try:
                member = guild.get_member(entry.user.name)
                if member is None:
                    member = await guild.fetch_member(entry.user.name)
                if member.top_role < guild.me.top_role:
                    roles_to_remove = [r for r in member.roles if r != guild.default_role]
                    if roles_to_remove:
                        await member.remove_roles(*roles_to_remove, reason="Unauthorized ban")
                    await guild.kick(member, reason="Ban not allowed – Admin immunity bypassed.")
                    print(f"Kicked {member} for unauthorized ban")
                else:
                    print("User has higher or equal role to bot, skipping.")
            except Exception as e:
                print(f"Error handling unauthorized ban: {e}")

@bot.event
async def on_member_remove(member):
    async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        if entry.user and entry.user != bot.user:
            if entry.user.top_role < member.guild.me.top_role:
                try:
                    await member.guild.kick(entry.user, reason="H O M E  ⛩  H E L L Security iS HeRe [kick]")
                except Exception as e:
                    print(f"Failed to kick: {e}")

user_messages = defaultdict(list)
SPAM_TIMEFRAME = 9
SPAM_THRESHOLD = 9

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    stream_status = discord.Streaming(
        name="discord.gg/fars | H O M E  ⛩  H E L L",
        url="https://twitch.tv/homehell",
    )
    await bot.change_presence(activity=stream_status)
    await setup_log_system()

async def mute_user(guild, member):
    mute_role = discord.utils.get(guild.roles, name="Mute")
    if not mute_role:
        mute_role = await guild.create_role(name="Mute", reason="H O M E  ⛩  H E L L Security iS HeRe [spam]")
        for channel in guild.channels:
            try:
                await channel.set_permissions(mute_role, send_messages=False)
            except:
                pass
    try:
        await member.edit(roles=[])
    except discord.Forbidden:
        print(f"Cannot remove roles from {member}")

    await member.add_roles(mute_role, reason="Spamming")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    now = message.created_at.timestamp()
    user_id = message.author.id
    user_messages[user_id] = [msg_time for msg_time in user_messages[user_id] if now - msg_time < SPAM_TIMEFRAME]
    user_messages[user_id].append(now)

    if len(user_messages[user_id]) >= SPAM_THRESHOLD:
        await message.channel.send(f"{message.author.mention} دفه اخرته اسپم میدی - H O M E  ⛩  H E L L Security iS HeRe [spam?]")
        await mute_user(message.guild, message.author)
        user_messages[user_id] = []
    await bot.process_commands(message)
    
@bot.command(name='kick')
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="H O M E  ⛩  H E L L"):
    if ctx.author.id == 1137024054411407442:
        await member.kick(reason=reason)
        await ctx.send(f'- {member} `Kicked` | H O M E  ⛩  H E L L')
    else:
        await ctx.send(f"{ctx.author.id} H O M E  ⛩  H E L L Security iS HeRe | ByE ByE")
        try:
            if ctx.author.top_role < ctx.guild.me.top_role:
                roles_to_remove = [r for r in ctx.author.roles if r != ctx.guild.default_role]
                if roles_to_remove:
                    await ctx.author.remove_roles(*roles_to_remove, reason="Unauthorized kick command")
                await ctx.guild.kick(ctx.author, reason="Tried to use kick command without permission")
        except Exception as e:
            print(f"Error punishing unauthorized kick attempt: {e}")

@bot.command(name='ban')
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="H O M E  ⛩  H E L L"):
    if ctx.author.id == 1137024054411407442:
        await member.ban(reason=reason)
        await ctx.send(f'- {member} `Banned` | H O M E  ⛩  H E L L')
    else:
        await ctx.send(f"{ctx.author.id} H O M E  ⛩  H E L L Security iS HeRe | ByE ByE")
        try:
            if ctx.author.top_role < ctx.guild.me.top_role:
                roles_to_remove = [r for r in ctx.author.roles if r != ctx.guild.default_role]
                if roles_to_remove:
                    await ctx.author.remove_roles(*roles_to_remove, reason="Unauthorized ban command")
                await ctx.guild.kick(ctx.author, reason="Tried to use ban command without permission")
        except Exception as e:
            print(f"Error punishing unauthorized ban attempt: {e}")

    
@bot.command(name='jvc')
@commands.has_permissions(administrator=True)
async def jvc(ctx , guild_id , voice_channel_id):
    print(f'Logged in as {bot.user}')
    guild = bot.get_guild(int(guild_id))
    if guild:
        voice_channel = guild.get_channel(int(voice_channel_id))
        if voice_channel and isinstance(voice_channel, discord.VoiceChannel):
            await voice_channel.connect()
            print(f'Joined {voice_channel.name}')
            await ctx.send(f"Joined to -> : {voice_channel.name}")
        else:
            print('- Voice channel not found or invalid xD')
            await ctx.send("- Channel Not found xD")
    else:
        print('- Guild not found')
        await ctx.send("- Guild Not Found xD")

@bot.event
async def on_member_ban(guild, user):
    channel = await get_log_channel(guild)
    if channel:
        entry = await get_audit_log_entry(guild, discord.AuditLogAction.ban, user)
        moderator = entry.user.name if entry else "Unknown"
        reason = entry.reason if entry and entry.reason else "No reason provided"
        
        await channel.send(f"🔨 **Member Banned**\n"
                         f"• User: {user.name}\n"
                         f"• By: {moderator}\n"
                         f"• Reason: {reason}\n"
                         f"• At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

@bot.event
async def on_member_unban(guild, user):
    channel = await get_log_channel(guild)
    if channel:
        entry = await get_audit_log_entry(guild, discord.AuditLogAction.unban, user)
        moderator = entry.user.name if entry else "Unknown"
        
        await channel.send(f"🎗️ **Member Unbanned**\n"
                         f"• User: {user.name}\n"
                         f"• By: {moderator}\n"
                         f"• At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

@bot.event
async def on_member_update(before, after):
    channel = await get_log_channel(before.guild)
    if not channel:
        return
    if before.nick != after.nick:
        entry = await get_audit_log_entry(before.guild, discord.AuditLogAction.member_update, after)
        moderator = entry.user.name if entry else "Self"
        
        await channel.send(f"📝 **Nickname Changed**\n"
                         f"• User: {after.name}\n"
                         f"• By: {moderator}\n"
                         f"• Before: {before.nick or 'None'}\n"
                         f"• After: {after.nick or 'None'}\n"
                         f"• At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    if before.timed_out_until != after.timed_out_until:
        entry = await get_audit_log_entry(before.guild, discord.AuditLogAction.member_update, after)
        moderator = entry.user.name if entry else "System"
        
        if after.timed_out_until:
            await channel.send(f"⏳ **Member Timed Out**\n"
                             f"• User: {after.name}\n"
                             f"• By: {moderator}\n"
                             f"• Duration: Until {after.timed_out_until.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                             f"• Reason: {entry.reason if entry and entry.reason else 'No reason provided'}\n"
                             f"• At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        else:
            await channel.send(f"⏳ **Timeout Removed**\n"
                             f"• User: {after.name}\n"
                             f"• By: {moderator}\n"
                             f"• At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

@bot.event
async def on_voice_state_update(member, before, after):
    channel = await get_log_channel(member.guild)
    if not channel:
        return
    if not before.channel and after.channel:
        await channel.send(f"🎤 **Joined Voice**\n"
                         f"• User: {member.name}\n"
                         f"• Channel: {after.channel.mention}\n"
                         f"• At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    elif before.channel and not after.channel:
        await channel.send(f"🎤 **Left Voice**\n"
                         f"• User: {member.name}\n"
                         f"• Channel: {before.channel.mention}\n"
                         f"• At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

    elif before.channel and after.channel and before.channel != after.channel:
        entry = await get_audit_log_entry(member.guild, discord.AuditLogAction.member_move)
        if entry and entry.target.id == member.name:
            await channel.send(f"🎤 **Moved Between Voice Channels**\n"
                             f"• User: {member.name}\n"
                             f"• By: {entry.user.name}\n"
                             f"• From: {before.channel.mention}\n"
                             f"• To: {after.channel.mention}\n"
                             f"• Reason: {entry.reason or 'No reason provided'}\n"
                             f"• At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        else:
            await channel.send(f"🎤 **Switched Voice Channels**\n"
                             f"• User: {member.name}\n"
                             f"• From: {before.channel.mention}\n"
                             f"• To: {after.channel.mention}\n"
                             f"• At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

@bot.event
async def on_guild_channel_update(before, after):
    channel = await get_log_channel(after.guild)
    if not channel:
        return
    if before.name != after.name:
        entry = await get_audit_log_entry(after.guild, discord.AuditLogAction.channel_update, after)
        moderator = entry.user.name if entry else "Unknown"
        await channel.send(f"🏷️ **Channel Renamed**\n"
                         f"• Channel: {after.name}\n"
                         f"• By: {moderator}\n"
                         f"• Before: {before.name}\n"
                         f"• After: {after.name}\n"
                         f"• At: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_logs(ctx):
    await setup_log_system()
    await ctx.send("Log system Takmil shod")        

bot.run(token)