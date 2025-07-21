import discord
from discord.ext import commands
from config import COLORS, is_module_enabled
import asyncio

class HelpCategoryView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot

        # Create dropdown with categories
        category_options = [
            discord.SelectOption(
                label="📊 Core Commands",
                value="core",
                description="Character creation, profile, and basic commands"
            ),
            discord.SelectOption(
                label="⚔️ Combat System",
                value="combat",
                description="Tactical combat, battles, and PvP arena"
            ),
            discord.SelectOption(
                label="🎒 Character Building",
                value="character",
                description="Stats, skills, equipment, and progression"
            ),
            discord.SelectOption(
                label="🏰 Dungeons & PvE",
                value="dungeons",
                description="Dungeon exploration and monster hunting"
            ),
            discord.SelectOption(
                label="🛒 Economy & Crafting",
                value="economy",
                description="Shop, crafting, trading, and resources"
            ),
            discord.SelectOption(
                label="👥 PvP & Factions",
                value="pvp",
                description="Arena battles, factions, and competitive play"
            ),
            discord.SelectOption(
                label="🔧 Admin & Moderation",
                value="admin",
                description="Administrative commands and bot management"
            )
        ]

        self.category_select = discord.ui.Select(
            placeholder="Choose a help category...",
            options=category_options,
            custom_id="help_category_select"
        )
        self.category_select.callback = self.category_callback
        self.add_item(self.category_select)

    async def category_callback(self, interaction: discord.Interaction):
        category = interaction.data['values'][0]
        embed = self.create_category_embed(category)
        await interaction.response.edit_message(embed=embed, view=self)

    def create_category_embed(self, category):
        if category == "core":
            embed = discord.Embed(
                title="📊 Core Commands",
                description="Essential commands to start your journey as a combatant:",
                color=COLORS['primary']
            )
            embed.add_field(
                name="Getting Started",
                value="`$startrpg` - Create your character and begin\n"
                      "`$profile [@user]` - View character stats and progress\n"
                      "`$classes` - View all available character classes\n"
                      "`$choose <class>` - Select your combat class",
                inline=False
            )
            embed.add_field(
                name="Character Management",
                value="`$allocate <stat> <points>` - Distribute stat points\n"
                      "`$skills` - View your combat abilities\n"
                      "`$inventory` - Manage your gear and items\n"
                      "`$equip <item>` - Equip weapons and armor",
                inline=False
            )

        elif category == "combat":
            embed = discord.Embed(
                title="⚔️ Combat System",
                description="Master the tactical combat engine - the heart of Project: Blood & Cheese:",
                color=COLORS['error']
            )
            embed.add_field(
                name="PvE Combat",
                value="`$battle [monster]` - Enter tactical combat\n"
                      "`$hunt` - Find monsters to fight\n"
                      "`$techniques` - View pre-combat techniques\n"
                      "`$miraculous` - Enter Miraculous Box dungeon",
                inline=False
            )
            embed.add_field(
                name="Combat Mechanics",
                value="**Skill Points (SP):** Generate with Basic Attacks, spend on Skills\n"
                      "**Ultimate Energy:** Build up to unleash devastating abilities\n"
                      "**Weakness Break:** Hit enemy weaknesses to stun them\n"
                      "**Follow-ups:** Chain attacks for bonus damage",
                inline=False
            )

        elif category == "character":
            embed = discord.Embed(
                title="🎒 Character Building",
                description="Forge your path to becoming a legendary combatant:",
                color=COLORS['secondary']
            )
            embed.add_field(
                name="Stats & Progression",
                value="`$allocate <stat> <points>` - Distribute stat points\n"
                      "`$path` - Choose your Miraculous Path (Lv20+)\n"
                      "`$respec` - Reset your stat allocation\n"
                      "`$artifacts` - Manage Kwami Artifacts",
                inline=False
            )
            embed.add_field(
                name="Combat Stats",
                value="**STR:** Physical damage & stamina\n"
                      "**DEX:** Crit chance, dodge, initiative\n"
                      "**CON:** Max HP & damage reduction\n"
                      "**INT:** Magical damage & max mana\n"
                      "**WIS:** Healing power & mana regen\n"
                      "**CHA:** Better shop prices & quest rewards",
                inline=False
            )

        elif category == "dungeons":
            embed = discord.Embed(
                title="🏰 Dungeons & PvE",
                description="Hunt monsters and explore dangerous territories for power:",
                color=COLORS['warning']
            )
            embed.add_field(
                name="Exploration",
                value="`$dungeon <name>` - Enter a dungeon\n"
                      "`$hunt` - Find monsters in the wild\n"
                      "`$explore` - Discover new locations\n"
                      "`$bosses` - View available boss fights",
                inline=False
            )
            embed.add_field(
                name="Special Dungeons",
                value="`$miraculous` - Miraculous Box (Artifact farming)\n"
                      "`$contested` - Enter contested PvP zones\n"
                      "`$raid` - Join group raids (coming soon)",
                inline=False
            )

        elif category == "economy":
            embed = discord.Embed(
                title="🛒 Economy & Crafting",
                description="Gather resources and forge legendary equipment:",
                color=COLORS['success']
            )
            embed.add_field(
                name="Shopping & Trading",
                value="`$shop [category]` - Browse items for purchase\n"
                      "`$sell <item>` - Sell items for gold\n"
                      "`$trade @user` - Trade with other players\n"
                      "`$market` - View player marketplace",
                inline=False
            )
            embed.add_field(
                name="Crafting System",
                value="`$craft <recipe>` - Forge equipment\n"
                      "`$recipes` - View known crafting recipes\n"
                      "`$materials` - Check crafting materials\n"
                      "`$forge` - Access the crafting interface",
                inline=False
            )

        elif category == "pvp":
            embed = discord.Embed(
                title="👥 PvP & Factions",
                description="Prove your combat mastery against other players:",
                color=COLORS['error']
            )
            embed.add_field(
                name="Arena Combat",
                value="`$arena` - Enter ranked PvP queue\n"
                      "`$duel @user` - Challenge someone to combat\n"
                      "`$ranking` - View Arena leaderboards\n"
                      "`$gladiator` - Gladiator Token shop",
                inline=False
            )
            embed.add_field(
                name="Faction Warfare",
                value="`$faction <name>` - Join a faction (Lv20+)\n"
                      "`$war` - View faction war status\n"
                      "`$bounty` - View active bounties\n"
                      "`$territory` - Check contested zones",
                inline=False
            )

        elif category == "admin":
            embed = discord.Embed(
                title="🔧 Admin & Moderation",
                description="Server management and bot administration:",
                color=COLORS['info']
            )
            embed.add_field(
                name="Bot Management",
                value="`$modules` - Enable/disable bot modules\n"
                      "`$prefix <new>` - Change command prefix\n"
                      "`$settings` - View server settings\n"
                      "`$reset @user` - Reset user data",
                inline=False
            )
            embed.add_field(
                name="RPG Management",
                value="`$giveitem @user <item>` - Give items to players\n"
                      "`$setlevel @user <level>` - Set player level\n"
                      "`$spawn <monster>` - Spawn monsters\n"
                      "`$event` - Start server events",
                inline=False
            )

        else:
            embed = discord.Embed(
                title="📚 Project: Blood & Cheese Help",
                description="Welcome to the ultimate combat-focused RPG! Choose a category to learn more:",
                color=COLORS['primary']
            )
            embed.add_field(
                name="🎯 Combat is King",
                value="Every system in this game revolves around making you a better fighter. "
                      "Train, craft, and battle your way to legendary status!",
                inline=False
            )

        embed.set_footer(text="Select a category above to view detailed commands")
        return embed

class HelpCog(commands.Cog):
    """Comprehensive help system with categorized commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["h", "commands"])
    async def help_command(self, ctx):
        """Display the interactive help menu."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        view = HelpCategoryView(self.bot)
        embed = discord.Embed(
            title="📚 Project: Blood & Cheese - Combat RPG Help",
            description="**Welcome to the ultimate combat-focused RPG experience!**\n\n"
                       "🎯 **Core Philosophy:** Combat is King! Every feature serves to make you a more powerful warrior.\n\n"
                       "🌟 **Your Journey:**\n"
                       "• Create your character and choose a combat class\n"
                       "• Master the tactical combat system\n"
                       "• Hunt monsters for resources and power\n"
                       "• Craft legendary equipment\n"
                       "• Dominate in PvP Arena battles\n"
                       "• Join factions for large-scale warfare\n\n"
                       "Select a category below to explore specific commands:",
            color=COLORS['primary']
        )
        embed.set_thumbnail(url="https://i.imgur.com/placeholder.png")
        embed.set_footer(text="Use the dropdown menu below to navigate help categories")

        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))