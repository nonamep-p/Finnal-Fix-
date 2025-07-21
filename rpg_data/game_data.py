# Bot Owner ID with special privileges
OWNER_ID = 1297013439125917766

# Owner commands and abilities
OWNER_PRIVILEGES = {
    "unlimited_gold": True,
    "all_items": True,
    "admin_commands": True,
    "spawn_items": True,
    "modify_player_data": True,
    "create_events": True,
    "access_hidden_content": True
}

# Character Classes with enhanced data
CHARACTER_CLASSES = {
    "warrior": {
        "name": "Warrior",
        "emoji": "⚔️",
        "role": "Tank/DPS",
        "description": "Masters of physical combat and unwavering defense",
        "base_stats": {"strength": 15, "constitution": 12, "dexterity": 8, "intelligence": 5, "wisdom": 8, "charisma": 7},
        "starting_skills": ["shield_bash", "berserker_rage", "taunt"],
        "passive": "Iron Will: +25% resistance to debuffs and fear effects",
        "ultimate": "Blade Storm: Devastating multi-hit attack that ignores armor",
        "preferred_weapons": ["sword", "axe", "mace"],
        "class_bonus": {"physical_damage": 0.15, "armor_penetration": 0.10}
    },
    "mage": {
        "name": "Mage",
        "emoji": "🔮",
        "role": "Burst DPS",
        "description": "Wielders of arcane magic and elemental destruction",
        "base_stats": {"strength": 5, "constitution": 8, "dexterity": 7, "intelligence": 15, "wisdom": 12, "charisma": 8},
        "starting_skills": ["fireball", "ice_shard", "mana_shield"],
        "passive": "Arcane Mastery: Spells have 15% chance to not consume mana",
        "ultimate": "Arcane Devastation: Massive area spell that pierces all resistances",
        "preferred_weapons": ["staff", "wand", "orb"],
        "class_bonus": {"spell_damage": 0.20, "mana_efficiency": 0.15}
    },
    "rogue": {
        "name": "Rogue",
        "emoji": "🗡️",
        "role": "Assassin",
        "description": "Swift shadows who strike from darkness with lethal precision",
        "base_stats": {"strength": 8, "constitution": 10, "dexterity": 15, "intelligence": 10, "wisdom": 7, "charisma": 5},
        "starting_skills": ["stealth_strike", "poison_blade", "shadow_step"],
        "passive": "Shadow Mastery: First attack each combat is guaranteed critical hit",
        "ultimate": "Thousand Cuts: Rapid succession of strikes with increasing damage",
        "preferred_weapons": ["dagger", "short_sword", "bow"],
        "class_bonus": {"critical_chance": 0.15, "dodge_chance": 0.10}
    },
    "archer": {
        "name": "Archer",
        "emoji": "🏹",
        "role": "Ranged DPS",
        "description": "Masters of precision who rain death from afar",
        "base_stats": {"strength": 10, "constitution": 9, "dexterity": 15, "intelligence": 8, "wisdom": 10, "charisma": 3},
        "starting_skills": ["piercing_shot", "multi_shot", "eagle_eye"],
        "passive": "Eagle Eye: Attacks ignore 50% of enemy dodge chance",
        "ultimate": "Rain of Arrows: Devastating barrage that hits all enemies",
        "preferred_weapons": ["bow", "crossbow", "throwing_weapon"],
        "class_bonus": {"range_damage": 0.20, "accuracy": 0.15}
    },
    "healer": {
        "name": "Healer",
        "emoji": "✨",
        "role": "Support",
        "description": "Divine conduits who mend wounds and protect allies",
        "base_stats": {"strength": 5, "constitution": 10, "dexterity": 7, "intelligence": 12, "wisdom": 15, "charisma": 6},
        "starting_skills": ["heal", "group_heal", "divine_protection"],
        "passive": "Divine Favor: Healing spells have 25% chance to grant temporary immunity",
        "ultimate": "Divine Intervention: Massive heal and resurrection of fallen allies",
        "preferred_weapons": ["staff", "mace", "holy_symbol"],
        "class_bonus": {"healing_power": 0.30, "support_effectiveness": 0.20}
    },
    "battlemage": {
        "name": "Battlemage",
        "emoji": "⚡",
        "role": "Hybrid DPS",
        "description": "Warriors who blend steel and sorcery in perfect harmony",
        "base_stats": {"strength": 12, "constitution": 10, "dexterity": 8, "intelligence": 12, "wisdom": 9, "charisma": 9},
        "starting_skills": ["flame_blade", "spell_sword", "elemental_weapon"],
        "passive": "Spell Sword: Weapon attacks have 20% chance to trigger spell effects",
        "ultimate": "Elemental Fury: Weapons become infused with all elements temporarily",
        "preferred_weapons": ["enchanted_sword", "staff", "magical_weapon"],
        "class_bonus": {"hybrid_damage": 0.15, "elemental_mastery": 0.10}
    },
    "chrono_knight": {
        "name": "Chrono Knight",
        "emoji": "⏰",
        "role": "Time Manipulator",
        "description": "Temporal warriors who bend time itself to their will",
        "base_stats": {"strength": 11, "constitution": 11, "dexterity": 12, "intelligence": 11, "wisdom": 12, "charisma": 8},
        "starting_skills": ["time_strike", "temporal_shield", "chronos_blessing"],
        "passive": "Temporal Mastery: 15% chance to take an extra turn after any action",
        "ultimate": "Time Fracture: Rewind enemy actions and multiply your own",
        "preferred_weapons": ["temporal_blade", "chrono_staff", "time_crystal"],
        "class_bonus": {"time_manipulation": 0.20, "turn_efficiency": 0.15}
    }
}

