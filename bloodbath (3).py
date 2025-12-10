#!/usr/bin/env python3
"""
BLOODBATH RPG - SINGLE PLAYER
Arrow keys or WASD to move, click to shoot, space to melee
"""

import pygame
import sys
import random
import math

pygame.init()

SCREEN_W, SCREEN_H = 1280, 720
TILE = 64
MAP_W, MAP_H = 80, 80
FPS = 60

C = {
    'bg': (30, 30, 50), 'blood': (200, 0, 0), 'purple': (120, 0, 200),
    'pink': (255, 50, 150), 'red': (220, 20, 20), 'gray': (45, 45, 55),
    'neon': (0, 255, 255), 'gold': (255, 215, 0), 'white': (255, 255, 255),
    'yellow': (255, 255, 0), 'green': (0, 255, 100), 'cop': (20, 20, 200),
    'table': (100, 60, 20), 'civilian': (200, 180, 160)
}

F = {
    'main': pygame.font.SysFont("arial", 28, bold=True),
    'big': pygame.font.SysFont("arial", 72, bold=True),
    'small': pygame.font.SysFont("arial", 20),
    'tiny': pygame.font.SysFont("arial", 16)
}

screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("BLOODBATH RPG")
clock = pygame.time.Clock()


class Player:
    def __init__(self):
        self.x, self.y = 500, 500
        self.w, self.h = 40, 60
        self.speed = 8
        self.health = 100
        self.max_health = 100
        self.cash = 1000
        self.wanted = 0
        # Starting loadout
        self.has_gun = True
        self.has_shotgun = False
        self.has_uzi = False
        self.ammo = 50
        self.hoes = 2
        self.alive = True
        self.respawn_timer = 0
        self.shoot_cooldown = 0
        # Drug inventory
        self.drugs = {'crack': 0, 'weed': 0, 'meth': 0}
        self.total_drugs_sold = 0
        # Stats/upgrades
        self.damage_mult = 1.0
        self.speed_bonus = 0
        self.armor = 0  # Damage reduction %
        # Lifetime stats
        self.kills = 0
        self.total_earned = 0
        self.missions_complete = 0
        # Building state
        self.inside = False
        self.building_type = None
        self.entry_pos = (500, 500)
        # Cooking minigame
        self.cooking = False
        self.cook_stage = 0
        self.cook_bar = 0.0
        self.cook_target = 0.5
        self.cook_zone = 0.15
        self.cook_speed = 0.012
        # Strip club
        self.mash_count = 0
        self.mash_target = 20
        # Screen effects
        self.damage_flash = 0
        self.screen_shake = 0
    
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    @property
    def center(self):
        return (self.x + self.w//2, self.y + self.h//2)


class Cop:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = 40, 60
        self.health = 80
        self.max_health = 80
        self.shoot_timer = 0
        self.angle = random.random() * 6.28
        self.alert = False
    
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    @property
    def center(self):
        return (self.x + self.w//2, self.y + self.h//2)


class Civilian:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = 35, 55
        self.angle = random.random() * 6.28
        self.move_timer = random.randint(60, 180)
        self.color = (
            random.randint(150, 220),
            random.randint(130, 200),
            random.randint(120, 180)
        )
        self.scared = False
        self.scared_timer = 0
    
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    @property
    def center(self):
        return (self.x + self.w//2, self.y + self.h//2)


class Hoe:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = 30, 50
        self.color = (
            random.randint(200, 255),
            random.randint(50, 150),
            random.randint(150, 255)
        )
        self.income_timer = 0
    
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


class Bullet:
    def __init__(self, x, y, angle, owner='player'):
        self.x, self.y = x, y
        self.vx = math.cos(angle) * 22
        self.vy = math.sin(angle) * 22
        self.owner = owner
        self.life = 50


class HealthPickup:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.amount = random.randint(20, 40)
        self.pulse = 0
    
    @property
    def rect(self):
        return pygame.Rect(self.x - 15, self.y - 15, 30, 30)


class DrugDealer:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.w, self.h = 38, 58
        # Prices fluctuate
        self.buy_price = random.randint(30, 60)   # Price to buy from dealer
        self.sell_price = random.randint(80, 150)  # Price dealer pays you
        self.stock = random.randint(5, 15)
        self.wants = random.randint(3, 10)
        self.cash = random.randint(200, 500)  # Dealer's cash for buying from player
        self.restock_timer = 0
    
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    @property
    def center(self):
        return (self.x + self.w//2, self.y + self.h//2)


class Mission:
    TYPES = ['kill_cops', 'earn_money', 'sell_drugs', 'survive', 'recruit_hoes']
    
    def __init__(self, mission_type=None, difficulty=1):
        self.type = mission_type or random.choice(self.TYPES)
        self.difficulty = difficulty
        self.active = False
        self.complete = False
        self.failed = False
        self.progress = 0
        self.start_value = 0  # Track starting point for incremental missions
        
        # Set targets based on type and difficulty
        if self.type == 'kill_cops':
            self.target = 3 + difficulty * 2
            self.description = f"Kill {self.target} cops"
            self.reward = 200 + difficulty * 150
        elif self.type == 'earn_money':
            self.target = 500 + difficulty * 300
            self.description = f"Earn ${self.target}"
            self.reward = 150 + difficulty * 100
        elif self.type == 'sell_drugs':
            self.target = 3 + difficulty * 2
            self.description = f"Sell {self.target} drugs"
            self.reward = 200 + difficulty * 150
        elif self.type == 'survive':
            self.target = 20 + difficulty * 10  # seconds
            self.description = f"Survive {self.target}s at 3+ stars"
            self.reward = 300 + difficulty * 250
            self.timer = 0
        elif self.type == 'recruit_hoes':
            self.target = 2 + difficulty
            self.description = f"Recruit {self.target} hoes"
            self.reward = 250 + difficulty * 200
    
    def start(self, player, game):
        """Start tracking this mission"""
        self.active = True
        self.progress = 0
        
        if self.type == 'earn_money':
            self.start_value = player.total_earned
        elif self.type == 'sell_drugs':
            self.start_value = player.total_drugs_sold
        elif self.type == 'kill_cops':
            self.start_value = player.kills
        elif self.type == 'recruit_hoes':
            self.start_value = len(game.hoes)
    
    def update(self, player, game):
        """Check mission progress"""
        if not self.active or self.complete:
            return
        
        if self.type == 'kill_cops':
            self.progress = player.kills - self.start_value
        elif self.type == 'earn_money':
            self.progress = player.total_earned - self.start_value
        elif self.type == 'sell_drugs':
            self.progress = player.total_drugs_sold - self.start_value
        elif self.type == 'survive':
            if player.wanted >= 3:
                self.timer += 1
                self.progress = self.timer // 60  # Convert to seconds
            else:
                self.timer = 0
                self.progress = 0
        elif self.type == 'recruit_hoes':
            self.progress = len(game.hoes) - self.start_value
        
        # Check completion
        if self.progress >= self.target:
            self.complete = True
    
    def get_progress_text(self):
        """Get progress display string"""
        if self.type == 'survive':
            return f"{self.progress}s / {self.target}s"
        return f"{self.progress} / {self.target}"


class Game:
    def __init__(self):
        self.player = Player()
        self.cops = []
        self.civilians = []
        self.hoes = []
        self.bullets = []
        self.blood = []
        self.buildings = []
        self.crack_dens = []
        self.strip_clubs = []
        self.gunstores = []
        self.upgrade_shops = []
        self.health_pickups = []
        self.drug_dealers = []
        self.camera = [0, 0]
        self.notification = None
        self.notification_timer = 0
        self.game_time = 0  # Total play time in frames
        # Win condition
        self.win_goal = 10000  # Cash goal to win
        self.game_won = False
        self.paused = False
        # Mission system
        self.available_missions = []
        self.active_mission = None
        self.completed_missions = 0
        self.mission_cooldown = 0
        self.mission_menu = False
        self.mission_selection = 0
        self.generate_world()
        self.spawn_npcs()
        # Spawn starting hoes near player
        for i in range(self.player.hoes):
            self.hoes.append(Hoe(self.player.x + random.randint(-100, 100), 
                                 self.player.y + random.randint(-100, 100)))
        # Generate initial missions
        self.generate_missions()
    
    def generate_world(self):
        random.seed(42)
        for x in range(MAP_W):
            for y in range(MAP_H):
                if random.random() < 0.06:
                    t = random.randint(1, 5)
                    rect = pygame.Rect(x*TILE, y*TILE, TILE, TILE)
                    self.buildings.append(rect)
                    center = (x*TILE + TILE//2, y*TILE + TILE//2)
                    if t == 2:
                        self.crack_dens.append((rect, center))
                    elif t == 3:
                        self.strip_clubs.append((rect, center))
                    elif t == 4:
                        self.gunstores.append((rect, center))
                    elif t == 5:
                        self.upgrade_shops.append((rect, center))
        random.seed()
        
        # Spawn drug dealers in open areas
        for _ in range(12):
            for _ in range(50):
                x = random.randint(200, MAP_W*TILE - 200)
                y = random.randint(200, MAP_H*TILE - 200)
                if not self.collides(x, y, 38, 58):
                    self.drug_dealers.append(DrugDealer(x, y))
                    break
    
    def spawn_npcs(self):
        # Spawn cops
        for _ in range(8):
            for _ in range(50):
                x = random.randint(100, MAP_W*TILE - 100)
                y = random.randint(100, MAP_H*TILE - 100)
                if not self.collides(x, y, 40, 60):
                    self.cops.append(Cop(x, y))
                    break
        
        # Spawn civilians
        for _ in range(30):
            for _ in range(50):
                x = random.randint(100, MAP_W*TILE - 100)
                y = random.randint(100, MAP_H*TILE - 100)
                if not self.collides(x, y, 35, 55):
                    self.civilians.append(Civilian(x, y))
                    break
    
    def generate_missions(self):
        """Generate available missions based on progress"""
        difficulty = 1 + self.completed_missions // 3  # Increase difficulty every 3 missions
        difficulty = min(difficulty, 5)  # Cap at 5
        
        self.available_missions = [
            Mission('kill_cops', difficulty),
            Mission('earn_money', difficulty),
            Mission('sell_drugs', difficulty),
        ]
        
        # Add harder missions at higher difficulties
        if difficulty >= 2:
            self.available_missions.append(Mission('survive', difficulty))
        if difficulty >= 3:
            self.available_missions.append(Mission('recruit_hoes', difficulty))
    
    def start_mission(self, mission):
        """Start a specific mission"""
        if self.active_mission:
            return False
        
        self.active_mission = mission
        mission.start(self.player, self)
        self.show_notification(f"Mission Started: {mission.description}", 180)
        return True
    
    def complete_mission(self):
        """Complete the active mission and give rewards"""
        if not self.active_mission or not self.active_mission.complete:
            return
        
        reward = self.active_mission.reward
        self.player.cash += reward
        self.player.total_earned += reward
        self.completed_missions += 1
        self.player.missions_complete += 1
        
        self.show_notification(f"Mission Complete! +${reward}", 180)
        self.spawn_message(self.player.x, self.player.y - 50, f"+${reward}", C['gold'])
        
        self.active_mission = None
        self.mission_cooldown = 300  # 5 second cooldown before new missions
        
        # Generate new missions
        self.generate_missions()
    
    def abandon_mission(self):
        """Abandon the current mission"""
        if self.active_mission:
            self.show_notification("Mission Abandoned", 120)
            self.active_mission = None
            self.mission_cooldown = 180  # 3 second cooldown
    
    def update_mission(self):
        """Update active mission progress"""
        if self.mission_cooldown > 0:
            self.mission_cooldown -= 1
        
        if self.active_mission:
            self.active_mission.update(self.player, self)
            
            if self.active_mission.complete:
                self.complete_mission()
    
    def collides(self, x, y, w, h):
        rect = pygame.Rect(x, y, w, h)
        for b in self.buildings:
            if rect.colliderect(b):
                return True
        return False
    
    def spawn_blood(self, x, y, n=15):
        for _ in range(n):
            self.blood.append({
                'x': x + random.randint(-25, 25),
                'y': y + random.randint(-25, 25),
                'life': 180
            })
    
    def spawn_message(self, x, y, text, color):
        """Spawn floating text message"""
        if not hasattr(self, 'floating_texts'):
            self.floating_texts = []
        self.floating_texts.append({
            'x': x, 'y': y, 
            'text': text, 
            'color': color,
            'life': 60,
            'vy': -2
        })
    
    def shoot(self, angle):
        p = self.player
        if p.ammo <= 0 or p.shoot_cooldown > 0 or p.inside:
            return
        
        if not (p.has_gun or p.has_shotgun or p.has_uzi):
            return
        
        spread = 0.1
        shots = 1
        
        if p.has_shotgun:
            spread = 0.25
            shots = 5
            p.shoot_cooldown = 30
        elif p.has_uzi:
            spread = 0.15
            p.shoot_cooldown = 5
        else:
            p.shoot_cooldown = 12
        
        for _ in range(shots):
            a = angle + random.uniform(-spread, spread)
            self.bullets.append(Bullet(p.x + p.w//2, p.y + p.h//2, a, 'player'))
        
        p.ammo -= 1
        p.ammo = max(0, p.ammo)  # Prevent negative ammo
        
        p.wanted = min(5, p.wanted + 0.2)
    
    def melee(self):
        p = self.player
        if p.inside:
            return
        
        # Hit cops
        for cop in self.cops[:]:
            dist = math.hypot(cop.x - p.x, cop.y - p.y)
            if dist < 80:
                cop.health -= 35
                self.spawn_blood(cop.center[0], cop.center[1], 12)
                cop.alert = True
                if cop.health <= 0:
                    self.cops.remove(cop)
                    self.spawn_blood(cop.center[0], cop.center[1], 30)
                    p.wanted = min(5, p.wanted + 1)
        
        # Hit civilians
        for civ in self.civilians[:]:
            dist = math.hypot(civ.x - p.x, civ.y - p.y)
            if dist < 80:
                self.civilians.remove(civ)
                self.spawn_blood(civ.center[0], civ.center[1], 25)
                p.wanted = min(5, p.wanted + 0.5)
                p.cash += random.randint(10, 50)
        
        p.wanted = min(5, p.wanted + 0.3)
    
    def enter_building(self):
        p = self.player
        if p.inside:
            return
        
        px, py = p.center
        
        for rect, center in self.crack_dens:
            if math.hypot(px - center[0], py - center[1]) < 80:
                p.inside = True
                p.building_type = 'crack'
                p.entry_pos = (p.x, p.y)
                p.cooking = False
                return
        
        for rect, center in self.strip_clubs:
            if math.hypot(px - center[0], py - center[1]) < 80:
                p.inside = True
                p.building_type = 'strip'
                p.entry_pos = (p.x, p.y)
                p.mash_count = 0
                p.mash_target = random.randint(12, 25)
                return
        
        for rect, center in self.gunstores:
            if math.hypot(px - center[0], py - center[1]) < 80:
                p.inside = True
                p.building_type = 'gun'
                p.entry_pos = (p.x, p.y)
                return
        
        for rect, center in self.upgrade_shops:
            if math.hypot(px - center[0], py - center[1]) < 80:
                p.inside = True
                p.building_type = 'upgrade'
                p.entry_pos = (p.x, p.y)
                p.upgrade_selection = 0
                return
        
        # Dealer interaction
        dealer = self.get_nearby_dealer()
        if dealer:
            p.inside = True
            p.building_type = 'dealer'
            p.entry_pos = (p.x, p.y)
            p.current_dealer = dealer
            p.dealer_selection = 0
            return
    
    def exit_building(self):
        p = self.player
        if not p.inside:
            return
        p.inside = False
        p.building_type = None
        p.cooking = False
        p.x, p.y = p.entry_pos
    
    def interact(self):
        p = self.player
        if not p.inside:
            return
        
        if p.building_type == 'crack':
            if not p.cooking:
                p.cooking = True
                p.cook_stage = 0
                p.cook_bar = 0.0
                p.cook_target = random.uniform(0.3, 0.7)
                p.cook_zone = 0.15
                p.cook_speed = 0.012
            else:
                # Check if hit the target
                if abs(p.cook_bar - p.cook_target) < p.cook_zone / 2:
                    p.cook_stage += 1
                    if p.cook_stage >= 3:
                        # Successful cook - get crack
                        p.drugs['crack'] += 3
                        self.spawn_message(p.x, p.y, "+3 CRACK", C['purple'])
                        p.cooking = False
                        self.exit_building()
                    else:
                        p.cook_bar = 0.0
                        p.cook_target = random.uniform(0.2, 0.8)
                        p.cook_zone = max(0.08, p.cook_zone - 0.02)
                        p.cook_speed += 0.004
                else:
                    # Failed
                    p.cook_stage = 0
                    p.cook_bar = 0.0
                    p.cook_zone = 0.15
                    p.cook_speed = 0.012
                    p.cook_target = random.uniform(0.3, 0.7)
        
        elif p.building_type == 'strip':
            p.mash_count += 1
            if p.mash_count >= p.mash_target:
                # Recruit a hoe
                hoe = Hoe(p.entry_pos[0] + random.randint(-50, 50),
                         p.entry_pos[1] + random.randint(-50, 50))
                self.hoes.append(hoe)
                p.cash += 50
                p.mash_count = 0
                p.mash_target = random.randint(12, 25)
        
        elif p.building_type == 'gun':
            # Gun store - buy selected item
            if not hasattr(p, 'gun_selection'):
                p.gun_selection = 0
            
            items = [
                ('Pistol', 200, 30, 'pistol'),
                ('Shotgun', 500, 20, 'shotgun'),
                ('Uzi', 800, 50, 'uzi'),
                ('Ammo x30', 100, 30, 'ammo'),
            ]
            
            name, price, ammo_bonus, item_type = items[p.gun_selection]
            
            # Check if already owned (except ammo)
            owned = False
            if item_type == 'pistol' and p.has_gun:
                owned = True
            elif item_type == 'shotgun' and p.has_shotgun:
                owned = True
            elif item_type == 'uzi' and p.has_uzi:
                owned = True
            
            if not owned and p.cash >= price:
                if item_type == 'pistol':
                    p.has_gun = True
                    p.ammo += ammo_bonus
                    p.cash -= price
                    self.spawn_message(p.x, p.y, "PISTOL!", C['gold'])
                elif item_type == 'shotgun':
                    p.has_shotgun = True
                    p.ammo += ammo_bonus
                    p.cash -= price
                    self.spawn_message(p.x, p.y, "SHOTGUN!", C['gold'])
                elif item_type == 'uzi':
                    p.has_uzi = True
                    p.ammo += ammo_bonus
                    p.cash -= price
                    self.spawn_message(p.x, p.y, "UZI!", C['gold'])
                elif item_type == 'ammo':
                    p.ammo += ammo_bonus
                    p.cash -= price
                    self.spawn_message(p.x, p.y, f"+{ammo_bonus} AMMO", C['yellow'])
        
        elif p.building_type == 'dealer':
            # Dealer interaction - buy/sell drugs
            if not hasattr(p, 'dealer_selection'):
                p.dealer_selection = 0
            if not hasattr(p, 'current_dealer'):
                return
            
            dealer = p.current_dealer
            
            if p.dealer_selection == 0:
                # Buy crack from dealer
                if dealer.stock > 0 and p.cash >= dealer.buy_price:
                    p.drugs['crack'] += 1
                    p.cash -= dealer.buy_price
                    dealer.stock -= 1
                    dealer.cash += dealer.buy_price
                    self.spawn_message(p.x, p.y, f"-${dealer.buy_price}", C['red'])
            elif p.dealer_selection == 1:
                # Sell crack to dealer
                if p.drugs['crack'] > 0 and dealer.cash >= dealer.sell_price:
                    p.drugs['crack'] -= 1
                    p.cash += dealer.sell_price
                    dealer.stock += 1
                    dealer.cash -= dealer.sell_price
                    p.total_drugs_sold += 1
                    p.total_earned += dealer.sell_price
                    self.spawn_message(p.x, p.y, f"+${dealer.sell_price}", C['green'])
        
        elif p.building_type == 'upgrade':
            # Upgrade shop interaction
            if not hasattr(p, 'upgrade_selection'):
                p.upgrade_selection = 0
            
            upgrades = [
                ('Max Health +25', 500, 'max_health', 25),
                ('Speed +1', 400, 'speed_bonus', 1),
                ('Armor +10%', 600, 'armor', 10),
                ('Damage +20%', 800, 'damage_mult', 0.2),
            ]
            
            name, price, attr, amount = upgrades[p.upgrade_selection]
            
            if p.cash >= price:
                p.cash -= price
                current = getattr(p, attr)
                setattr(p, attr, current + amount)
                
                # Apply max_health bonus immediately
                if attr == 'max_health':
                    p.health = min(p.health + amount, p.max_health)
                
                self.spawn_message(p.x, p.y, f"{name}!", C['neon'])
    
    def update(self, dt):
        p = self.player
        
        if not p.alive:
            p.respawn_timer -= 1
            if p.respawn_timer <= 0:
                p.alive = True
                p.health = p.max_health
                p.x, p.y = 500, 500
                p.wanted = 0
                p.inside = False
            return
        
        p.shoot_cooldown = max(0, p.shoot_cooldown - 1)
        p.wanted = max(0, p.wanted - 0.001)
        
        # Decay screen effects
        if p.damage_flash > 0:
            p.damage_flash -= 1
        if p.screen_shake > 0:
            p.screen_shake -= 1
        
        # Update missions
        self.update_mission()
        
        # Cooking bar
        if p.cooking:
            p.cook_bar += p.cook_speed
            if p.cook_bar > 1.0:
                p.cook_bar = 0.0
        
        # Hoe income
        for hoe in self.hoes:
            hoe.income_timer += 1
            if hoe.income_timer >= 300:  # Every 5 seconds at 60fps
                p.cash += 15
                hoe.income_timer = 0
        
        # Update hoes - follow player
        for hoe in self.hoes:
            dx = p.x - hoe.x
            dy = p.y - hoe.y
            dist = math.hypot(dx, dy)
            if dist > 100:
                hoe.x += dx / dist * 4
                hoe.y += dy / dist * 4
        
        if p.inside:
            return
        
        # Update cops
        for cop in self.cops:
            dist = math.hypot(p.x - cop.x, p.y - cop.y)
            
            # Alert if player has wanted level or is close
            if p.wanted >= 1 or dist < 300:
                cop.alert = True
            
            if cop.alert and dist < 600:
                # Chase player
                dx = p.x - cop.x
                dy = p.y - cop.y
                d = dist + 0.1
                speed = 3.5 if p.wanted >= 3 else 2.5
                
                nx = cop.x + dx/d * speed
                ny = cop.y + dy/d * speed
                
                if not self.collides(nx, cop.y, cop.w, cop.h):
                    cop.x = nx
                if not self.collides(cop.x, ny, cop.w, cop.h):
                    cop.y = ny
                
                # Shoot at player
                cop.shoot_timer += 1
                if cop.shoot_timer > 60 and dist < 400:
                    a = math.atan2(dy, dx) + random.uniform(-0.1, 0.1)
                    self.bullets.append(Bullet(cop.x + cop.w//2, cop.y + cop.h//2, a, 'cop'))
                    cop.shoot_timer = 0
            else:
                # Patrol
                cop.angle += 0.02
                nx = cop.x + math.cos(cop.angle) * 1.5
                ny = cop.y + math.sin(cop.angle) * 1.5
                if not self.collides(nx, ny, cop.w, cop.h):
                    cop.x, cop.y = nx, ny
        
        # Update civilians
        for civ in self.civilians:
            dist = math.hypot(p.x - civ.x, p.y - civ.y)
            
            # Scare civilians if shooting or wanted
            if p.wanted >= 1 and dist < 300:
                civ.scared = True
                civ.scared_timer = 180
            
            if civ.scared and civ.scared_timer > 0:
                civ.scared_timer -= 1
                # Run away from player
                dx = civ.x - p.x
                dy = civ.y - p.y
                d = dist + 0.1
                nx = civ.x + dx/d * 4
                ny = civ.y + dy/d * 4
                if not self.collides(nx, ny, civ.w, civ.h):
                    civ.x, civ.y = nx, ny
            else:
                civ.scared = False
                # Random walking
                civ.move_timer -= 1
                if civ.move_timer <= 0:
                    civ.angle = random.random() * 6.28
                    civ.move_timer = random.randint(60, 180)
                
                nx = civ.x + math.cos(civ.angle) * 1
                ny = civ.y + math.sin(civ.angle) * 1
                if not self.collides(nx, ny, civ.w, civ.h):
                    civ.x, civ.y = nx, ny
        
        # Update bullets
        for b in self.bullets[:]:
            b.x += b.vx
            b.y += b.vy
            b.life -= 1
            
            # Remove if expired or hit building
            if b.life <= 0 or self.collides(b.x - 4, b.y - 4, 8, 8):
                self.bullets.remove(b)
                continue
            
            # Hit player
            if b.owner == 'cop':
                if abs(b.x - p.center[0]) < 25 and abs(b.y - p.center[1]) < 35:
                    # Apply armor damage reduction
                    base_damage = 25
                    actual_damage = int(base_damage * (1 - p.armor / 100))
                    p.health -= actual_damage
                    p.damage_flash = 10  # Screen flash effect
                    self.spawn_blood(b.x, b.y, 10)
                    self.bullets.remove(b)
                    if p.health <= 0:
                        p.alive = False
                        p.respawn_timer = 180
                        self.spawn_blood(p.center[0], p.center[1], 50)
                    continue
            
            # Hit cops
            if b.owner == 'player':
                for cop in self.cops[:]:
                    if abs(b.x - cop.center[0]) < 25 and abs(b.y - cop.center[1]) < 35:
                        # Apply damage multiplier
                        base_damage = 35
                        actual_damage = int(base_damage * p.damage_mult)
                        cop.health -= actual_damage
                        cop.alert = True
                        self.spawn_blood(b.x, b.y, 12)
                        if b in self.bullets:
                            self.bullets.remove(b)
                        if cop.health <= 0:
                            self.cops.remove(cop)
                            self.spawn_blood(cop.center[0], cop.center[1], 35)
                            p.wanted = min(5, p.wanted + 1)
                            p.cash += random.randint(20, 50)
                            p.kills += 1
                            p.total_earned += random.randint(20, 50)
                        break
                
                # Hit civilians
                for civ in self.civilians[:]:
                    if abs(b.x - civ.center[0]) < 20 and abs(b.y - civ.center[1]) < 30:
                        self.civilians.remove(civ)
                        self.spawn_blood(b.x, b.y, 20)
                        if b in self.bullets:
                            self.bullets.remove(b)
                        p.wanted = min(5, p.wanted + 0.5)
                        p.cash += random.randint(5, 30)
                        # Scare nearby civilians
                        for c in self.civilians:
                            if math.hypot(c.x - civ.x, c.y - civ.y) < 200:
                                c.scared = True
                                c.scared_timer = 180
                        break
        
        # Decay blood
        for b in self.blood[:]:
            b['life'] -= 1
            if b['life'] <= 0:
                self.blood.remove(b)
        
        # Respawn cops if too few
        if len(self.cops) < 5 + int(p.wanted * 2):
            for _ in range(50):
                angle = random.random() * 6.28
                dist = random.randint(800, 1200)
                x = p.x + math.cos(angle) * dist
                y = p.y + math.sin(angle) * dist
                x = max(100, min(MAP_W*TILE - 100, x))
                y = max(100, min(MAP_H*TILE - 100, y))
                if not self.collides(x, y, 40, 60):
                    cop = Cop(x, y)
                    cop.alert = p.wanted >= 2
                    self.cops.append(cop)
                    break
        
        # Respawn civilians
        if len(self.civilians) < 20:
            for _ in range(50):
                x = random.randint(100, MAP_W*TILE - 100)
                y = random.randint(100, MAP_H*TILE - 100)
                if not self.collides(x, y, 35, 55) and math.hypot(x - p.x, y - p.y) > 600:
                    self.civilians.append(Civilian(x, y))
                    break
        
        # Spawn health pickups occasionally
        if len(self.health_pickups) < 5 and random.random() < 0.002:
            for _ in range(50):
                x = random.randint(100, MAP_W*TILE - 100)
                y = random.randint(100, MAP_H*TILE - 100)
                if not self.collides(x - 15, y - 15, 30, 30):
                    self.health_pickups.append(HealthPickup(x, y))
                    break
        
        # Collect health pickups
        for hp in self.health_pickups[:]:
            if math.hypot(p.center[0] - hp.x, p.center[1] - hp.y) < 40:
                if p.health < p.max_health:
                    heal = min(hp.amount, p.max_health - p.health)
                    p.health += heal
                    self.spawn_message(hp.x, hp.y, f"+{heal} HP", C['green'])
                    self.health_pickups.remove(hp)
        
        # Update floating texts
        if hasattr(self, 'floating_texts'):
            for ft in self.floating_texts[:]:
                ft['y'] += ft['vy']
                ft['life'] -= 1
                if ft['life'] <= 0:
                    self.floating_texts.remove(ft)
        
        # Update notification
        if self.notification_timer > 0:
            self.notification_timer -= 1
            if self.notification_timer <= 0:
                self.notification = None
        
        # Update game time
        self.game_time += 1
        
        # Check win condition
        if p.total_earned >= self.win_goal and not self.game_won:
            self.game_won = True
            self.show_notification("YOU WIN! Press ESC to see stats", 300)
    
    def draw_world(self):
        p = self.player
        cam = self.camera
        
        # Ground
        for ty in range(max(0, int(cam[1]//TILE) - 1), min(MAP_H, int((cam[1]+SCREEN_H)//TILE) + 2)):
            for tx in range(max(0, int(cam[0]//TILE) - 1), min(MAP_W, int((cam[0]+SCREEN_W)//TILE) + 2)):
                col = (22, 22, 32) if (tx + ty) % 2 == 0 else (28, 28, 38)
                pygame.draw.rect(screen, col, (tx*TILE - cam[0], ty*TILE - cam[1], TILE, TILE))
        
        # Buildings
        crack_rects = [r for r, c in self.crack_dens]
        strip_rects = [r for r, c in self.strip_clubs]
        gun_rects = [r for r, c in self.gunstores]
        upgrade_rects = [r for r, c in self.upgrade_shops]
        
        for b in self.buildings:
            bx, by = b.x - cam[0], b.y - cam[1]
            if bx < -TILE or bx > SCREEN_W or by < -TILE or by > SCREEN_H:
                continue
            
            if b in crack_rects:
                pygame.draw.rect(screen, C['purple'], (bx, by, TILE, TILE))
                screen.blit(F['tiny'].render("CRACK", True, C['neon']), (bx + 6, by + 24))
            elif b in strip_rects:
                pygame.draw.rect(screen, (150, 0, 100), (bx, by, TILE, TILE))
                screen.blit(F['tiny'].render("XXX", True, C['pink']), (bx + 16, by + 24))
            elif b in gun_rects:
                pygame.draw.rect(screen, (180, 150, 50), (bx, by, TILE, TILE))
                screen.blit(F['tiny'].render("GUN", True, (40, 30, 0)), (bx + 16, by + 24))
            elif b in upgrade_rects:
                pygame.draw.rect(screen, (50, 80, 120), (bx, by, TILE, TILE))
                screen.blit(F['tiny'].render("UPGR", True, C['neon']), (bx + 10, by + 24))
            else:
                pygame.draw.rect(screen, C['gray'], (bx, by, TILE, TILE))
        
        # Drug dealers
        for dealer in self.drug_dealers:
            dx, dy = dealer.x - cam[0], dealer.y - cam[1]
            if dx < -50 or dx > SCREEN_W + 50 or dy < -50 or dy > SCREEN_H + 50:
                continue
            pygame.draw.ellipse(screen, (20, 20, 30), (dx + 3, dy + 53, 32, 8))
            pygame.draw.rect(screen, (50, 150, 50), (dx, dy, dealer.w, dealer.h))
            pygame.draw.rect(screen, (0, 0, 0), (dx, dy, dealer.w, dealer.h), 2)
            pygame.draw.circle(screen, (180, 150, 120), (int(dx + dealer.w//2), int(dy + 12)), 9)
            # Dollar sign above head
            screen.blit(F['small'].render("$", True, C['green']), (dx + dealer.w//2 - 5, dy - 20))
        
        # Health pickups
        for hp in self.health_pickups:
            hx, hy = hp.x - cam[0], hp.y - cam[1]
            if hx < -30 or hx > SCREEN_W + 30 or hy < -30 or hy > SCREEN_H + 30:
                continue
            hp.pulse = (hp.pulse + 0.1) % 6.28
            size = 12 + int(math.sin(hp.pulse) * 3)
            pygame.draw.rect(screen, C['red'], (hx - size//2, hy - 4, size, 8))
            pygame.draw.rect(screen, C['red'], (hx - 4, hy - size//2, 8, size))
            pygame.draw.rect(screen, C['white'], (hx - size//2, hy - 4, size, 8), 1)
            pygame.draw.rect(screen, C['white'], (hx - 4, hy - size//2, 8, size), 1)
        
        # Blood
        for b in self.blood:
            bx, by = b['x'] - cam[0], b['y'] - cam[1]
            size = max(2, b['life'] // 30)
            pygame.draw.circle(screen, C['blood'], (int(bx), int(by)), size)
        
        # Hoes
        for hoe in self.hoes:
            hx, hy = hoe.x - cam[0], hoe.y - cam[1]
            pygame.draw.ellipse(screen, (20, 20, 30), (hx + 3, hy + 45, 24, 8))
            pygame.draw.ellipse(screen, hoe.color, (hx, hy, hoe.w, hoe.h))
            pygame.draw.ellipse(screen, (0, 0, 0), (hx, hy, hoe.w, hoe.h), 2)
        
        # Civilians
        for civ in self.civilians:
            cx, cy = civ.x - cam[0], civ.y - cam[1]
            pygame.draw.ellipse(screen, (20, 20, 30), (cx + 3, cy + 50, 28, 8))
            pygame.draw.rect(screen, civ.color, (cx, cy, civ.w, civ.h))
            pygame.draw.rect(screen, (0, 0, 0), (cx, cy, civ.w, civ.h), 2)
            pygame.draw.circle(screen, (255, 220, 180), (int(cx + civ.w//2), int(cy + 12)), 8)
            if civ.scared:
                screen.blit(F['tiny'].render("!", True, C['red']), (cx + civ.w//2 - 3, cy - 18))
        
        # Cops
        for cop in self.cops:
            cx, cy = cop.x - cam[0], cop.y - cam[1]
            pygame.draw.ellipse(screen, (20, 20, 30), (cx + 3, cy + 55, 32, 8))
            pygame.draw.rect(screen, C['cop'], (cx, cy, cop.w, cop.h))
            pygame.draw.rect(screen, (0, 0, 0), (cx, cy, cop.w, cop.h), 2)
            pygame.draw.circle(screen, (255, 220, 180), (int(cx + cop.w//2), int(cy + 12)), 9)
            # Health bar
            if cop.health < cop.max_health:
                pygame.draw.rect(screen, (60, 0, 0), (cx, cy - 10, 40, 6))
                pygame.draw.rect(screen, C['red'], (cx, cy - 10, 40 * cop.health // cop.max_health, 6))
            if cop.alert:
                screen.blit(F['tiny'].render("!", True, C['red']), (cx + cop.w//2 - 3, cy - 22))
        
        # Player
        if p.alive and not p.inside:
            px, py = p.x - cam[0], p.y - cam[1]
            pygame.draw.ellipse(screen, (20, 20, 30), (px + 3, py + 55, 32, 10))
            pygame.draw.rect(screen, C['purple'], (px, py, p.w, p.h))
            pygame.draw.rect(screen, (0, 0, 0), (px, py, p.w, p.h), 3)
            pygame.draw.circle(screen, (255, 230, 200), (int(px + p.w//2), int(py + 14)), 10)
            pygame.draw.rect(screen, C['gold'], (px - 2, py - 2, p.w + 4, p.h + 4), 2)
        
        # Bullets
        for b in self.bullets:
            bx, by = b.x - cam[0], b.y - cam[1]
            col = C['yellow'] if b.owner == 'player' else C['red']
            pygame.draw.circle(screen, col, (int(bx), int(by)), 5)
            pygame.draw.circle(screen, C['white'], (int(bx), int(by)), 3)
        
        # Floating texts
        if hasattr(self, 'floating_texts'):
            for ft in self.floating_texts[:]:
                fx, fy = ft['x'] - cam[0], ft['y'] - cam[1]
                alpha = int(255 * ft['life'] / 60)
                txt = F['main'].render(ft['text'], True, ft['color'])
                txt.set_alpha(alpha)
                screen.blit(txt, (fx - txt.get_width()//2, fy))
    
    def draw_interior(self):
        p = self.player
        
        if p.building_type == 'crack':
            screen.fill((40, 0, 60))
            
            # Table
            pygame.draw.rect(screen, C['table'], (SCREEN_W//2 - 100, SCREEN_H//2 - 40, 200, 100))
            pygame.draw.rect(screen, C['gold'], (SCREEN_W//2 - 100, SCREEN_H//2 - 40, 200, 100), 4)
            
            title = F['big'].render("CRACK DEN", True, C['purple'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 60))
            
            if not p.cooking:
                hint = F['main'].render("Press SPACE to cook", True, C['neon'])
                screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 120))
            else:
                stage = F['main'].render(f"Stage {p.cook_stage + 1}/3", True, C['gold'])
                screen.blit(stage, (SCREEN_W//2 - stage.get_width()//2, 150))
                
                # Bar
                bar_rect = pygame.Rect(200, 420, 880, 50)
                pygame.draw.rect(screen, (50, 50, 70), bar_rect)
                
                # Target zone
                zone_x = 200 + int((p.cook_target - p.cook_zone/2) * 880)
                zone_w = int(p.cook_zone * 880)
                pygame.draw.rect(screen, C['green'], (zone_x, 420, zone_w, 50))
                
                # Indicator
                ind_x = 200 + int(p.cook_bar * 880)
                pygame.draw.rect(screen, C['neon'], (ind_x - 3, 415, 6, 60))
                
                pygame.draw.rect(screen, C['white'], bar_rect, 3)
                
                hint = F['main'].render("Press SPACE in the GREEN zone!", True, C['white'])
                screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 520))
        
        elif p.building_type == 'strip':
            screen.fill((60, 0, 50))
            
            title = F['big'].render("STRIP CLUB", True, C['pink'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 60))
            
            # Progress bar
            bar_rect = pygame.Rect(300, 320, 680, 50)
            pygame.draw.rect(screen, (80, 40, 60), bar_rect)
            progress = min(1.0, p.mash_count / p.mash_target)
            pygame.draw.rect(screen, C['pink'], (300, 320, int(680 * progress), 50))
            pygame.draw.rect(screen, C['white'], bar_rect, 3)
            
            counter = F['big'].render(f"{p.mash_count}/{p.mash_target}", True, C['gold'])
            screen.blit(counter, (SCREEN_W//2 - counter.get_width()//2, 220))
            
            hint = F['main'].render("MASH SPACE to recruit!", True, C['white'])
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 420))
            
            hoes_txt = F['main'].render(f"Your Hoes: {len(self.hoes)}", True, C['neon'])
            screen.blit(hoes_txt, (SCREEN_W//2 - hoes_txt.get_width()//2, 500))
        
        elif p.building_type == 'gun':
            screen.fill((50, 40, 30))
            
            title = F['big'].render("GUN STORE", True, C['gold'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 60))
            
            # Initialize selection if needed
            if not hasattr(p, 'gun_selection'):
                p.gun_selection = 0
            
            # Display items
            items = [
                ("1. Pistol + 30 Ammo - $200", 200, p.has_gun, 0),
                ("2. Shotgun + 20 Ammo - $500", 500, p.has_shotgun, 1),
                ("3. Uzi + 50 Ammo - $800", 800, p.has_uzi, 2),
                ("4. Ammo Refill (25) - $100", 100, False, 3),
            ]
            
            y = 180
            for text, price, owned, idx in items:
                # Selection indicator
                selected = (p.gun_selection == idx)
                prefix = "► " if selected else "  "
                
                if idx == 3:  # Ammo refill
                    if not p.has_gun and not p.has_shotgun and not p.has_uzi:
                        col = (80, 80, 80)  # Gray if no weapon
                        txt = F['main'].render(prefix + text + " [NO WEAPON]", True, col)
                    elif p.cash >= price:
                        col = C['neon'] if selected else C['gold']
                        txt = F['main'].render(prefix + text, True, col)
                    else:
                        col = C['red']
                        txt = F['main'].render(prefix + text, True, col)
                elif owned:
                    col = C['green']
                    txt = F['main'].render(prefix + text + " [OWNED]", True, col)
                elif p.cash >= price:
                    col = C['neon'] if selected else C['gold']
                    txt = F['main'].render(prefix + text, True, col)
                else:
                    col = C['red']
                    txt = F['main'].render(prefix + text, True, col)
                screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, y))
                y += 50
            
            hint = F['main'].render("SPACE = Buy Selected Item", True, C['white'])
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 420))
            
            ammo_txt = F['main'].render(f"Your Ammo: {p.ammo}", True, C['neon'])
            screen.blit(ammo_txt, (SCREEN_W//2 - ammo_txt.get_width()//2, 480))
            
            cash_txt = F['main'].render(f"Your Cash: ${p.cash}", True, C['gold'])
            screen.blit(cash_txt, (SCREEN_W//2 - cash_txt.get_width()//2, 520))
        
        elif p.building_type == 'dealer':
            screen.fill((20, 40, 20))
            
            title = F['big'].render("DRUG DEALER", True, C['green'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 60))
            
            if hasattr(p, 'current_dealer'):
                dealer = p.current_dealer
                if not hasattr(p, 'dealer_selection'):
                    p.dealer_selection = 0
                
                # Show dealer info
                info = F['main'].render(f"Dealer Stock: {dealer.stock} | Dealer Cash: ${dealer.cash}", True, C['white'])
                screen.blit(info, (SCREEN_W//2 - info.get_width()//2, 140))
                
                # Options
                options = [
                    (f"BUY Crack - ${dealer.buy_price} each", dealer.stock > 0 and p.cash >= dealer.buy_price),
                    (f"SELL Crack - ${dealer.sell_price} each", p.drugs['crack'] > 0 and dealer.cash >= dealer.sell_price),
                ]
                
                y = 220
                for i, (text, available) in enumerate(options):
                    selected = (p.dealer_selection == i)
                    prefix = "► " if selected else "  "
                    col = C['neon'] if selected and available else (C['green'] if available else C['red'])
                    txt = F['main'].render(prefix + text, True, col)
                    screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, y))
                    y += 60
                
                # Player inventory
                inv = F['main'].render(f"Your Crack: {p.drugs['crack']} | Your Cash: ${p.cash}", True, C['gold'])
                screen.blit(inv, (SCREEN_W//2 - inv.get_width()//2, 400))
                
                hint = F['main'].render("W/S = Select | SPACE = Confirm", True, C['white'])
                screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 500))
        
        elif p.building_type == 'upgrade':
            screen.fill((30, 30, 60))
            
            title = F['big'].render("UPGRADE SHOP", True, C['neon'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 60))
            
            if not hasattr(p, 'upgrade_selection'):
                p.upgrade_selection = 0
            
            upgrades = [
                (f"Max Health +25 - $500", 500, f"Current: {p.max_health}"),
                (f"Speed +1 - $400", 400, f"Current: {p.speed + p.speed_bonus}"),
                (f"Armor +10% - $600", 600, f"Current: {p.armor}%"),
                (f"Damage +20% - $800", 800, f"Current: {int(p.damage_mult * 100)}%"),
            ]
            
            y = 180
            for i, (text, price, current) in enumerate(upgrades):
                selected = (p.upgrade_selection == i)
                prefix = "► " if selected else "  "
                available = p.cash >= price
                col = C['neon'] if selected and available else (C['gold'] if available else C['red'])
                txt = F['main'].render(prefix + text, True, col)
                screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, y))
                # Show current stat
                curr_txt = F['small'].render(current, True, (150, 150, 150))
                screen.blit(curr_txt, (SCREEN_W//2 + 200, y + 5))
                y += 55
            
            cash_txt = F['main'].render(f"Your Cash: ${p.cash}", True, C['gold'])
            screen.blit(cash_txt, (SCREEN_W//2 - cash_txt.get_width()//2, 450))
            
            hint = F['main'].render("W/S = Select | SPACE = Buy", True, C['white'])
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 520))
        
        # Exit hint
        exit_txt = F['small'].render("ESC = Exit", True, (150, 150, 150))
        screen.blit(exit_txt, (20, SCREEN_H - 40))
    
    def draw_hud(self):
        p = self.player
        
        # Background
        hud = pygame.Surface((SCREEN_W, 60), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 180))
        screen.blit(hud, (0, 0))
        
        # Name & cash
        screen.blit(F['main'].render("RICO", True, C['purple']), (15, 8))
        screen.blit(F['main'].render(f"${p.cash}", True, C['gold']), (15, 32))
        
        # Weapon
        if p.has_uzi:
            weapon = "UZI"
        elif p.has_shotgun:
            weapon = "SHOTGUN"
        elif p.has_gun:
            weapon = "PISTOL"
        else:
            weapon = "FISTS"
        
        has_weapon = p.has_gun or p.has_shotgun or p.has_uzi
        if has_weapon and p.ammo > 0:
            weapon_col = C['yellow']
        elif has_weapon and p.ammo <= 0:
            weapon_col = C['red']
        else:
            weapon_col = C['gray']
        
        ammo_str = f" [{p.ammo}]" if has_weapon else ""
        empty_str = " EMPTY!" if has_weapon and p.ammo <= 0 else ""
        screen.blit(F['small'].render(f"{weapon}{ammo_str}{empty_str}", True, weapon_col), (120, 10))
        
        # Hoes and Drugs
        screen.blit(F['small'].render(f"Hoes: {len(self.hoes)}", True, C['pink']), (120, 32))
        drugs_total = sum(p.drugs.values())
        if drugs_total > 0:
            screen.blit(F['small'].render(f"Crack: {p.drugs['crack']}", True, C['purple']), (200, 32))
        
        # Wanted stars
        for i in range(5):
            col = C['gold'] if i < int(p.wanted) else (60, 60, 60)
            screen.blit(F['main'].render("★", True, col), (300 + i * 24, 15))
        
        # Health bar
        bar_x = SCREEN_W - 260
        pygame.draw.rect(screen, (40, 40, 50), (bar_x, 18, 240, 24))
        hw = int(240 * p.health / p.max_health)
        col = C['green'] if p.health > 30 else C['red']
        pygame.draw.rect(screen, col, (bar_x, 18, hw, 24))
        pygame.draw.rect(screen, C['white'], (bar_x, 18, 240, 24), 2)
        hp_txt = F['small'].render(f"HP: {p.health}/{p.max_health}", True, C['white'])
        screen.blit(hp_txt, (bar_x + 120 - hp_txt.get_width()//2, 20))
        
        # Armor indicator
        if p.armor > 0:
            armor_txt = F['tiny'].render(f"Armor: {p.armor}%", True, C['neon'])
            screen.blit(armor_txt, (bar_x, 44))
        
        # Minimap (bottom right)
        if not p.inside:
            map_size = 120
            map_x, map_y = SCREEN_W - map_size - 10, SCREEN_H - map_size - 35
            pygame.draw.rect(screen, (20, 20, 30), (map_x, map_y, map_size, map_size))
            pygame.draw.rect(screen, C['white'], (map_x, map_y, map_size, map_size), 1)
            
            # Scale: world to minimap
            scale = map_size / 800
            center_x, center_y = p.x, p.y
            
            # Draw buildings on minimap
            for b in self.buildings:
                bx = map_x + map_size//2 + int((b.x - center_x) * scale)
                by = map_y + map_size//2 + int((b.y - center_y) * scale)
                if map_x < bx < map_x + map_size and map_y < by < map_y + map_size:
                    pygame.draw.rect(screen, (60, 60, 70), (bx, by, 2, 2))
            
            # Draw dealers on minimap (green dots)
            for dealer in self.drug_dealers:
                dx = map_x + map_size//2 + int((dealer.x - center_x) * scale)
                dy = map_y + map_size//2 + int((dealer.y - center_y) * scale)
                if map_x < dx < map_x + map_size and map_y < dy < map_y + map_size:
                    pygame.draw.circle(screen, C['green'], (dx, dy), 2)
            
            # Draw cops on minimap (blue dots)
            for cop in self.cops:
                cx = map_x + map_size//2 + int((cop.x - center_x) * scale)
                cy = map_y + map_size//2 + int((cop.y - center_y) * scale)
                if map_x < cx < map_x + map_size and map_y < cy < map_y + map_size:
                    pygame.draw.circle(screen, C['cop'], (cx, cy), 2)
            
            # Player always at center (gold)
            pygame.draw.circle(screen, C['gold'], (map_x + map_size//2, map_y + map_size//2), 3)
        
        # Stats display (bottom left)
        if not p.inside:
            stats_txt = F['tiny'].render(f"Kills: {p.kills} | Earned: ${p.total_earned} | Missions: {self.completed_missions}", True, (100, 100, 100))
            screen.blit(stats_txt, (10, SCREEN_H - 55))
        
        # Active mission display (top right)
        if self.active_mission and not p.inside:
            m = self.active_mission
            mission_bg = pygame.Rect(SCREEN_W - 300, 65, 290, 55)
            pygame.draw.rect(screen, (0, 0, 0, 200), mission_bg)
            pygame.draw.rect(screen, C['neon'], mission_bg, 2)
            
            mission_txt = F['small'].render(f"MISSION: {m.description}", True, C['neon'])
            screen.blit(mission_txt, (SCREEN_W - 295, 70))
            
            progress_txt = F['small'].render(f"Progress: {m.get_progress_text()} | ${m.reward}", True, C['gold'])
            screen.blit(progress_txt, (SCREEN_W - 295, 92))
        elif not self.active_mission and not p.inside and self.mission_cooldown <= 0:
            # Show hint to press TAB for missions
            hint_txt = F['tiny'].render("Press TAB for missions", True, (100, 100, 100))
            screen.blit(hint_txt, (SCREEN_W - hint_txt.get_width() - 10, 70))
        
        # Notification
        if self.notification:
            notif = F['main'].render(self.notification, True, C['gold'])
            notif_bg = pygame.Rect(SCREEN_W//2 - notif.get_width()//2 - 10, 70, notif.get_width() + 20, 40)
            pygame.draw.rect(screen, (0, 0, 0), notif_bg)
            pygame.draw.rect(screen, C['gold'], notif_bg, 2)
            screen.blit(notif, (SCREEN_W//2 - notif.get_width()//2, 75))
        
        # Dead
        if not p.alive:
            dead = F['big'].render("WASTED", True, C['red'])
            screen.blit(dead, (SCREEN_W//2 - dead.get_width()//2, SCREEN_H//2 - 50))
            resp = F['main'].render("Respawning...", True, C['white'])
            screen.blit(resp, (SCREEN_W//2 - resp.get_width()//2, SCREEN_H//2 + 30))
    
    def draw_crosshair(self):
        p = self.player
        has_weapon = p.has_gun or p.has_shotgun or p.has_uzi
        
        if not p.alive or p.inside:
            return
        
        # Check for auto-aim target
        nearest_cop, cop_dist = self.get_nearest_cop(400)
        
        if has_weapon and p.ammo > 0:
            if nearest_cop:
                # Draw lock-on indicator on the cop
                cx = nearest_cop.center[0] - self.camera[0]
                cy = nearest_cop.center[1] - self.camera[1]
                
                # Pulsing lock-on brackets
                pulse = math.sin(pygame.time.get_ticks() * 0.01) * 3
                size = 25 + pulse
                
                # Corner brackets
                pygame.draw.line(screen, C['red'], (cx - size, cy - size), (cx - size + 10, cy - size), 3)
                pygame.draw.line(screen, C['red'], (cx - size, cy - size), (cx - size, cy - size + 10), 3)
                pygame.draw.line(screen, C['red'], (cx + size, cy - size), (cx + size - 10, cy - size), 3)
                pygame.draw.line(screen, C['red'], (cx + size, cy - size), (cx + size, cy - size + 10), 3)
                pygame.draw.line(screen, C['red'], (cx - size, cy + size), (cx - size + 10, cy + size), 3)
                pygame.draw.line(screen, C['red'], (cx - size, cy + size), (cx - size, cy + size - 10), 3)
                pygame.draw.line(screen, C['red'], (cx + size, cy + size), (cx + size - 10, cy + size), 3)
                pygame.draw.line(screen, C['red'], (cx + size, cy + size), (cx + size, cy + size - 10), 3)
                
                # Distance indicator
                dist_txt = F['tiny'].render(f"{int(cop_dist)}m", True, C['red'])
                screen.blit(dist_txt, (cx - dist_txt.get_width()//2, cy + size + 5))
            else:
                # Normal crosshair when no target
                mx, my = pygame.mouse.get_pos()
                pygame.draw.circle(screen, C['white'], (mx, my), 16, 2)
                pygame.draw.circle(screen, C['red'], (mx, my), 4)
        elif has_weapon and p.ammo <= 0:
            # Empty crosshair
            mx, my = pygame.mouse.get_pos()
            pygame.draw.circle(screen, (100, 100, 100), (mx, my), 16, 1)
            pygame.draw.line(screen, (100, 100, 100), (mx - 12, my), (mx + 12, my), 1)
            pygame.draw.line(screen, (100, 100, 100), (mx, my - 12), (mx, my + 12), 1)
    
    def check_near_building(self):
        p = self.player
        if p.inside:
            return None
        
        px, py = p.center
        
        for rect, center in self.crack_dens:
            if math.hypot(px - center[0], py - center[1]) < 80:
                return "CRACK DEN"
        for rect, center in self.strip_clubs:
            if math.hypot(px - center[0], py - center[1]) < 80:
                return "STRIP CLUB"
        for rect, center in self.gunstores:
            if math.hypot(px - center[0], py - center[1]) < 80:
                return "GUN STORE"
        for rect, center in self.upgrade_shops:
            if math.hypot(px - center[0], py - center[1]) < 80:
                return "UPGRADE SHOP"
        for dealer in self.drug_dealers:
            if math.hypot(px - dealer.center[0], py - dealer.center[1]) < 80:
                return "DEALER"
        return None
    
    def get_nearby_dealer(self):
        """Get the dealer closest to player if within range"""
        p = self.player
        px, py = p.center
        for dealer in self.drug_dealers:
            if math.hypot(px - dealer.center[0], py - dealer.center[1]) < 80:
                return dealer
        return None
    
    def get_nearest_cop(self, max_range=400):
        """Get the nearest cop within range for auto-aim"""
        p = self.player
        px, py = p.center
        nearest = None
        nearest_dist = max_range
        
        for cop in self.cops:
            dist = math.hypot(cop.center[0] - px, cop.center[1] - py)
            if dist < nearest_dist:
                nearest = cop
                nearest_dist = dist
        
        return nearest, nearest_dist if nearest else (None, 0)
    
    def draw_pause_screen(self):
        """Draw pause menu or win screen"""
        p = self.player
        
        # Darken background
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        if self.game_won:
            # Win screen
            title = F['big'].render("YOU WIN!", True, C['gold'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 100))
            
            subtitle = F['main'].render(f"You earned ${self.win_goal}!", True, C['neon'])
            screen.blit(subtitle, (SCREEN_W//2 - subtitle.get_width()//2, 180))
        else:
            # Pause screen
            title = F['big'].render("PAUSED", True, C['white'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 100))
        
        # Stats
        play_time = self.game_time // 60  # seconds
        minutes, seconds = divmod(play_time, 60)
        
        stats = [
            f"Time Played: {minutes}:{seconds:02d}",
            f"Total Kills: {p.kills}",
            f"Total Earned: ${p.total_earned}",
            f"Drugs Sold: {p.total_drugs_sold}",
            f"Current Cash: ${p.cash}",
            f"Hoes: {len(self.hoes)}",
        ]
        
        y = 250
        for stat in stats:
            txt = F['main'].render(stat, True, C['white'])
            screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, y))
            y += 40
        
        # Instructions
        hint = F['small'].render("Press ESC to resume | Press Q to quit", True, (150, 150, 150))
        screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 80))
        
        # Goal progress
        progress = min(1.0, p.total_earned / self.win_goal)
        bar_w = 400
        pygame.draw.rect(screen, (40, 40, 50), (SCREEN_W//2 - bar_w//2, 500, bar_w, 30))
        pygame.draw.rect(screen, C['gold'], (SCREEN_W//2 - bar_w//2, 500, int(bar_w * progress), 30))
        pygame.draw.rect(screen, C['white'], (SCREEN_W//2 - bar_w//2, 500, bar_w, 30), 2)
        goal_txt = F['small'].render(f"Goal: ${p.total_earned} / ${self.win_goal}", True, C['white'])
        screen.blit(goal_txt, (SCREEN_W//2 - goal_txt.get_width()//2, 540))
    
    def draw_mission_select(self):
        """Draw mission selection screen"""
        p = self.player
        
        # Darken background
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        title = F['big'].render("MISSIONS", True, C['neon'])
        screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 60))
        
        if self.active_mission:
            # Show active mission with abandon option
            active_txt = F['main'].render("ACTIVE MISSION:", True, C['gold'])
            screen.blit(active_txt, (SCREEN_W//2 - active_txt.get_width()//2, 150))
            
            m = self.active_mission
            desc_txt = F['main'].render(m.description, True, C['white'])
            screen.blit(desc_txt, (SCREEN_W//2 - desc_txt.get_width()//2, 200))
            
            progress_txt = F['main'].render(f"Progress: {m.get_progress_text()}", True, C['neon'])
            screen.blit(progress_txt, (SCREEN_W//2 - progress_txt.get_width()//2, 240))
            
            reward_txt = F['main'].render(f"Reward: ${m.reward}", True, C['gold'])
            screen.blit(reward_txt, (SCREEN_W//2 - reward_txt.get_width()//2, 280))
            
            hint = F['small'].render("Press X to abandon mission | TAB to close", True, (150, 150, 150))
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 80))
        else:
            # Show available missions
            subtitle = F['main'].render(f"Difficulty: {1 + self.completed_missions // 3}", True, C['white'])
            screen.blit(subtitle, (SCREEN_W//2 - subtitle.get_width()//2, 130))
            
            if not hasattr(self, 'mission_selection'):
                self.mission_selection = 0
            
            y = 200
            for i, mission in enumerate(self.available_missions):
                selected = (i == self.mission_selection)
                prefix = "► " if selected else "  "
                col = C['neon'] if selected else C['white']
                
                txt = F['main'].render(f"{prefix}{mission.description}", True, col)
                screen.blit(txt, (SCREEN_W//2 - 200, y))
                
                reward_txt = F['small'].render(f"${mission.reward}", True, C['gold'])
                screen.blit(reward_txt, (SCREEN_W//2 + 150, y + 5))
                
                y += 45
            
            hint = F['small'].render("W/S = Select | SPACE = Accept | TAB = Close", True, (150, 150, 150))
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 80))
    
    def run(self):
        running = True
        
        while running:
            dt = clock.tick(FPS) / 1000.0
            
            # Events
            shoot = False
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                if e.type == pygame.KEYDOWN:
                    # Handle pause/quit
                    if e.key == pygame.K_ESCAPE:
                        if self.mission_menu:
                            self.mission_menu = False
                        elif self.paused:
                            self.paused = False
                        elif self.player.inside:
                            self.exit_building()
                        else:
                            self.paused = True
                    if e.key == pygame.K_q and self.paused:
                        running = False
                    
                    # Mission menu toggle
                    if e.key == pygame.K_TAB and not self.player.inside and not self.paused:
                        self.mission_menu = not self.mission_menu
                        if self.mission_menu:
                            self.mission_selection = 0
                    
                    # Mission menu navigation
                    if self.mission_menu:
                        if e.key == pygame.K_w or e.key == pygame.K_UP:
                            if len(self.available_missions) > 0:
                                self.mission_selection = (self.mission_selection - 1) % len(self.available_missions)
                        if e.key == pygame.K_s or e.key == pygame.K_DOWN:
                            if len(self.available_missions) > 0:
                                self.mission_selection = (self.mission_selection + 1) % len(self.available_missions)
                        if e.key == pygame.K_SPACE and not self.active_mission:
                            # Accept selected mission
                            if len(self.available_missions) > 0:
                                self.start_mission(self.available_missions[self.mission_selection])
                                self.mission_menu = False
                        if e.key == pygame.K_x and self.active_mission:
                            # Abandon mission
                            self.abandon_mission()
                        continue
                    
                    # Skip other inputs if paused
                    if self.paused:
                        continue
                    
                    if e.key == pygame.K_e:
                        self.enter_building()
                    if e.key == pygame.K_SPACE:
                        if self.player.inside:
                            self.interact()
                        else:
                            self.melee()
                    if e.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    # Menu navigation when inside buildings
                    if self.player.inside:
                        p = self.player
                        if e.key == pygame.K_w or e.key == pygame.K_UP:
                            if p.building_type == 'gun':
                                p.gun_selection = (p.gun_selection - 1) % 4
                            elif p.building_type == 'dealer':
                                p.dealer_selection = (p.dealer_selection - 1) % 2
                            elif p.building_type == 'upgrade':
                                p.upgrade_selection = (p.upgrade_selection - 1) % 4
                        if e.key == pygame.K_s or e.key == pygame.K_DOWN:
                            if p.building_type == 'gun':
                                p.gun_selection = (p.gun_selection + 1) % 4
                            elif p.building_type == 'dealer':
                                p.dealer_selection = (p.dealer_selection + 1) % 2
                            elif p.building_type == 'upgrade':
                                p.upgrade_selection = (p.upgrade_selection + 1) % 4
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if not self.paused:
                        shoot = True
            
            # Held keys
            keys = pygame.key.get_pressed()
            p = self.player  # Need p defined for pause screen
            if pygame.mouse.get_pressed()[0] and not self.paused:
                shoot = True
            
            # Skip game logic if paused
            if self.paused:
                # Draw game state behind pause menu
                screen.fill(C['bg'])
                if p.inside:
                    self.draw_interior()
                else:
                    self.draw_world()
                self.draw_hud()
                self.draw_pause_screen()
                pygame.display.flip()
                continue
            
            # Skip game logic if mission menu open
            if self.mission_menu:
                screen.fill(C['bg'])
                self.draw_world()
                self.draw_hud()
                self.draw_mission_select()
                pygame.display.flip()
                continue
            
            # Movement
            if p.alive and not p.inside:
                dx = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
                dy = (keys[pygame.K_s] or keys[pygame.K_DOWN]) - (keys[pygame.K_w] or keys[pygame.K_UP])
                
                if dx and dy:
                    dx *= 0.707
                    dy *= 0.707
                
                actual_speed = p.speed + p.speed_bonus
                nx = p.x + dx * actual_speed
                ny = p.y + dy * actual_speed
                
                if not self.collides(nx, p.y, p.w, p.h):
                    p.x = nx
                if not self.collides(p.x, ny, p.w, p.h):
                    p.y = ny
                
                p.x = max(0, min(MAP_W*TILE - p.w, p.x))
                p.y = max(0, min(MAP_H*TILE - p.h, p.y))
            
            # Shooting with auto-aim
            if shoot and p.alive and not p.inside:
                # Check for nearest cop to auto-aim
                nearest_cop, cop_dist = self.get_nearest_cop(400)
                
                if nearest_cop:
                    # Auto-aim at nearest cop
                    angle = math.atan2(
                        nearest_cop.center[1] - p.center[1],
                        nearest_cop.center[0] - p.center[0]
                    )
                else:
                    # Manual aim with mouse
                    mx, my = pygame.mouse.get_pos()
                    angle = math.atan2(my - SCREEN_H//2, mx - SCREEN_W//2)
                
                self.shoot(angle)
            
            # Update camera
            self.camera[0] += (p.x - SCREEN_W//2 + p.w//2 - self.camera[0]) * 0.1
            self.camera[1] += (p.y - SCREEN_H//2 + p.h//2 - self.camera[1]) * 0.1
            
            # Apply screen shake
            if p.screen_shake > 0:
                self.camera[0] += random.randint(-5, 5)
                self.camera[1] += random.randint(-5, 5)
            
            # Update game
            self.update(dt)
            
            # Draw
            screen.fill(C['bg'])
            
            if p.inside:
                self.draw_interior()
            else:
                self.draw_world()
                
                # Near building prompt
                near = self.check_near_building()
                if near:
                    prompt = F['main'].render(f"Press E to enter {near}", True, C['gold'])
                    bg_rect = pygame.Rect(SCREEN_W//2 - prompt.get_width()//2 - 10, SCREEN_H - 80, 
                                         prompt.get_width() + 20, 40)
                    pygame.draw.rect(screen, (0, 0, 0), bg_rect)
                    pygame.draw.rect(screen, C['gold'], bg_rect, 2)
                    screen.blit(prompt, (SCREEN_W//2 - prompt.get_width()//2, SCREEN_H - 75))
            
            self.draw_hud()
            self.draw_crosshair()
            
            # Damage flash overlay
            if p.damage_flash > 0:
                flash = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                alpha = int(100 * p.damage_flash / 10)
                flash.fill((255, 0, 0, alpha))
                screen.blit(flash, (0, 0))
            
            # Controls hint
            if not p.inside:
                hint = F['tiny'].render("WASD=Move | Click=Shoot | Space=Melee | E=Enter", True, (80, 80, 80))
                screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 25))
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
