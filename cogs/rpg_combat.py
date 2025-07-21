import discord
from discord.ext import commands
from replit import db
import random
import asyncio
from rpg_data.game_data import TACTICAL_MONSTERS, ITEMS, TACTICAL_SKILLS, RARITY_COLORS, ULTIMATE_ABILITIES, DAMAGE_TYPES, TECHNIQUES, SYNERGY_STATES
from utils.helpers import create_embed, format_number
from config import COLORS, is_module_enabled
import logging

logger = logging.getLogger(__name__)

# Active combat sessions
active_combats = {}

# Enhanced monster data with weaknesses
TACTICAL_MONSTERS = {
    'goblin': {
        'name': 'Goblin Warrior',
        'emoji': '👹',
        'hp': 120,
        'max_hp': 120,
        'toughness': 60,
        'max_toughness': 60,
        'weakness_type': 'physical',
        'attack': 25,
        'defense': 8,
        'xp_reward': 35,
        'gold_reward': 15,
        'skills': ['quick_slash'],
        'loot_table': {'health_potion': 0.4, 'iron_sword': 0.2}
    },
    'orc': {
        'name': 'Orc Berserker',
        'emoji': '👺',
        'hp': 180,
        'max_hp': 180,
        'toughness': 80,
        'max_toughness': 80,
        'weakness_type': 'ice',
        'attack': 35,
        'defense': 12,
        'xp_reward': 60,
        'gold_reward': 25,
        'skills': ['berserker_rage'],
        'loot_table': {'health_potion': 0.3, 'steel_armor': 0.15}
    },
    'ice_elemental': {
        'name': 'Ice Elemental',
        'emoji': '🧊',
        'hp': 150,
        'max_hp': 150,
        'toughness': 70,
        'max_toughness': 70,
        'weakness_type': 'fire',
        'attack': 30,
        'defense': 15,
        'xp_reward': 50,
        'gold_reward': 20,
        'skills': ['ice_blast'],
        'loot_table': {'mana_potion': 0.5, 'ice_crystal': 0.3}
    },
    'dragon': {
        'name': 'Ancient Dragon',
        'emoji': '🐉',
        'hp': 400,
        'max_hp': 400,
        'toughness': 120,
        'max_toughness': 120,
        'weakness_type': 'lightning',
        'attack': 60,
        'defense': 25,
        'xp_reward': 200,
        'gold_reward': 100,
        'skills': ['dragon_breath', 'tail_sweep'],
        'loot_table': {'dragon_scale': 0.8, 'legendary_weapon': 0.1}
    },
    # Miraculous Box special monsters
    'artifact_guardian': {
        'name': 'Kwami Artifact Guardian',
        'emoji': '🛡️',
        'hp': 200,
        'max_hp': 200,
        'toughness': 90,
        'max_toughness': 90,
        'weakness_type': 'quantum',
        'attack': 45,
        'defense': 20,
        'xp_reward': 100,
        'gold_reward': 75,
        'skills': ['artifact_shield', 'guardian_slam'],
        'artifact_drops': ['guardians_bastion']
    },
    'kwami_phantom': {
        'name': 'Kwami Phantom',
        'emoji': '👻',
        'hp': 180,
        'max_hp': 180,
        'toughness': 70,
        'max_toughness': 70,
        'weakness_type': 'imaginary',
        'attack': 50,
        'defense': 15,
        'xp_reward': 110,
        'gold_reward': 80,
        'skills': ['phantom_strike', 'phase_shift'],
        'artifact_drops': ['cat_noirs_folly', 'plaggs_chaos']
    },
    'miraculous_sentinel': {
        'name': 'Miraculous Sentinel',
        'emoji': '⚔️',
        'hp': 220,
        'max_hp': 220,
        'toughness': 100,
        'max_toughness': 100,
        'weakness_type': 'physical',
        'attack': 40,
        'defense': 25,
        'xp_reward': 120,
        'gold_reward': 90,
        'skills': ['sentinel_guard', 'miraculous_beam'],
        'artifact_drops': ['ladybugs_luck', 'hawk_moths_dominion']
    }
}

# Enhanced skills with SP costs and Ultimate abilities
TACTICAL_SKILLS = {
    'power_strike': {
        'name': 'Power Strike',
        'cost': 1,
        'cost_type': 'skill_points',
        'damage': 40,
        'toughness_damage': 15,
        'damage_type': 'physical',
        'ultimate_gain': 20,
        'description': 'A powerful physical attack that costs 1 SP.'
    },
    'flame_slash': {
        'name': 'Flame Slash',
        'cost': 1,
        'cost_type': 'skill_points',
        'damage': 35,
        'toughness_damage': 20,
        'damage_type': 'fire',
        'ultimate_gain': 20,
        'description': 'A burning sword technique that costs 1 SP.'
    },
    'ice_lance': {
        'name': 'Ice Lance',
        'cost': 1,
        'cost_type': 'skill_points',
        'damage': 38,
        'toughness_damage': 18,
        'damage_type': 'ice',
        'ultimate_gain': 20,
        'description': 'A piercing ice attack that costs 1 SP.'
    },
    'lightning_bolt': {
        'name': 'Lightning Bolt',
        'cost': 1,
        'cost_type': 'skill_points',
        'damage': 42,
        'toughness_damage': 22,
        'damage_type': 'lightning',
        'ultimate_gain': 20,
        'description': 'An electrifying attack that costs 1 SP.'
    },
    'heal': {
        'name': 'Healing Light',
        'cost': 1,
        'cost_type': 'skill_points',
        'heal': 50,
        'ultimate_gain': 15,
        'description': 'Restores health using 1 SP.'
    }
}