# Level progression
def XP_FOR_NEXT_LEVEL(level):
    """Calculate XP needed for next level."""
    return int(100 * (1.5 ** (level - 1)))

STAT_POINTS_PER_LEVEL = 2

# Rarity colors for embeds
RARITY_COLORS = {
    'common': 0x808080,     # Gray
    'uncommon': 0x00FF00,   # Green  
    'rare': 0x0080FF,       # Blue
    'epic': 0x8000FF,       # Purple
    'legendary': 0xFFD700,  # Gold
    'mythic': 0xFF0080,     # Pink
    'divine': 0x00FFFF,     # Cyan
    'cosmic': 0xFF4500      # Orange Red
}

# Expanded item database with detailed stats and hidden items
ITEMS = {
    # Common Weapons
    "rusty_dagger": {
        "name": "Rusty Dagger",
        "type": "weapon",
        "rarity": "common",
        "price": 50,
        "attack": 8,
        "description": "A worn dagger that's seen better days",
        "effects": []
    },
    "wooden_sword": {
        "name": "Wooden Sword",
        "type": "weapon",
        "rarity": "common",
        "price": 100,
        "attack": 12,
        "description": "Basic training sword made of sturdy oak",
        "effects": []
    },
    "iron_sword": {
        "name": "Iron Sword",
        "type": "weapon",
        "rarity": "uncommon",
        "price": 500,
        "attack": 25,
        "description": "A reliable iron blade forged by skilled smiths",
        "effects": []
    },
    "steel_blade": {
        "name": "Steel Blade",
        "type": "weapon",
        "rarity": "rare",
        "price": 2000,
        "attack": 45,
        "critical_chance": 5,
        "description": "Superior steel crafted with precision",
        "effects": ["5% chance to ignore armor"]
    },
    "mithril_sword": {
        "name": "Mithril Sword",
        "type": "weapon",
        "rarity": "epic",
        "price": 10000,
        "attack": 75,
        "critical_chance": 10,
        "critical_damage": 150,
        "description": "Legendary mithril blade, light as a feather, sharp as death",
        "effects": ["Ignores 25% of enemy defense", "10% chance for double strike"]
    },

    # Legendary Weapons
    "plagg_claw": {
        "name": "Plagg's Claw",
        "type": "weapon",
        "rarity": "legendary",
        "price": 100000,
        "attack": 150,
        "critical_chance": 25,
        "critical_damage": 200,
        "description": "Forged from Plagg's own essence, radiates chaotic power",
        "effects": ["Cataclysm: 15% chance to destroy enemy equipment", "Chaos Strike: Damage varies wildly (50-300% base)"],
        "set_bonus": "Destruction Set: +50% damage to structures"
    },

    # Hidden/Divine Weapons (Owner only)
    "reality_render": {
        "name": "Reality Render",
        "type": "weapon",
        "rarity": "cosmic",
        "price": 1000000,
        "attack": 500,
        "critical_chance": 50,
        "critical_damage": 500,
        "description": "A blade that cuts through the fabric of reality itself",
        "effects": ["Dimensional Slash: Ignores all defenses", "Reality Break: 25% chance to delete enemy from existence"],
        "owner_only": True
    },

    # Armor Sets
    "leather_vest": {
        "name": "Leather Vest",
        "type": "armor",
        "rarity": "common",
        "price": 150,
        "defense": 10,
        "hp": 25,
        "description": "Basic leather protection for novice adventurers",
        "effects": []
    },
    "chainmail_armor": {
        "name": "Chainmail Armor",
        "type": "armor",
        "rarity": "uncommon",
        "price": 800,
        "defense": 25,
        "hp": 75,
        "description": "Interlocked metal rings provide solid protection",
        "effects": ["10% chance to reduce incoming damage by half"]
    },
    "plate_armor": {
        "name": "Plate Armor",
        "type": "armor",
        "rarity": "rare",
        "price": 3000,
        "defense": 50,
        "hp": 150,
        "description": "Heavy plate armor favored by knights",
        "effects": ["Damage reduction: -5 damage from all attacks", "Immunity to critical hits from common weapons"]
    },
    "dragon_scale_mail": {
        "name": "Dragon Scale Mail",
        "type": "armor",
        "rarity": "epic",
        "price": 15000,
        "defense": 100,
        "hp": 300,
        "mana": 100,
        "description": "Armor crafted from authentic dragon scales",
        "effects": ["Fire immunity", "25% magic resistance", "Intimidation aura: -10% enemy accuracy"]
    },

    # Legendary Armor
    "tikki_blessing": {
        "name": "Tikki's Blessing",
        "type": "armor",
        "rarity": "legendary",
        "price": 75000,
        "defense": 200,
        "hp": 500,
        "mana": 200,
        "description": "Blessed by the Kwami of Creation herself",
        "effects": ["Lucky Charm: 20% chance to negate any attack", "Creative Force: Regenerate 5% HP per turn", "Miraculous Shield: Immunity to instant death"],
        "set_bonus": "Creation Set: All abilities cost no mana"
    },

    # Consumables
    "health_potion": {
        "name": "Health Potion",
        "type": "consumable",
        "rarity": "common",
        "price": 50,
        "heal_amount": 100,
        "description": "Restores 100 HP instantly",
        "effects": ["Instant heal: +100 HP"]
    },
    "mana_potion": {
        "name": "Mana Potion",
        "type": "consumable",
        "rarity": "common",
        "price": 75,
        "mana_amount": 50,
        "description": "Restores 50 Mana instantly",
        "effects": ["Instant mana: +50 MP"]
    },
    "greater_health_potion": {
        "name": "Greater Health Potion",
        "type": "consumable",
        "rarity": "rare",
        "price": 500,
        "heal_amount": 500,
        "description": "Restores 500 HP and removes debuffs",
        "effects": ["Instant heal: +500 HP", "Removes all negative status effects"]
    },
    "elixir_of_power": {
        "name": "Elixir of Power",
        "type": "consumable",
        "rarity": "epic",
        "price": 2000,
        "description": "Temporarily doubles all stats for 5 battles",
        "effects": ["Power Surge: +100% to all stats for 5 battles"]
    },

    # Hidden Consumables
    "plagg_cheese": {
        "name": "Plagg's Special Camembert",
        "type": "consumable",
        "rarity": "legendary",
        "price": 10000,
        "description": "Plagg's favorite cheese, grants his blessing",
        "effects": ["Chaos Blessing: Random massive stat boost", "Cataclysm: Next attack ignores all defenses", "Cheese Power: +1000% luck for next battle"]
    },

    # Accessories
    "silver_ring": {
        "name": "Silver Ring",
        "type": "accessory",
        "rarity": "common",
        "price": 200,
        "attack": 5,
        "description": "A simple silver band with minor enchantments",
        "effects": []
    },
    "amulet_of_protection": {
        "name": "Amulet of Protection",
        "type": "accessory",
        "rarity": "uncommon",
        "price": 1000,
        "defense": 15,
        "hp": 50,
        "description": "Provides magical protection against harm",
        "effects": ["5% chance to completely avoid damage"]
    },
    "ring_of_power": {
        "name": "Ring of Power",
        "type": "accessory",
        "rarity": "rare",
        "price": 5000,
        "attack": 25,
        "mana": 100,
        "critical_chance": 10,
        "description": "Ancient ring pulsing with magical energy",
        "effects": ["Spell crit: Magic attacks can critical hit", "Mana efficiency: -25% spell costs"]
    },

    # Kwami Artifacts (Set items)
    "tikki_earrings": {
        "name": "Tikki's Earrings",
        "type": "artifact",
        "rarity": "legendary",
        "price": 50000,
        "slot": "head",
        "set": "creation_set",
        "hp": 200,
        "mana": 150,
        "description": "The miraculous of the ladybug, grants creation powers",
        "effects": ["Lucky Charm: Create helpful items in battle", "Miraculous Ladybug: Heal all allies"],
        "set_bonus": "2-piece: +25% healing | 4-piece: Revive with 50% HP when defeated"
    },
    "plagg_ring": {
        "name": "Plagg's Ring",
        "type": "artifact",
        "rarity": "legendary",
        "price": 50000,
        "slot": "hands",
        "set": "destruction_set",
        "attack": 100,
        "critical_damage": 50,
        "description": "The miraculous of the black cat, grants destruction powers",
        "effects": ["Cataclysm: Destroy enemy equipment", "Nine Lives: Avoid death 9 times"],
        "set_bonus": "2-piece: +50% crit damage | 4-piece: Cataclysm affects all enemies"
    },

    # Owner-only God Items
    "admin_blade": {
        "name": "Administrator's Edge",
        "type": "weapon",
        "rarity": "divine",
        "price": 0,
        "attack": 9999,
        "critical_chance": 100,
        "critical_damage": 1000,
        "description": "The weapon of absolute authority",
        "effects": ["Admin Strike: Instantly defeats any non-boss enemy", "Command: Force enemies to flee", "Debug: See all hidden stats"],
        "owner_only": True
    },
    "god_armor": {
        "name": "Divinity's Embrace",
        "type": "armor",
        "rarity": "divine",
        "price": 0,
        "defense": 9999,
        "hp": 999999,
        "mana": 999999,
        "description": "Armor befitting a god",
        "effects": ["Invulnerability: Immune to all damage", "Omnipresence: Act infinite times per turn", "Divine Aura: All allies gain +1000% stats"],
        "owner_only": True
    }
}

