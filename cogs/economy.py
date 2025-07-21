
import discord
from discord.ext import commands
from replit import db
import random
import asyncio
from datetime import datetime, timedelta
from utils.helpers import create_embed, format_number
from config import COLORS, is_module_enabled
import logging

logger = logging.getLogger(__name__)

class AuctionHouseView(discord.ui.View):
    """View for browsing auction house."""
    
    def __init__(self, user_id):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.current_page = 0

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

        auction_house = db.get("auction_house", {})
        max_pages = (len(auction_house) - 1) // 5 + 1 if auction_house else 1

        if self.current_page < max_pages - 1:
            self.current_page += 1
        await self.update_auction_display(interaction)

    async def update_auction_display(self, interaction):
        """Update the auction house display."""
        auction_house = db.get("auction_house", {})
        
        embed = discord.Embed(
            title="🏛️ Auction House",
            description="*Player-driven marketplace for rare items*",
            color=COLORS['primary']
        )

        if not auction_house:
            embed.add_field(name="No Active Auctions", value="No items currently listed", inline=False)
        else:
            items_per_page = 5
            start_idx = self.current_page * items_per_page
            end_idx = start_idx + items_per_page
            page_items = list(auction_house.items())[start_idx:end_idx]

            auction_text = ""
            for listing_id, auction in page_items:
                current_bid = auction.get('current_bid', auction['starting_bid'])
                time_left = auction['end_time'] - datetime.now().timestamp()
                hours_left = max(0, int(time_left / 3600))
                
                auction_text += f"**ID {listing_id}:** {auction['item_name']}\n"
                auction_text += f"💰 Bid: {format_number(current_bid)} gold\n"
                auction_text += f"⏰ {hours_left}h left\n\n"

            embed.add_field(name="🏷️ Current Auctions", value=auction_text, inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

class Economy(commands.Cog):
    """Economy system for earning and spending money."""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="work")
    async def work(self, ctx):
        """Work to earn money."""
        if not is_module_enabled("economy", ctx.guild.id):
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
        
        # Check cooldown (1 hour)
        last_work = player_data.get('last_work', 0)
        current_time = datetime.now().timestamp()
        cooldown = 3600  # 1 hour
        
        if current_time - last_work < cooldown:
            remaining = cooldown - (current_time - last_work)
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            await ctx.send(f"⏰ You can work again in {minutes}m {seconds}s!")
            return
        
        # Work earnings
        base_earnings = random.randint(50, 150)
        level_bonus = player_data['level'] * 10
        total_earnings = base_earnings + level_bonus
        
        # Update player data
        player_data['gold'] += total_earnings
        player_data['last_work'] = current_time
        rpg_core.save_player_data(ctx.author.id, player_data)
        
        embed = discord.Embed(
            title="💼 Work Complete!",
            description=f"You worked hard and earned **{format_number(total_earnings)}** gold!\n\n"
                       f"Base earnings: {base_earnings}\n"
                       f"Level bonus: {level_bonus}\n\n"
                       f"Total gold: {format_number(player_data['gold'])}",
            color=COLORS['success']
        )
        await ctx.send(embed=embed)

    @commands.command(name="auction")
    async def auction(self, ctx, action: str = None, *, args: str = None):
        """Access the player-driven auction house."""
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
        
        if not action:
            # Show auction house main interface
            view = AuctionHouseView(ctx.author.id)
            embed = discord.Embed(
                title="🏛️ Auction House - Player Economy Hub",
                description="**Welcome to the central marketplace!**\n\n"
                           "Here players buy and sell equipment, materials, and rare items.\n"
                           "All items are player-listed with real market prices!\n\n"
                           "**Available Actions:**\n"
                           "• `$auction sell <item> <start_bid> <buyout>` - List an item\n"
                           "• `$auction bid <listing_id> <amount>` - Bid on an item\n"
                           "• `$auction buyout <listing_id>` - Buy instantly\n"
                           "• `$auction search <item_name>` - Search for items",
                color=COLORS['warning']
            )
            await ctx.send(embed=embed, view=view)
            return
        
        if action == "sell":
            await self.auction_sell(ctx, args, rpg_core, player_data)
        elif action == "bid":
            await self.auction_bid(ctx, args, rpg_core, player_data)
        elif action == "buyout":
            await self.auction_buyout(ctx, args, rpg_core, player_data)
        elif action == "search":
            await self.auction_search(ctx, args)
        else:
            embed = create_embed("Invalid Action", "Use: sell, bid, buyout, or search", COLORS['error'])
            await ctx.send(embed=embed)
    
    async def auction_sell(self, ctx, args, rpg_core, player_data):
        """List an item for sale."""
        if not args:
            await ctx.send("Usage: `$auction sell <item> <starting_bid> <buyout_price>`")
            return
        
        parts = args.split()
        if len(parts) < 3:
            await ctx.send("Usage: `$auction sell <item> <starting_bid> <buyout_price>`")
            return
        
        item_name = parts[0].lower()
        try:
            starting_bid = int(parts[1])
            buyout_price = int(parts[2])
        except ValueError:
            await ctx.send("❌ Bid and buyout prices must be numbers!")
            return
        
        # Check if player has the item
        if item_name not in player_data['inventory'] or player_data['inventory'][item_name] <= 0:
            await ctx.send(f"❌ You don't have any {item_name.replace('_', ' ')}!")
            return
        
        if starting_bid <= 0 or buyout_price <= starting_bid:
            await ctx.send("❌ Invalid prices! Buyout must be higher than starting bid.")
            return
        
        # Remove item from inventory
        player_data['inventory'][item_name] -= 1
        if player_data['inventory'][item_name] <= 0:
            del player_data['inventory'][item_name]
        
        rpg_core.save_player_data(ctx.author.id, player_data)
        
        # Create auction listing
        auction_house = db.get("auction_house", {})
        listing_id = len(auction_house) + 1
        
        end_time = datetime.now() + timedelta(hours=24)  # 24 hour auctions
        
        auction_house[str(listing_id)] = {
            "seller_id": ctx.author.id,
            "item_name": item_name,
            "quantity": 1,
            "starting_bid": starting_bid,
            "current_bid": None,
            "current_bidder": None,
            "buyout_price": buyout_price,
            "end_time": end_time.timestamp(),
            "bids": []
        }
        
        db["auction_house"] = auction_house
        
        embed = discord.Embed(
            title="📝 Item Listed!",
            description=f"**{item_name.replace('_', ' ').title()}** has been listed!\n\n"
                       f"**Starting Bid:** {format_number(starting_bid)} gold\n"
                       f"**Buyout Price:** {format_number(buyout_price)} gold\n"
                       f"**Listing ID:** {listing_id}\n"
                       f"**Duration:** 24 hours",
            color=COLORS['success']
        )
        await ctx.send(embed=embed)
    
    async def auction_bid(self, ctx, args, rpg_core, player_data):
        """Place a bid on an auction."""
        if not args:
            await ctx.send("Usage: `$auction bid <listing_id> <amount>`")
            return
        
        parts = args.split()
        if len(parts) < 2:
            await ctx.send("Usage: `$auction bid <listing_id> <amount>`")
            return
        
        try:
            listing_id = parts[0]
            bid_amount = int(parts[1])
        except ValueError:
            await ctx.send("❌ Invalid listing ID or bid amount!")
            return
        
        auction_house = db.get("auction_house", {})
        if listing_id not in auction_house:
            await ctx.send("❌ Auction listing not found!")
            return
        
        auction = auction_house[listing_id]
        
        # Check if auction has expired
        if auction['end_time'] < datetime.now().timestamp():
            await ctx.send("❌ This auction has expired!")
            return
        
        # Check if player is trying to bid on their own item
        if auction['seller_id'] == ctx.author.id:
            await ctx.send("❌ You cannot bid on your own item!")
            return
        
        # Check if bid is high enough
        minimum_bid = auction['current_bid'] + 1 if auction['current_bid'] else auction['starting_bid']
        if bid_amount < minimum_bid:
            await ctx.send(f"❌ Bid must be at least {format_number(minimum_bid)} gold!")
            return
        
        # Check if player has enough gold
        if player_data['gold'] < bid_amount:
            await ctx.send(f"❌ You need {format_number(bid_amount)} gold to place this bid!")
            return
        
        # Return gold to previous bidder
        if auction['current_bidder']:
            prev_bidder_data = rpg_core.get_player_data(auction['current_bidder'])
            if prev_bidder_data:
                prev_bidder_data['gold'] += auction['current_bid']
                rpg_core.save_player_data(auction['current_bidder'], prev_bidder_data)
        
        # Deduct gold from new bidder
        player_data['gold'] -= bid_amount
        rpg_core.save_player_data(ctx.author.id, player_data)
        
        # Update auction
        auction['current_bid'] = bid_amount
        auction['current_bidder'] = ctx.author.id
        auction['bids'].append({
            "bidder": ctx.author.id,
            "amount": bid_amount,
            "time": datetime.now().timestamp()
        })
        
        auction_house[listing_id] = auction
        db["auction_house"] = auction_house
        
        embed = discord.Embed(
            title="✅ Bid Placed!",
            description=f"You bid **{format_number(bid_amount)} gold** on **{auction['item_name'].replace('_', ' ').title()}**!\n\n"
                       f"You are now the highest bidder!",
            color=COLORS['success']
        )
        await ctx.send(embed=embed)
    
    async def auction_buyout(self, ctx, args, rpg_core, player_data):
        """Buy an item instantly at buyout price."""
        if not args:
            await ctx.send("Usage: `$auction buyout <listing_id>`")
            return
        
        listing_id = args.strip()
        auction_house = db.get("auction_house", {})
        
        if listing_id not in auction_house:
            await ctx.send("❌ Auction listing not found!")
            return
        
        auction = auction_house[listing_id]
        
        # Check if auction has expired
        if auction['end_time'] < datetime.now().timestamp():
            await ctx.send("❌ This auction has expired!")
            return
        
        # Check if player is trying to buy their own item
        if auction['seller_id'] == ctx.author.id:
            await ctx.send("❌ You cannot buy your own item!")
            return
        
        buyout_price = auction['buyout_price']
        
        # Check if player has enough gold
        if player_data['gold'] < buyout_price:
            await ctx.send(f"❌ You need {format_number(buyout_price)} gold for buyout!")
            return
        
        # Return gold to previous bidder if any
        if auction['current_bidder']:
            prev_bidder_data = rpg_core.get_player_data(auction['current_bidder'])
            if prev_bidder_data:
                prev_bidder_data['gold'] += auction['current_bid']
                rpg_core.save_player_data(auction['current_bidder'], prev_bidder_data)
        
        # Complete the transaction
        player_data['gold'] -= buyout_price
        item_name = auction['item_name']
        
        if item_name in player_data['inventory']:
            player_data['inventory'][item_name] += auction['quantity']
        else:
            player_data['inventory'][item_name] = auction['quantity']
        
        rpg_core.save_player_data(ctx.author.id, player_data)
        
        # Pay the seller
        seller_data = rpg_core.get_player_data(auction['seller_id'])
        if seller_data:
            seller_data['gold'] += buyout_price
            rpg_core.save_player_data(auction['seller_id'], seller_data)
        
        # Remove the auction
        del auction_house[listing_id]
        db["auction_house"] = auction_house
        
        embed = discord.Embed(
            title="🛒 Purchase Complete!",
            description=f"You bought **{item_name.replace('_', ' ').title()}** for **{format_number(buyout_price)} gold**!\n\n"
                       f"The item has been added to your inventory.",
            color=COLORS['success']
        )
        await ctx.send(embed=embed)
    
    async def auction_search(self, ctx, search_term):
        """Search for items in the auction house."""
        if not search_term:
            await ctx.send("Usage: `$auction search <item_name>`")
            return
        
        auction_house = db.get("auction_house", {})
        search_term = search_term.lower()
        
        matching_auctions = []
        for listing_id, auction in auction_house.items():
            if search_term in auction['item_name'].lower():
                matching_auctions.append((listing_id, auction))
        
        if not matching_auctions:
            await ctx.send(f"❌ No items found matching '{search_term}'!")
            return
        
        embed = discord.Embed(
            title=f"🔍 Search Results: '{search_term}'",
            color=COLORS['info']
        )
        
        for listing_id, auction in matching_auctions[:10]:  # Show max 10 results
            current_bid = auction['current_bid'] or auction['starting_bid']
            time_left = auction['end_time'] - datetime.now().timestamp()
            hours_left = max(0, int(time_left / 3600))
            
            embed.add_field(
                name=f"ID {listing_id}: {auction['item_name'].replace('_', ' ').title()}",
                value=f"💰 Current: {format_number(current_bid)} gold\n"
                      f"💎 Buyout: {format_number(auction['buyout_price'])} gold\n"
                      f"⏰ {hours_left}h left",
                inline=True
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot))
