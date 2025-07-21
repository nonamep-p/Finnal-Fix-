import discord
from discord.ext import commands
import random
import asyncio
import logging
from replit import db
from config import COLORS, is_module_enabled
from utils.helpers import create_embed, format_number
from rpg_data.game_data import ITEMS, RARITY_COLORS, TACTICAL_MONSTERS, CHARACTER_CLASSES

# Add crafting recipes for the crafting system
CRAFTING_RECIPES = {
    'iron_sword': {
        'name': 'Iron Sword',
        'level_required': 5,
        'rarity': 'common',
        'type': 'weapon',
        'materials': {'iron_ore': 3, 'wood': 2},
        'description': 'A basic iron sword for new adventurers'
    },
    'health_potion': {
        'name': 'Health Potion',
        'level_required': 1,
        'rarity': 'common',
        'type': 'consumable',
        'materials': {'healing_herbs': 2, 'water': 1},
        'description': 'Restores health when consumed'
    }
}
from datetime import datetime

logger = logging.getLogger(__name__)

class ArenaMatchView(discord.ui.View):
    """Arena matchmaking and battle interface."""

    def __init__(self, player_id, rpg_core):
        super().__init__(timeout=300)
        self.player_id = player_id
        self.rpg_core = rpg_core
        self.searching = False

    @discord.ui.button(label="🔍 Find Match", style=discord.ButtonStyle.primary)
    async def find_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Not your arena interface!", ephemeral=True)
            return

        if self.searching:
            await interaction.response.send_message("Already searching for a match!", ephemeral=True)
            return

        self.searching = True
        button.disabled = True
        button.label = "🔍 Searching..."

        await interaction.response.edit_message(view=self)

        # Simulate matchmaking delay
        await asyncio.sleep(3)

        embed = discord.Embed(
            title="🏆 Arena Match Found!",
            description="**Opponent:** Training Dummy (Bot)\n**Rating:** Similar to yours\n\nPrepare for tactical combat!",
            color=COLORS['primary']
        )
        await interaction.edit_original_response(embed=embed, view=None)