# Kwami Artifact Sets
KWAMI_ARTIFACT_SETS = {
    "creation_set": {
        "name": "Miraculous of Creation",
        "kwami": "Tikki",
        "bonuses": {
            2: {"description": "+25% healing power", "effect": "healing_boost_25"},
            4: {"description": "Revive with 50% HP when defeated", "effect": "miraculous_revival"}
        }
    },
    "destruction_set": {
        "name": "Miraculous of Destruction", 
        "kwami": "Plagg",
        "bonuses": {
            2: {"description": "+50% critical damage", "effect": "crit_damage_boost_50"},
            4: {"description": "Cataclysm affects all enemies", "effect": "area_cataclysm"}
        }
    },
    "illusion_set": {
        "name": "Miraculous of Illusion",
        "kwami": "Trixx",
        "bonuses": {
            2: {"description": "+30% dodge chance", "effect": "dodge_boost_30"},
            4: {"description": "Mirage: Confuse all enemies", "effect": "mass_confusion"}
        }
    },
    "transmission_set": {
        "name": "Miraculous of Transmission",
        "kwami": "Nooroo",
        "bonuses": {
            2: {"description": "+40% ability range", "effect": "range_boost_40"},
            4: {"description": "Share abilities with all allies", "effect": "power_transmission"}
        }
    },
    "emotion_set": {
        "name": "Miraculous of Emotion",
        "kwami": "Duusu",
        "bonuses": {
            2: {"description": "+35% status effect duration", "effect": "status_duration_35"},
            4: {"description": "Amok: Create powerful sentient beings", "effect": "amok_creation"}
        }
    }
}

