
# 🧀 Plagg Bot - Discord RPG Bot

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Discord.py](https://img.shields.io/badge/discord.py-2.3+-blue.svg)](https://github.com/Rapptz/discord.py)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Replit](https://img.shields.io/badge/hosting-Replit-orange.svg)](https://replit.com)

A comprehensive Discord RPG bot featuring **Plagg**, the Kwami of Destruction from Miraculous Ladybug. Experience tactical combat, character progression, and economy systems with a chaotic cheese-loving personality!

## 🎮 Features Overview

### ⚔️ **Advanced RPG System**
- **7 Unique Classes**: Warrior, Mage, Rogue, Archer, Healer, Battlemage, Chrono Knight
- **Tactical Combat**: Strategic turn-based battles with SP system and Ultimate abilities
- **Character Progression**: XP-based leveling with stat allocation and skill trees
- **Hidden Classes**: Unlock legendary classes through achievements
- **Miraculous Paths**: Choose specialized combat paths (Destruction, Preservation, Abundance, Hunt)

### 🛡️ **Equipment & Items System**
- **8 Rarity Tiers**: Common to Cosmic with unique effects
- **Kwami Artifacts**: Set equipment with powerful bonuses
- **300+ Items**: Weapons, armor, accessories, consumables
- **Owner Privileges**: Exclusive divine-tier equipment
- **Dynamic Stats**: Attack, Defense, HP, Mana, special effects

### 🏰 **Adventure & Activities**
- **Tactical Combat**: Weakness system, toughness breaking, follow-up attacks
- **Dungeon System**: Multi-floor dungeons with boss encounters
- **Mini-Games**: Hunting, exploring, fishing, gambling
- **Miraculous Box**: Special artifact farming area
- **Quest System**: Daily, weekly, and story quests

### 🏛️ **Social & Economy**
- **Guild System**: Create/join guilds with level-based perks
- **PvP Arena**: Ranked combat with rating system
- **Auction House**: Player-to-player item trading
- **Crafting System**: Create equipment from materials
- **Achievement System**: 50+ achievements with rewards

### 🤖 **AI & Moderation**
- **Google Gemini Integration**: Advanced AI conversations
- **Moderation Tools**: Comprehensive admin commands
- **Economy System**: Work, daily rewards, banking
- **Help System**: Interactive command documentation
- **24/7 Uptime**: Web server keep-alive mechanism

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Discord Bot Token
- Google Gemini API Key (optional for AI features)
- Replit account (recommended hosting)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/plagg-bot.git
cd plagg-bot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```env
DISCORD_BOT_TOKEN=your_discord_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

4. **Run the bot:**
```bash
python main.py
```

### Replit Deployment (Recommended)

1. Import this repository to Replit
2. Add secrets in Replit's environment:
   - `DISCORD_BOT_TOKEN`: Your Discord bot token
   - `GEMINI_API_KEY`: Your Google Gemini API key
3. Click the "Run" button

## 📖 Command Guide

### 🎮 **Core RPG Commands**
```
$startrpg           - Create your character
$profile [@user]    - View character stats
$classes           - View all available classes
$allocate <stat> <points> - Allocate stat points
$path              - Choose your Miraculous Path (Level 20+)
```

### ⚔️ **Combat Commands**
```
$battle [monster]  - Start tactical combat
$hunt             - Hunt monsters for loot
$arena            - Enter PvP arena
$skills           - View your abilities
```

### 🎒 **Inventory & Equipment**
```
$inventory        - View your items
$equip <item>     - Equip gear
$unequip <slot>   - Remove equipment
$use <item>       - Use consumables
$artifacts        - Manage Kwami Artifacts
```

### 🏪 **Economy Commands**
```
$work             - Earn gold through work
$daily            - Claim daily rewards
$shop             - Browse item shop
$auction          - Access auction house
$balance          - Check your gold
```

### 🎯 **Activities**
```
$explore          - Explore for treasure
$fish             - Try your luck fishing
$gamble <amount>  - Risk gold for rewards
$miraculous       - Enter Miraculous Box
$quest            - View available quests
```

### 🏰 **Social Features**
```
$guild [action]   - Guild management
$achievements     - View your progress
$leaderboard      - Server rankings
$trade <user>     - Trade with players
```

### 👑 **Owner Commands** (UserID: 1297013439125917766)
```
$ownerhelp                    - View admin commands
$spawn <user> <item> <qty>    - Spawn items
$setstat <user> <stat> <value> - Modify stats
$unlock <user> <type> <content> - Unlock content
```

## 🔧 Technical Architecture

### **Core Structure**
```
plagg-bot/
├── cogs/                 # Bot modules
│   ├── rpg_core.py      # Character system
│   ├── rpg_combat.py    # Combat mechanics
│   ├── rpg_games.py     # Activities & games
│   ├── economy.py       # Economy system
│   ├── ai_chatbot.py    # AI integration
│   └── moderation.py    # Admin tools
├── rpg_data/            # Game data
│   └── game_data.py     # Items, classes, monsters
├── utils/               # Utilities
│   ├── database.py      # Data management
│   ├── helpers.py       # Helper functions
│   └── achievements.py  # Achievement system
├── main.py              # Bot entry point
├── config.py            # Configuration
└── web_server.py        # Keep-alive server
```

### **Database Schema**
- **Replit DB**: Key-value storage for persistence
- **Player Data**: Stats, inventory, progress
- **Guild Data**: Guild info and member lists
- **Global Data**: Leaderboards and statistics

### **External APIs**
- **Discord API**: Core bot functionality
- **Google Gemini**: AI conversation features
- **Replit DB**: Persistent data storage

## 🎨 Game Balance & Design

### **Class Balance Philosophy**
- Each class has unique strengths and weaknesses
- Multiple viable playstyles within each class
- Path system provides late-game specialization
- Hidden classes reward dedicated players

### **Economy Design**
- Progressive item tiers with meaningful upgrades
- Multiple income sources (work, combat, trading)
- Gold sinks prevent inflation
- Auction house enables player economy

### **Combat Mechanics**
- Skill Point system adds resource management
- Weakness/resistance creates tactical depth
- Ultimate abilities provide climactic moments
- Status effects and synergies reward planning

## 🛡️ Security & Privacy

- **No Sensitive Data Storage**: Bot tokens stored securely
- **Rate Limiting**: Prevents spam and abuse
- **Permission Checks**: Commands respect user roles
- **Data Protection**: User data handled responsibly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Development Guidelines**
- Follow Python PEP 8 style guide
- Add comprehensive docstrings
- Test new features thoroughly
- Maintain backward compatibility
- Update documentation

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Miraculous Ladybug**: Original characters and concepts
- **Discord.py**: Excellent Python Discord library
- **Google Gemini**: Advanced AI capabilities
- **Replit**: Reliable hosting platform
- **Community**: Feedback and suggestions

## 🐛 Bug Reports & Feature Requests

Please use the [GitHub Issues](https://github.com/yourusername/plagg-bot/issues) page to:
- Report bugs with detailed reproduction steps
- Request new features with clear descriptions
- Suggest improvements to existing systems
- Ask questions about bot functionality

## 📊 Bot Statistics

- **Commands**: 50+ unique commands
- **Items**: 300+ weapons, armor, and consumables
- **Monsters**: 25+ tactical enemies with unique AI
- **Classes**: 7 base + hidden legendary classes
- **Achievements**: 50+ progress milestones
- **Uptime**: 99.9% availability on Replit

---

**Made with 🧀 and chaos by the Plagg development team**

*"Claws out for adventure!"* - Plagg, Kwami of Destruction