# Ultimate abilities by class
ULTIMATE_ABILITIES = {
    'warrior': {
        'name': 'Blade Storm',
        'description': 'Unleashes a devastating series of strikes',
        'damage': 120,
        'toughness_damage': 50,
        'damage_type': 'physical'
    },
    'mage': {
        'name': 'Arcane Devastation',
        'description': 'Channels pure magical energy',
        'damage': 100,
        'toughness_damage': 60,
        'damage_type': 'quantum'
    },
    'rogue': {
        'name': 'Shadow Assassination',
        'description': 'Strikes from the shadows with lethal precision',
        'damage': 110,
        'toughness_damage': 40,
        'damage_type': 'physical'
    }
}

class SkillSelectionView(discord.ui.View):
    """Enhanced skill selection with SP costs."""

    def __init__(self, combat_view):
        super().__init__(timeout=60)
        self.combat_view = combat_view

        # Get available skills based on SP
        available_skills = []
        skill_points = combat_view.combat_state['skill_points']

        for skill_name in combat_view.player_data.get('skills', ['power_strike', 'heal']):
            if skill_name in TACTICAL_SKILLS:
                skill = TACTICAL_SKILLS[skill_name]
                cost = skill.get('cost', 1)

                if skill_points >= cost:
                    available_skills.append(discord.SelectOption(
                        label=f"{skill['name']} (Cost: {cost} SP)",
                        value=skill_name,
                        description=skill['description'][:50],
                        emoji="✨"
                    ))

        if not available_skills:
            available_skills.append(discord.SelectOption(
                label="Not enough Skill Points",
                value="none",
                description="Use Basic Attack to generate SP"
            ))

        skill_select = discord.ui.Select(placeholder="Choose a skill...", options=available_skills)
        skill_select.callback = self.skill_selected
        self.add_item(skill_select)

    async def skill_selected(self, interaction: discord.Interaction):
        if interaction.user.id != self.combat_view.player_id:
            await interaction.response.send_message("Not your combat!", ephemeral=True)
            return

        skill_name = interaction.data['values'][0]
        if skill_name == "none":
            await interaction.response.send_message("Not enough Skill Points!", ephemeral=True)
            return

        await self.combat_view.use_skill(interaction, skill_name)

class TechniqueSelectionView(discord.ui.View):
    """Pre-combat technique selection."""

    def __init__(self, combat_view):
        super().__init__(timeout=60)
        self.combat_view = combat_view

        # Get available techniques
        player_data = combat_view.player_data
        available_techniques = []
        technique_points = player_data['resources'].get('technique_points', 0)

        from rpg_data.game_data import TECHNIQUES

        for tech_name in player_data.get('techniques', ['ambush']):
            if tech_name in TECHNIQUES:
                tech = TECHNIQUES[tech_name]
                cost = tech.get('cost', 1)

                if technique_points >= cost:
                    available_techniques.append(discord.SelectOption(
                        label=f"{tech['name']} (Cost: {cost} TP)",
                        value=tech_name,
                        description=tech['description'][:50],
                        emoji="⚡"
                    ))

        if not available_techniques:
            available_techniques.append(discord.SelectOption(
                label="No Technique Points",
                value="none",
                description="Not enough Technique Points available"
            ))

        tech_select = discord.ui.Select(placeholder="Choose a technique...", options=available_techniques)
        tech_select.callback = self.technique_selected
        self.add_item(tech_select)

    async def technique_selected(self, interaction: discord.Interaction):
        if interaction.user.id != self.combat_view.player_id:
            await interaction.response.send_message("Not your combat!", ephemeral=True)
            return

        technique_name = interaction.data['values'][0]
        if technique_name == "none":
            await interaction.response.send_message("No Technique Points available!", ephemeral=True)
            return

        await self.combat_view.apply_technique(interaction, technique_name)