# Crafting Recipes
CRAFTING_RECIPES = {
    "iron_sword": {
        "name": "Iron Sword",
        "materials": {"iron_ore": 3, "wood": 2},
        "result": "iron_sword",
        "skill_required": 1,
        "xp_reward": 15
    },
    "steel_armor": {
        "name": "Steel Armor",
        "materials": {"steel_ingot": 5, "leather": 3},
        "result": "steel_armor", 
        "skill_required": 3,
        "xp_reward": 25
    },
    "health_potion": {
        "name": "Health Potion",
        "materials": {"healing_herbs": 2, "water": 1},
        "result": "health_potion",
        "skill_required": 1,
        "xp_reward": 10
    },
    "mana_potion": {
        "name": "Mana Potion",
        "materials": {"mana_crystal": 1, "water": 1},
        "result": "mana_potion",
        "skill_required": 2,
        "xp_reward": 12
    }
}

# Tactical Skills for combat
TACTICAL_SKILLS = {
    "warrior": {
        "shield_bash": {
            "name": "Shield Bash",
            "description": "Stun enemy for 1 turn",
            "damage": 15,
            "mana_cost": 10,
            "cooldown": 2,
            "effect": "stun"
        },
        "berserker_rage": {
            "name": "Berserker Rage", 
            "description": "Double damage for 2 turns",
            "damage": 0,
            "mana_cost": 20,
            "cooldown": 4,
            "effect": "rage"
        }
    },
    "mage": {
        "fireball": {
            "name": "Fireball",
            "description": "High damage fire attack",
            "damage": 35,
            "mana_cost": 15,
            "cooldown": 1,
            "effect": "burn"
        },
        "ice_shard": {
            "name": "Ice Shard",
            "description": "Slow enemy movement",
            "damage": 25,
            "mana_cost": 12,
            "cooldown": 1,
            "effect": "slow"
        }
    },
    "rogue": {
        "stealth_strike": {
            "name": "Stealth Strike",
            "description": "High crit chance attack",
            "damage": 30,
            "mana_cost": 10,
            "cooldown": 2,
            "effect": "crit"
        },
        "poison_blade": {
            "name": "Poison Blade",
            "description": "Poison damage over time",
            "damage": 20,
            "mana_cost": 8,
            "cooldown": 1,
            "effect": "poison"
        }
    },
    "archer": {
        "piercing_shot": {
            "name": "Piercing Shot",
            "description": "Ignores armor",
            "damage": 28,
            "mana_cost": 12,
            "cooldown": 2,
            "effect": "pierce"
        },
        "multi_shot": {
            "name": "Multi Shot",
            "description": "Hit multiple targets",
            "damage": 20,
            "mana_cost": 15,
            "cooldown": 3,
            "effect": "multi"
        }
    },
    "healer": {
        "heal": {
            "name": "Heal",
            "description": "Restore HP to ally",
            "damage": -30,
            "mana_cost": 10,
            "cooldown": 1,
            "effect": "heal"
        },
        "group_heal": {
            "name": "Group Heal",
            "description": "Heal entire party",
            "damage": -20,
            "mana_cost": 25,
            "cooldown": 4,
            "effect": "group_heal"
        }
    }
}

