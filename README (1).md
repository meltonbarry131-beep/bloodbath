# 🩸 BLOODBATH RPG

A GTA-style open-world action RPG built with Python and Pygame.

## 🎮 How to Play

### Controls
| Key | Action |
|-----|--------|
| WASD / Arrow Keys | Move |
| Mouse Click | Shoot (auto-aims at nearest cop!) |
| Space | Melee attack (outside) / Interact (inside buildings) |
| E | Enter buildings/talk to dealers |
| TAB | Open mission menu |
| ESC | Pause menu / Exit buildings / Close menus |
| W/S | Navigate menus |
| X | Abandon mission (in mission menu) |
| F11 | Toggle fullscreen |
| Q | Quit (while paused) |

### Objective
**Earn $10,000 to win the game!**

Make money through:
- 📋 **Missions** - Complete objectives for cash rewards
- 💊 **Drug dealing** - Buy low from dealers, sell high to others
- 🔪 **Combat** - Kill cops and civilians for cash
- 👠 **Hoes** - Recruit at strip clubs for passive income
- 🧪 **Cooking** - Make crack at crack dens

## 🎯 Auto-Aim System
When a cop is within 400 units, your crosshair automatically locks onto them with red targeting brackets. Just click to shoot - no aiming required!

## 📋 Mission System
Press **TAB** to open the mission menu and select from available missions:
- **Kill Cops** - Eliminate a target number of police
- **Earn Money** - Make money through any means
- **Sell Drugs** - Deal crack to dealers  
- **Survive** - Stay alive at 3+ wanted stars
- **Recruit Hoes** - Build your empire

Missions get harder as you complete more (difficulty increases every 3 missions).

## 🏢 Locations

| Building | Color | Purpose |
|----------|-------|---------|
| CRACK DEN | Purple | Cook crack (minigame) |
| STRIP CLUB | Pink/XXX | Recruit hoes |
| GUN STORE | Yellow | Buy weapons & ammo |
| UPGRADE SHOP | Blue | Buy stat upgrades |
| DEALER ($) | Green NPC | Buy/sell drugs |

## 📊 Game Systems

### Wanted Level (★★★★★)
- Increases when you shoot or kill
- Higher levels = more aggressive cops
- Decays slowly over time
- Resets on death

### Drug Economy
- **Crack Dens**: Cook crack for free (timing minigame)
- **Dealers**: Buy crack cheap ($30-60), sell high ($80-150)
- Prices vary between dealers - shop around!

### Upgrades
- **Max Health +25** ($500)
- **Speed +1** ($400)
- **Armor +10%** ($600) - Reduces incoming damage
- **Damage +20%** ($800) - Increases weapon damage

### Weapons
| Weapon | Price | Features |
|--------|-------|----------|
| Pistol | $200 | Basic, reliable |
| Shotgun | $500 | Spread shot, high damage |
| Uzi | $800 | Rapid fire |

## 🗺️ HUD Guide

- **Top Left**: Player name, cash, weapon, hoes, drugs
- **Top Right**: Health bar, armor, active mission
- **Center Stars**: Wanted level
- **Bottom Right**: Minimap (green = dealers, blue = cops, gold = you)
- **Bottom Left**: Lifetime stats

## 💡 Tips

1. **Use auto-aim** - Just click when the red brackets appear on cops
2. **Take missions** - They're the fastest way to earn money
3. **Early game**: Cook crack at dens, sell to dealers for quick cash
4. **Recruit hoes** early - they generate passive income
5. **Buy Armor first** - makes combat much easier
6. **Watch the minimap** - avoid cops when wanted level is high
7. **Find cheap dealers** - drug prices vary significantly

## ⚙️ Requirements

```bash
pip install pygame
```

## 🚀 Running the Game

```bash
python bloodbath.py
```

## 📝 Version History

- **v1.1** - Added mission system & auto-aim
  - 5 mission types with scaling difficulty
  - Auto-lock targeting on nearby cops
  - TAB menu for mission selection
  
- **v1.0** - Initial release
  - Open-world exploration
  - Combat system (shooting + melee)
  - Drug economy (cooking + dealing)
  - Building interiors (4 types)
  - Upgrade system
  - Minimap
  - Win condition ($10,000)

---
*Made with 🩸 and Python*