class CraftingView(discord.ui.View):
    """Crafting interface for creating combat equipment."""

    def __init__(self, player_id, rpg_core):
        super().__init__(timeout=300)
        self.player_id = player_id
        self.rpg_core = rpg_core

        # Create recipe dropdown
        recipe_options = []
        for recipe_key, recipe_data in list(CRAFTING_RECIPES.items())[:10]:  # Limit to first 10
            recipe_options.append(discord.SelectOption(
                label=recipe_data['name'],
                value=recipe_key,
                description=f"Level {recipe_data['level_required']} {recipe_data['rarity']} {recipe_data['type']}"
            ))

        if recipe_options:
            recipe_select = discord.ui.Select(placeholder="Choose a recipe to craft...", options=recipe_options)
            recipe_select.callback = self.craft_item
            self.add_item(recipe_select)

    async def craft_item(self, interaction: discord.Interaction):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Not your crafting interface!", ephemeral=True)
            return

        recipe_key = interaction.data['values'][0]
        recipe = CRAFTING_RECIPES[recipe_key]

        player_data = self.rpg_core.get_player_data(self.player_id)

        # Check level requirement
        if player_data['level'] < recipe['level_required']:
            await interaction.response.send_message(f"❌ Need level {recipe['level_required']} to craft this!", ephemeral=True)
            return

        # Check materials (simplified - assume player has materials for demo)
        materials_text = "\n".join([f"• {name}: {amount}" for name, amount in recipe['materials'].items()])

        embed = discord.Embed(
            title=f"🔨 Crafting: {recipe['name']}",
            description=f"**Materials Required:**\n{materials_text}\n\n"
                       f"**Result:** {recipe['rarity'].title()} {recipe['type']}\n"
                       f"{recipe['description']}",
            color=COLORS['warning']
        )
        embed.set_footer(text="Crafting system coming soon!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

class RPGGames(commands.Cog):
    """Fun RPG mini-games and activities."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="hunt")
    async def hunt(self, ctx):
        """Go hunting for monsters and loot."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        rpg_core = self.bot.get_cog('RPGCore')
        if not rpg_core:
            await ctx.send("❌ RPG system not loaded.")
            return

        player_data = rpg_core.get_player_data(ctx.author.id)
        if not player_data:
            embed = create_embed("No Character", "Use `$startrpg` first!", COLORS['error'])
            await ctx.send(embed=embed)
            return

        if player_data.get('in_combat'):
            embed = create_embed("Already Hunting", "Finish your current adventure first!", COLORS['warning'])
            await ctx.send(embed=embed)
            return

        # Mark as in combat
        player_data['in_combat'] = True
        rpg_core.save_player_data(ctx.author.id, player_data)

        # Choose random monster based on player level
        suitable_monsters = []
        for monster_key, monster_data in TACTICAL_MONSTERS.items():
            level_diff = abs(monster_data['level'] - player_data['level'])
            if level_diff <= 5:  # Within 5 levels
                suitable_monsters.append(monster_key)

        if not suitable_monsters:
            suitable_monsters = list(TACTICAL_MONSTERS.keys())[:3]  # Fallback to first 3

        monster_key = random.choice(suitable_monsters)
        monster = TACTICAL_MONSTERS[monster_key]

        embed = discord.Embed(
            title="🏹 Hunting Expedition",
            description=f"You venture into the wilderness and encounter a **{monster['name']}**!\n\n"
                       f"**Level:** {monster['level']}\n"
                       f"**HP:** {monster['hp']}\n"
                       f"**Rarity:** {monster['rarity'].title()}\n\n"
                       "⚔️ Battle commencing...",
            color=COLORS['warning']
        )

        await ctx.send(embed=embed)
        await asyncio.sleep(2)

        # Start combat
        from cogs.rpg_combat import TacticalCombatView, active_combats

        message = await ctx.send("Initializing combat...")
        combat_view = TacticalCombatView(ctx.author.id, monster_key, message, rpg_core)
        active_combats[ctx.channel.id] = combat_view

        await combat_view.update_view()

    @commands.command(name="explore")
    async def explore(self, ctx):
        """Explore areas for treasure and adventures."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        rpg_core = self.bot.get_cog('RPGCore')
        if not rpg_core:
            await ctx.send("❌ RPG system not loaded.")
            return

        player_data = rpg_core.get_player_data(ctx.author.id)
        if not player_data:
            embed = create_embed("No Character", "Use `$startrpg` first!", COLORS['error'])
            await ctx.send(embed=embed)
            return

        # Check cooldown
        import time
        last_explore = player_data.get('last_explore', 0)
        cooldown = 1800  # 30 minutes

        if time.time() - last_explore < cooldown:
            remaining = cooldown - (time.time() - last_explore)
            minutes = int(remaining // 60)
            await ctx.send(f"⏰ You can explore again in {minutes} minutes!")
            return

        # Update cooldown
        player_data['last_explore'] = time.time()

        # Random exploration results
        outcomes = [
            ("treasure", 0.4),
            ("monster", 0.3),
            ("nothing", 0.2),
            ("rare_find", 0.1)
        ]

        # Weighted random selection
        rand = random.random()
        cumulative = 0
        outcome = "nothing"

        for result, weight in outcomes:
            cumulative += weight
            if rand <= cumulative:
                outcome = result
                break

        if outcome == "treasure":
            # Find random item
            common_items = [k for k, v in ITEMS.items() if v.get('rarity') == 'common']
            item = random.choice(common_items) if common_items else 'health_potion'

            if item in player_data['inventory']:
                player_data['inventory'][item] += 1
            else:
                player_data['inventory'][item] = 1

            gold_found = random.randint(20, 100)
            player_data['gold'] += gold_found

            embed = discord.Embed(
                title="💎 Treasure Found!",
                description=f"While exploring, you discovered:\n\n"
                           f"• **{ITEMS[item]['name']}**\n"
                           f"• **{format_number(gold_found)} Gold**\n\n"
                           "Your exploration skills are improving!",
                color=COLORS['success']
            )

        elif outcome == "monster":
            embed = discord.Embed(
                title="⚔️ Hostile Encounter!",
                description="Your exploration disturbed a dangerous creature!\n\n"
                           "Use `$hunt` to engage in combat when ready.",
                color=COLORS['warning']
            )

        elif outcome == "rare_find":
            # Rare item or large gold amount
            rare_items = [k for k, v in ITEMS.items() if v.get('rarity') in ['rare', 'epic']]
            if rare_items and random.random() < 0.7:
                item = random.choice(rare_items)
                if item in player_data['inventory']:
                    player_data['inventory'][item] += 1
                else:
                    player_data['inventory'][item] = 1

                embed = discord.Embed(
                    title="✨ Rare Discovery!",
                    description=f"You found something extraordinary!\n\n"
                               f"**{ITEMS[item]['name']}** ({ITEMS[item]['rarity'].title()})\n\n"
                               "This is a once-in-a-lifetime find!",
                    color=RARITY_COLORS.get(ITEMS[item]['rarity'], COLORS['primary'])
                )
            else:
                large_gold = random.randint(500, 1500)
                player_data['gold'] += large_gold

                embed = discord.Embed(
                    title="💰 Hidden Cache!",
                    description=f"You discovered a hidden treasure cache!\n\n"
                               f"**Found:** {format_number(large_gold)} gold\n\n"
                               "Someone must have stashed this here long ago.",
                    color=COLORS['success']
                )

        else:  # nothing
            embed = discord.Embed(
                title="🚶 Peaceful Exploration",
                description="You explored the area thoroughly but found nothing of particular interest.\n\n"
                           "Sometimes the journey itself is the reward.\n\n"
                           "✨ *You gained some experience from the exercise.*",
                color=COLORS['secondary']
            )
            # Small XP gain even for nothing
            player_data['xp'] += random.randint(5, 15)
            rpg_core.level_up_check(player_data)

        rpg_core.save_player_data(ctx.author.id, player_data)
        await ctx.send(embed=embed)

    @commands.command(name="fish")
    async def fish(self, ctx):
        """Try your luck at fishing."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        rpg_core = self.bot.get_cog('RPGCore')
        if not rpg_core:
            await ctx.send("❌ RPG system not loaded.")
            return

        player_data = rpg_core.get_player_data(ctx.author.id)
        if not player_data:
            embed = create_embed("No Character", "Use `$startrpg` first!", COLORS['error'])
            await ctx.send(embed=embed)
            return

        # Check if player has fishing rod (optional)
        has_rod = 'fishing_rod' in player_data.get('inventory', {})

        # Base success rates
        base_success = 0.6
        rare_chance = 0.1

        if has_rod:
            base_success += 0.2
            rare_chance += 0.1

        embed = discord.Embed(
            title="🎣 Fishing...",
            description="You cast your line into the water and wait patiently...",
            color=COLORS['info']
        )
        message = await ctx.send(embed=embed)
        await asyncio.sleep(3)  # Suspense!

        if random.random() < base_success:
            # Caught something!
            if random.random() < rare_chance:
                # Rare catch
                catches = ['golden_fish', 'ancient_boot', 'message_bottle', 'pearl']
                catch = random.choice(catches)
                value = random.randint(100, 500)

                embed = discord.Embed(
                    title="🌟 Rare Catch!",
                    description=f"Amazing! You caught a **{catch.replace('_', ' ').title()}**!\n\n"
                               f"You can sell it for **{format_number(value)} gold**!",
                    color=COLORS['legendary']
                )
                player_data['gold'] += value
            else:
                # Common catch
                catches = ['salmon', 'trout', 'bass', 'carp']
                catch = random.choice(catches)
                value = random.randint(10, 50)

                embed = discord.Embed(
                    title="🐟 Good Catch!",
                    description=f"You caught a nice **{catch}**!\n\n"
                               f"Sold for **{format_number(value)} gold**.",
                    color=COLORS['success']
                )
                player_data['gold'] += value
        else:
            # Nothing caught
            embed = discord.Embed(
                title="🎣 No Luck",
                description="The fish weren't biting today.\n\n"
                           "Better luck next time! 🐟",
                color=COLORS['secondary']
            )

        # Small XP gain regardless
        player_data['xp'] += random.randint(3, 10)
        rpg_core.level_up_check(player_data)
        rpg_core.save_player_data(ctx.author.id, player_data)

        await message.edit(embed=embed)

    @commands.command(name="gamble")
    async def gamble(self, ctx, amount: int = None):
        """Gamble gold for a chance to win big."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        rpg_core = self.bot.get_cog('RPGCore')
        if not rpg_core:
            await ctx.send("❌ RPG system not loaded.")
            return

        player_data = rpg_core.get_player_data(ctx.author.id)
        if not player_data:
            embed = create_embed("No Character", "Use `$startrpg` first!", COLORS['error'])
            await ctx.send(embed=embed)
            return

        if amount is None:
            embed = discord.Embed(
                title="🎰 Plagg's Casino",
                description="**Welcome to my chaotic casino!** 🧀\n\n"
                           "Place your bets and let fate decide!\n\n"
                           "**Usage:** `$gamble <amount>`\n"
                           "**Min Bet:** 10 gold\n"
                           "**Max Bet:** 1000 gold\n\n"
                           "**Odds:**\n"
                           "• 🎯 Jackpot (5x): 5% chance\n"
                           "• 💎 Big Win (3x): 15% chance\n"
                           "• 🟢 Win (2x): 30% chance\n"
                           "• ❌ Lose All: 50% chance",
                color=COLORS['warning']
            )
            await ctx.send(embed=embed)
            return

        if amount < 10 or amount > 1000:
            await ctx.send("❌ Bet must be between 10 and 1000 gold!")
            return

        if player_data['gold'] < amount:
            await ctx.send(f"❌ You only have {format_number(player_data['gold'])} gold!")
            return

        # Deduct bet amount
        player_data['gold'] -= amount

        # Determine outcome
        rand = random.random()

        if rand < 0.05:  # 5% - Jackpot
            winnings = amount * 5
            player_data['gold'] += winnings
            result_emoji = "🎯"
            result_title = "JACKPOT!"
            result_desc = f"INCREDIBLE! You hit the jackpot!\n\n**Won:** {format_number(winnings)} gold"
            result_color = COLORS['legendary']

        elif rand < 0.20:  # 15% - Big win
            winnings = amount * 3
            player_data['gold'] += winnings
            result_emoji = "💎"
            result_title = "Big Win!"
            result_desc = f"Excellent! A big win!\n\n**Won:** {format_number(winnings)} gold"
            result_color = COLORS['success']

        elif rand < 0.50:  # 30% - Regular win
            winnings = amount * 2
            player_data['gold'] += winnings
            result_emoji = "🟢"
            result_title = "You Win!"
            result_desc = f"Nice! You doubled your money!\n\n**Won:** {format_number(winnings)} gold"
            result_color = COLORS['primary']

        else:  # 50% - Lose
            result_emoji = "❌"
            result_title = "You Lose!"
            result_desc = f"The house always wins... sometimes!\n\n**Lost:** {format_number(amount)} gold"
            result_color = COLORS['error']

        embed = discord.Embed(
            title=f"{result_emoji} {result_title}",
            description=f"{result_desc}\n\n**Current Gold:** {format_number(player_data['gold'])}",
            color=result_color
        )

        rpg_core.save_player_data(ctx.author.id, player_data)
        await ctx.send(embed=embed)

    @commands.command(name="guild")
    async def guild(self, ctx, action: str = None, *, args: str = None):
        """Manage your guild for community progression."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        rpg_core = self.bot.get_cog('RPGCore')
        if not rpg_core:
            await ctx.send("❌ RPG system not available.")
            return

        player_data = rpg_core.get_player_data(ctx.author.id)
        if not player_data:
            embed = create_embed("No Character", "Create a character with `$startrpg` first!", COLORS['error'])
            await ctx.send(embed=embed)
            return

        if not action:
            # Show guild info or invite to join
            guild_id = player_data.get('guild_id')
            if guild_id:
                guild_data = db.get(f"guild_{guild_id}")
                if guild_data:
                    await self.show_guild_info(ctx, guild_data, player_data)
                    return

            embed = discord.Embed(
                title="🏰 Guild System - Join the Community!",
                description="**Guilds provide powerful benefits for all members:**\n\n"
                           "🌟 **Guild Perks (All Levels):**\n"
                           "• Shared guild bank for resources\n"
                           "• Private guild chat channel\n"
                           "• Group dungeon access\n"
                           "• Weekly guild events\n\n"
                           "📈 **Level Benefits:**\n"
                           "• **Level 1:** +5% XP for all members\n"
                           "• **Level 3:** +10% Gold Find\n"
                           "• **Level 5:** +15% Crafting Speed\n"
                           "• **Level 10:** Access to Guild Raids\n\n"
                           "**Commands:**\n"
                           "`$guild create <name>` - Create a guild (5000 gold)\n"
                           "`$guild join <guild_name>` - Request to join\n"
                           "`$guild leave` - Leave your current guild",
                color=COLORS['primary']
            )
            await ctx.send(embed=embed)
            return

        if action == "create":
            await self.create_guild(ctx, args, rpg_core, player_data)
        elif action == "join":
            await self.join_guild(ctx, args, rpg_core, player_data)
        elif action == "leave":
            await self.leave_guild(ctx, rpg_core, player_data)
        elif action == "invite":
            await self.invite_to_guild(ctx, args, rpg_core, player_data)
        elif action == "bank":
            await self.guild_bank(ctx, args, rpg_core, player_data)
        elif action == "level":
            await self.guild_level_up(ctx, rpg_core, player_data)
        else:
            embed = create_embed("Invalid Action", "Use: create, join, leave, invite, bank, or level", COLORS['error'])
            await ctx.send(embed=embed)

    async def create_guild(self, ctx, guild_name, rpg_core, player_data):
        """Create a new guild."""
        if not guild_name:
            await ctx.send("Usage: `$guild create <guild_name>`")
            return

        if player_data.get('guild_id'):
            embed = create_embed("Already in Guild", "Leave your current guild first!", COLORS['warning'])
            await ctx.send(embed=embed)
            return

        creation_cost = 5000
        if player_data['gold'] < creation_cost:
            embed = create_embed("Insufficient Gold", f"Creating a guild costs {format_number(creation_cost)} gold!", COLORS['error'])
            await ctx.send(embed=embed)
            return

        # Check if guild name is taken
        all_guilds = db.get("all_guilds", {})
        for guild_id, name in all_guilds.items():
            if name.lower() == guild_name.lower():
                embed = create_embed("Name Taken", "A guild with that name already exists!", COLORS['error'])
                await ctx.send(embed=embed)
                return

        # Create guild
        guild_id = f"guild_{len(all_guilds) + 1}"
        guild_data = {
            "name": guild_name,
            "leader": ctx.author.id,
            "members": [ctx.author.id],
            "level": 1,
            "xp": 0,
            "bank": {"gold": 0, "items": {}},
            "created_date": datetime.now().isoformat(),
            "description": f"A powerful guild led by {ctx.author.display_name}",
            "perks": ["xp_boost_5"]
        }

        # Save guild data
        db[f"guild_{guild_id}"] = guild_data
        all_guilds[guild_id] = guild_name
        db["all_guilds"] = all_guilds

        # Update player data
        player_data['guild_id'] = guild_id
        player_data['gold'] -= creation_cost
        rpg_core.save_player_data(ctx.author.id, player_data)

        embed = discord.Embed(
            title="🏰 Guild Created!",
            description=f"**{guild_name}** has been founded!\n\n"
                       f"**Leader:** {ctx.author.display_name}\n"
                       f"**Level:** 1\n"
                       f"**Active Perks:** +5% XP for all members\n\n"
                       f"Use `$guild invite @user` to invite members!",
            color=COLORS['success']
        )
        await ctx.send(embed=embed)

    async def show_guild_info(self, ctx, guild_data, player_data):
        """Display detailed guild information."""
        embed = discord.Embed(
            title=f"🏰 {guild_data['name']}",
            description=guild_data.get('description', 'A mighty guild of adventurers'),
            color=COLORS['primary']
        )

        # Guild stats
        member_count = len(guild_data['members'])
        xp_needed = (guild_data['level'] * 1000) - guild_data['xp']

        stats_text = (f"**Level:** {guild_data['level']}\n"
                     f"**Members:** {member_count}/20\n"
                     f"**XP:** {format_number(guild_data['xp'])}\n"
                     f"**XP to Next Level:** {format_number(xp_needed)}")
        embed.add_field(name="📊 Guild Stats", value=stats_text, inline=True)

        # Guild bank
        bank_gold = guild_data['bank']['gold']
        bank_items = len(guild_data['bank']['items'])
        bank_text = (f"**Gold:** {format_number(bank_gold)}\n"
                    f"**Items:** {bank_items} types")
        embed.add_field(name="🏦 Guild Bank", value=bank_text, inline=True)

        # Active perks
        perk_descriptions = {
            "xp_boost_5": "+5% XP for all members",
            "gold_boost_10": "+10% Gold Find",
            "craft_speed_15": "+15% Crafting Speed",
            "raid_access": "Access to Guild Raids"
        }

        perks_text = ""
        for perk in guild_data.get('perks', []):
            if perk in perk_descriptions:
                perks_text += f"• {perk_descriptions[perk]}\n"

        embed.add_field(name="🌟 Active Perks", value=perks_text or "None", inline=False)

        # Members list
        members_text = ""
        rpg_core = self.bot.get_cog('RPGCore')
        for member_id in guild_data['members'][:10]:  # Show max 10 members
            try:
                user = await self.bot.fetch_user(member_id)
                role = "👑 Leader" if member_id == guild_data['leader'] else "⚔️ Member"

                member_data = rpg_core.get_player_data(member_id)
                level = member_data['level'] if member_data else "?"

                members_text += f"{role} {user.display_name} (Lv.{level})\n"
            except:
                continue

        if len(guild_data['members']) > 10:
            members_text += f"... and {len(guild_data['members']) - 10} more"

        embed.add_field(name="👥 Members", value=members_text or "None", inline=False)

        embed.set_footer(text="Use $guild bank to access shared resources | $guild level to contribute to guild growth")
        await ctx.send(embed=embed)

    @commands.command(name="contested")
    async def contested_zones(self, ctx):
        """View contested zones where faction warfare occurs."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        embed = discord.Embed(
            title="⚔️ Contested Zones - Faction Warfare",
            description="Dangerous territories where opposing factions clash for control:",
            color=COLORS['error']
        )

        contested_zones = [
            {
                'name': 'Louvre Shadows',
                'level': '15-20',
                'control': 'Miraculous Order',
                'benefits': 'Double XP from elite monsters',
                'danger': 'High - Enemy faction members can attack you'
            },
            {
                'name': 'Catacombs of Power',
                'level': '20-25',
                'control': 'Shadow Moth Syndicate',
                'benefits': 'Rare crafting materials',
                'danger': 'Extreme - Boss-level monsters and PvP'
            }
        ]

        for zone in contested_zones:
            embed.add_field(
                name=f"🏴 {zone['name']} (Level {zone['level']})",
                value=f"**Controlled by:** {zone['control']}\n"
                      f"**Benefits:** {zone['benefits']}\n"
                      f"**Danger Level:** {zone['danger']}",
                inline=False
            )

        embed.set_footer(text="Join a faction to access contested zones!")
        await ctx.send(embed=embed)

    @commands.command(name="prestige")
    async def prestige(self, ctx):
        """Reset your character for permanent power bonuses."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        rpg_core = self.bot.get_cog('RPGCore')
        if not rpg_core:
            await ctx.send("❌ RPG system not available.")
            return

        player_data = rpg_core.get_player_data(ctx.author.id)
        if not player_data:
            embed = create_embed("No Character", "Create a character with `$startrpg` first!", COLORS['error'])
            await ctx.send(embed=embed)
            return

        if player_data['level'] < 50:
            embed = create_embed("Level Too Low", f"You must reach Level 50 to prestige. Current: {player_data['level']}", COLORS['warning'])
            await ctx.send(embed=embed)
            return

        current_prestige = player_data.get('prestige_level', 0)

        embed = discord.Embed(
            title="⭐ Prestige System - The Ultimate Reset",
            description=f"**Current Prestige Level:** {current_prestige}\n\n"
                       f"**Prestige Benefits (Per Level):**\n"
                       f"• +2% to ALL stats permanently\n"
                       f"• +5% XP gain in future runs\n"
                       f"• +3% Gold find bonus\n"
                       f"• Prestige-exclusive cosmetics\n"
                       f"• Access to Prestige-only dungeons\n\n"
                       f"**⚠️ WARNING: Prestiging will reset:**\n"
                       f"• Your level back to 1\n"
                       f"• All equipment (kept in special storage)\n"
                       f"• All skills (must relearn)\n\n"
                       f"**You KEEP:**\n"
                       f"• Gold and inventory items\n"
                       f"• Guild membership\n"
                       f"• Achievements and titles\n"
                       f"• Permanent stat bonuses\n\n"
                       f"Use `$prestige confirm` to proceed!",
            color=COLORS['warning']
        )

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RPGGames(bot))