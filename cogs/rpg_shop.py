import discord
from discord.ext import commands
from rpg_data.game_data import ITEMS, RARITY_COLORS
from utils.helpers import create_embed, format_number
from config import COLORS, is_module_enabled
from utils.database import get_user_rpg_data, update_user_rpg_data
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

class ItemDetailView(discord.ui.View):
    """Detailed view for a specific item."""

    def __init__(self, item_key, item_data, user_id, rpg_core):
        super().__init__(timeout=300)
        self.item_key = item_key
        self.item_data = item_data
        self.user_id = user_id
        self.rpg_core = rpg_core

    @discord.ui.button(label="💰 Buy Item", style=discord.ButtonStyle.success)
    async def buy_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your shop!", ephemeral=True)
            return

        player_data = self.rpg_core.get_player_data(self.user_id)
        if not player_data:
            await interaction.response.send_message("❌ Player data not found!", ephemeral=True)
            return

        price = self.item_data.get('price', 0)
        if player_data['gold'] < price:
            await interaction.response.send_message(
                f"❌ Insufficient gold! You need {format_number(price)} but only have {format_number(player_data['gold'])}.",
                ephemeral=True
            )
            return

        # Purchase the item
        player_data['gold'] -= price
        if self.item_key in player_data['inventory']:
            player_data['inventory'][self.item_key] += 1
        else:
            player_data['inventory'][self.item_key] = 1

        self.rpg_core.save_player_data(self.user_id, player_data)

        embed = create_embed(
            "✅ Purchase Successful!",
            f"You bought **{self.item_data['name']}** for {format_number(price)} gold!\n\n"
            f"**Remaining Gold:** {format_number(player_data['gold'])}",
            COLORS['success']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label="🏷️ List on Auction", style=discord.ButtonStyle.primary)
    async def list_auction(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your shop!", ephemeral=True)
            return

        # Check if player owns this item
        player_data = self.rpg_core.get_player_data(self.user_id)
        if not player_data or player_data['inventory'].get(self.item_key, 0) <= 0:
            await interaction.response.send_message("❌ You don't own this item!", ephemeral=True)
            return

        modal = AuctionListModal(self.item_key, self.item_data, self.user_id, self.rpg_core)
        await interaction.response.send_modal(modal)

class AuctionListModal(discord.ui.Modal):
    """Modal for listing items on auction."""

    def __init__(self, item_key, item_data, user_id, rpg_core):
        super().__init__(title=f"List {item_data['name']} on Auction")
        self.item_key = item_key
        self.item_data = item_data
        self.user_id = user_id
        self.rpg_core = rpg_core

        self.price_input = discord.ui.TextInput(
            label="Starting Price",
            placeholder="Enter starting bid price in gold",
            max_length=10,
            required=True
        )
        self.add_item(self.price_input)

        self.duration_input = discord.ui.TextInput(
            label="Duration (hours)",
            placeholder="Enter auction duration (1-168 hours)",
            max_length=3,
            default="24",
            required=True
        )
        self.add_item(self.duration_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            price = int(self.price_input.value)
            duration = int(self.duration_input.value)

            if price <= 0 or duration <= 0 or duration > 168:
                await interaction.response.send_message("❌ Invalid price or duration!", ephemeral=True)
                return

            # Create auction listing
            listing_id = f"auction_{self.user_id}_{int(datetime.now().timestamp())}"
            listing = {
                'id': listing_id,
                'seller_id': self.user_id,
                'item_key': self.item_key,
                'item_name': self.item_data['name'],
                'starting_price': price,
                'current_bid': price,
                'highest_bidder': None,
                'bids': [],
                'created_at': datetime.now().isoformat(),
                'expires_at': (datetime.now() + timedelta(hours=duration)).isoformat(),
                'status': 'active'
            }

            # Remove item from player inventory
            player_data = self.rpg_core.get_player_data(self.user_id)
            player_data['inventory'][self.item_key] -= 1
            if player_data['inventory'][self.item_key] <= 0:
                del player_data['inventory'][self.item_key]

            # Add to auction listings
            from replit import db
            auction_listings = db.get('auction_listings', [])
            auction_listings.append(listing)
            db['auction_listings'] = auction_listings

            self.rpg_core.save_player_data(self.user_id, player_data)

            embed = create_embed(
                "🏷️ Item Listed on Auction!",
                f"**{self.item_data['name']}** has been listed for {duration} hours\n"
                f"**Starting Price:** {format_number(price)} gold",
                COLORS['success']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError:
            await interaction.response.send_message("❌ Please enter valid numbers!", ephemeral=True)

class AuctionView(discord.ui.View):
    """View for browsing auction listings."""

    def __init__(self, user_id, rpg_core):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.rpg_core = rpg_core
        self.current_page = 0

    async def update_auction_display(self, interaction):
        """Update the auction display."""
        from replit import db
        auction_listings = db.get('auction_listings', [])

        # Filter active auctions
        now = datetime.now()
        active_auctions = []
        for listing in auction_listings:
            expires_at = datetime.fromisoformat(listing['expires_at'])
            if expires_at > now and listing['status'] == 'active':
                active_auctions.append(listing)

        embed = discord.Embed(
            title="🏛️ Auction House",
            description="*Welcome to the auction house! Buy and sell items with other players.*",
            color=COLORS['primary']
        )

        if not active_auctions:
            embed.add_field(name="No Active Auctions", value="No items are currently being auctioned.", inline=False)
        else:
            items_per_page = 5
            start_idx = self.current_page * items_per_page
            end_idx = start_idx + items_per_page
            page_auctions = active_auctions[start_idx:end_idx]

            auction_text = ""
            for auction in page_auctions:
                time_left = datetime.fromisoformat(auction['expires_at']) - datetime.now()
                hours_left = max(0, int(time_left.total_seconds() / 3600))

                auction_text += (f"**{auction['item_name']}**\n"
                               f"Current Bid: {format_number(auction['current_bid'])} gold\n"
                               f"Time Left: {hours_left}h\n"
                               f"Bids: {len(auction['bids'])}\n\n")

            embed.add_field(name="🏷️ Current Auctions", value=auction_text, inline=False)

            # Page info
            total_pages = (len(active_auctions) - 1) // items_per_page + 1 if active_auctions else 1
            embed.set_footer(text=f"Page {self.current_page + 1} of {total_pages}")

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your auction view!", ephemeral=True)
            return

        if self.current_page > 0:
            self.current_page -= 1
        await self.update_auction_display(interaction)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your auction view!", ephemeral=True)
            return

        from replit import db
        auction_listings = db.get('auction_listings', [])
        active_auctions = [a for a in auction_listings if a['status'] == 'active']
        max_pages = (len(active_auctions) - 1) // 5 + 1 if active_auctions else 1

        if self.current_page < max_pages - 1:
            self.current_page += 1
        await self.update_auction_display(interaction)

    @discord.ui.button(label="💰 Place Bid", style=discord.ButtonStyle.success)
    async def place_bid(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your auction view!", ephemeral=True)
            return

        modal = BidModal(self.user_id, self.rpg_core)
        await interaction.response.send_modal(modal)

class BidModal(discord.ui.Modal):
    """Modal for placing bids."""

    def __init__(self, user_id, rpg_core):
        super().__init__(title="Place Bid")
        self.user_id = user_id
        self.rpg_core = rpg_core

        self.auction_id_input = discord.ui.TextInput(
            label="Auction ID",
            placeholder="Enter the auction ID you want to bid on",
            max_length=50
        )
        self.add_item(self.auction_id_input)

        self.bid_input = discord.ui.TextInput(
            label="Bid Amount",
            placeholder="Enter your bid amount in gold",
            max_length=10
        )
        self.add_item(self.bid_input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            auction_id = self.auction_id_input.value
            bid_amount = int(self.bid_input.value)

            from replit import db
            auction_listings = db.get('auction_listings', [])

            # Find the auction
            auction = None
            for listing in auction_listings:
                if listing['id'] == auction_id:
                    auction = listing
                    break

            if not auction:
                await interaction.response.send_message("❌ Auction not found!", ephemeral=True)
                return

            if auction['seller_id'] == self.user_id:
                await interaction.response.send_message("❌ You cannot bid on your own auction!", ephemeral=True)
                return

            if bid_amount <= auction['current_bid']:
                await interaction.response.send_message(f"❌ Bid must be higher than current bid of {format_number(auction['current_bid'])} gold!", ephemeral=True)
                return

            player_data = self.rpg_core.get_player_data(self.user_id)
            if player_data['gold'] < bid_amount:
                await interaction.response.send_message("❌ Insufficient gold!", ephemeral=True)
                return

            # Place the bid
            auction['current_bid'] = bid_amount
            auction['highest_bidder'] = self.user_id
            auction['bids'].append({
                'bidder_id': self.user_id,
                'amount': bid_amount,
                'timestamp': datetime.now().isoformat()
            })

            db['auction_listings'] = auction_listings

            embed = create_embed(
                "✅ Bid Placed!",
                f"You bid {format_number(bid_amount)} gold on **{auction['item_name']}**!",
                COLORS['success']
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        except ValueError:
            await interaction.response.send_message("❌ Please enter a valid bid amount!", ephemeral=True)

class ShopView(discord.ui.View):
    def __init__(self, rpg_core_cog, user_id):
        super().__init__(timeout=300)
        self.rpg_core = rpg_core_cog
        self.user_id = user_id
        self.current_category = "weapons"
        self.current_page = 0

    async def update_shop_display(self, interaction):
        """Update the shop display with current category and page."""
        player_data = self.rpg_core.get_player_data(self.user_id)
        if not player_data:
            await interaction.response.send_message("❌ Player data not found!", ephemeral=True)
            return

        # Filter items by category
        category_items = {k: v for k, v in ITEMS.items() if v['type'] == self.current_category}

        embed = discord.Embed(
            title=f"🏪 Plagg's Mystical Shop - {self.current_category.title()}",
            description=f"*Welcome to my shop! I've got the finest gear this side of Paris!*\n\n💰 **Your Gold:** {format_number(player_data['gold'])}",
            color=COLORS['warning']
        )

        if not category_items:
            embed.add_field(name="No Items", value="No items available in this category.", inline=False)
        else:
            items_list = list(category_items.items())
            items_per_page = 5
            start_idx = self.current_page * items_per_page
            end_idx = start_idx + items_per_page
            page_items = items_list[start_idx:end_idx]

            items_text = ""
            for i, (item_key, item_data) in enumerate(page_items, 1):
                rarity_color = "⚪" if item_data['rarity'] == 'common' else "🟢" if item_data['rarity'] == 'uncommon' else "🔵" if item_data['rarity'] == 'rare' else "🟣"
                price = item_data.get('price', 0)
                items_text += f"{rarity_color} **{item_data['name']}** - {format_number(price)} gold\n"

                # Add stats preview
                stats_preview = []
                if item_data.get('attack'):
                    stats_preview.append(f"⚔️{item_data['attack']}")
                if item_data.get('defense'):
                    stats_preview.append(f"🛡️{item_data.get('defense', 0)}")
                if item_data.get('hp'):
                    stats_preview.append(f"❤️{item_data.get('hp', 0)}")
                if item_data.get('mana'):
                    stats_preview.append(f"💙{item_data.get('mana', 0)}")
                if stats_preview:
                    items_text += f"   *{' | '.join(stats_preview)}*\n"
                items_text += f"   *{item_data.get('description', 'No description')}*\n\n"

            embed.add_field(name="📦 Available Items", value=items_text or "No items on this page.", inline=False)

            # Page info
            total_pages = (len(items_list) - 1) // items_per_page + 1 if items_list else 1
            embed.set_footer(text=f"Page {self.current_page + 1} of {total_pages} | Use /iteminfo <name> for detailed stats")

        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.select(
        placeholder="Choose item category...",
        options=[
            discord.SelectOption(label="Weapons", value="weapon", emoji="⚔️"),
            discord.SelectOption(label="Armor", value="armor", emoji="🛡️"),
            discord.SelectOption(label="Consumables", value="consumable", emoji="🧪"),
            discord.SelectOption(label="Accessories", value="accessory", emoji="💎"),
            discord.SelectOption(label="Artifacts", value="artifact", emoji="✨")
        ]
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your shop!", ephemeral=True)
            return

        self.current_category = select.values[0]
        self.current_page = 0
        await self.update_shop_display(interaction)

    @discord.ui.button(label="◀ Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your shop!", ephemeral=True)
            return

        if self.current_page > 0:
            self.current_page -= 1
        await self.update_shop_display(interaction)

    @discord.ui.button(label="Next ▶", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your shop!", ephemeral=True)
            return

        category_items = {k: v for k, v in ITEMS.items() if v['type'] == self.current_category}
        max_pages = (len(category_items) - 1) // 5 + 1 if category_items else 1

        if self.current_page < max_pages - 1:
            self.current_page += 1
        await self.update_shop_display(interaction)

    @discord.ui.button(label="🏛️ Auction House", style=discord.ButtonStyle.primary)
    async def auction_house(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ This is not your shop!", ephemeral=True)
            return

        auction_view = AuctionView(self.user_id, self.rpg_core)
        embed = discord.Embed(
            title="🏛️ Auction House",
            description="*Welcome to the auction house! Buy and sell items with other players.*",
            color=COLORS['primary']
        )
        await interaction.response.edit_message(embed=embed, view=auction_view)

class RPGShop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rpgshop", aliases=["store"])
    async def rpg_shop(self, ctx):
        """Browse Plagg's mystical item shop."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        rpg_core = self.bot.get_cog('RPGCore')
        if not rpg_core:
            await ctx.send("❌ RPG system not loaded properly.")
            return

        player_data = rpg_core.get_player_data(ctx.author.id)
        if not player_data:
            embed = create_embed(
                "No Profile Found",
                "You need to `$startrpg` first!",
                COLORS['error']
            )
            await ctx.send(embed=embed)
            return

        view = ShopView(rpg_core, ctx.author.id)

        embed = discord.Embed(
            title="🏪 Plagg's Mystical Shop",
            description=f"*Welcome to my shop! I've got the finest gear this side of Paris!*\n\n💰 **Your Gold:** {format_number(player_data['gold'])}",
            color=COLORS['warning']
        )

        # Show weapons by default
        weapon_items = {k: v for k, v in ITEMS.items() if v['type'] == 'weapon'}
        items_text = ""
        for item_key, item_data in list(weapon_items.items())[:5]:
            rarity_color = "⚪" if item_data['rarity'] == 'common' else "🟢" if item_data['rarity'] == 'uncommon' else "🔵"
            price = item_data.get('price', 0)
            items_text += f"{rarity_color} **{item_data['name']}** - {format_number(price)} gold\n"
            if item_data.get('attack'):
                items_text += f"   *⚔️{item_data['attack']}*\n"
            items_text += f"   *{item_data.get('description', 'No description')}*\n\n"

        embed.add_field(name="⚔️ Weapons", value=items_text or "No weapons available.", inline=False)
        embed.set_footer(text="Use the dropdown to browse categories, then use $buy <item name> to purchase")

        await ctx.send(embed=embed, view=view)

    @commands.command(name="iteminfo")
    async def item_info(self, ctx, *, item_name: str):
        """Get detailed information about an item."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        rpg_core = self.bot.get_cog('RPGCore')
        if not rpg_core:
            await ctx.send("❌ RPG system not loaded properly.")
            return

        # Find the item
        item_data = None
        item_key = None
        for key, data in ITEMS.items():
            if key == item_name.lower().replace(" ", "_") or data['name'].lower() == item_name.lower():
                item_data = data
                item_key = key
                break

        if not item_data:
            await ctx.send(f"❌ Item '{item_name}' not found!")
            return

        rarity_color = RARITY_COLORS.get(item_data['rarity'], 0x808080)
        embed = discord.Embed(
            title=f"{item_data['name']}",
            description=item_data.get('description', 'No description available'),
            color=rarity_color
        )

        # Basic info
        embed.add_field(name="Type", value=item_data['type'].title(), inline=True)
        embed.add_field(name="Rarity", value=item_data['rarity'].title(), inline=True)
        if 'price' in item_data:
            embed.add_field(name="Price", value=format_number(item_data['price']), inline=True)

        # Stats
        stats_text = ""
        if item_data.get('attack'):
            stats_text += f"⚔️ **Attack:** {item_data['attack']}\n"
        if item_data.get('defense'):
            stats_text += f"🛡️ **Defense:** {item_data['defense']}\n"
        if item_data.get('hp'):
            stats_text += f"❤️ **HP Bonus:** {item_data['hp']}\n"
        if item_data.get('mana'):
            stats_text += f"💙 **Mana Bonus:** {item_data['mana']}\n"
        if item_data.get('critical_chance'):
            stats_text += f"💥 **Crit Chance:** {item_data['critical_chance']}%\n"
        if item_data.get('critical_damage'):
            stats_text += f"⚡ **Crit Damage:** {item_data['critical_damage']}%\n"

        if stats_text:
            embed.add_field(name="📊 Stats", value=stats_text, inline=False)

        # Special effects
        if item_data.get('effects'):
            effects_text = ""
            for effect in item_data['effects']:
                effects_text += f"✨ {effect}\n"
            embed.add_field(name="🌟 Special Effects", value=effects_text, inline=False)

        # Set bonuses for artifacts
        if item_data.get('set_bonus'):
            embed.add_field(name="🔗 Set Bonus", value=item_data['set_bonus'], inline=False)

        view = ItemDetailView(item_key, item_data, ctx.author.id, rpg_core)
        await ctx.send(embed=embed, view=view)

    @commands.command(name="buy")
    async def buy_item(self, ctx, *, item_name: str):
        """Buy an item from the shop."""
        if not is_module_enabled("rpg", ctx.guild.id):
            return

        rpg_core = self.bot.get_cog('RPGCore')
        if not rpg_core:
            await ctx.send("❌ RPG system not loaded properly.")
            return

        player_data = rpg_core.get_player_data(ctx.author.id)
        if not player_data:
            embed = create_embed(
                "No Profile Found",
                "You need to `$startrpg` first!",
                COLORS['error']
            )
            await ctx.send(embed=embed)
            return

        # Find the item
        item_data = None
        item_key = None
        for key, data in ITEMS.items():
            if key == item_name.lower().replace(" ", "_") or data['name'].lower() == item_name.lower():
                item_data = data
                item_key = key
                break

        if not item_data:
            # Show similar items
            similar_items = []
            for key, data in ITEMS.items():
                if item_name.lower() in data['name'].lower():
                    similar_items.append(data['name'])

            error_msg = f"❌ Item '{item_name}' not found!"
            if similar_items:
                error_msg += f"\n\n**Did you mean:**\n" + "\n".join(f"• {item}" for item in similar_items[:5])

            await ctx.send(error_msg)
            return

        price = item_data.get('price', 0)
        if player_data['gold'] < price:
            embed = create_embed(
                "Insufficient Gold",
                f"You need {format_number(price)} gold but only have {format_number(player_data['gold'])}.",
                COLORS['error']
            )
            await ctx.send(embed=embed)
            return

        # Purchase the item
        player_data['gold'] -= price
        if item_key in player_data['inventory']:
            player_data['inventory'][item_key] += 1
        else:
            player_data['inventory'][item_key] = 1

        rpg_core.save_player_data(ctx.author.id, player_data)

        rarity_color = RARITY_COLORS.get(item_data['rarity'], 0x808080)
        embed = discord.Embed(
            title="✅ Purchase Successful!",
            description=f"You bought **{item_data['name']}** for {format_number(price)} gold!",
            color=rarity_color
        )
        embed.add_field(name="Remaining Gold", value=format_number(player_data['gold']), inline=True)
        embed.add_field(name="Item Type", value=item_data['type'].title(), inline=True)

        if item_data.get('attack'):
            embed.add_field(name="Attack", value=item_data['attack'], inline=True)
        if item_data.get('defense'):
            embed.add_field(name="Defense", value=item_data.get('defense', 0), inline=True)

        embed.set_footer(text="Use $equip <item> to equip gear or $use <item> for consumables")
        await ctx.send(embed=embed)

    

async def setup(bot):
    await bot.add_cog(RPGShop(bot))