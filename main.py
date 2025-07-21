import discord
from discord.ext import commands
import os
import logging
import asyncio
from datetime import datetime
import threading
from web_server import run_web_server
from config import COLORS, EMOJIS, get_server_config
from utils.database import initialize_database
import signal

# Configure logging with better formatting
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for different log levels."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Color the level name
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        # Shorten logger names for cleaner output
        name_mapping = {
            '__main__': '🧀 PLAGG',
            'discord.client': '🤖 DISCORD',
            'discord.gateway': '🌐 GATEWAY',
            'web_server': '🌍 SERVER',
            'utils.database': '💾 DATABASE'
        }
        
        # Use shorter name if available
        if record.name in name_mapping:
            record.name = name_mapping[record.name]
        elif record.name.startswith('cogs.'):
            # Format cog names nicely
            cog_name = record.name.replace('cogs.', '').upper()
            record.name = f"⚡ {cog_name}"
        
        return super().format(record)

# Create formatters
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
console_formatter = ColoredFormatter(
    '%(asctime)s | %(name)-12s | %(levelname)-7s | %(message)s',
    datefmt='%H:%M:%S'
)

# Configure handlers
file_handler = logging.FileHandler('bot.log')
file_handler.setFormatter(file_formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(console_formatter)

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler, console_handler]
)
logger = logging.getLogger(__name__)

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix='$',
    intents=intents,
    help_command=None,  # We'll implement our own
    case_insensitive=True,
    owner_id=1297013439125917766  # NoNameP_P's user ID
)

async def send_startup_message():
    """Send startup message to all guilds."""
    startup_embed = discord.Embed(
        title="🧀 Plagg Has Awakened!",
        description=(
            "**The Kwami of Destruction is back online!**\n\n"
            "✨ **Ready to serve:**\n"
            "• AI Chatbot powered by Google Gemini\n"
            "• Complete RPG system with adventures\n"
            "• Economy and trading features\n"
            "• Moderation tools\n\n"
            "Type `$help` to get started or mention me to chat!"
        ),
        color=COLORS['success'],
        timestamp=datetime.now()
    )
    startup_embed.set_thumbnail(url=bot.user.display_avatar.url if bot.user else None)
    startup_embed.set_footer(text="Plagg - Kwami of Destruction | Bot Online")

    for guild in bot.guilds:
        try:
            # Try to find a suitable channel
            channel = None
            
            # Look for bot-specific channels first
            for ch in guild.text_channels:
                if any(term in ch.name.lower() for term in ['bot', 'general', 'announcements', 'status']):
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
            
            # If no suitable channel found, try the first channel we can send to
            if not channel:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
            
            if channel:
                await channel.send(embed=startup_embed)
                logger.info(f"Sent startup message to {guild.name} in #{channel.name}")
            else:
                logger.warning(f"No suitable channel found in {guild.name} for startup message")
                
        except Exception as e:
            logger.error(f"Failed to send startup message to {guild.name}: {e}")

async def send_shutdown_message():
    """Send shutdown message to all guilds."""
    shutdown_embed = discord.Embed(
        title="🧀 Plagg is Going to Sleep...",
        description=(
            "**The Kwami of Destruction is going offline.**\n\n"
            "⚠️ **Services temporarily unavailable:**\n"
            "• AI Chatbot responses\n"
            "• RPG adventures and battles\n"
            "• Economy and trading\n"
            "• All bot commands\n\n"
            "Don't worry, I'll be back soon! 💤"
        ),
        color=COLORS['warning'],
        timestamp=datetime.now()
    )
    shutdown_embed.set_thumbnail(url=bot.user.display_avatar.url if bot.user else None)
    shutdown_embed.set_footer(text="Plagg - Kwami of Destruction | Bot Offline")

    for guild in bot.guilds:
        try:
            # Try to find a suitable channel
            channel = None
            
            # Look for bot-specific channels first
            for ch in guild.text_channels:
                if any(term in ch.name.lower() for term in ['bot', 'general', 'announcements', 'status']):
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
            
            # If no suitable channel found, try the first channel we can send to
            if not channel:
                for ch in guild.text_channels:
                    if ch.permissions_for(guild.me).send_messages:
                        channel = ch
                        break
            
            if channel:
                await channel.send(embed=shutdown_embed)
                logger.info(f"Sent shutdown message to {guild.name} in #{channel.name}")
            else:
                logger.warning(f"No suitable channel found in {guild.name} for shutdown message")
                
        except Exception as e:
            logger.error(f"Failed to send shutdown message to {guild.name}: {e}")