# Tactical Monsters for combat encounters
TACTICAL_MONSTERS = {
    "goblin_warrior": {
        "name": "Goblin Warrior",
        "level": 3,
        "hp": 80,
        "max_hp": 80,
        "attack": 15,
        "defense": 8,
        "speed": 12,
        "xp_reward": 50,
        "gold_reward": 25,
        "rarity": "common",
        "ai_type": "aggressive",
        "abilities": ["power_strike", "intimidate"],
        "resistances": {},
        "weaknesses": {"fire": 1.5},
        "loot_table": {
            "rusty_dagger": 0.3,
            "health_potion": 0.5,
            "goblin_fang": 0.2
        }
    },
    "frost_elemental": {
        "name": "Frost Elemental",
        "level": 8,
        "hp": 150,
        "max_hp": 150,
        "attack": 25,
        "defense": 15,
        "speed": 8,
        "xp_reward": 120,
        "gold_reward": 60,
        "rarity": "uncommon",
        "ai_type": "defensive",
        "abilities": ["ice_shard", "frost_armor", "freeze"],
        "resistances": {"ice": 0.5, "water": 0.5},
        "weaknesses": {"fire": 2.0},
        "loot_table": {
            "ice_crystal": 0.6,
            "frost_essence": 0.3,
            "mana_potion": 0.4
        }
    },
    "shadow_assassin": {
        "name": "Shadow Assassin",
        "level": 12,
        "hp": 120,
        "max_hp": 120,
        "attack": 40,
        "defense": 10,
        "speed": 20,
        "xp_reward": 180,
        "gold_reward": 90,
        "rarity": "rare",
        "ai_type": "tactical",
        "abilities": ["stealth_strike", "shadow_step", "poison_blade"],
        "resistances": {"dark": 0.3},
        "weaknesses": {"light": 1.8},
        "loot_table": {
            "shadow_essence": 0.5,
            "poison_vial": 0.3,
            "stealth_cloak": 0.1
        }
    },
    "ancient_dragon": {
        "name": "Ancient Dragon",
        "level": 25,
        "hp": 800,
        "max_hp": 800,
        "attack": 80,
        "defense": 40,
        "speed": 15,
        "xp_reward": 1000,
        "gold_reward": 500,
        "rarity": "legendary",
        "ai_type": "boss",
        "abilities": ["dragon_breath", "wing_buffet", "tail_sweep", "intimidating_roar"],
        "resistances": {"fire": 0.2, "physical": 0.8},
        "weaknesses": {"ice": 1.5},
        "loot_table": {
            "dragon_scale": 0.8,
            "dragon_heart": 0.3,
            "legendary_gem": 0.1,
            "ancient_gold": 1.0
        }
    },
    "goblin_chieftain": {
        "name": "Goblin Chieftain",
        "level": 6,
        "hp": 200,
        "max_hp": 200,
        "attack": 30,
        "defense": 18,
        "speed": 10,
        "xp_reward": 300,
        "gold_reward": 150,
        "rarity": "rare",
        "ai_type": "boss",
        "abilities": ["war_cry", "tribal_rage", "commanding_shout"],
        "resistances": {},
        "weaknesses": {"magic": 1.3},
        "loot_table": {
            "chieftain_axe": 0.4,
            "tribal_mask": 0.3,
            "gold_pouch": 0.8
        }
    },
    "shadow_lord": {
        "name": "Shadow Lord",
        "level": 18,
        "hp": 500,
        "max_hp": 500,
        "attack": 60,
        "defense": 30,
        "speed": 18,
        "xp_reward": 800,
        "gold_reward": 400,
        "rarity": "epic",
        "ai_type": "boss",
        "abilities": ["shadow_realm", "dark_manipulation", "void_strike", "shadow_army"],
        "resistances": {"dark": 0.1, "physical": 0.7},
        "weaknesses": {"light": 2.0},
        "loot_table": {
            "shadow_crown": 0.5,
            "void_crystal": 0.4,
            "dark_essence": 0.8
        }
    },
    "ancient_red_dragon": {
        "name": "Ancient Red Dragon",
        "level": 35,
        "hp": 1500,
        "max_hp": 1500,
        "attack": 120,
        "defense": 60,
        "speed": 20,
        "xp_reward": 2000,
        "gold_reward": 1000,
        "rarity": "legendary",
        "ai_type": "boss",
        "abilities": ["inferno_breath", "meteor_strike", "dragon_fear", "ancient_magic", "fire_shield"],
        "resistances": {"fire": 0.0, "physical": 0.6},
        "weaknesses": {"ice": 1.8, "water": 1.5},
        "loot_table": {
            "red_dragon_scale": 0.9,
            "dragon_lord_heart": 0.5,
            "ancient_ruby": 0.3,
            "fire_essence": 0.8,
            "legendary_treasure": 0.2
        }
    },
    "artifact_guardian": {
        "name": "Artifact Guardian",
        "level": 20,
        "hp": 400,
        "max_hp": 400,
        "attack": 50,
        "defense": 35,
        "speed": 12,
        "xp_reward": 600,
        "gold_reward": 300,
        "rarity": "epic",
        "ai_type": "defensive",
        "abilities": ["guardian_shield", "artifact_power", "protective_barrier"],
        "resistances": {"magic": 0.5},
        "weaknesses": {"chaos": 1.5},
        "loot_table": {
            "artifact_fragment": 0.8,
            "guardian_essence": 0.4,
            "protection_rune": 0.3
        }
    },
    "kwami_phantom": {
        "name": "Kwami Phantom",
        "level": 22,
        "hp": 300,
        "max_hp": 300,
        "attack": 45,
        "defense": 25,
        "speed": 25,
        "xp_reward": 700,
        "gold_reward": 350,
        "rarity": "epic",
        "ai_type": "tactical",
        "abilities": ["phase_shift", "spectral_attack", "kwami_blessing"],
        "resistances": {"physical": 0.3},
        "weaknesses": {"miraculous": 2.0},
        "loot_table": {
            "kwami_essence": 0.7,
            "spectral_dust": 0.5,
            "phantom_core": 0.2
        }
    },
    "miraculous_sentinel": {
        "name": "Miraculous Sentinel",
        "level": 24,
        "hp": 600,
        "max_hp": 600,
        "attack": 55,
        "defense": 40,
        "speed": 15,
        "xp_reward": 900,
        "gold_reward": 450,
        "rarity": "legendary",
        "ai_type": "boss",
        "abilities": ["miraculous_power", "guardian_strike", "sentinel_shield", "power_surge"],
        "resistances": {"all": 0.8},
        "weaknesses": {"corruption": 1.5},
        "loot_table": {
            "miraculous_fragment": 0.9,
            "sentinel_core": 0.4,
            "guardian_blessing": 0.3,
            "rare_kwami_treat": 0.6
        }
    }
}

