import discord
from discord.ext import commands
import asyncio

import os

TOKEN = os.getenv("TOKEN")
MAIN_SERVER_ID = int(os.getenv("MAIN_SERVER_ID"))
AUDIT_SERVER_ID = int(os.getenv("AUDIT_SERVER_ID"))


# Audit Log Categories Mapping
CATEGORY_MAPPING = {
    discord.AuditLogAction.ban: "bans-kicks",
    discord.AuditLogAction.unban: "bans-kicks",
    discord.AuditLogAction.kick: "bans-kicks",
    discord.AuditLogAction.message_delete: "message-deletes",
    discord.AuditLogAction.member_update: "role-changes",
    discord.AuditLogAction.channel_create: "channel-create-delete",
    discord.AuditLogAction.channel_delete: "channel-create-delete",
    discord.AuditLogAction.channel_update: "channel-updates",
    discord.AuditLogAction.guild_update: "server-settings-changes"
}

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.guild_messages = True
intents.message_content = True
intents.presences = True
intents.guild_scheduled_events = True
intents.moderation = True

bot = commands.Bot(command_prefix="!", intents=intents)

def get_audit_channel(guild, action_type):
    """Get the corresponding audit log channel in the audit server."""
    category_name = CATEGORY_MAPPING.get(action_type, "other-logs")
    for channel in guild.text_channels:
        if channel.name == category_name:
            return channel
    return None

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_audit_log_entry_create(entry):
    """Capture new audit log entries and send to the audit log server."""
    main_guild = bot.get_guild(MAIN_SERVER_ID)
    audit_guild = bot.get_guild(AUDIT_SERVER_ID)
    if not main_guild or not audit_guild:
        return

    log_channel = get_audit_channel(audit_guild, entry.action)
    if log_channel:
        embed = discord.Embed(title=f"Audit Log: {entry.action.name}", color=discord.Color.red())
        embed.add_field(name="User", value=entry.user, inline=True)
        embed.add_field(name="Target", value=entry.target, inline=True)
        embed.add_field(name="Reason", value=entry.reason or "No reason provided", inline=False)
        embed.timestamp = entry.created_at
        await log_channel.send(embed=embed)

bot.run(TOKEN)