class TacticalCombatView(discord.ui.View):
    """Enhanced combat view with tactical mechanics."""

    def __init__(self, player_id, monster_key, initial_message, rpg_core_cog, technique_used=None):
        super().__init__(timeout=300)
        self.player_id = player_id
        self.monster_key = monster_key
        self.message = initial_message
        self.rpg_core = rpg_core_cog
        self.combat_log = []
        self.turn_count = 0
        self.technique_used = technique_used

        # Load and prepare player data
        self.player_data = self.rpg_core.get_player_data(player_id)

        # Migrate old data format if needed
        if 'resources' not in self.player_data:
            self.player_data['resources'] = {
                'hp': self.player_data.get('hp', 100),
                'max_hp': self.player_data.get('max_hp', 100),
                'mana': self.player_data.get('mana', 50),
                'max_mana': self.player_data.get('max_mana', 50),
                'stamina': self.player_data.get('stamina', 50),
                'max_stamina': self.player_data.get('max_stamina', 50),
                'ultimate_energy': 0
            }

        # Initialize combat state with tactical elements
        monster_data = TACTICAL_MONSTERS.get(monster_key, TACTICAL_MONSTERS['goblin']).copy()

        self.combat_state = {
            'in_combat': True,
            'skill_points': 3,
            'max_skill_points': 5,
            'enemy': monster_data,
            'turn': 'player',
            'enemy_broken_turns': 0,
            'synergy_states': [],
            'follow_up_queue': []
        }

        # Apply technique effects if used
        if technique_used:
            self.apply_technique_effects(technique_used)

        self.add_log(f"⚔️ A wild **{monster_data['name']} {monster_data['emoji']}** appears!")
        self.add_log(f"🔍 Enemy weakness: {DAMAGE_TYPES.get(monster_data['weakness_type'], '❓')} {monster_data['weakness_type'].title()}")

    def apply_technique_effects(self, technique_name):
        """Apply pre-combat technique effects."""
        from rpg_data.game_data import TECHNIQUES

        if technique_name not in TECHNIQUES:
            return

        tech = TECHNIQUES[technique_name]
        effect = tech.get('effect', {})

        if effect['type'] == 'skill_points':
            self.combat_state['skill_points'] += effect['amount']
            self.add_log(f"⚡ Technique: {tech['name']} grants +{effect['amount']} Skill Points!")

        elif effect['type'] == 'enemy_debuff':
            # Apply debuff to enemy
            enemy = self.combat_state['enemy']
            if effect['stat'] == 'defense':
                enemy['defense'] = max(0, enemy.get('defense', 0) + effect['amount'])
                self.add_log(f"⚡ Technique: Enemy defense reduced by {abs(effect['amount'])}!")
            elif effect['stat'] == 'marked':
                enemy['marked_damage'] = effect['amount']
                enemy['marked_turns'] = effect['duration']
                self.add_log(f"⚡ Technique: Enemy marked for +{int(effect['amount']*100)}% damage!")

        elif effect['type'] == 'shield':
            self.player_data['resources']['shield'] = self.player_data['resources'].get('shield', 0) + effect['amount']
            self.add_log(f"⚡ Technique: Gained {effect['amount']} shield points!")

        elif effect['type'] == 'ultimate_energy':
            old_energy = self.player_data['resources'].get('ultimate_energy', 0)
            max_energy = self.player_data.get('derived_stats', {}).get('max_ultimate_energy', 100)
            self.player_data['resources']['ultimate_energy'] = min(max_energy, old_energy + effect['amount'])
            self.add_log(f"⚡ Technique: Gained {effect['amount']} Ultimate Energy!")

    async def apply_technique(self, interaction, technique_name):
        """Apply selected technique and start combat."""
        from rpg_data.game_data import TECHNIQUES

        if technique_name not in TECHNIQUES:
            await interaction.response.send_message("❌ Invalid technique!", ephemeral=True)
            return

        tech = TECHNIQUES[technique_name]
        cost = tech.get('cost', 1)

        # Deduct technique points
        self.player_data['resources']['technique_points'] -= cost
        self.rpg_core.save_player_data(self.player_id, self.player_data)

        # Apply technique effects
        self.apply_technique_effects(technique_name)

        # Start combat
        await interaction.response.edit_message(content=f"⚡ Used **{tech['name']}**! Combat begins!", embed=None, view=None)
        await asyncio.sleep(1)
        await self.update_view()

    def add_log(self, text):
        """Add entry to combat log."""
        self.combat_log.append(f"• {text}")
        if len(self.combat_log) > 12:
            self.combat_log.pop(0)

    def create_bar(self, current, maximum, length=10, fill="█", empty="░"):
        """Create visual progress bar."""
        if maximum == 0:
            return empty * length
        percentage = current / maximum
        filled = int(percentage * length)
        empty_count = length - filled
        return fill * filled + empty * empty_count

    def create_sp_display(self):
        """Create skill points display."""
        sp = self.combat_state['skill_points']
        max_sp = self.combat_state['max_skill_points']
        filled = "💎" * sp
        empty = "▢" * (max_sp - sp)
        return f"{filled}{empty} ({sp}/{max_sp})"

    async def create_embed(self):
        """Generate comprehensive tactical combat embed."""
        enemy = self.combat_state['enemy']
        resources = self.player_data['resources']

        embed = discord.Embed(
            title=f"⚔️ Tactical Combat: {self.player_data['name']} vs. {enemy['name']}", 
            color=COLORS['error']
        )

        # Skill Points display at the top
        embed.add_field(
            name="💎 Skill Points (Shared Resource)",
            value=f"**SP:** {self.create_sp_display()}",
            inline=False
        )

        # Player status
        player_hp_bar = self.create_bar(resources['hp'], resources['max_hp'])
        ultimate_bar = self.create_bar(
            resources.get('ultimate_energy', 0), 
            self.player_data.get('derived_stats', {}).get('max_ultimate_energy', 100)
        )

        embed.add_field(
            name=f"👤 {self.player_data['name']}",
            value=f"❤️ **HP:** {resources['hp']}/{resources['max_hp']} {player_hp_bar}\n"
                  f"⚡ **Ultimate:** {ultimate_bar} ({resources.get('ultimate_energy', 0)}/100)",
            inline=True
        )

        # Enemy status with toughness
        enemy_hp_bar = self.create_bar(enemy['hp'], enemy['max_hp'])

        if enemy.get('is_broken', False):
            toughness_display = "💥 [ BROKEN ] 💥"
        else:
            toughness_bar = self.create_bar(enemy['toughness'], enemy['max_toughness'])
            toughness_display = f"🛡️ {enemy['toughness']}/{enemy['max_toughness']} {toughness_bar}"

        embed.add_field(
            name=f"{enemy['emoji']} {enemy['name']}",
            value=f"❤️ **HP:** {enemy['hp']}/{enemy['max_hp']} {enemy_hp_bar}\n"
                  f"{toughness_display}\n"
                  f"🔍 **Weakness:** {DAMAGE_TYPES.get(enemy['weakness_type'], '❓')} {enemy['weakness_type'].title()}",
            inline=True
        )

        # Turn indicator
        turn_text = "🎯 **Your Turn**" if self.combat_state['turn'] == 'player' else "🔴 **Enemy Turn**"
        if enemy.get('is_broken', False):
            turn_text += " (Enemy Stunned!)"

        embed.add_field(name="Current Turn", value=f"{turn_text} | Turn {self.turn_count + 1}", inline=False)

        # Combat log
        if self.combat_log:
            log_content = "\n".join(self.combat_log[-10:])
            embed.add_field(name="📜 Combat Log", value=f"```{log_content}```", inline=False)

        return embed

    async def update_view(self):
        """Update combat display and button states."""
        enemy = self.combat_state['enemy']
        resources = self.player_data['resources']

        # Update button availability
        for item in self.children:
            if hasattr(item, 'label'):
                if item.label == "💥 ULTIMATE":
                    # Ultimate button only available when energy is full
                    item.disabled = (
                        self.combat_state['turn'] != 'player' or
                        resources.get('ultimate_energy', 0) < 100 or
                        resources['hp'] <= 0 or
                        enemy['hp'] <= 0
                    )
                    item.style = discord.ButtonStyle.success if resources.get('ultimate_energy', 0) >= 100 else discord.ButtonStyle.secondary
                else:
                    item.disabled = (
                        self.combat_state['turn'] != 'player' or
                        resources['hp'] <= 0 or
                        enemy['hp'] <= 0
                    )

        embed = await self.create_embed()
        try:
            await self.message.edit(embed=embed, view=self)
        except discord.NotFound:
            pass

    async def check_weakness_break(self, damage_type, toughness_damage):
        """Check and handle weakness break mechanics."""
        enemy = self.combat_state['enemy']

        weakness_match = damage_type == enemy['weakness_type']

        if weakness_match and toughness_damage > 0:
            old_toughness = enemy['toughness']
            enemy['toughness'] = max(0, enemy['toughness'] - toughness_damage)

            self.add_log(f"💥 Weakness hit! Toughness damage: {toughness_damage}")

            # Check for break
            if old_toughness > 0 and enemy['toughness'] == 0:
                enemy['is_broken'] = True
                self.combat_state['enemy_broken_turns'] = 1
                self.add_log(f"🔥 WEAKNESS BREAK! {enemy['name']} is stunned and vulnerable!")

                # Check for follow-up attack triggers
                await self.check_follow_up_triggers('toughness_break')
                return True

        return False

    async def check_follow_up_triggers(self, trigger_type, damage=None):
        """Check and execute follow-up attacks."""
        player_data = self.player_data
        follow_up_triggers = player_data.get('follow_up_triggers', [])

        # Path-based follow-ups
        chosen_path = player_data.get('chosen_path')
        if chosen_path == 'destruction' and trigger_type == 'toughness_break':
            if random.random() < 0.30:  # 30% chance
                await self.execute_follow_up_attack()

        # Check for other follow-up conditions
        if trigger_type == 'critical_hit' and 'crit_follow_up' in follow_up_triggers:
            if random.random() < 0.25:  # 25% chance
                await self.execute_follow_up_attack()

    async def execute_follow_up_attack(self):
        """Execute a follow-up attack."""
        enemy = self.combat_state['enemy']

        # Calculate follow-up damage (50% of base attack)
        base_damage = 25
        follow_up_damage = random.randint(base_damage - 5, base_damage + 10)

        # Apply damage multiplier if enemy is broken
        if enemy.get('is_broken', False):
            follow_up_damage = int(follow_up_damage * 1.3)

        enemy['hp'] = max(0, enemy['hp'] - follow_up_damage)

        self.add_log(f"⚡ FOLLOW-UP ATTACK! Dealt {follow_up_damage} additional damage!")

        # Generate small ultimate energy
        ultimate_gain = 5
        old_ultimate = self.player_data['resources'].get('ultimate_energy', 0)
        max_ultimate = self.player_data.get('derived_stats', {}).get('max_ultimate_energy', 100)
        self.player_data['resources']['ultimate_energy'] = min(max_ultimate, old_ultimate + ultimate_gain)

    def apply_synergy_state(self, state_name):
        """Apply a synergy state to the player."""
        from rpg_data.game_data import SYNERGY_STATES

        if state_name in SYNERGY_STATES:
            state_data = SYNERGY_STATES[state_name].copy()
            self.combat_state['synergy_states'].append(state_data)
            self.add_log(f"✨ Synergy State: {state_data['emoji']} {state_data['name']} activated!")

    def check_synergy_states(self, action_type):
        """Check and consume synergy states for bonuses."""
        bonuses = {}
        states_to_remove = []

        for i, state in enumerate(self.combat_state['synergy_states']):
            if action_type == 'basic_attack' and state['effect'] == 'riposte_damage':
                shield_amount = self.player_data['resources'].get('shield', 0)
                bonuses['riposte_bonus'] = shield_amount * 2
                states_to_remove.append(i)
                self.add_log(f"⚔️ Riposte Strike! Bonus damage from shield: +{bonuses['riposte_bonus']}")

            elif action_type == 'skill' and state['effect'] == 'guaranteed_crit':
                bonuses['guaranteed_crit'] = True
                states_to_remove.append(i)
                self.add_log(f"🎯 Opportunist Strike! Guaranteed critical hit!")

            elif action_type == 'spell' and state['effect'] == 'free_enhanced_spell':
                bonuses['free_spell'] = True
                bonuses['spell_damage_boost'] = 0.5
                states_to_remove.append(i)
                self.add_log(f"✨ Arcane Resonance! Free enhanced spell!")

        # Remove consumed states
        for i in reversed(states_to_remove):
            removed_state = self.combat_state['synergy_states'].pop(i)
            self.add_log(f"💫 {removed_state['name']} consumed!")

        return bonuses

    async def apply_break_effects(self):
        """Apply effects when enemy is broken."""
        enemy = self.combat_state['enemy']

        if enemy.get('is_broken', False):
            # Enemy skips turn while broken
            if self.combat_state['enemy_broken_turns'] > 0:
                self.add_log(f"💫 {enemy['name']} is stunned and skips their turn!")
                self.combat_state['enemy_broken_turns'] -= 1

                # Restore toughness and remove break after stun
                if self.combat_state['enemy_broken_turns'] <= 0:
                    enemy['is_broken'] = False
                    enemy['toughness'] = enemy['max_toughness']
                    self.add_log(f"🛡️ {enemy['name']} recovers and toughness is restored!")

                return True

        return False

    async def end_combat(self, victory):
        """Handle combat conclusion with enhanced rewards."""
        self.player_data['in_combat'] = False
        enemy = self.combat_state['enemy']

        if victory:
            # Calculate enhanced rewards
            base_xp = enemy['xp_reward']
            base_gold = enemy['gold_reward']

            # Level multiplier
            level_mult = 1 + (self.player_data['level'] - 1) * 0.1
            xp_gained = int(base_xp * level_mult)
            gold_gained = int(base_gold * level_mult)

            self.player_data['xp'] += xp_gained
            self.player_data['gold'] += gold_gained

            # Loot drops
            loot_found = []
            for item_name, chance in enemy.get('loot_table', {}).items():
                if random.random() < chance:
                    if item_name in self.player_data['inventory']:
                        self.player_data['inventory'][item_name] += 1
                    else:
                        self.player_data['inventory'][item_name] = 1
                    loot_found.append(item_name)

            # Artifact drops for Miraculous Box
            if hasattr(self, 'is_miraculous_box') and self.is_miraculous_box:
                artifact_sets = enemy.get('artifact_drops', [])
                if artifact_sets:
                    # Guaranteed artifact drop
                    chosen_set = random.choice(artifact_sets)
                    slots = ['head', 'hands', 'body', 'feet']
                    chosen_slot = random.choice(slots)

                    from rpg_data.game_data import KWAMI_ARTIFACT_SETS
                    if chosen_set in KWAMI_ARTIFACT_SETS:
                        set_data = KWAMI_ARTIFACT_SETS[chosen_set]
                        artifact = {
                            'name': f"{set_data['name']} - {chosen_slot.title()}",
                            'set': chosen_set,
                            'slot': chosen_slot,
                            'rarity': 'legendary'
                        }

                        if 'kwami_artifacts' not in self.player_data:
                            self.player_data['kwami_artifacts'] = []
                        self.player_data['kwami_artifacts'].append(artifact)

                        self.add_log(f"✨ KWAMI ARTIFACT FOUND: {artifact['name']}!")
                        loot_found.append(f"Kwami Artifact: {artifact['name']}")

            self.add_log(f"🏆 Victory! Gained {xp_gained} XP and {gold_gained} gold!")
            if loot_found:
                items_str = ", ".join([item.replace('_', ' ').title() for item in loot_found])
                self.add_log(f"💎 Found: {items_str}")

            # Check for level up
            leveled_up = self.rpg_core.level_up_check(self.player_data)
            if leveled_up:
                self.add_log(f"⭐ LEVEL UP! You are now level {self.player_data['level']}!")

            final_embed = discord.Embed(
                title="🏆 TACTICAL VICTORY! 🏆",
                description="\n".join(self.combat_log),
                color=COLORS['success']
            )
        else:
            # Defeat consequences
            gold_lost = max(1, int(self.player_data['gold'] * 0.15))
            self.player_data['gold'] = max(0, self.player_data['gold'] - gold_lost)
            self.player_data['resources']['hp'] = max(1, self.player_data['resources']['max_hp'] // 4)

            self.add_log(f"💀 Defeat! Lost {gold_lost} gold and most of your health.")

            final_embed = discord.Embed(
                title="☠️ TACTICAL DEFEAT ☠️",
                description="\n".join(self.combat_log),
                color=COLORS['error']
            )

        # Reset ultimate energy and save
        self.player_data['resources']['ultimate_energy'] = 0
        self.rpg_core.save_player_data(self.player_id, self.player_data)

        try:
            await self.message.edit(content="Combat concluded.", embed=final_embed, view=None)
        except discord.NotFound:
            pass

        if self.message.channel.id in active_combats:
            del active_combats[self.message.channel.id]
        self.stop()

    async def monster_turn(self):
        """Enhanced monster AI with tactical considerations."""
        enemy = self.combat_state['enemy']

        # Check if broken/stunned
        if await self.apply_break_effects():
            self.combat_state['turn'] = 'player'
            await self.update_view()
            return

        # Monster attacks
        damage = random.randint(enemy['attack'] - 5, enemy['attack'] + 10)

        # Apply broken damage bonus
        if enemy.get('was_broken_last_turn', False):
            damage = int(damage * 0.8)  # Reduced damage after recovering
            enemy['was_broken_last_turn'] = False

        self.player_data['resources']['hp'] = max(0, self.player_data['resources']['hp'] - damage)
        self.add_log(f"{enemy['name']} attacks for {damage} damage!")

        self.combat_state['turn'] = 'player'
        self.turn_count += 1
        await self.update_view()

        # Check for player defeat
        if self.player_data['resources']['hp'] <= 0:
            await self.end_combat(victory=False)

    async def use_skill(self, interaction, skill_name):
        """Execute tactical skill with SP costs."""
        await interaction.response.defer()

        if skill_name not in TACTICAL_SKILLS:
            return

        skill = TACTICAL_SKILLS[skill_name]
        sp_cost = skill.get('cost', 1)

        # Check SP
        if self.combat_state['skill_points'] < sp_cost:
            self.add_log(f"❌ Not enough Skill Points! Need {sp_cost} SP.")
            await self.update_view()
            return

        # Consume SP
        self.combat_state['skill_points'] -= sp_cost

        enemy = self.combat_state['enemy']

        if 'heal' in skill:
            # Healing skill
            heal_amount = skill['heal']
            old_hp = self.player_data['resources']['hp']
            self.player_data['resources']['hp'] = min(
                self.player_data['resources']['max_hp'], 
                self.player_data['resources']['hp'] + heal_amount
            )
            actual_heal = self.player_data['resources']['hp'] - old_hp

            self.add_log(f"✨ Used {skill['name']}! Healed {actual_heal} HP for {sp_cost} SP.")

        elif 'damage' in skill:
            # Attack skill
            base_damage = skill['damage']
            damage = random.randint(base_damage - 5, base_damage + 10)

            # Check for weakness break
            toughness_damage = skill.get('toughness_damage', 0)
            damage_type = skill.get('damage_type', 'physical')

            was_broken = await self.check_weakness_break(damage_type, toughness_damage)

            # Apply damage multiplier if enemy is broken
            if enemy.get('is_broken', False):
                damage = int(damage * 1.5)
                self.add_log(f"💥 Bonus damage on broken enemy!")

            enemy['hp'] = max(0, enemy['hp'] - damage)
            self.add_log(f"⚔️ Used {skill['name']}! Dealt {damage} {damage_type} damage for {sp_cost} SP.")

        # Grant ultimate energy
        ultimate_gain = skill.get('ultimate_gain', 15)
        old_ultimate = self.player_data['resources'].get('ultimate_energy', 0)
        max_ultimate = self.player_data.get('derived_stats', {}).get('max_ultimate_energy', 100)
        self.player_data['resources']['ultimate_energy'] = min(max_ultimate, old_ultimate + ultimate_gain)

        if self.player_data['resources']['ultimate_energy'] - old_ultimate > 0:
            self.add_log(f"⚡ Gained {self.player_data['resources']['ultimate_energy'] - old_ultimate} Ultimate Energy!")

        # End turn
        self.combat_state['turn'] = 'monster'
        await self.update_view()
        await asyncio.sleep(1.5)

        # Check for victory
        if enemy['hp'] <= 0:
            await self.end_combat(victory=True)
            return

        await self.monster_turn()

    # Combat buttons
    @discord.ui.button(label="⚔️ Basic Attack", style=discord.ButtonStyle.secondary, emoji="⚔️")
    async def basic_attack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Not your combat!", ephemeral=True)
            return

        await interaction.response.defer()

        # Check synergy states for bonuses
        synergy_bonuses = self.check_synergy_states('basic_attack')

        # Basic attack generates SP and ultimate energy
        base_damage = 20
        damage = random.randint(base_damage - 5, base_damage + 8)

        # Apply synergy bonuses
        if 'riposte_bonus' in synergy_bonuses:
            damage += synergy_bonuses['riposte_bonus']

        # Check for critical hit
        crit_chance = self.player_data['derived_stats'].get('critical_chance', 0.05)
        is_critical = random.random() < crit_chance or synergy_bonuses.get('guaranteed_crit', False)

        if is_critical:
            crit_multiplier = self.player_data['derived_stats'].get('critical_damage', 1.5)
            damage = int(damage * crit_multiplier)
            self.add_log(f"💥 CRITICAL HIT! ({int(crit_multiplier*100)}% damage)")
            await self.check_follow_up_triggers('critical_hit', damage)

        # Generate SP
        if self.combat_state['skill_points'] < self.combat_state['max_skill_points']:
            self.combat_state['skill_points'] += 1
            sp_gained = 1
        else:
            sp_gained = 0

        # Generate ultimate energy
        ultimate_gain = 10
        old_ultimate = self.player_data['resources'].get('ultimate_energy', 0)
        max_ultimate = self.player_data.get('derived_stats', {}).get('max_ultimate_energy', 100)
        self.player_data['resources']['ultimate_energy'] = min(max_ultimate, old_ultimate + ultimate_gain)

        # Check for weakness (basic attacks are physical)
        enemy = self.combat_state['enemy']
        if enemy['weakness_type'] == 'physical':
            toughness_damage = 8
            await self.check_weakness_break('physical', toughness_damage)

        # Apply damage multiplier if enemy is broken
        if enemy.get('is_broken', False):
            damage = int(damage * 1.3)
            self.add_log(f"💥 Bonus damage on broken enemy!")

        # Apply Path of Hunt bonus for low HP enemies
        if self.player_data.get('chosen_path') == 'hunt' and enemy['hp'] <= enemy['max_hp'] * 0.5:
            damage = int(damage * 1.2)
            self.add_log(f"🎯 Hunt Bonus! +20% damage to wounded enemy!")

        enemy['hp'] = max(0, enemy['hp'] - damage)

        log_msg = f"⚔️ Basic Attack! Dealt {damage} physical damage"
        if sp_gained > 0:
            log_msg += f", gained {sp_gained} SP"
        if ultimate_gain > 0:
            log_msg += f", gained {ultimate_gain} Ultimate Energy"
        log_msg += "!"

        self.add_log(log_msg)

        self.combat_state['turn'] = 'monster'
        await self.update_view()
        await asyncio.sleep(1.5)

        if enemy['hp'] <= 0:
            await self.end_combat(victory=True)
            return

        await self.monster_turn()

    @discord.ui.button(label="✨ Skills", style=discord.ButtonStyle.primary, emoji="✨")
    async def skills(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Not your combat!", ephemeral=True)
            return

        skill_view = SkillSelectionView(self)
        await interaction.response.send_message("Choose a skill:", view=skill_view, ephemeral=True)

    @discord.ui.button(label="💥 ULTIMATE", style=discord.ButtonStyle.secondary, emoji="💥")
    async def ultimate(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Not your combat!", ephemeral=True)
            return

        # Check if ultimate is ready
        if self.player_data['resources'].get('ultimate_energy', 0) < 100:
            await interaction.response.send_message("❌ Ultimate not ready!", ephemeral=True)
            return

        await interaction.response.defer()

        # Get ultimate based on class
        player_class = self.player_data.get('player_class', 'warrior')
        ultimate_data = ULTIMATE_ABILITIES.get(player_class, ULTIMATE_ABILITIES['warrior'])

        # Consume ultimate energy
        self.player_data['resources']['ultimate_energy'] = 0

        enemy = self.combat_state['enemy']

        # Calculate ultimate damage
        base_damage = ultimate_data['damage']
        damage = random.randint(base_damage - 10, base_damage + 20)

        # Check for weakness break
        toughness_damage = ultimate_data.get('toughness_damage', 30)
        damage_type = ultimate_data.get('damage_type', 'physical')
        await self.check_weakness_break(damage_type, toughness_damage)

        # Apply damage multiplier if enemy is broken
        if enemy.get('is_broken', False):
            damage = int(damage * 1.8)
            self.add_log(f"💥 Massive bonus damage on broken enemy!")

        enemy['hp'] = max(0, enemy['hp'] - damage)

        self.add_log(f"🌟 ULTIMATE: {ultimate_data['name']}!")
        self.add_log(f"💥 Dealt {damage} {damage_type} damage with ultimate power!")

        # Ultimate doesn't end turn - player can still act
        await self.update_view()

        if enemy['hp'] <= 0:
            await self.end_combat(victory=True)
            return

    @discord.ui.button(label="🧪 Items", style=discord.ButtonStyle.success, emoji="🧪")
    async def use_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Not your combat!", ephemeral=True)
            return

        # Quick health potion use
        if 'health_potion' in self.player_data['inventory'] and self.player_data['inventory']['health_potion'] > 0:
            self.player_data['inventory']['health_potion'] -= 1
            heal_amount = 60
            old_hp = self.player_data['resources']['hp']
            self.player_data['resources']['hp'] = min(
                self.player_data['resources']['max_hp'], 
                self.player_data['resources']['hp'] + heal_amount
            )
            actual_heal = self.player_data['resources']['hp'] - old_hp

            # Generate small ultimate energy
            ultimate_gain = 5
            old_ultimate = self.player_data['resources'].get('ultimate_energy', 0)
            max_ultimate = self.player_data.get('derived_stats', {}).get('max_ultimate_energy', 100)
            self.player_data['resources']['ultimate_energy'] = min(max_ultimate, old_ultimate + ultimate_gain)

            self.add_log(f"🧪 Used Health Potion! Healed {actual_heal} HP, gained {ultimate_gain} Ultimate Energy!")
            await interaction.response.defer()

            self.combat_state['turn'] = 'monster'
            await self.update_view()
            await asyncio.sleep(1)
            await self.monster_turn()
        else:
            await interaction.response.send_message("❌ No health potions available!", ephemeral=True)

    @discord.ui.button(label="🏃 Flee", style=discord.ButtonStyle.secondary, emoji="🏃")
    async def flee(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Not your combat!", ephemeral=True)
            return

        await interaction.response.defer()

        # Flee always succeeds but has consequences
        self.add_log("🏃 You fled from combat!")
        self.player_data['in_combat'] = False
        self.player_data['resources']['ultimate_energy'] = 0  # Lose ultimate energy
        self.rpg_core.save_player_data(self.player_id, self.player_data)

        embed = await self.create_embed()
        embed.title = "🏃 Fled from Combat"
        embed.color = COLORS['warning']

        try:
            await self.message.edit(content="You escaped but lost all Ultimate Energy!", embed=embed, view=None)
        except discord.NotFound:
            pass

        if self.message.channel.id in active_combats:
            del active_combats[self.message.channel.id]
        self.stop()

class RPGCombat(commands.Cog):
    """Enhanced RPG combat system with tactical mechanics."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="battle", aliases=["fight", "combat"])
    async def battle(self, ctx, monster_name: str = None):
        """Initiate tactical combat with enhanced mechanics."""
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

        if player_data.get('in_combat') or ctx.channel.id in active_combats:
            embed = create_embed("Already Fighting", "Finish your current battle first!", COLORS['warning'])
            await ctx.send(embed=embed)
            return

        if player_data['resources']['hp'] <= 0:
            embed = create_embed("No Health", "You need to heal first! Use `$heal` or rest.", COLORS['error'])
            await ctx.send(embed=embed)
            return

        # Select monster
        if monster_name:
            monster_key = monster_name.lower().replace(' ', '_')
            if monster_key not in TACTICAL_MONSTERS:
                available = ", ".join(TACTICAL_MONSTERS.keys())
                embed = create_embed("Monster Not Found", f"Available: {available}", COLORS['error'])
                await ctx.send(embed=embed)
                return
        else:
            # Level-appropriate random monster
            level = player_data.get('level', 1)
            if level >= 5:
                available_monsters = list(TACTICAL_MONSTERS.keys())
            elif level >= 3:
                available_monsters = ['goblin', 'orc', 'ice_elemental']
            else:
                available_monsters = ['goblin']

            monster_key = random.choice(available_monsters)

        # Start tactical combat
        player_data['in_combat'] = True
        rpg_core.save_player_data(ctx.author.id, player_data)

        embed = discord.Embed(
            title="⚔️ Tactical Combat Initiated!", 
            description="Preparing for enhanced battle with SP and Ultimate systems...", 
            color=COLORS['primary']
        )
        message = await ctx.send(embed=embed)

        await asyncio.sleep(1)

        view = TacticalCombatView(ctx.author.id, monster_key, message, rpg_core)
        active_combats[ctx.channel.id] = view

        await view.update_view()

async def setup(bot):
    await bot.add_cog(RPGCombat(bot))