# Monster database with detailed AI and rewards
MONSTERS = {
    "shadow_moth": {
        "name": "Shadow Moth",
        "level": 1,
        "hp": 50,
        "attack": 8,
        "defense": 3,
        "xp_reward": 25,
        "gold_reward": 15,
        "rarity": "common",
        "abilities": ["Dark Wing", "Akuma Creation"],
        "loot_table": {
            "health_potion": 0.3,
            "akuma_fragment": 0.1
        }
    },
    "akumatized_villain": {
        "name": "Akumatized Villain",
        "level": 5,
        "hp": 150,
        "attack": 25,
        "defense": 10,
        "xp_reward": 100,
        "gold_reward": 75,
        "rarity": "uncommon",
        "abilities": ["Akuma Power", "Emotional Outburst", "Dark Transformation"],
        "loot_table": {
            "purified_akuma": 0.5,
            "dark_essence": 0.2,
            "corrupted_jewelry": 0.1
        }
    },
    "sentimonster": {
        "name": "Sentimonster",
        "level": 10,
        "hp": 400,
        "attack": 60,
        "defense": 25,
        "xp_reward": 250,
        "gold_reward": 200,
        "rarity": "rare",
        "abilities": ["Emotional Echo", "Sentient Strike", "Amok Bond"],
        "loot_table": {
            "amok_feather": 0.4,
            "emotional_core": 0.2,
            "peacock_essence": 0.05
        }
    },

    # Boss Monsters
    "hawkmoth_avatar": {
        "name": "Hawkmoth's Avatar",
        "level": 25,
        "hp": 2000,
        "max_hp": 2000,
        "attack": 80,
        "defense": 40,
        "speed": 15,
        "xp_reward": 1500,
        "gold_reward": 750,
        "rarity": "legendary",
        "ai_type": "boss",
        "abilities": ["akuma_storm", "dark_manipulation", "hawkmoth_transformation", "emotional_drain"],
        "resistances": {"dark": 0.2, "emotional": 0.1},
        "weaknesses": {"light": 1.8, "purification": 2.0},
        "loot_table": {
            "hawkmoth_miraculous": 0.5,
            "dark_essence": 0.8,
            "butterfly_brooch": 0.3,
            "legendary_gem": 0.2
        }
    }
}

# Damage types for combat system
DAMAGE_TYPES = {
    'physical': '⚔️',
    'fire': '🔥',
    'ice': '🧊',
    'lightning': '⚡',
    'water': '💧',
    'earth': '🌍',
    'wind': '💨',
    'light': '✨',
    'dark': '🌑',
    'quantum': '🌟',
    'imaginary': '👻',
    'chaos': '🌀'
}

# Techniques system for pre-combat setup
TECHNIQUES = {
    'ambush': {
        'name': 'Ambush',
        'description': 'Start combat with bonus skill points',
        'cost': 1,
        'effect': {
            'type': 'skill_points',
            'amount': 2
        }
    },
    'preparation': {
        'name': 'Preparation',
        'description': 'Start with shield and ultimate energy',
        'cost': 2,
        'effect': {
            'type': 'shield',
            'amount': 50
        }
    },
    'marking': {
        'name': 'Hunter\'s Mark',
        'description': 'Mark enemy for increased damage',
        'cost': 1,
        'effect': {
            'type': 'enemy_debuff',
            'stat': 'marked',
            'amount': 0.25,
            'duration': 3
        }
    }
}

# Synergy states for combat bonuses
SYNERGY_STATES = {
    'riposte': {
        'name': 'Riposte Stance',
        'emoji': '⚔️',
        'effect': 'riposte_damage',
        'description': 'Next basic attack deals bonus damage based on shield'
    },
    'opportunist': {
        'name': 'Opportunist',
        'emoji': '🎯',
        'effect': 'guaranteed_crit',
        'description': 'Next skill attack is guaranteed critical'
    },
    'arcane_resonance': {
        'name': 'Arcane Resonance',
        'emoji': '✨',
        'effect': 'free_enhanced_spell',
        'description': 'Next spell costs no mana and deals bonus damage'
    }
}

# Ultimate abilities by class
ULTIMATE_ABILITIES = {
    'warrior': {
        'name': 'Blade Storm',
        'description': 'Unleashes a devastating series of strikes',
        'damage': 120,
        'toughness_damage': 50,
        'damage_type': 'physical',
        'team_effects': {'all_allies': {'damage_boost': 0.15, 'duration': 3}}
    },
    'mage': {
        'name': 'Arcane Devastation',
        'description': 'Channels pure magical energy',
        'damage': 100,
        'toughness_damage': 60,
        'damage_type': 'quantum',
        'team_effects': {'all_enemies': {'vulnerability': 'quantum', 'duration': 2}}
    },
    'rogue': {
        'name': 'Shadow Assassination',
        'description': 'Strikes from the shadows with lethal precision',
        'damage': 110,
        'toughness_damage': 40,
        'damage_type': 'physical',
        'team_effects': {'self': {'stealth': True, 'crit_boost': 0.5, 'duration': 2}}
    },
    'archer': {
        'name': 'Rain of Arrows',
        'description': 'Fires a volley that hits all enemies',
        'damage': 80,
        'toughness_damage': 30,
        'damage_type': 'physical',
        'target': 'all_enemies',
        'team_effects': {'all_allies': {'speed_boost': 0.25, 'duration': 3}}
    },
    'healer': {
        'name': 'Divine Intervention',
        'description': 'Massive healing and protective buffs',
        'heal': 150,
        'damage_type': 'quantum',
        'team_effects': {'all_allies': {'damage_reduction': 0.3, 'heal_over_time': 25, 'duration': 5}}
    },
    'chrono_weave': {
        'name': 'Temporal Mastery',
        'description': 'Manipulates time itself',
        'damage': 90,
        'toughness_damage': 40,
        'damage_type': 'quantum',
        'team_effects': {'all_allies': {'extra_turn': True}, 'all_enemies': {'speed_reduction': 0.5, 'duration': 2}}
    }
}

