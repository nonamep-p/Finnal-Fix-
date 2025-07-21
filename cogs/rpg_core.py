import discord
from discord.ext import commands
from replit import db
from rpg_data.game_data import OWNER_ID, XP_FOR_NEXT_LEVEL, STAT_POINTS_PER_LEVEL, ITEMS, CHARACTER_CLASSES
from utils.helpers import create_embed, format_number
from config import COLORS, is_module_enabled
import logging

logger = logging.getLogger(__name__)



class ClassSelectionView(discord.ui.View):
    """Interactive class selection for new characters."""

    def __init__(self, rpg_core, user_id):
        super().__init__(timeout=300)
        self.rpg_core = rpg_core
        self.user_id = user_id

        # Create class selection dropdown
        class_options = []
        for class_key, class_data in CHARACTER_CLASSES.items():
            class_options.append(discord.SelectOption(
                label=f"{class_data['emoji']} {class_data['name']}",
                value=class_key,
                description=f"{class_data['role']} - {class_data['description'][:50]}..."
            ))

        self.class_select = discord.ui.Select(
            placeholder="Choose your combat class...",
            options=class_options,
            custom_id="class_select"
        )
        self.class_select.callback = self.class_selected
        self.add_item(self.class_select)

    async def class_selected(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your character creation!", ephemeral=True)
            return

        class_key = interaction.data['values'][0]
        await self.create_character(interaction, class_key)

    async def create_character(self, interaction, class_key):
        """Create character with selected class."""
        class_data = CHARACTER_CLASSES[class_key]

        # Create character data
        character_data = {
            "name": interaction.user.display_name,
            "class": class_key,
            "level": 1,
            "xp": 0,
            "gold": 100,
            "stats": class_data['base_stats'].copy(),
            "unallocated_points": 0,
            "resources": {
                "hp": 100 + (class_data['base_stats']['constitution'] * 10),
                "max_hp": 100 + (class_data['base_stats']['constitution'] * 10),
                "mana": 50 + (class_data['base_stats']['intelligence'] * 5),
                "max_mana": 50 + (class_data['base_stats']['intelligence'] * 5),
                "stamina": 50 + (class_data['base_stats']['dexterity'] * 3),
                "max_stamina": 50 + (class_data['base_stats']['dexterity'] * 3),
                "ultimate_energy": 0,
                "technique_points": 3,
                "max_technique_points": 3
            },
            "derived_stats": {
                "max_ultimate_energy": 100,
                "attack": 10 + (class_data['base_stats']['strength'] * 2),
                "magic_attack": 10 + (class_data['base_stats']['intelligence'] * 2),
                "defense": 5 + class_data['base_stats']['constitution'],
                "critical_chance": 0.05 + (class_data['base_stats']['dexterity'] * 0.005),
                "critical_damage": 1.5,
                "dodge_chance": 0.05 + (class_data['base_stats']['dexterity'] * 0.005),
                "damage_reduction": 0.0,
                "initiative": class_data['base_stats']['dexterity']
            },
            "inventory": {"health_potion": 3, "mana_potion": 2},
            "equipment": {"weapon": None, "armor": None, "accessory": None, "artifact": None},
            "skills": class_data['starting_skills'],
            "techniques": ["ambush"],
            "in_combat": False,
            "arena_rating": 1000,
            "arena_wins": 0,
            "arena_losses": 0,
            "faction": None,
            "chosen_path": None,
            "gladiator_tokens": 0,
            "crafting_level": 1,
            "recipes_known": [],
            "titles": [],
            "active_title": None,
            "bounties": [],
            "kill_count": {},
            "damage_type": "physical" if class_key in ['warrior', 'rogue', 'archer'] else "magical"
        }

        # Save character
        self.rpg_core.save_player_data(self.user_id, character_data)

        # Create response embed
        embed = discord.Embed(
            title=f"⚔️ Character Created: {class_data['emoji']} {class_data['name']}",
            description=f"**Welcome to Project: Blood & Cheese, {character_data['name']}!**\n\n"
                       f"**Class:** {class_data['name']} ({class_data['role']})\n"
                       f"**Combat Focus:** {class_data['description']}\n\n"
                       f"**Starting Equipment:**\n"
                       f"• 100 Gold Coins\n"
                       f"• 3 Health Potions\n"
                       f"• 2 Mana Potions\n"
                       f"• Class Skills: {', '.join(class_data['starting_skills'])}\n\n"
                       f"**Passive Ability:** {class_data['passive']}\n"
                       f"**Ultimate:** {class_data['ultimate']}\n\n"
                       f"🎯 **Your path to power begins now!**\n"
                       f"Use `$battle` to start fighting monsters and gain experience!",
            color=COLORS['success']
        )

        # Add starting stats
        stats_text = ""
        for stat, value in character_data['stats'].items():
            stats_text += f"**{stat.upper()}:** {value} | "
        embed.add_field(name="📊 Starting Stats", value=stats_text[:-3], inline=False)

        # Add combat stats
        combat_text = (f"**HP:** {character_data['resources']['max_hp']}\n"
                      f"**Attack:** {character_data['derived_stats']['attack']}\n"
                      f"**Defense:** {character_data['derived_stats']['defense']}\n"
                      f"**Crit Chance:** {int(character_data['derived_stats']['critical_chance']*100)}%")
        embed.add_field(name="⚔️ Combat Stats", value=combat_text, inline=True)

        await interaction.response.edit_message(embed=embed, view=None)

class PathSelectionView(discord.ui.View):
    """Path selection interface for high-level characters."""

    def __init__(self, rpg_core, user_id):
        super().__init__(timeout=300)
        self.rpg_core = rpg_core
        self.user_id = user_id

    @discord.ui.button(label="💥 Destruction", style=discord.ButtonStyle.danger)
    async def destruction_path(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your path selection!", ephemeral=True)
            return
        await self.select_path(interaction, "destruction")

    @discord.ui.button(label="🛡️ Preservation", style=discord.ButtonStyle.secondary)
    async def preservation_path(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your path selection!", ephemeral=True)
            return
        await self.select_path(interaction, "preservation")

    @discord.ui.button(label="❤️‍🩹 Abundance", style=discord.ButtonStyle.success)
    async def abundance_path(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your path selection!", ephemeral=True)
            return
        await self.select_path(interaction, "abundance")

    @discord.ui.button(label="🎯 The Hunt", style=discord.ButtonStyle.primary)
    async def hunt_path(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("This is not your path selection!", ephemeral=True)
            return
        await self.select_path(interaction, "hunt")

    async def select_path(self, interaction, path_name):
        """Handle path selection and apply bonuses."""
        player_data = self.rpg_core.get_player_data(self.user_id)
        if not player_data:
            await interaction.response.send_message("❌ Character not found!", ephemeral=True)
            return

        if player_data.get('chosen_path'):
            await interaction.response.send_message("❌ You have already chosen a path!", ephemeral=True)
            return

        # Set the chosen path
        player_data['chosen_path'] = path_name

        # Apply path bonuses
        if path_name == "destruction":
            player_data['derived_stats']['critical_damage'] += 0.2
            player_data['derived_stats']['follow_up_chance'] = 0.30
        elif path_name == "preservation":
            player_data['derived_stats']['damage_reduction'] += 0.15
            player_data['derived_stats']['shield_generation'] = 0.10
        elif path_name == "abundance":
            player_data['derived_stats']['healing_bonus'] = 0.25
            player_data['derived_stats']['support_effectiveness'] = 0.20
        elif path_name == "hunt":
            player_data['derived_stats']['execution_threshold'] = 0.30
            player_data['derived_stats']['precision_bonus'] = 0.15

        self.rpg_core.save_player_data(self.user_id, player_data)

        path_descriptions = {
            "destruction": "💥 **Path of Destruction** - The Annihilator\n• +20% Critical Damage\n• 30% Follow-up Attack chance on Weakness Break\n• Bonus damage when defeating enemies",
            "preservation": "🛡️ **Path of Preservation** - The Guardian\n• +15% Damage Reduction\n• Generate shield on successful blocks\n• Enhanced defensive abilities",
            "abundance": "❤️‍🩹 **Path of Abundance** - The Nurturer\n• +25% Healing Power\n• +20% Support ability effectiveness\n• Buffs grant heal-over-time effects",
            "hunt": "🎯 **Path of The Hunt** - The Finisher\n• Execute enemies below 30% HP for massive damage\n• +15% Precision against wounded foes\n• Enhanced single-target abilities"
        }

        embed = discord.Embed(
            title=f"🌟 Path Chosen Successfully!",
            description=f"You have permanently chosen the:\n\n{path_descriptions[path_name]}\n\n"
                       "Your character has been enhanced with powerful new abilities!\n"
                       "Use `$profile` to see your updated combat stats.",
            color=COLORS['success']
        )

        await interaction.response.edit_message(embed=embed, view=None)

class RPGCore(commands.Cog):
    """Core RPG system focused on combat mastery."""

    def __init__(self, bot):
        self.bot = bot

    def get_player_data(self, user_id):
        """Get player data from database."""
        return db.get(f"rpg_player_{user_id}")

    def save_player_data(self, user_id, data):
        """Save player data to database."""
        db[f"rpg_player_{user_id}"] = data

    def level_up_check(self, player_data):
        """Check and handle level ups."""
        current_level = player_data['level']
        current_xp = player_data['xp']
        xp_needed = XP_FOR_NEXT_LEVEL(current_level)

        leveled_up = False
        while current_xp >= xp_needed:
            player_data['level'] += 1
            player_data['xp'] -= xp_needed
            player_data['unallocated_points'] += STAT_POINTS_PER_LEVEL

            # Increase resources
            class_data = CHARACTER_CLASSES.get(player_data['class'], CHARACTER_CLASSES['warrior'])
            hp_gain = 20 + (player_data['stats']['constitution'] * 2)
            mana_gain = 10 + (player_data['stats']['intelligence'] * 2)

            player_data['resources']['max_hp'] += hp_gain
            player_data['resources']['max_mana'] += mana_gain
            player_data['resources']['hp'] = player_data['resources']['max_hp']  # Full heal
            player_data['resources']['mana'] = player_data['resources']['max_mana']

            leveled_up = True
            current_level = player_data['level']
            current_xp = player_data['xp']
            xp_needed = XP_FOR_NEXT_LEVEL(current_level)

        return leveled_up

    @commands.command(name="startrpg")
    async def start_rpg(self, ctx):
        """Begin your journey as a combatant in Project: Blood & Cheese."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        player = self.get_player_data(ctx.author.id)
        if player:
            embed = create_embed(
                "Character Already Exists",
                f"You already have a **{CHARACTER_CLASSES[player['class']]['emoji']} {CHARACTER_CLASSES[player['class']]['name']}** character!\n\n"
                f"Use `$profile` to view your stats or `$battle` to start fighting!",
                COLORS['warning']
            )
            await ctx.send(embed=embed)
            return

        # Show class selection
        view = ClassSelectionView(self, ctx.author.id)
        embed = discord.Embed(
            title="⚔️ Welcome to Project: Blood & Cheese! ⚔️",
            description="**The ultimate combat-focused RPG experience!**\n\n"
                       "🎯 **Your Mission:** Become the greatest warrior in all of Paris through strategic combat, "
                       "powerful equipment, and relentless training.\n\n"
                       "**Choose your combat class wisely - this decision will define your fighting style:**",
            color=COLORS['primary']
        )

        # Add class descriptions
        for class_key, class_data in CHARACTER_CLASSES.items():
            embed.add_field(
                name=f"{class_data['emoji']} {class_data['name']} - {class_data['role']}",
                value=f"{class_data['description']}\n*{class_data['passive']}*",
                inline=False
            )

        embed.set_footer(text="Select your class from the dropdown menu below!")
        await ctx.send(embed=embed, view=view)

    @commands.command(name="profile")
    async def profile(self, ctx, member: discord.Member = None):
        """View your or another player's combat profile."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        target_user = member or ctx.author
        player = self.get_player_data(target_user.id)

        if not player:
            embed = create_embed(
                "No Character Found",
                f"{target_user.display_name} hasn't created a character yet.\nUse `$startrpg` to begin your combat journey!",
                COLORS['error']
            )
            await ctx.send(embed=embed)
            return

        class_data = CHARACTER_CLASSES[player['class']]
        xp_needed = XP_FOR_NEXT_LEVEL(player['level'])

        embed = discord.Embed(
            title=f"⚔️ {player['name']} - {class_data['emoji']} {class_data['name']}",
            color=COLORS['primary']
        )
        embed.set_thumbnail(url=target_user.display_avatar.url)

        # Level and XP
        embed.add_field(
            name="📊 Combat Level",
            value=f"**Level:** {player['level']}\n**XP:** {format_number(player['xp'])} / {format_number(xp_needed)}",
            inline=True
        )

        # Resources
        embed.add_field(
            name="💰 Resources",
            value=f"**Gold:** {format_number(player['gold'])}\n**Status:** {'🔴 In Combat' if player.get('in_combat') else '🟢 Ready to Fight'}",
            inline=True
        )

        # Core Stats
        stats_text = ""
        for stat, value in player['stats'].items():
            stats_text += f"**{stat.upper()}:** {value}\n"
        if player.get('unallocated_points', 0) > 0:
            stats_text += f"\n**Unallocated:** {player['unallocated_points']} points"
        embed.add_field(name="📊 Base Stats", value=stats_text, inline=True)

        # Combat Stats
        resources = player['resources']
        derived = player['derived_stats']
        combat_text = (f"**HP:** {resources['hp']}/{resources['max_hp']}\n"
                      f"**MP:** {resources['mana']}/{resources['max_mana']}\n"
                      f"**Attack:** {derived['attack']}\n"
                      f"**Defense:** {derived['defense']}\n"
                      f"**Crit:** {int(derived['critical_chance']*100)}% / {int((derived['critical_damage']-1)*100)}%")
        embed.add_field(name="⚔️ Combat Stats", value=combat_text, inline=True)

        # Arena Stats
        if player['arena_wins'] > 0 or player['arena_losses'] > 0:
            total_matches = player['arena_wins'] + player['arena_losses']
            win_rate = int((player['arena_wins'] / total_matches) * 100) if total_matches > 0 else 0
            arena_text = f"**Rating:** {player['arena_rating']}\n**Record:** {player['arena_wins']}-{player['arena_losses']} ({win_rate}%)"
            embed.add_field(name="🏆 Arena Record", value=arena_text, inline=True)

        # Path and Class info
        class_info = f"**Class:** {class_data['name']}\n**Role:** {class_data['role']}"
        if player.get('chosen_path'):
            class_info += f"\n**Path:** {player['chosen_path'].title()}"
        if player.get('faction'):
            class_info += f"\n**Faction:** {player['faction']}"
        embed.add_field(name="🌟 Character Info", value=class_info, inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="classes")
    async def classes(self, ctx):
        """View all available character classes."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        embed = discord.Embed(
            title="⚔️ Combat Classes - Choose Your Fighting Style",
            description="Each class has a unique role in combat and different paths to power:",
            color=COLORS['primary']
        )

        for class_key, class_data in CHARACTER_CLASSES.items():
            embed.add_field(
                name=f"{class_data['emoji']} {class_data['name']} - {class_data['role']}",
                value=f"**Focus:** {class_data['description']}\n"
                      f"**Passive:** {class_data['passive']}\n"
                      f"**Ultimate:** {class_data['ultimate']}",
                inline=False
            )

        embed.set_footer(text="Use $startrpg to create your character!")
        await ctx.send(embed=embed)

    @commands.command(name="allocate")
    async def allocate_stats(self, ctx, stat: str, points: int = 1):
        """Allocate stat points to enhance your combat abilities."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        player = self.get_player_data(ctx.author.id)
        if not player:
            await ctx.send(embed=create_embed("No Character", "Use `$startrpg` first!", COLORS['error']))
            return

        valid_stats = ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']
        stat = stat.lower()

        if stat not in valid_stats:
            await ctx.send(embed=create_embed("Invalid Stat", f"Choose from: {', '.join(valid_stats)}", COLORS['error']))
            return

        if points < 1 or points > player.get('unallocated_points', 0):
            await ctx.send(embed=create_embed("Invalid Points", f"You have {player.get('unallocated_points', 0)} points available.", COLORS['error']))
            return

        # Allocate points
        player['stats'][stat] += points
        player['unallocated_points'] -= points

        # Recalculate derived stats
        player['derived_stats']['attack'] = 10 + (player['stats']['strength'] * 2)
        player['derived_stats']['magic_attack'] = 10 + (player['stats']['intelligence'] * 2)
        player['derived_stats']['defense'] = 5 + player['stats']['constitution']
        player['derived_stats']['critical_chance'] = 0.05 + (player['stats']['dexterity'] * 0.005)
        player['derived_stats']['dodge_chance'] = 0.05 + (player['stats']['dexterity'] * 0.005)
        player['derived_stats']['initiative'] = player['stats']['dexterity']

        # Update HP/Mana if constitution/intelligence changed
        if stat == 'constitution':
            hp_gain = points * 10
            player['resources']['max_hp'] += hp_gain
            player['resources']['hp'] += hp_gain
        elif stat == 'intelligence':
            mana_gain = points * 5
            player['resources']['max_mana'] += mana_gain
            player['resources']['mana'] += mana_gain
        elif stat == 'dexterity':
            stamina_gain = points * 3
            player['resources']['max_stamina'] += stamina_gain
            player['resources']['stamina'] += stamina_gain

        self.save_player_data(ctx.author.id, player)

        embed = discord.Embed(
            title="📊 Stats Allocated!",
            description=f"Added **{points}** points to **{stat.upper()}**!\n\n"
                       f"**New {stat.upper()}:** {player['stats'][stat]}\n"
                       f"**Remaining Points:** {player['unallocated_points']}",
            color=COLORS['success']
        )
        await ctx.send(embed=embed)

    @commands.command(name="path")
    async def choose_path(self, ctx):
        """Choose your Miraculous Path at level 20."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        player = self.get_player_data(ctx.author.id)
        if not player:
            await ctx.send(embed=create_embed("No Character", "Use `$startrpg` first!", COLORS['error']))
            return

        if player['level'] < 20:
            await ctx.send(embed=create_embed("Path Locked", f"Reach Level 20 to choose your path. Current: {player['level']}", COLORS['warning']))
            return

        if player.get('chosen_path'):
            await ctx.send(embed=create_embed("Path Chosen", f"You've chosen the **{player['chosen_path'].title()}** path!", COLORS['info']))
            return

        view = PathSelectionView(self, ctx.author.id)
        embed = discord.Embed(
            title="🌟 Choose Your Miraculous Path",
            description="This choice is **permanent** and will define your combat mastery:\n\n"
                       "Each path grants powerful passive abilities that complement your class.",
            color=COLORS['primary']
        )

        embed.add_field(
            name="💥 Path of Destruction",
            value="**The Annihilator** - Pure offensive power\n• +20% Critical Damage\n• Follow-up attacks\n• Execution bonuses",
            inline=True
        )
        embed.add_field(
            name="🛡️ Path of Preservation", 
            value="**The Guardian** - Defensive mastery\n• +15% Damage Reduction\n• Shield generation\n• Protective abilities",
            inline=True
        )
        embed.add_field(
            name="❤️‍🩹 Path of Abundance",
            value="**The Nurturer** - Support excellence\n• +25% Healing Power\n• Enhanced buffs\n• Team synergy",
            inline=True
        )
        embed.add_field(
            name="🎯 Path of The Hunt",
            value="**The Finisher** - Precision strikes\n• Execute low HP enemies\n• Enhanced precision\n• Single-target mastery",
            inline=True
        )

        await ctx.send(embed=embed, view=view)

    @commands.command(name="achievements")
    async def view_achievements(self, ctx):
        """View your achievements and progress."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        player = self.get_player_data(ctx.author.id)
        if not player:
            await ctx.send(embed=create_embed("No Character", "Use `$startrpg` first!", COLORS['error']))
            return

        from utils.achievements import get_available_achievements
        achievements = get_available_achievements(str(ctx.author.id))

        embed = discord.Embed(
            title=f"🏆 {ctx.author.display_name}'s Achievements",
            description="Your journey of accomplishment and glory!",
            color=COLORS['primary']
        )

        completed_count = sum(1 for a in achievements if a['completed'])
        total_count = len(achievements)
        
        embed.add_field(
            name="📊 Progress",
            value=f"**Completed:** {completed_count}/{total_count}\n**Hidden Unlocked:** {sum(1 for a in achievements if a.get('hidden', False))}",
            inline=False
        )

        # Group by tier
        tiers = {}
        for achievement in achievements:
            tier = achievement['tier']
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(achievement)

        tier_emojis = {
            'bronze': '🥉',
            'silver': '🥈', 
            'gold': '🥇',
            'platinum': '💎',
            'legendary': '🌟',
            'mythic': '✨'
        }

        for tier, tier_achievements in tiers.items():
            if not tier_achievements:
                continue
                
            tier_text = ""
            for ach in tier_achievements[:5]:  # Show first 5 per tier
                status = "✅" if ach['completed'] else "❌"
                hidden_text = " 🔒" if ach.get('hidden', False) else ""
                tier_text += f"{status} **{ach['name']}**{hidden_text}\n"
                tier_text += f"   *{ach['description']}*\n"
                
                if not ach['completed'] and 'progress' in ach:
                    progress_text = ""
                    for req, prog in ach['progress'].items():
                        progress_text += f"   {prog['current']}/{prog['required']} ({prog['percentage']}%) "
                    tier_text += f"   {progress_text}\n"
                tier_text += "\n"

            if tier_text:
                embed.add_field(
                    name=f"{tier_emojis.get(tier, '🏆')} {tier.title()} Tier",
                    value=tier_text[:1024],  # Discord field limit
                    inline=False
                )

        await ctx.send(embed=embed)

    @commands.command(name="hiddenclasses")
    async def hidden_classes(self, ctx):
        """View available hidden classes (if requirements are met)."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        player = self.get_player_data(ctx.author.id)
        if not player:
            await ctx.send(embed=create_embed("No Character", "Use `$startrpg` first!", COLORS['error']))
            return

        from utils.achievements import HIDDEN_CLASSES, check_hidden_class_unlock
        
        embed = discord.Embed(
            title="🌟 Hidden Classes",
            description="Legendary classes that transcend normal limitations...",
            color=COLORS['legendary']
        )

        unlocked_classes = player.get('unlocked_hidden_classes', [])
        visible_classes = []

        for class_key, class_data in HIDDEN_CLASSES.items():
            can_unlock = check_hidden_class_unlock(str(ctx.author.id), class_key)
            is_unlocked = class_key in unlocked_classes
            
            # Only show if unlocked or close to unlocking
            if is_unlocked or can_unlock:
                visible_classes.append((class_key, class_data, is_unlocked))

        if not visible_classes:
            embed.description = "No hidden classes are available to you yet.\n\nComplete achievements and prove your worth to unlock these legendary paths!"
        else:
            for class_key, class_data, is_unlocked in visible_classes:
                status = "✅ **UNLOCKED**" if is_unlocked else "🔒 **LOCKED**"
                
                embed.add_field(
                    name=f"{class_data['emoji']} {class_data['name']} {status}",
                    value=f"**Role:** {class_data['role']}\n"
                          f"**Description:** {class_data['description']}\n"
                          f"**Passive:** {class_data['passive']}\n"
                          f"**Ultimate:** {class_data['ultimate']}",
                    inline=False
                )

        await ctx.send(embed=embed)

    # Owner-only commands
    @commands.command(name="ownerhelp", hidden=True)
    async def owner_help(self, ctx):
        """Owner-only help command."""
        from rpg_data.game_data import is_owner, OWNER_COMMANDS
        
        if not is_owner(ctx.author.id):
            return

        embed = discord.Embed(
            title="👑 Owner Commands",
            description="Administrative commands for the bot owner",
            color=COLORS['legendary']
        )

        commands_text = ""
        for cmd, desc in OWNER_COMMANDS.items():
            commands_text += f"**${cmd}** - {desc}\n"

        embed.add_field(name="Available Commands", value=commands_text, inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="spawn", hidden=True)
    async def spawn_item(self, ctx, user: discord.Member, item_name: str, quantity: int = 1):
        """Spawn items for players (Owner only)."""
        from rpg_data.game_data import is_owner, ITEMS
        
        if not is_owner(ctx.author.id):
            return

        player = self.get_player_data(user.id)
        if not player:
            await ctx.send("❌ Target player has no character!")
            return

        # Find item
        item_key = None
        for key, data in ITEMS.items():
            if key == item_name.lower().replace(" ", "_") or data['name'].lower() == item_name.lower():
                item_key = key
                break

        if not item_key:
            await ctx.send(f"❌ Item '{item_name}' not found!")
            return

        # Add item to player
        if item_key in player['inventory']:
            player['inventory'][item_key] += quantity
        else:
            player['inventory'][item_key] = quantity

        self.save_player_data(user.id, player)

        embed = create_embed(
            "✅ Item Spawned",
            f"Gave **{quantity}x {ITEMS[item_key]['name']}** to {user.display_name}",
            COLORS['success']
        )
        await ctx.send(embed=embed)

    @commands.command(name="setstat", hidden=True)
    async def set_stat(self, ctx, user: discord.Member, stat: str, value: int):
        """Set a player's stat (Owner only)."""
        from rpg_data.game_data import is_owner
        
        if not is_owner(ctx.author.id):
            return

        player = self.get_player_data(user.id)
        if not player:
            await ctx.send("❌ Target player has no character!")
            return

        valid_stats = ['level', 'gold', 'xp', 'hp', 'mana']
        if stat not in valid_stats:
            await ctx.send(f"❌ Invalid stat! Valid: {', '.join(valid_stats)}")
            return

        if stat == 'hp':
            player['resources']['hp'] = value
        elif stat == 'mana':
            player['resources']['mana'] = value
        else:
            player[stat] = value

        self.save_player_data(user.id, player)

        embed = create_embed(
            "✅ Stat Modified",
            f"Set {user.display_name}'s **{stat}** to **{value}**",
            COLORS['success']
        )
        await ctx.send(embed=embed)

    @commands.command(name="unlock", hidden=True)
    async def unlock_content(self, ctx, user: discord.Member, content_type: str, content_name: str):
        """Unlock hidden content for players (Owner only)."""
        from rpg_data.game_data import is_owner
        
        if not is_owner(ctx.author.id):
            return

        player = self.get_player_data(user.id)
        if not player:
            await ctx.send("❌ Target player has no character!")
            return

        if content_type == "class":
            unlocked_classes = player.get('unlocked_hidden_classes', [])
            if content_name not in unlocked_classes:
                unlocked_classes.append(content_name)
                player['unlocked_hidden_classes'] = unlocked_classes
        elif content_type == "achievement":
            completed = player.get('completed_achievements', [])
            if content_name not in completed:
                completed.append(content_name)
                player['completed_achievements'] = completed
        else:
            await ctx.send("❌ Invalid content type! Use 'class' or 'achievement'")
            return

        self.save_player_data(user.id, player)

        embed = create_embed(
            "✅ Content Unlocked",
            f"Unlocked **{content_type}: {content_name}** for {user.display_name}",
            COLORS['success']
        )
        await ctx.send(embed=embed)

    @commands.command(name="inventory", aliases=["inv"])
    async def inventory(self, ctx):
        """Display your inventory."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return
            
        player = self.get_player_data(ctx.author.id)
        if not player:
            embed = create_embed(
                "No Profile Found",
                "You need to `$startrpg` first!",
                COLORS['error']
            )
            await ctx.send(embed=embed)
            return

        inventory = player.get('inventory', {})
        
        embed = discord.Embed(
            title=f"🎒 {ctx.author.display_name}'s Inventory",
            color=COLORS['secondary']
        )

        if not inventory:
            embed.description = "Your inventory is empty!"
        else:
            items_text = ""
            for item_name, quantity in inventory.items():
                if item_name in ITEMS:
                    item_data = ITEMS[item_name]
                    rarity_emoji = "⚪" if item_data['rarity'] == 'common' else "🟢" if item_data['rarity'] == 'uncommon' else "🔵"
                    items_text += f"{rarity_emoji} **{item_data['name']}** x{quantity}\n"
                else:
                    items_text += f"❓ **{item_name}** x{quantity}\n"
            
            embed.description = items_text

        embed.set_footer(text="Use $use <item> to use consumables or $equip <item> to equip gear")
        await ctx.send(embed=embed)

    @commands.command(name="artifacts")
    async def artifacts(self, ctx):
        """Manage your Kwami Artifacts."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return
            
        player = self.get_player_data(ctx.author.id)
        if not player:
            embed = create_embed(
                "No Profile Found",
                "You need to `$startrpg` first!",
                COLORS['error']
            )
            await ctx.send(embed=embed)
            return

        equipped_artifacts = player.get('equipped_artifacts', {})
        kwami_artifacts = player.get('kwami_artifacts', [])
        
        embed = discord.Embed(
            title=f"✨ {ctx.author.display_name}'s Kwami Artifacts",
            color=COLORS['primary']
        )

        # Show equipped artifacts
        equipped_text = ""
        for slot in ['head', 'hands', 'body', 'feet']:
            artifact = equipped_artifacts.get(slot)
            if artifact:
                equipped_text += f"**{slot.title()}:** {artifact['name']} ({artifact['set']})\n"
            else:
                equipped_text += f"**{slot.title()}:** Empty\n"
        
        embed.add_field(name="🎽 Equipped Artifacts", value=equipped_text or "No artifacts equipped", inline=False)

        # Show set bonuses
        from rpg_data.game_data import KWAMI_ARTIFACT_SETS
        set_counts = {}
        for artifact in equipped_artifacts.values():
            if artifact:
                set_name = artifact['set']
                set_counts[set_name] = set_counts.get(set_name, 0) + 1

        if set_counts:
            bonus_text = ""
            for set_name, count in set_counts.items():
                if set_name in KWAMI_ARTIFACT_SETS:
                    set_data = KWAMI_ARTIFACT_SETS[set_name]
                    bonus_text += f"**{set_data['name']}:** {count}/4 pieces\n"
                    
                    # Show active bonuses
                    for piece_req, bonus in set_data['bonuses'].items():
                        if count >= piece_req:
                            bonus_text += f"  ✅ ({piece_req}) {bonus['description']}\n"
                        else:
                            bonus_text += f"  ❌ ({piece_req}) {bonus['description']}\n"
                    bonus_text += "\n"
            
            embed.add_field(name="🌟 Set Bonuses", value=bonus_text, inline=False)

        # Show inventory of artifacts
        if kwami_artifacts:
            artifact_text = ""
            for artifact in kwami_artifacts[:10]:  # Show first 10
                artifact_text += f"• **{artifact['name']}** ({artifact['set']}) - {artifact['slot'].title()}\n"
            
            if len(kwami_artifacts) > 10:
                artifact_text += f"... and {len(kwami_artifacts) - 10} more"
            
            embed.add_field(name="🎒 Artifact Storage", value=artifact_text, inline=False)

        embed.set_footer(text="Use $equipartifact <name> to equip artifacts")
        await ctx.send(embed=embed)

    @commands.command(name="miraculous", aliases=["box"])
    async def miraculous_box(self, ctx):
        """Enter the Miraculous Box for artifact farming."""
        import asyncio
        import random
        if not is_module_enabled("rpg", ctx.guild.id):
            return
            
        player = self.get_player_data(ctx.author.id)
        if not player:
            embed = create_embed(
                "No Profile Found",
                "You need to `$startrpg` first!",
                COLORS['error']
            )
            await ctx.send(embed=embed)
            return

        miraculous_energy = player['resources'].get('miraculous_energy', 0)
        energy_cost = 40

        if miraculous_energy < energy_cost:
            embed = create_embed(
                "Insufficient Energy",
                f"You need {energy_cost} Miraculous Energy to enter the box.\n"
                f"Current energy: {miraculous_energy}/{player['resources'].get('max_miraculous_energy', 120)}\n\n"
                "Energy regenerates over time!",
                COLORS['warning']
            )
            await ctx.send(embed=embed)
            return

        if player.get('in_combat'):
            embed = create_embed(
                "Cannot Enter",
                "You cannot enter the Miraculous Box while in combat!",
                COLORS['error']
            )
            await ctx.send(embed=embed)
            return

        # Deduct energy
        player['resources']['miraculous_energy'] -= energy_cost
        player['in_combat'] = True
        self.save_player_data(ctx.author.id, player)

        embed = discord.Embed(
            title="✨ Entering the Miraculous Box",
            description=f"🌟 You step into the mystical Miraculous Box...\n\n"
                       f"⚡ Energy consumed: {energy_cost}\n"
                       f"🔋 Remaining energy: {player['resources']['miraculous_energy']}\n\n"
                       "Prepare for a challenging encounter!",
            color=COLORS['primary']
        )

        await ctx.send(embed=embed)
        await asyncio.sleep(2)

        # Start special artifact dungeon combat
        from cogs.rpg_combat import TacticalCombatView, active_combats

        special_monsters = ['artifact_guardian', 'kwami_phantom', 'miraculous_sentinel']
        monster_key = random.choice(special_monsters)

        message = await ctx.send("Initializing Miraculous Box encounter...")
        
        view = TacticalCombatView(ctx.author.id, monster_key, message, self)
        view.is_miraculous_box = True  # Flag for special rewards
        active_combats[ctx.channel.id] = view
        
        await view.update_view()

async def setup(bot):
    await bot.add_cog(RPGCore(bot))