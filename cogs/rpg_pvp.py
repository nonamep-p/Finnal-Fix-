
import discord
from discord.ext import commands
from replit import db
import random
import asyncio
from rpg_data.game_data import PVP_ARENAS, TOURNAMENT_BRACKETS, BATTLE_FORMATIONS, BATTLE_EFFECTS
from utils.helpers import create_embed, format_number
from config import COLORS, is_module_enabled
import logging

logger = logging.getLogger(__name__)

class PvPMatchmakingView(discord.ui.View):
    """Advanced PvP matchmaking system."""
    
    def __init__(self, player_id, rpg_core):
        super().__init__(timeout=300)
        self.player_id = player_id
        self.rpg_core = rpg_core
        self.searching = False
        
    @discord.ui.button(label="🔍 Find Ranked Match", style=discord.ButtonStyle.primary)
    async def find_ranked_match(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Not your PvP interface!", ephemeral=True)
            return
            
        player_data = self.rpg_core.get_player_data(self.player_id)
        current_rating = player_data.get('arena_rating', 1000)
        
        # Find appropriate arena
        available_arena = None
        for arena_key, arena_data in PVP_ARENAS.items():
            min_rating, max_rating = arena_data['rating_range']
            if min_rating <= current_rating <= max_rating:
                available_arena = arena_data
                break
                
        if not available_arena:
            await interaction.response.send_message("❌ No arena available for your rating!", ephemeral=True)
            return
            
        # Start matchmaking
        button.disabled = True
        button.label = "🔍 Searching for opponent..."
        await interaction.response.edit_message(view=self)
        
        # Simulate matchmaking (3-8 seconds)
        await asyncio.sleep(random.randint(3, 8))
        
        # Create AI opponent based on player level
        await self.create_pvp_battle(interaction, available_arena)
        
    @discord.ui.button(label="🏆 Join Tournament", style=discord.ButtonStyle.success)
    async def join_tournament(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Not your PvP interface!", ephemeral=True)
            return
            
        # Show tournament selection
        view = TournamentSelectionView(self.player_id, self.rpg_core)
        embed = discord.Embed(
            title="🏆 Tournament Selection",
            description="Choose your tournament tier:",
            color=COLORS['primary']
        )
        
        for tournament_key, tournament_data in TOURNAMENT_BRACKETS.items():
            embed.add_field(
                name=f"{tournament_data['name']}",
                value=f"**Participants:** {tournament_data['participants']}\n"
                      f"**Entry Cost:** {tournament_data['entry_cost']} coins\n"
                      f"**Winner Prize:** {tournament_data['rewards']['winner']['coins']} coins",
                inline=False
            )
            
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    async def create_pvp_battle(self, interaction, arena_data):
        """Create PvP battle against AI opponent."""
        player_data = self.rpg_core.get_player_data(self.player_id)
        
        # Generate AI opponent
        opponent = self.generate_ai_opponent(player_data)
        
        embed = discord.Embed(
            title=f"⚔️ {arena_data['name']} - RANKED MATCH",
            description=f"**Opponent Found!**\n\n"
                       f"🤖 **{opponent['name']}** (Lv.{opponent['level']})\n"
                       f"⭐ **Rating:** {opponent['rating']}\n"
                       f"🏆 **Record:** {opponent['wins']}-{opponent['losses']}\n\n"
                       f"**Match Type:** Best of 3 rounds\n"
                       f"**Stakes:** ±{arena_data['rewards']['arena_tokens']} Arena Tokens",
            color=COLORS['error']
        )
        
        await interaction.edit_original_response(embed=embed, view=None)
        await asyncio.sleep(2)
        
        # Start PvP combat
        combat_view = PvPCombatView(self.player_id, opponent, arena_data, self.rpg_core)
        message = await interaction.followup.send("Starting PvP battle...", wait=True)
        combat_view.message = message
        await combat_view.update_view()
        
    def generate_ai_opponent(self, player_data):
        """Generate AI opponent based on player stats."""
        level_variance = random.randint(-3, 3)
        opponent_level = max(1, player_data['level'] + level_variance)
        
        rating_variance = random.randint(-100, 100)
        opponent_rating = max(0, player_data.get('arena_rating', 1000) + rating_variance)
        
        classes = ['warrior', 'mage', 'rogue', 'archer', 'healer', 'chrono_weave']
        opponent_class = random.choice(classes)
        
        # Generate realistic win/loss record
        total_matches = random.randint(20, 200)
        win_rate = 0.45 + (random.random() * 0.1)  # 45-55% win rate
        wins = int(total_matches * win_rate)
        losses = total_matches - wins
        
        opponent_names = [
            "ShadowStrike", "BladeDancer", "FrostMage", "ArcaneTempest", 
            "StealthHunter", "IronGuard", "LightningBolt", "ChaosReign",
            "MysticSage", "CrimsonFury", "VoidWalker", "StarShaper"
        ]
        
        return {
            'name': random.choice(opponent_names),
            'level': opponent_level,
            'class': opponent_class,
            'rating': opponent_rating,
            'wins': wins,
            'losses': losses,
            'is_ai': True
        }

class PvPCombatView(discord.ui.View):
    """Advanced PvP combat with team formations."""
    
    def __init__(self, player_id, opponent, arena_data, rpg_core):
        super().__init__(timeout=600)
        self.player_id = player_id
        self.opponent = opponent
        self.arena_data = arena_data
        self.rpg_core = rpg_core
        
        # Combat state
        self.rounds_won = {'player': 0, 'opponent': 0}
        self.current_round = 1
        self.max_rounds = 3
        
        # Load player data
        self.player_data = self.rpg_core.get_player_data(player_id)
        
    async def update_view(self):
        """Update PvP combat interface."""
        embed = discord.Embed(
            title=f"⚔️ PvP Round {self.current_round}/{self.max_rounds}",
            description=f"**{self.player_data['name']}** vs **{self.opponent['name']}**",
            color=COLORS['error']
        )
        
        # Round score
        embed.add_field(
            name="🏆 Match Score",
            value=f"**You:** {self.rounds_won['player']} rounds\n**Opponent:** {self.rounds_won['opponent']} rounds",
            inline=True
        )
        
        # Current arena
        embed.add_field(
            name="🏟️ Arena",
            value=f"**{self.arena_data['name']}**\nRanked PvP Battle",
            inline=True
        )
        
        try:
            await self.message.edit(embed=embed, view=self)
        except discord.NotFound:
            pass
            
    @discord.ui.button(label="⚔️ Attack", style=discord.ButtonStyle.danger)
    async def attack_opponent(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("Not your PvP match!", ephemeral=True)
            return
            
        await interaction.response.defer()
        
        # Simulate round result
        player_power = self.calculate_combat_power(self.player_data)
        opponent_power = self.calculate_opponent_power()
        
        # Add some randomness for exciting matches
        player_roll = random.uniform(0.8, 1.2)
        opponent_roll = random.uniform(0.8, 1.2)
        
        player_final = player_power * player_roll
        opponent_final = opponent_power * opponent_roll
        
        if player_final > opponent_final:
            self.rounds_won['player'] += 1
            result_text = f"🏆 **Round {self.current_round} Victory!**\nYou outmaneuvered your opponent!"
            result_color = COLORS['success']
        else:
            self.rounds_won['opponent'] += 1
            result_text = f"💀 **Round {self.current_round} Defeat!**\nYour opponent was stronger this round."
            result_color = COLORS['error']
            
        self.current_round += 1
        
        # Check for match end
        if self.rounds_won['player'] >= 2 or self.rounds_won['opponent'] >= 2:
            await self.end_pvp_match(interaction)
        else:
            embed = discord.Embed(
                title=result_text,
                description=f"Preparing for Round {self.current_round}...",
                color=result_color
            )
            await interaction.edit_original_response(embed=embed, view=None)
            await asyncio.sleep(2)
            await self.update_view()
            
    async def end_pvp_match(self, interaction):
        """Handle PvP match conclusion."""
        player_won = self.rounds_won['player'] > self.rounds_won['opponent']
        
        # Calculate rating changes
        rating_change = self.calculate_rating_change(player_won)
        
        # Update player data
        if player_won:
            self.player_data['arena_wins'] += 1
            self.player_data['arena_rating'] += rating_change
            tokens_gained = self.arena_data['rewards']['arena_tokens']
            coins_gained = self.arena_data['rewards']['coins_per_win']
            
            self.player_data['arena_tokens'] = self.player_data.get('arena_tokens', 0) + tokens_gained
            self.player_data['gold'] += coins_gained
            
            result_title = "🏆 VICTORY! 🏆"
            result_desc = (f"Magnificent PvP victory!\n\n"
                          f"**Rewards:**\n"
                          f"• +{rating_change} Arena Rating\n"
                          f"• +{tokens_gained} Arena Tokens\n"
                          f"• +{coins_gained} Coins")
            result_color = COLORS['success']
        else:
            self.player_data['arena_losses'] += 1
            self.player_data['arena_rating'] = max(0, self.player_data['arena_rating'] + rating_change)
            
            result_title = "💀 DEFEAT 💀"
            result_desc = (f"A valiant effort, but not enough this time.\n\n"
                          f"**Changes:**\n"
                          f"• {rating_change} Arena Rating\n"
                          f"• Learn from this defeat!")
            result_color = COLORS['error']
            
        self.rpg_core.save_player_data(self.player_id, self.player_data)
        
        embed = discord.Embed(
            title=result_title,
            description=result_desc,
            color=result_color
        )
        
        embed.add_field(
            name="📊 Match Summary",
            value=f"**Final Score:** {self.rounds_won['player']}-{self.rounds_won['opponent']}\n"
                  f"**New Rating:** {self.player_data['arena_rating']}\n"
                  f"**Total Record:** {self.player_data.get('arena_wins', 0)}-{self.player_data.get('arena_losses', 0)}",
            inline=False
        )
        
        await interaction.edit_original_response(embed=embed, view=None)
        self.stop()
        
    def calculate_combat_power(self, player_data):
        """Calculate player's combat power for PvP."""
        base_power = player_data['level'] * 100
        stats_power = sum(player_data['stats'].values()) * 10
        equipment_power = len(player_data.get('inventory', {})) * 5
        
        return base_power + stats_power + equipment_power
        
    def calculate_opponent_power(self):
        """Calculate AI opponent's combat power."""
        return self.opponent['level'] * 100 + random.randint(50, 150)
        
    def calculate_rating_change(self, won):
        """Calculate ELO-style rating change."""
        base_change = 25
        if won:
            return base_change + random.randint(0, 10)
        else:
            return -(base_change - random.randint(0, 10))

class TournamentSelectionView(discord.ui.View):
    """Tournament selection interface."""
    
    def __init__(self, player_id, rpg_core):
        super().__init__(timeout=300)
        self.player_id = player_id
        self.rpg_core = rpg_core
        
    @discord.ui.button(label="🥉 Daily Tournament", style=discord.ButtonStyle.secondary)
    async def join_daily(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.join_tournament(interaction, 'daily_tournament')
        
    @discord.ui.button(label="🏆 Weekly Championship", style=discord.ButtonStyle.primary)
    async def join_weekly(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.join_tournament(interaction, 'weekly_championship')
        
    async def join_tournament(self, interaction, tournament_key):
        """Handle tournament registration."""
        tournament_data = TOURNAMENT_BRACKETS[tournament_key]
        player_data = self.rpg_core.get_player_data(self.player_id)
        
        entry_cost = tournament_data['entry_cost']
        
        if player_data['gold'] < entry_cost:
            await interaction.response.send_message(
                f"❌ Not enough gold! Need {entry_cost} coins to enter.", 
                ephemeral=True
            )
            return
            
        # Deduct entry fee
        player_data['gold'] -= entry_cost
        self.rpg_core.save_player_data(self.player_id, player_data)
        
        embed = discord.Embed(
            title=f"🏆 Tournament Registration Successful!",
            description=f"You've entered the **{tournament_data['name']}**!\n\n"
                       f"**Entry Fee:** {entry_cost} coins\n"
                       f"**Duration:** {tournament_data['duration_hours']} hours\n"
                       f"**Participants:** {tournament_data['participants']}\n\n"
                       f"Tournament battles will begin soon!\n"
                       f"Check back for match updates.",
            color=COLORS['success']
        )
        
        await interaction.response.edit_message(embed=embed, view=None)

class RPGPvP(commands.Cog):
    """Comprehensive PvP system with rankings and tournaments."""
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="pvp")
    async def pvp_arena(self, ctx):
        """Enter the PvP arena for ranked battles."""
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
            
        if player_data['level'] < 10:
            embed = create_embed(
                "Level Too Low", 
                f"You need Level 10 to enter PvP! Current: {player_data['level']}", 
                COLORS['warning']
            )
            await ctx.send(embed=embed)
            return
            
        if player_data.get('in_combat'):
            embed = create_embed("Already Fighting", "Finish your current battle first!", COLORS['warning'])
            await ctx.send(embed=embed)
            return
            
        view = PvPMatchmakingView(ctx.author.id, rpg_core)
        
        # Determine current arena
        current_rating = player_data.get('arena_rating', 1000)
        current_arena = None
        for arena_key, arena_data in PVP_ARENAS.items():
            min_rating, max_rating = arena_data['rating_range']
            if min_rating <= current_rating <= max_rating:
                current_arena = arena_data
                break
                
        embed = discord.Embed(
            title="⚔️ PvP Arena - Competitive Combat",
            description="Welcome to the ultimate test of combat skill!",
            color=COLORS['error']
        )
        
        if current_arena:
            embed.add_field(
                name=f"🏟️ Current Arena: {current_arena['name']}",
                value=f"**Rating Range:** {current_arena['rating_range'][0]}-{current_arena['rating_range'][1]}",
                inline=False
            )
            
        # Player PvP stats
        wins = player_data.get('arena_wins', 0)
        losses = player_data.get('arena_losses', 0)
        total_matches = wins + losses
        win_rate = int((wins / total_matches) * 100) if total_matches > 0 else 0
        
        embed.add_field(
            name="📊 Your PvP Stats",
            value=f"**Rating:** {current_rating}\n"
                  f"**Record:** {wins}-{losses} ({win_rate}%)\n"
                  f"**Arena Tokens:** {player_data.get('arena_tokens', 0)}",
            inline=True
        )
        
        await ctx.send(embed=embed, view=view)
        
    @commands.command(name="rankings")
    async def pvp_rankings(self, ctx):
        """View PvP leaderboards."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return
            
        # This would pull from database of all players
        embed = discord.Embed(
            title="🏆 PvP Arena Rankings",
            description="Top warriors in competitive combat:",
            color=COLORS['primary']
        )
        
        # Sample leaderboard (would be real data in full implementation)
        sample_rankings = [
            {"name": "ChampionDestroyer", "rating": 2847, "record": "247-23"},
            {"name": "BladeMaster2000", "rating": 2756, "record": "198-31"},
            {"name": "MysticSage", "rating": 2643, "record": "156-22"},
        ]
        
        ranking_text = ""
        for i, player in enumerate(sample_rankings, 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            ranking_text += f"{emoji} **{player['name']}** - {player['rating']} ({player['record']})\n"
            
        embed.add_field(name="Top Players", value=ranking_text, inline=False)
        embed.set_footer(text="Compete in ranked matches to climb the leaderboard!")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(RPGPvP(bot))