# Team combat formations
BATTLE_FORMATIONS = {
    'balanced': {
        'name': 'Balanced Formation',
        'positions': 4,
        'bonuses': {'all_stats': 0.05},
        'description': 'Well-rounded formation for general combat'
    },
    'aggressive': {
        'name': 'Aggressive Assault',
        'positions': 4,
        'bonuses': {'attack': 0.15, 'speed': 0.10, 'defense': -0.05},
        'description': 'High damage output at the cost of defense'
    },
    'defensive': {
        'name': 'Fortress Wall',
        'positions': 4,
        'bonuses': {'defense': 0.20, 'damage_reduction': 0.10, 'attack': -0.05},
        'description': 'Maximum survivability for endurance fights'
    },
    'speed_blitz': {
        'name': 'Lightning Strike',
        'positions': 4,
        'bonuses': {'speed': 0.25, 'critical_chance': 0.10, 'hp': -0.10},
        'description': 'Strike first and strike hard'
    }
}

# Advanced buff/debuff system
BATTLE_EFFECTS = {
    'damage_boost': {
        'name': 'Damage Boost',
        'type': 'buff',
        'stackable': True,
        'max_stacks': 5,
        'icon': '⚔️'
    },
    'vulnerability': {
        'name': 'Vulnerability',
        'type': 'debuff',
        'stackable': False,
        'damage_taken_multiplier': 1.25,
        'icon': '💔'
    },
    'stealth': {
        'name': 'Stealth',
        'type': 'buff',
        'stackable': False,
        'dodge_chance_bonus': 0.5,
        'icon': '👤'
    },
    'burn': {
        'name': 'Burn',
        'type': 'debuff',
        'stackable': True,
        'max_stacks': 10,
        'damage_per_turn': 15,
        'icon': '🔥'
    },
    'freeze': {
        'name': 'Freeze',
        'type': 'debuff',
        'stackable': False,
        'speed_reduction': 0.5,
        'chance_to_skip_turn': 0.3,
        'icon': '🧊'
    },
    'shock': {
        'name': 'Shock',
        'type': 'debuff',
        'stackable': True,
        'max_stacks': 5,
        'spread_on_defeat': True,
        'icon': '⚡'
    }
}

# PvP Arena system
PVP_ARENAS = {
    'rookie_arena': {
        'name': 'Rookie Arena',
        'rating_range': [0, 1200],
        'rewards': {'coins_per_win': 100, 'arena_tokens': 5},
        'unlock_level': 10
    },
    'veteran_arena': {
        'name': 'Veteran Arena', 
        'rating_range': [1200, 1800],
        'rewards': {'coins_per_win': 200, 'arena_tokens': 10},
        'unlock_level': 20
    },
    'master_arena': {
        'name': 'Master Arena',
        'rating_range': [1800, 2500],
        'rewards': {'coins_per_win': 500, 'arena_tokens': 20},
        'unlock_level': 35
    },
    'legendary_arena': {
        'name': 'Legendary Arena',
        'rating_range': [2500, 9999],
        'rewards': {'coins_per_win': 1000, 'arena_tokens': 50, 'legendary_materials': 1},
        'unlock_level': 50
    }
}

# Arena tournament system
TOURNAMENT_BRACKETS = {
    'daily_tournament': {
        'name': 'Daily Chaos Tournament',
        'participants': 16,
        'entry_cost': 100,
        'duration_hours': 24,
        'rewards': {
            'winner': {'coins': 5000, 'arena_tokens': 100, 'tournament_trophy': 1},
            'finalist': {'coins': 2500, 'arena_tokens': 50},
            'semifinalist': {'coins': 1000, 'arena_tokens': 25}
        }
    },
    'weekly_championship': {
        'name': 'Weekly Championship',
        'participants': 32,
        'entry_cost': 500,
        'duration_hours': 168,
        'rewards': {
            'winner': {'coins': 25000, 'arena_tokens': 500, 'championship_crown': 1},
            'finalist': {'coins': 15000, 'arena_tokens': 300},
            'semifinalist': {'coins': 8000, 'arena_tokens': 150}
        }
    }
}