async def graceful_shutdown():
    """Handle graceful shutdown with notifications."""
    logger.info("Initiating graceful shutdown...")
    
    try:
        # Send shutdown messages
        await send_shutdown_message()
        
        # Wait a moment for messages to send
        await asyncio.sleep(2)
        
        # Close bot connection
        await bot.close()
        logger.info("Bot shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    asyncio.create_task(graceful_shutdown())

@bot.event
async def on_ready():
    """Called when the bot is ready."""
    # Startup banner
    print("\n" + "="*60)
    print("🧀 PLAGG - KWAMI OF DESTRUCTION BOT")
    print("="*60)
    print(f"✅ Bot User: {bot.user.name}#{bot.user.discriminator}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"🏰 Connected to {len(bot.guilds)} guilds")
    print(f"👥 Serving {sum(guild.member_count for guild in bot.guilds)} users")
    print("="*60 + "\n")
    
    logger.info("🧀 Plagg (Kwami of Destruction) has awakened!")
    logger.info(f"🏰 Causing chaos in {len(bot.guilds)} guilds")

    # Initialize database
    try:
        await initialize_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    # Add persistent views - none needed currently
    pass

    # Set bot status
    try:
        await bot.change_presence(
            activity=discord.Game(name="AI Chat & RPG Adventures | $help")
        )
    except Exception as e:
        logger.error(f"Error setting bot presence: {e}")

    # Send startup message to guilds
    await send_startup_message()

@bot.event
async def on_guild_join(guild):
    """Called when the bot joins a new guild."""
    logger.info(f"Joined new guild: {guild.name} ({guild.id})")

    # Try to send welcome message
    try:
        # Find a suitable channel to send welcome message
        channel = None

        # Try to find general or welcome channel
        for ch in guild.text_channels:
            if ch.name.lower() in ['general', 'welcome', 'bot-commands']:
                if ch.permissions_for(guild.me).send_messages:
                    channel = ch
                    break

        # If no suitable channel found, try the first channel we can send to
        if not channel:
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    channel = ch
                    break

        if channel:
            embed = discord.Embed(
                title="🧀 Thanks for adding Plagg - AI Chatbot!",
                description=(
                    "I'm Plagg, your AI companion with gaming features!\n\n"
                    "**🤖 Main Feature - AI Chat:**\n"
                    "• Advanced AI chatbot powered by Google Gemini\n"
                    "• Natural conversations with Plagg's personality\n"
                    "• Context-aware responses and memory\n"
                    "• Just mention me or reply to chat!\n\n"
                    "**🎮 Bonus Features:**\n"
                    "• Complete RPG system with adventures and battles\n"
                    "• Moderation and admin tools\n\n"
                    "**🚀 Getting Started:**\n"
                    "Mention me `@Plagg` to start chatting!\n"
                    "Use `$help` for all commands\n"
                    "Use `$start` for RPG features\n\n"
                    "**Credits:** Created by NoNameP_P"
                ),
                color=COLORS['success']
            )
            embed.set_thumbnail(url=bot.user.display_avatar.url)
            embed.set_footer(text="Plagg AI Chatbot | Made by NoNameP_P | Ready to chat!")

            await channel.send(embed=embed)
    except Exception as e:
        logger.error(f"Error sending welcome message to {guild.name}: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Global error handler for commands."""
    if isinstance(error, commands.CommandNotFound):
        # Don't respond to unknown commands
        return

    elif isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title="❌ Missing Permissions",
            description="You don't have the required permissions to use this command.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BotMissingPermissions):
        embed = discord.Embed(
            title="❌ Bot Missing Permissions",
            description="I don't have the required permissions to execute this command.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(
            title="⏰ Command on Cooldown",
            description=f"This command is on cooldown. Try again in {error.retry_after:.1f} seconds.",
            color=COLORS['warning']
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="❌ Missing Required Argument",
            description=f"Missing required argument: `{error.param.name}`\n\nUse `$help {ctx.command.name}` for more info.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="❌ Invalid Argument",
            description=f"Invalid argument provided. Use `$help {ctx.command.name}` for correct usage.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)

    else:
        logger.error(f"Unhandled error in command {ctx.command}: {error}")
        embed = discord.Embed(
            title="❌ An Error Occurred",
            description="An unexpected error occurred. Please try again later.",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)

@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler for events."""
    logger.error(f"Error in event {event}: {args}")

async def load_cogs():
    """Load all cogs."""
    # Load cogs
    initial_extensions = [
        'cogs.admin',
        'cogs.ai_chatbot', 
        'cogs.economy',
        'cogs.help',
        'cogs.moderation',
        'cogs.rpg_core',
        'cogs.rpg_games',
        'cogs.rpg_combat',
        'cogs.rpg_dungeons',
        'cogs.rpg_shop'
    ]

    loaded_count = 0
    failed_count = 0

    for cog in initial_extensions:
        try:
            await bot.load_extension(cog)
            cog_name = cog.replace('cogs.', '').upper()
            logger.info(f"✅ {cog_name} module loaded successfully")
            loaded_count += 1
        except Exception as e:
            cog_name = cog.replace('cogs.', '').upper()
            logger.error(f"❌ {cog_name} module failed: {e}")
            failed_count += 1
    
    # Summary
    logger.info(f"📊 Module Summary: {loaded_count} loaded, {failed_count} failed")

async def main():
    """Main function to run the bot."""
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start web server in a separate thread
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # Load cogs
    await load_cogs()

    # Get token from environment
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        return

    # Run the bot
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested via KeyboardInterrupt")
        await send_shutdown_message()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        await send_shutdown_message()
    finally:
        try:
            if not bot.is_closed():
                await bot.close()
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())