# Light cone equivalents (Kwami Charms)
KWAMI_CHARMS = {
    'plaggs_destruction': {
        'name': "Plagg's Destructive Charm",
        'rarity': 'legendary',
        'stats': {'attack': 45, 'critical_damage': 0.25},
        'passive': 'Chaos Strike: 15% chance to deal 200% damage and break enemy toughness',
        'max_level': 80,
        'unlock_level': 30
    },
    'tikki_creation': {
        'name': "Tikki's Creative Charm", 
        'rarity': 'legendary',
        'stats': {'hp': 200, 'healing_bonus': 0.30},
        'passive': 'Lucky Charm: Healing abilities have 20% chance to grant random beneficial effect',
        'max_level': 80,
        'unlock_level': 30
    },
    'sass_intuition': {
        'name': "Sass's Temporal Charm",
        'rarity': 'epic',
        'stats': {'speed': 25, 'ultimate_energy_gain': 0.20},
        'passive': 'Second Chance: 10% chance to reset cooldowns when using ultimate',
        'max_level': 60,
        'unlock_level': 25
    }
}

# Weekly dungeon rotations
WEEKLY_DUNGEONS = {
    'monday_madness': {
        'name': 'Monday Madness: Speed Trial',
        'special_rules': ['double_speed', 'time_limit_300'],
        'bonus_rewards': {'xp_multiplier': 2.0},
        'featured_elements': ['wind', 'lightning']
    },
    'tuesday_tactics': {
        'name': 'Tuesday Tactics: No Ultimates',
        'special_rules': ['no_ultimates', 'skill_cost_reduction'],
        'bonus_rewards': {'skill_books': 2},
        'featured_elements': ['physical', 'quantum']
    },
    'wednesday_weakness': {
        'name': 'Wednesday Weakness: Element Focus',
        'special_rules': ['weakness_damage_x3', 'random_weaknesses'],
        'bonus_rewards': {'element_crystals': 5},
        'featured_elements': ['fire', 'ice', 'lightning']
    },
    'thursday_team': {
        'name': 'Thursday Team: Synergy Challenge',
        'special_rules': ['mandatory_team_size_4', 'synergy_bonuses'],
        'bonus_rewards': {'team_formation_scrolls': 1},
        'featured_elements': ['all']
    },
    'friday_frenzy': {
        'name': 'Friday Frenzy: Chaos Mode',
        'special_rules': ['random_effects', 'double_enemies', 'chaos_buffs'],
        'bonus_rewards': {'chaos_essence': 3},
        'featured_elements': ['quantum', 'imaginary']
    },
    'weekend_warriors': {
        'name': 'Weekend Warriors: Boss Rush',
        'special_rules': ['only_bosses', 'no_healing_items', 'ultimate_energy_boost'],
        'bonus_rewards': {'boss_materials': 3, 'legendary_chance': 0.15},
        'featured_elements': ['all']
    }
}

# End game content
END_GAME_CONTENT = {
    # Item ascension system
    "ascension": {
        "name": "Ascended Gear",
        "description": "Equipment that has transcended mortal limitations",
        "rarity_multiplier": 50.0,
        "level_requirement": 90,
        "drop_chance": 0.001,
        "base_value": 1000000,
        "upgrade_materials": {
            "divine_essence": 100,
            "celestial_fragment": 50,
            "transcendent_core": 20,
            "eternal_spark": 5
        }
    }
}

# Trading system
TRADING_SYSTEM = {
    "trade_tax": 0.05,  # 5% tax on trades
    "max_trade_value": 1000000,
    "trade_cooldown": 300,  # 5 minutes
    "auction_duration": 86400,  # 24 hours
    "bid_increment": 0.05  # 5% minimum bid increase
}

# Achievement system
ACHIEVEMENTS = {
    "first_battle": {
        "name": "First Blood",
        "description": "Win your first battle",
        "reward_gold": 100,
        "reward_xp": 50,
        "icon": "⚔️"
    },
    "level_10": {
        "name": "Getting Started",
        "description": "Reach level 10",
        "reward_gold": 500,
        "reward_xp": 100,
        "icon": "📈"
    },
    "dungeon_master": {
        "name": "Dungeon Master",
        "description": "Complete 10 dungeons",
        "reward_gold": 2000,
        "reward_xp": 500,
        "icon": "🏰"
    },
    "wealthy": {
        "name": "Wealthy Adventurer",
        "description": "Accumulate 100,000 gold",
        "reward_gold": 10000,
        "reward_xp": 1000,
        "icon": "💰"
    }
}

# PvP system configuration
PVP_CONFIG = {
    "seasons": {
        "current_season": 1,
        "season_duration": 2592000,  # 30 days
        "rewards": {
            "bronze": {"gold": 1000, "items": ["bronze_trophy"]},
            "silver": {"gold": 3000, "items": ["silver_trophy"]},
            "gold": {"gold": 7000, "items": ["gold_trophy"]},
            "platinum": {"gold": 15000, "items": ["platinum_trophy"]},
            "diamond": {"gold": 30000, "items": ["diamond_trophy"]},
            "master": {"gold": 60000, "items": ["master_trophy"]},
            "grandmaster": {"gold": 100000, "items": ["grandmaster_trophy"]}
        }
    },
    "ranking_system": {
        "bronze": {"min_rating": 0, "max_rating": 1199},
        "silver": {"min_rating": 1200, "max_rating": 1699},
        "gold": {"min_rating": 1700, "max_rating": 2199},
        "platinum": {"min_rating": 2200, "max_rating": 2699},
        "diamond": {"min_rating": 2700, "max_rating": 3199},
        "master": {"min_rating": 3200, "max_rating": 3699},
        "grandmaster": {"min_rating": 3700, "max_rating": 9999}
    },
    "matchmaking": {
        "rating_tolerance": 200,
        "max_wait_time": 300,
        "skill_variance": 0.15
    }
}