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
    'table': (100, 60, 20), 'civilian': (200, 180, 160),
    # New colors for expanded features
    'gang_red': (180, 30, 30), 'gang_blue': (30, 60, 180), 'gang_green': (30, 150, 30),
    'car_red': (200, 50, 50), 'car_blue': (50, 100, 200), 'car_black': (40, 40, 45),
    'night': (10, 10, 30), 'dawn': (80, 60, 100), 'day': (30, 30, 50),
    'orange': (255, 150, 50), 'dark_purple': (60, 0, 100),
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
        self.x, self.y = 200, 200  # Spawn in open area
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
        self.has_rifle = False
        self.has_rpg = False
        self.current_weapon = 'pistol'  # Current selected weapon
        self.ammo = 50
        self.rockets = 0
        self.hoes = 2
        self.alive = True
        self.respawn_timer = 0
        self.shoot_cooldown = 0
        # Vehicle state
        self.in_vehicle = False
        self.current_vehicle = None
        # Gang reputation (-100 to 100 for each gang)
        self.gang_rep = {'red': 0, 'blue': 0, 'green': 0}
        # Drug inventory
        self.drugs = {'crack': 0, 'weed': 0, 'meth': 0}
        self.total_drugs_sold = 0
        # Stats/upgrades
        self.damage_mult = 1.0
        self.speed_bonus = 0
        self.armor = 0  # Damage reduction %
        # Lifetime stats
        self.kills = 0
        self.gang_kills = 0
        self.total_earned = 0
        self.missions_complete = 0
        self.vehicles_stolen = 0
        self.vehicles_destroyed = 0
        # Building state
        self.inside = False
        self.building_type = None
        self.entry_pos = (200, 200)
        # Cooking minigame
        self.cooking = False
        self.cook_stage = 0
        self.cook_bar = 0.0
        self.cook_target = 0.5
        self.cook_zone = 0.15
        self.cook_speed = 0.012
        # Strip club - RIZZ BATTLE rhythm game
        self.rizz_sequence = []  # Arrow keys to hit
        self.rizz_index = 0  # Current position in sequence
        self.rizz_combo = 0  # Combo counter
        self.rizz_score = 0  # Total score this session
        self.rizz_timer = 0  # Time to hit current key
        self.rizz_message = ""  # Feedback message
        self.rizz_message_timer = 0
        self.rizz_target = 500  # Score needed to recruit
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
        self.damage_bonus = 0  # Extra damage from weapons like rifle


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


class Vehicle:
    TYPES = {
        'car': {'w': 80, 'h': 45, 'speed': 14, 'health': 150, 'color': 'car_red'},
        'sports': {'w': 85, 'h': 40, 'speed': 20, 'health': 100, 'color': 'car_blue'},
        'truck': {'w': 100, 'h': 55, 'speed': 10, 'health': 250, 'color': 'car_black'},
    }
    
    def __init__(self, x, y, vtype='car'):
        self.x, self.y = x, y
        self.vtype = vtype
        stats = self.TYPES[vtype]
        self.w, self.h = stats['w'], stats['h']
        self.max_speed = stats['speed']
        self.health = stats['health']
        self.max_health = stats['health']
        self.color_key = stats['color']
        self.angle = random.random() * 6.28
        self.velocity = 0
        self.occupied = False
        self.driver = None
    
    @property
    def rect(self):
        return pygame.Rect(self.x - self.w//2, self.y - self.h//2, self.w, self.h)
    
    @property
    def center(self):
        return (self.x, self.y)


class GangMember:
    def __init__(self, x, y, gang='red'):
        self.x, self.y = x, y
        self.w, self.h = 38, 58
        self.health = 60
        self.max_health = 60
        self.gang = gang  # 'red', 'blue', 'green'
        self.shoot_timer = 0
        self.target = None
        self.alert = False
        self.patrol_angle = random.random() * 6.28
    
    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)
    
    @property
    def center(self):
        return (self.x + self.w//2, self.y + self.h//2)
    
    @property
    def color(self):
        colors = {'red': C['gang_red'], 'blue': C['gang_blue'], 'green': C['gang_green']}
        return colors.get(self.gang, C['gang_red'])


class Particle:
    """For visual effects like explosions, sparks, smoke"""
    def __init__(self, x, y, ptype='spark'):
        self.x, self.y = x, y
        self.ptype = ptype
        self.life = 30
        
        if ptype == 'spark':
            self.vx = random.uniform(-5, 5)
            self.vy = random.uniform(-5, 5)
            self.color = C['yellow']
            self.size = random.randint(2, 4)
        elif ptype == 'smoke':
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-3, -1)
            self.color = (100, 100, 100)
            self.size = random.randint(5, 12)
            self.life = 45
        elif ptype == 'explosion':
            angle = random.random() * 6.28
            speed = random.uniform(3, 10)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.color = random.choice([C['yellow'], C['orange'], C['red']])
            self.size = random.randint(4, 10)
            self.life = 25
        elif ptype == 'shell':
            self.vx = random.uniform(-2, 2)
            self.vy = random.uniform(-4, -1)
            self.color = C['gold']
            self.size = 3
            self.life = 40
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.ptype == 'smoke':
            self.vy -= 0.05  # Rise up
            self.size += 0.3
        elif self.ptype in ['spark', 'explosion']:
            self.vy += 0.3  # Gravity
        elif self.ptype == 'shell':
            self.vy += 0.2
        self.life -= 1


class Mission:
    TYPES = ['kill_cops', 'earn_money', 'sell_drugs', 'survive', 'recruit_hoes', 
             'kill_gangs', 'steal_vehicles', 'destroy_vehicles', 'rampage']
    
    def __init__(self, mission_type=None, difficulty=1):
        self.type = mission_type or random.choice(self.TYPES)
        self.difficulty = difficulty
        self.active = False
        self.complete = False
        self.failed = False
        self.progress = 0
        self.start_value = 0  # Track starting point for incremental missions
        self.timer = 0  # For survive/rampage missions
        self.time_limit = 0  # For timed missions
        
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
        elif self.type == 'recruit_hoes':
            self.target = 2 + difficulty
            self.description = f"Recruit {self.target} hoes"
            self.reward = 250 + difficulty * 200
        elif self.type == 'kill_gangs':
            self.target = 4 + difficulty * 2
            self.description = f"Kill {self.target} gang members"
            self.reward = 300 + difficulty * 200
        elif self.type == 'steal_vehicles':
            self.target = 2 + difficulty
            self.description = f"Steal {self.target} vehicles"
            self.reward = 250 + difficulty * 150
        elif self.type == 'destroy_vehicles':
            self.target = 1 + difficulty
            self.description = f"Destroy {self.target} vehicles"
            self.reward = 400 + difficulty * 250
        elif self.type == 'rampage':
            self.target = 30 + difficulty * 15  # seconds
            self.time_limit = self.target * 60  # frames
            self.kill_target = 5 + difficulty * 3
            self.description = f"Kill {self.kill_target} in {self.target}s"
            self.reward = 500 + difficulty * 300
    
    def start(self, player, game):
        """Start tracking this mission"""
        self.active = True
        self.progress = 0
        self.start_value = 0  # Initialize for all types
        self.timer = 0
        
        if self.type == 'earn_money':
            self.start_value = player.total_earned
        elif self.type == 'sell_drugs':
            self.start_value = player.total_drugs_sold
        elif self.type == 'kill_cops':
            self.start_value = player.kills
        elif self.type == 'recruit_hoes':
            self.start_value = len(game.hoes)
        elif self.type == 'survive':
            self.timer = 0
        elif self.type == 'kill_gangs':
            self.start_value = player.gang_kills
        elif self.type == 'steal_vehicles':
            self.start_value = player.vehicles_stolen
        elif self.type == 'destroy_vehicles':
            self.start_value = getattr(player, 'vehicles_destroyed', 0)
        elif self.type == 'rampage':
            self.start_value = player.kills + player.gang_kills
            self.timer = self.time_limit
    
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
        elif self.type == 'kill_gangs':
            self.progress = player.gang_kills - self.start_value
        elif self.type == 'steal_vehicles':
            self.progress = player.vehicles_stolen - self.start_value
        elif self.type == 'destroy_vehicles':
            self.progress = getattr(player, 'vehicles_destroyed', 0) - self.start_value
        elif self.type == 'rampage':
            self.timer -= 1
            total_kills = player.kills + player.gang_kills
            self.progress = total_kills - self.start_value
            if self.timer <= 0 and self.progress < self.kill_target:
                self.failed = True
                self.active = False
            if self.progress >= self.kill_target:
                self.target = self.kill_target  # For completion check
        
        # Check completion
        if self.progress >= self.target:
            self.complete = True
    
    def get_progress_text(self):
        """Get progress display string"""
        if self.type == 'survive':
            return f"{self.progress}s / {self.target}s"
        elif self.type == 'rampage':
            time_left = max(0, self.timer // 60)
            return f"{self.progress}/{self.kill_target} kills ({time_left}s left)"
        return f"{self.progress} / {self.target}"


class Game:
    def __init__(self):
        self.player = Player()
        self.cops = []
        self.civilians = []
        self.hoes = []
        self.bullets = []
        self.rockets = []  # RPG rockets
        self.blood = []
        self.buildings = []
        self.crack_dens = []
        self.strip_clubs = []
        self.gunstores = []
        self.upgrade_shops = []
        self.safe_houses = []  # Save points
        self.health_pickups = []
        self.drug_dealers = []
        # New systems
        self.vehicles = []
        self.police_cars = []  # Cop vehicles that chase
        self.gang_members = []
        self.particles = []
        self.gang_territories = {'red': [], 'blue': [], 'green': []}
        # Radio system
        self.radio_stations = [
            {'name': 'OHIO FM', 'genre': 'Brainrot'},
            {'name': 'SIGMA RADIO', 'genre': 'Grindset'},
            {'name': 'SKIBIDI 101', 'genre': 'Toilet Core'},
            {'name': 'NPC BEATS', 'genre': 'Lo-Fi'},
            {'name': 'FANUM TAX', 'genre': 'Drill'},
            {'name': 'GOATED.FM', 'genre': 'W Music'},
            {'name': 'OFF', 'genre': 'touch grass'},
        ]
        self.current_station = 6  # Off by default
        # Camera and UI
        self.camera = [0, 0]
        self.notification = None
        self.notification_timer = 0
        self.game_time = 0  # Total play time in frames
        # Day/night cycle (1 full cycle = 7200 frames = 2 minutes)
        self.time_of_day = 0  # 0-7200
        self.day_length = 7200
        # Game state
        self.game_state = 'title'  # 'title', 'playing', 'gameover', 'victory'
        self.title_selection = 0
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
        # Save system
        self.has_save = False
        self.generate_world()
        self.spawn_npcs()
        self.spawn_vehicles()
        self.spawn_gangs()
        self.spawn_police_cars()
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
                    t = random.randint(1, 6)
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
                    elif t == 6:
                        self.safe_houses.append((rect, center))
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
    
    def spawn_vehicles(self):
        """Spawn vehicles around the map"""
        vehicle_types = ['car', 'car', 'car', 'sports', 'truck']
        for _ in range(15):
            for _ in range(50):
                x = random.randint(200, MAP_W*TILE - 200)
                y = random.randint(200, MAP_H*TILE - 200)
                if not self.collides(x - 50, y - 30, 100, 60):
                    vtype = random.choice(vehicle_types)
                    self.vehicles.append(Vehicle(x, y, vtype))
                    break
    
    def spawn_gangs(self):
        """Spawn gang members in territories"""
        # Define gang territories (rough areas of map)
        territories = {
            'red': (0, 0, MAP_W*TILE//3, MAP_H*TILE//2),
            'blue': (MAP_W*TILE*2//3, 0, MAP_W*TILE, MAP_H*TILE//2),
            'green': (MAP_W*TILE//3, MAP_H*TILE//2, MAP_W*TILE*2//3, MAP_H*TILE),
        }
        
        for gang, (x1, y1, x2, y2) in territories.items():
            # Spawn 6-10 members per gang
            for _ in range(random.randint(6, 10)):
                for _ in range(50):
                    x = random.randint(x1 + 100, x2 - 100)
                    y = random.randint(y1 + 100, y2 - 100)
                    if not self.collides(x, y, 38, 58):
                        self.gang_members.append(GangMember(x, y, gang))
                        break
    
    def spawn_police_cars(self):
        """Spawn police vehicles"""
        for _ in range(4):
            for _ in range(50):
                x = random.randint(300, MAP_W*TILE - 300)
                y = random.randint(300, MAP_H*TILE - 300)
                if not self.collides(x - 50, y - 30, 100, 60):
                    self.police_cars.append({
                        'x': x, 'y': y,
                        'angle': random.random() * 6.28,
                        'velocity': 0,
                        'chasing': False,
                        'health': 200,
                        'max_health': 200,
                    })
                    break
    
    def spawn_particles(self, x, y, ptype, count=10):
        """Spawn particle effects"""
        for _ in range(count):
            self.particles.append(Particle(x, y, ptype))
    
    def create_explosion(self, x, y):
        """Create an explosion that damages nearby entities"""
        p = self.player
        explosion_radius = 150
        explosion_damage = 100
        
        # Visual effects
        self.spawn_particles(x, y, 'explosion', 30)
        self.spawn_particles(x, y, 'smoke', 15)
        
        # Screen shake
        p.screen_shake = 20
        
        # Damage cops
        for cop in self.cops[:]:
            dist = math.hypot(cop.center[0] - x, cop.center[1] - y)
            if dist < explosion_radius:
                damage = int(explosion_damage * (1 - dist / explosion_radius))
                cop.health -= damage
                self.spawn_blood(cop.center[0], cop.center[1], 15)
                if cop.health <= 0:
                    self.cops.remove(cop)
                    self.spawn_blood(cop.center[0], cop.center[1], 40)
                    p.kills += 1
                    p.cash += random.randint(30, 60)
                    p.total_earned += random.randint(30, 60)
                    p.wanted = min(5, p.wanted + 1)
        
        # Damage gang members
        for gang in self.gang_members[:]:
            dist = math.hypot(gang.center[0] - x, gang.center[1] - y)
            if dist < explosion_radius:
                damage = int(explosion_damage * (1 - dist / explosion_radius))
                gang.health -= damage
                self.spawn_blood(gang.center[0], gang.center[1], 15)
                if gang.health <= 0:
                    self.gang_members.remove(gang)
                    self.spawn_blood(gang.center[0], gang.center[1], 35)
                    p.gang_kills += 1
                    p.cash += random.randint(40, 80)
                    p.total_earned += random.randint(40, 80)
        
        # Damage civilians
        for civ in self.civilians[:]:
            dist = math.hypot(civ.center[0] - x, civ.center[1] - y)
            if dist < explosion_radius:
                self.civilians.remove(civ)
                self.spawn_blood(civ.center[0], civ.center[1], 20)
                p.wanted = min(5, p.wanted + 0.3)
        
        # Damage vehicles
        for vehicle in self.vehicles[:]:
            dist = math.hypot(vehicle.x - x, vehicle.y - y)
            if dist < explosion_radius:
                damage = int(explosion_damage * (1 - dist / explosion_radius))
                vehicle.health -= damage
                if vehicle.health <= 0:
                    self.vehicles.remove(vehicle)
                    self.spawn_particles(vehicle.x, vehicle.y, 'explosion', 20)
                    p.vehicles_destroyed += 1
        
        # Damage player if close
        player_dist = math.hypot(p.center[0] - x, p.center[1] - y)
        if player_dist < explosion_radius:
            damage = int(explosion_damage * (1 - player_dist / explosion_radius) * (1 - p.armor / 100))
            p.health -= damage
            p.damage_flash = 15
            if p.health <= 0:
                p.alive = False
                p.respawn_timer = 180
                self.spawn_blood(p.center[0], p.center[1], 50)
    
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
            self.available_missions.append(Mission('kill_gangs', difficulty))
        if difficulty >= 3:
            self.available_missions.append(Mission('recruit_hoes', difficulty))
            self.available_missions.append(Mission('steal_vehicles', difficulty))
        if difficulty >= 4:
            self.available_missions.append(Mission('destroy_vehicles', difficulty))
            self.available_missions.append(Mission('rampage', difficulty))
    
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
            elif self.active_mission.failed:
                self.show_notification("Mission Failed!", 120)
                self.active_mission = None
                self.mission_cooldown = 180
                self.generate_missions()
    
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
    
    def show_notification(self, text, duration=120):
        """Show a notification at the top of the screen"""
        self.notification = text
        self.notification_timer = duration
    
    def shoot(self, angle):
        p = self.player
        if p.shoot_cooldown > 0 or p.inside:
            return
        
        weapon = p.current_weapon
        
        # Check for RPG (uses rockets, not ammo)
        if weapon == 'rpg' and p.has_rpg and p.rockets > 0:
            p.rockets -= 1
            p.shoot_cooldown = 60
            self.rockets.append({
                'x': p.x + p.w//2,
                'y': p.y + p.h//2,
                'angle': angle,
                'vx': math.cos(angle) * 12,
                'vy': math.sin(angle) * 12,
                'life': 120
            })
            self.spawn_particles(p.x + p.w//2, p.y + p.h//2, 'smoke', 5)
            p.wanted = min(5, p.wanted + 0.5)
            return
        
        # Regular weapons need ammo
        if p.ammo <= 0:
            return
        
        # Check if player has the selected weapon
        weapon_check = {
            'pistol': p.has_gun,
            'shotgun': p.has_shotgun,
            'uzi': p.has_uzi,
            'rifle': p.has_rifle,
        }
        
        if weapon not in weapon_check or not weapon_check.get(weapon, False):
            return
        
        spread = 0.1
        shots = 1
        damage_bonus = 0
        
        if weapon == 'rifle':
            spread = 0.02
            p.shoot_cooldown = 20
            damage_bonus = 25
        elif weapon == 'shotgun':
            spread = 0.25
            shots = 5
            p.shoot_cooldown = 30
        elif weapon == 'uzi':
            spread = 0.15
            p.shoot_cooldown = 5
        else:  # pistol
            p.shoot_cooldown = 12
        
        for _ in range(shots):
            a = angle + random.uniform(-spread, spread)
            b = Bullet(p.x + p.w//2, p.y + p.h//2, a, 'player')
            b.damage_bonus = damage_bonus
            self.bullets.append(b)
        
        self.spawn_particles(p.x + p.w//2, p.y + p.h//2, 'shell', 1)
        
        p.ammo -= 1
        p.ammo = max(0, p.ammo)
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
    
    def enter_vehicle(self):
        """Try to enter a nearby vehicle"""
        p = self.player
        if p.inside or p.in_vehicle:
            return False
        
        px, py = p.center
        for vehicle in self.vehicles:
            dist = math.hypot(px - vehicle.x, py - vehicle.y)
            if dist < 80 and not vehicle.occupied:
                p.in_vehicle = True
                p.current_vehicle = vehicle
                vehicle.occupied = True
                vehicle.driver = p
                p.vehicles_stolen += 1
                p.wanted = min(5, p.wanted + 0.5)
                self.show_notification(f"Entered {vehicle.vtype.upper()}", 60)
                return True
        return False
    
    def exit_vehicle(self):
        """Exit current vehicle"""
        p = self.player
        if not p.in_vehicle or not p.current_vehicle:
            return
        
        vehicle = p.current_vehicle
        # Place player next to vehicle
        p.x = vehicle.x + vehicle.w//2 + 20
        p.y = vehicle.y
        p.in_vehicle = False
        vehicle.occupied = False
        vehicle.driver = None
        p.current_vehicle = None
    
    def get_nearby_vehicle(self):
        """Get nearest vehicle within range"""
        p = self.player
        px, py = p.center
        for vehicle in self.vehicles:
            if math.hypot(px - vehicle.x, py - vehicle.y) < 80:
                return vehicle
        return None
    
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
                # Init RIZZ BATTLE
                p.rizz_sequence = [random.choice(['W', 'A', 'S', 'D']) for _ in range(8)]
                p.rizz_index = 0
                p.rizz_combo = 0
                p.rizz_score = 0
                p.rizz_timer = 120  # 2 seconds per key
                p.rizz_message = "SHOW YOUR RIZZ!"
                p.rizz_message_timer = 60
                p.rizz_target = 400 + len(self.hoes) * 100  # Harder with more hoes
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
        
        for rect, center in self.safe_houses:
            if math.hypot(px - center[0], py - center[1]) < 80:
                p.inside = True
                p.building_type = 'safe'
                p.entry_pos = (p.x, p.y)
                p.safe_selection = 0
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
            # RIZZ BATTLE - This is handled in the main loop now
            pass
        
        elif p.building_type == 'gun':
            # Gun store - buy selected item
            if not hasattr(p, 'gun_selection'):
                p.gun_selection = 0
            
            items = [
                ('Pistol', 200, 30, 'pistol'),
                ('Shotgun', 500, 20, 'shotgun'),
                ('Uzi', 800, 50, 'uzi'),
                ('Rifle', 1200, 15, 'rifle'),
                ('RPG', 2000, 0, 'rpg'),
                ('Ammo x30', 100, 30, 'ammo'),
                ('Rockets x3', 300, 3, 'rockets'),
            ]
            
            name, price, ammo_bonus, item_type = items[p.gun_selection % len(items)]
            
            # Check if already owned (except ammo/rockets)
            owned = False
            if item_type == 'pistol' and p.has_gun:
                owned = True
            elif item_type == 'shotgun' and p.has_shotgun:
                owned = True
            elif item_type == 'uzi' and p.has_uzi:
                owned = True
            elif item_type == 'rifle' and p.has_rifle:
                owned = True
            elif item_type == 'rpg' and p.has_rpg:
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
                elif item_type == 'rifle':
                    p.has_rifle = True
                    p.ammo += ammo_bonus
                    p.cash -= price
                    self.spawn_message(p.x, p.y, "RIFLE!", C['gold'])
                elif item_type == 'rpg':
                    p.has_rpg = True
                    p.rockets += 3
                    p.cash -= price
                    self.spawn_message(p.x, p.y, "RPG!", C['red'])
                elif item_type == 'ammo':
                    p.ammo += ammo_bonus
                    p.cash -= price
                    self.spawn_message(p.x, p.y, f"+{ammo_bonus} AMMO", C['yellow'])
                elif item_type == 'rockets':
                    p.rockets += ammo_bonus
                    p.cash -= price
                    self.spawn_message(p.x, p.y, f"+{ammo_bonus} ROCKETS", C['orange'])
        
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
        
        elif p.building_type == 'safe':
            # Safe house - save/heal
            if not hasattr(p, 'safe_selection'):
                p.safe_selection = 0
            
            if p.safe_selection == 0:
                # Save game
                self.has_save = True
                self.save_data = {
                    'cash': p.cash,
                    'health': p.health,
                    'max_health': p.max_health,
                    'ammo': p.ammo,
                    'rockets': p.rockets,
                    'has_gun': p.has_gun,
                    'has_shotgun': p.has_shotgun,
                    'has_uzi': p.has_uzi,
                    'has_rifle': p.has_rifle,
                    'has_rpg': p.has_rpg,
                    'armor': p.armor,
                    'damage_mult': p.damage_mult,
                    'speed_bonus': p.speed_bonus,
                    'drugs': p.drugs.copy(),
                    'kills': p.kills,
                    'total_earned': p.total_earned,
                    'completed_missions': self.completed_missions,
                    'x': p.x, 'y': p.y,
                }
                self.show_notification("Game Saved!", 120)
                self.spawn_message(p.x, p.y, "SAVED!", C['green'])
            elif p.safe_selection == 1:
                # Full heal (costs $200)
                if p.cash >= 200 and p.health < p.max_health:
                    p.cash -= 200
                    p.health = p.max_health
                    p.wanted = max(0, p.wanted - 2)  # Reduce wanted level
                    self.show_notification("Fully Healed!", 90)
                    self.spawn_message(p.x, p.y, "HEALED!", C['green'])
    
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
            
            # Cops are lazy - need higher wanted or very close
            if p.wanted >= 2 or (p.wanted >= 1 and dist < 200):
                cop.alert = True
            elif dist > 800:
                cop.alert = False  # Cops give up chase if too far
            
            if cop.alert and dist < 500:
                # Chase player (but they're kinda slow)
                dx = p.x - cop.x
                dy = p.y - cop.y
                d = dist + 0.1
                speed = 2.8 if p.wanted >= 4 else 1.8  # Slower cops
                
                # Cops get tired sometimes
                if random.random() < 0.1:
                    speed *= 0.5  # Donut break
                
                nx = cop.x + dx/d * speed
                ny = cop.y + dy/d * speed
                
                if not self.collides(nx, cop.y, cop.w, cop.h):
                    cop.x = nx
                if not self.collides(cop.x, ny, cop.w, cop.h):
                    cop.y = ny
                
                # Shoot at player (cops have bad aim and shoot less often)
                cop.shoot_timer += 1
                if cop.shoot_timer > 90 and dist < 350:  # Slower shooting, shorter range
                    a = math.atan2(dy, dx) + random.uniform(-0.25, 0.25)  # Terrible aim
                    self.bullets.append(Bullet(cop.x + cop.w//2, cop.y + cop.h//2, a, 'cop'))
                    cop.shoot_timer = random.randint(-30, 0)  # Random delay
            else:
                # Patrol (or eat donuts)
                cop.angle += 0.015
                nx = cop.x + math.cos(cop.angle) * 1.0
                ny = cop.y + math.sin(cop.angle) * 1.0
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
        
        # Update gang members
        for gang in self.gang_members[:]:
            # Find targets (other gang members or player if hostile)
            gang.shoot_timer += 1
            
            # Check if player is hostile to this gang
            player_hostile = p.gang_rep.get(gang.gang, 0) < -30
            
            # Find nearest enemy
            nearest_enemy = None
            nearest_dist = 400
            
            # Check other gang members
            for other in self.gang_members:
                if other.gang != gang.gang:
                    dist = math.hypot(other.x - gang.x, other.y - gang.y)
                    if dist < nearest_dist:
                        nearest_enemy = other
                        nearest_dist = dist
            
            # Check player if hostile
            if player_hostile:
                player_dist = math.hypot(p.x - gang.x, p.y - gang.y)
                if player_dist < nearest_dist:
                    nearest_enemy = p
                    nearest_dist = player_dist
            
            if nearest_enemy and nearest_dist < 350:
                gang.alert = True
                # Move toward enemy
                dx = nearest_enemy.x - gang.x
                dy = nearest_enemy.y - gang.y
                d = nearest_dist + 0.1
                nx = gang.x + dx/d * 2
                ny = gang.y + dy/d * 2
                if not self.collides(nx, ny, gang.w, gang.h):
                    gang.x, gang.y = nx, ny
                
                # Shoot at enemy
                if gang.shoot_timer > 45 and nearest_dist < 300:
                    angle = math.atan2(dy, dx) + random.uniform(-0.15, 0.15)
                    self.bullets.append(Bullet(gang.center[0], gang.center[1], angle, f'gang_{gang.gang}'))
                    gang.shoot_timer = 0
            else:
                gang.alert = False
                # Patrol
                gang.patrol_angle += 0.015
                nx = gang.x + math.cos(gang.patrol_angle) * 1
                ny = gang.y + math.sin(gang.patrol_angle) * 1
                if not self.collides(nx, ny, gang.w, gang.h):
                    gang.x, gang.y = nx, ny
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)
        
        # Update rockets (RPG)
        for rocket in self.rockets[:]:
            rocket['x'] += rocket['vx']
            rocket['y'] += rocket['vy']
            rocket['life'] -= 1
            
            # Spawn smoke trail
            if random.random() < 0.5:
                self.spawn_particles(rocket['x'], rocket['y'], 'smoke', 1)
            
            # Check collision with buildings or expired
            if rocket['life'] <= 0 or self.collides(rocket['x'] - 5, rocket['y'] - 5, 10, 10):
                # Explode!
                self.create_explosion(rocket['x'], rocket['y'])
                self.rockets.remove(rocket)
                continue
            
            # Check collision with cops
            for cop in self.cops[:]:
                if math.hypot(cop.center[0] - rocket['x'], cop.center[1] - rocket['y']) < 40:
                    self.create_explosion(rocket['x'], rocket['y'])
                    self.rockets.remove(rocket)
                    break
            
            # Check collision with vehicles
            for vehicle in self.vehicles[:]:
                if math.hypot(vehicle.x - rocket['x'], vehicle.y - rocket['y']) < 50:
                    self.create_explosion(rocket['x'], rocket['y'])
                    if rocket in self.rockets:
                        self.rockets.remove(rocket)
                    break
        
        # Update police cars
        for pcar in self.police_cars[:]:
            # Chase player if wanted level is high enough
            if p.wanted >= 3 and not p.in_vehicle:
                pcar['chasing'] = True
            elif p.wanted >= 2 and p.in_vehicle:
                pcar['chasing'] = True
            else:
                pcar['chasing'] = False
            
            if pcar['chasing']:
                # Drive toward player
                dx = p.x - pcar['x']
                dy = p.y - pcar['y']
                target_angle = math.atan2(dy, dx)
                
                # Smooth turn toward player
                angle_diff = target_angle - pcar['angle']
                while angle_diff > math.pi: angle_diff -= 2 * math.pi
                while angle_diff < -math.pi: angle_diff += 2 * math.pi
                pcar['angle'] += angle_diff * 0.05
                
                # Accelerate
                pcar['velocity'] = min(pcar['velocity'] + 0.2, 12)
            else:
                # Slow down and patrol
                pcar['velocity'] *= 0.98
                pcar['angle'] += 0.01
            
            # Move police car
            nx = pcar['x'] + math.cos(pcar['angle']) * pcar['velocity']
            ny = pcar['y'] + math.sin(pcar['angle']) * pcar['velocity']
            
            if not self.collides(nx - 45, ny - 25, 90, 50):
                pcar['x'] = nx
                pcar['y'] = ny
            else:
                pcar['velocity'] *= -0.3
            
            # Keep in bounds
            pcar['x'] = max(100, min(MAP_W*TILE - 100, pcar['x']))
            pcar['y'] = max(100, min(MAP_H*TILE - 100, pcar['y']))
        
        # Update day/night cycle
        self.time_of_day = (self.time_of_day + 1) % self.day_length
        
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
                        # Apply damage multiplier and bonus
                        base_damage = 35 + b.damage_bonus
                        actual_damage = int(base_damage * p.damage_mult)
                        cop.health -= actual_damage
                        cop.alert = True
                        self.spawn_blood(b.x, b.y, 12)
                        self.spawn_particles(b.x, b.y, 'spark', 3)
                        if b in self.bullets:
                            self.bullets.remove(b)
                        if cop.health <= 0:
                            self.cops.remove(cop)
                            self.spawn_blood(cop.center[0], cop.center[1], 35)
                            p.wanted = min(5, p.wanted + 1)
                            cash = random.randint(20, 50)
                            p.cash += cash
                            p.kills += 1
                            p.total_earned += cash
                            # Meme kill messages
                            kill_msgs = [
                                f"+${cash} ez clap", f"+${cash} gg no re", 
                                f"+${cash} BOZO", f"+${cash} ratio'd",
                                f"+${cash} skill diff", f"+${cash} smoked",
                                f"+${cash} packed", f"+${cash} sent to ohio"
                            ]
                            self.spawn_message(cop.center[0], cop.center[1] - 30, 
                                             random.choice(kill_msgs), C['gold'])
                        break
                
                # Hit gang members
                for gang in self.gang_members[:]:
                    if abs(b.x - gang.center[0]) < 22 and abs(b.y - gang.center[1]) < 32:
                        base_damage = 35 + b.damage_bonus
                        actual_damage = int(base_damage * p.damage_mult)
                        gang.health -= actual_damage
                        self.spawn_blood(b.x, b.y, 12)
                        self.spawn_particles(b.x, b.y, 'spark', 3)
                        # Decrease reputation with this gang
                        p.gang_rep[gang.gang] = max(-100, p.gang_rep[gang.gang] - 10)
                        if b in self.bullets:
                            self.bullets.remove(b)
                        if gang.health <= 0:
                            self.gang_members.remove(gang)
                            self.spawn_blood(gang.center[0], gang.center[1], 35)
                            cash = random.randint(30, 80)
                            p.cash += cash
                            p.gang_kills += 1
                            p.total_earned += cash
                            # Gang kill messages
                            gang_msgs = [
                                f"+${cash} gang gang", f"+${cash} opps down",
                                f"+${cash} no cap fr", f"+${cash} caught lackin",
                                f"+${cash} smoking that pack", f"+${cash} rip bozo"
                            ]
                            self.spawn_message(gang.center[0], gang.center[1] - 30,
                                             random.choice(gang_msgs), C['gold'])
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
            
            # Gang bullets hitting player
            if b.owner.startswith('gang_'):
                if abs(b.x - p.center[0]) < 25 and abs(b.y - p.center[1]) < 35:
                    base_damage = 20
                    actual_damage = int(base_damage * (1 - p.armor / 100))
                    p.health -= actual_damage
                    p.damage_flash = 10
                    self.spawn_blood(b.x, b.y, 8)
                    if b in self.bullets:
                        self.bullets.remove(b)
                    if p.health <= 0:
                        p.alive = False
                        p.respawn_timer = 180
                        self.spawn_blood(p.center[0], p.center[1], 50)
                    continue
                
                # Gang bullets hitting other gang members
                shooter_gang = b.owner.split('_')[1]
                for gang in self.gang_members[:]:
                    if gang.gang != shooter_gang:
                        if abs(b.x - gang.center[0]) < 22 and abs(b.y - gang.center[1]) < 32:
                            gang.health -= 25
                            self.spawn_blood(b.x, b.y, 10)
                            if b in self.bullets:
                                self.bullets.remove(b)
                            if gang.health <= 0:
                                self.gang_members.remove(gang)
                                self.spawn_blood(gang.center[0], gang.center[1], 30)
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
            self.show_notification("GOATED! YOU'RE LITERALLY HIM! ESC for stats", 300)
    
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
        safe_rects = [r for r, c in self.safe_houses]
        
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
            elif b in safe_rects:
                pygame.draw.rect(screen, (30, 100, 30), (bx, by, TILE, TILE))
                screen.blit(F['tiny'].render("SAFE", True, C['green']), (bx + 10, by + 24))
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
        if p.alive and not p.inside and not p.in_vehicle:
            px, py = p.x - cam[0], p.y - cam[1]
            pygame.draw.ellipse(screen, (20, 20, 30), (px + 3, py + 55, 32, 10))
            pygame.draw.rect(screen, C['purple'], (px, py, p.w, p.h))
            pygame.draw.rect(screen, (0, 0, 0), (px, py, p.w, p.h), 3)
            pygame.draw.circle(screen, (255, 230, 200), (int(px + p.w//2), int(py + 14)), 10)
            pygame.draw.rect(screen, C['gold'], (px - 2, py - 2, p.w + 4, p.h + 4), 2)
        
        # Vehicles
        for vehicle in self.vehicles:
            vx, vy = vehicle.x - cam[0], vehicle.y - cam[1]
            if vx < -100 or vx > SCREEN_W + 100 or vy < -100 or vy > SCREEN_H + 100:
                continue
            
            # Draw vehicle body
            color = C.get(vehicle.color_key, C['car_red'])
            
            # Rotate vehicle shape based on angle
            cos_a = math.cos(vehicle.angle)
            sin_a = math.sin(vehicle.angle)
            hw, hh = vehicle.w // 2, vehicle.h // 2
            
            # Simple rectangle for now (rotated)
            points = [
                (vx + cos_a * hw - sin_a * hh, vy + sin_a * hw + cos_a * hh),
                (vx - cos_a * hw - sin_a * hh, vy - sin_a * hw + cos_a * hh),
                (vx - cos_a * hw + sin_a * hh, vy - sin_a * hw - cos_a * hh),
                (vx + cos_a * hw + sin_a * hh, vy + sin_a * hw - cos_a * hh),
            ]
            pygame.draw.polygon(screen, color, points)
            pygame.draw.polygon(screen, (0, 0, 0), points, 2)
            
            # Windshield
            ws_points = [
                (vx + cos_a * hw * 0.4 - sin_a * hh * 0.6, vy + sin_a * hw * 0.4 + cos_a * hh * 0.6),
                (vx + cos_a * hw * 0.4 + sin_a * hh * 0.6, vy + sin_a * hw * 0.4 - cos_a * hh * 0.6),
                (vx + cos_a * hw * 0.1 + sin_a * hh * 0.6, vy + sin_a * hw * 0.1 - cos_a * hh * 0.6),
                (vx + cos_a * hw * 0.1 - sin_a * hh * 0.6, vy + sin_a * hw * 0.1 + cos_a * hh * 0.6),
            ]
            pygame.draw.polygon(screen, (100, 150, 200), ws_points)
            
            # Show if occupied
            if vehicle.occupied:
                pygame.draw.circle(screen, C['gold'], (int(vx), int(vy)), 5)
            
            # Health bar if damaged
            if vehicle.health < vehicle.max_health:
                bar_x = vx - 30
                bar_y = vy - hh - 15
                pygame.draw.rect(screen, (60, 0, 0), (bar_x, bar_y, 60, 5))
                pygame.draw.rect(screen, C['green'], (bar_x, bar_y, 60 * vehicle.health // vehicle.max_health, 5))
        
        # Police cars
        for pcar in self.police_cars:
            px, py = pcar['x'] - cam[0], pcar['y'] - cam[1]
            if px < -100 or px > SCREEN_W + 100 or py < -100 or py > SCREEN_H + 100:
                continue
            
            # Draw police car
            cos_a = math.cos(pcar['angle'])
            sin_a = math.sin(pcar['angle'])
            hw, hh = 45, 25
            
            points = [
                (px + cos_a * hw - sin_a * hh, py + sin_a * hw + cos_a * hh),
                (px - cos_a * hw - sin_a * hh, py - sin_a * hw + cos_a * hh),
                (px - cos_a * hw + sin_a * hh, py - sin_a * hw - cos_a * hh),
                (px + cos_a * hw + sin_a * hh, py + sin_a * hw - cos_a * hh),
            ]
            pygame.draw.polygon(screen, C['cop'], points)
            pygame.draw.polygon(screen, (0, 0, 0), points, 2)
            
            # Light bar (red/blue flashing)
            flash = (self.game_time // 10) % 2
            light_col = C['red'] if flash else C['cop']
            pygame.draw.circle(screen, light_col, (int(px), int(py - 5)), 8)
            
            # Health bar
            if pcar['health'] < pcar['max_health']:
                pygame.draw.rect(screen, (60, 0, 0), (px - 30, py - hh - 12, 60, 5))
                pygame.draw.rect(screen, C['red'], (px - 30, py - hh - 12, 60 * pcar['health'] // pcar['max_health'], 5))
        
        # Rockets (RPG)
        for rocket in self.rockets:
            rx, ry = rocket['x'] - cam[0], rocket['y'] - cam[1]
            if rx < -20 or rx > SCREEN_W + 20 or ry < -20 or ry > SCREEN_H + 20:
                continue
            
            # Draw rocket
            angle = rocket['angle']
            length = 15
            pygame.draw.line(screen, C['orange'], 
                (rx - math.cos(angle) * length, ry - math.sin(angle) * length),
                (rx + math.cos(angle) * length/2, ry + math.sin(angle) * length/2), 4)
            pygame.draw.circle(screen, C['red'], (int(rx + math.cos(angle) * length/2), int(ry + math.sin(angle) * length/2)), 5)
        
        # Gang members
        for gang in self.gang_members:
            gx, gy = gang.x - cam[0], gang.y - cam[1]
            if gx < -50 or gx > SCREEN_W + 50 or gy < -50 or gy > SCREEN_H + 50:
                continue
            pygame.draw.ellipse(screen, (20, 20, 30), (gx + 3, gy + 53, 32, 8))
            pygame.draw.rect(screen, gang.color, (gx, gy, gang.w, gang.h))
            pygame.draw.rect(screen, (0, 0, 0), (gx, gy, gang.w, gang.h), 2)
            pygame.draw.circle(screen, (200, 170, 140), (int(gx + gang.w//2), int(gy + 12)), 9)
            # Gang bandana indicator
            pygame.draw.rect(screen, gang.color, (gx + 5, gy + 3, gang.w - 10, 8))
            # Health bar
            if gang.health < gang.max_health:
                pygame.draw.rect(screen, (60, 0, 0), (gx, gy - 10, 38, 5))
                pygame.draw.rect(screen, gang.color, (gx, gy - 10, 38 * gang.health // gang.max_health, 5))
            if gang.alert:
                screen.blit(F['tiny'].render("!", True, C['white']), (gx + gang.w//2 - 3, gy - 20))
        
        # Particles
        for particle in self.particles:
            px, py = particle.x - cam[0], particle.y - cam[1]
            if px < -20 or px > SCREEN_W + 20 or py < -20 or py > SCREEN_H + 20:
                continue
            alpha = int(255 * particle.life / 45)
            size = int(particle.size)
            if particle.ptype == 'smoke':
                # Draw smoke as fading circle
                pygame.draw.circle(screen, (80, 80, 80), (int(px), int(py)), size)
            else:
                pygame.draw.circle(screen, particle.color, (int(px), int(py)), max(1, size))
        
        # Bullets
        for b in self.bullets:
            bx, by = b.x - cam[0], b.y - cam[1]
            if b.owner == 'player':
                col = C['yellow']
            elif b.owner == 'cop':
                col = C['red']
            else:
                # Gang bullets - use gang color
                gang_name = b.owner.split('_')[1] if '_' in b.owner else 'red'
                col = C.get(f'gang_{gang_name}', C['red'])
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
            
            # Pulsing background effect
            pulse = int(abs(math.sin(self.game_time * 0.1)) * 30)
            pygame.draw.rect(screen, (60 + pulse, 0, 50 + pulse), (0, 0, SCREEN_W, SCREEN_H))
            
            title = F['big'].render("✧ RIZZ BATTLE ✧", True, C['pink'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 30))
            
            subtitle = F['small'].render("show ur rizz to recruit", True, C['neon'])
            screen.blit(subtitle, (SCREEN_W//2 - subtitle.get_width()//2, 85))
            
            # Score display
            score_txt = F['main'].render(f"RIZZ POINTS: {p.rizz_score}/{p.rizz_target}", True, C['gold'])
            screen.blit(score_txt, (SCREEN_W//2 - score_txt.get_width()//2, 130))
            
            # Combo display
            if p.rizz_combo > 0:
                combo_col = C['neon'] if p.rizz_combo < 5 else C['gold'] if p.rizz_combo < 10 else C['pink']
                combo_txt = F['main'].render(f"COMBO x{p.rizz_combo}", True, combo_col)
                screen.blit(combo_txt, (SCREEN_W//2 - combo_txt.get_width()//2, 165))
            
            # Arrow sequence display
            if len(p.rizz_sequence) > 0 and p.rizz_index < len(p.rizz_sequence):
                arrow_symbols = {'W': '↑', 'A': '←', 'S': '↓', 'D': '→'}
                
                # Draw upcoming arrows
                y_pos = 280
                start_x = SCREEN_W//2 - (len(p.rizz_sequence) * 45) // 2
                
                for i, key in enumerate(p.rizz_sequence):
                    x_pos = start_x + i * 45
                    
                    if i < p.rizz_index:
                        # Already hit - green
                        col = C['green']
                        alpha = 100
                    elif i == p.rizz_index:
                        # Current - pulsing yellow
                        pulse = int(abs(math.sin(self.game_time * 0.15)) * 50)
                        col = (255, 255, pulse)
                        # Draw highlight box
                        pygame.draw.rect(screen, col, (x_pos - 5, y_pos - 5, 50, 70), 3)
                    else:
                        # Upcoming - white
                        col = C['white']
                    
                    arrow = F['big'].render(arrow_symbols[key], True, col)
                    screen.blit(arrow, (x_pos, y_pos))
                    
                    # Key label below
                    key_txt = F['small'].render(key, True, col)
                    screen.blit(key_txt, (x_pos + 15, y_pos + 50))
                
                # Timer bar for current key
                timer_ratio = p.rizz_timer / 120
                bar_w = 300
                pygame.draw.rect(screen, (80, 40, 60), (SCREEN_W//2 - bar_w//2, 380, bar_w, 20))
                pygame.draw.rect(screen, C['neon'], (SCREEN_W//2 - bar_w//2, 380, int(bar_w * timer_ratio), 20))
                pygame.draw.rect(screen, C['white'], (SCREEN_W//2 - bar_w//2, 380, bar_w, 20), 2)
                
                # Timer decreases
                p.rizz_timer -= 1
                if p.rizz_timer <= 0:
                    # TIME OUT - reset combo
                    p.rizz_combo = 0
                    p.rizz_timer = 120
                    p.rizz_message = "TOO SLOW! no rizz..."
                    p.rizz_message_timer = 40
            
            # Message display
            if p.rizz_message_timer > 0:
                msg_scale = min(1.0, p.rizz_message_timer / 20)
                msg = F['main'].render(p.rizz_message, True, C['gold'])
                screen.blit(msg, (SCREEN_W//2 - msg.get_width()//2, 440))
                p.rizz_message_timer -= 1
            
            # Stats
            hoes_txt = F['main'].render(f"Your Hoes: {len(self.hoes)}", True, C['pink'])
            screen.blit(hoes_txt, (SCREEN_W//2 - hoes_txt.get_width()//2, 520))
            
            hint = F['small'].render("Press the arrow keys in order! ESC to leave", True, (150, 150, 150))
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 560))
        
        elif p.building_type == 'gun':
            screen.fill((50, 40, 30))
            
            title = F['big'].render("GUN STORE", True, C['gold'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 40))
            
            # Initialize selection if needed
            if not hasattr(p, 'gun_selection'):
                p.gun_selection = 0
            
            # Display items
            items = [
                ("Pistol + 30 Ammo - $200", 200, p.has_gun, 'pistol'),
                ("Shotgun + 20 Ammo - $500", 500, p.has_shotgun, 'shotgun'),
                ("Uzi + 50 Ammo - $800", 800, p.has_uzi, 'uzi'),
                ("Rifle + 15 Ammo - $1200", 1200, p.has_rifle, 'rifle'),
                ("RPG + 3 Rockets - $2000", 2000, p.has_rpg, 'rpg'),
                ("Ammo x30 - $100", 100, False, 'ammo'),
                ("Rockets x3 - $300", 300, False, 'rockets'),
            ]
            
            y = 130
            for idx, (text, price, owned, item_type) in enumerate(items):
                selected = (p.gun_selection == idx)
                prefix = "► " if selected else "  "
                
                if item_type == 'ammo':
                    if not (p.has_gun or p.has_shotgun or p.has_uzi or p.has_rifle):
                        col = (80, 80, 80)
                        txt = F['main'].render(prefix + text + " [NO WEAPON]", True, col)
                    elif p.cash >= price:
                        col = C['neon'] if selected else C['gold']
                        txt = F['main'].render(prefix + text, True, col)
                    else:
                        col = C['red']
                        txt = F['main'].render(prefix + text, True, col)
                elif item_type == 'rockets':
                    if not p.has_rpg:
                        col = (80, 80, 80)
                        txt = F['main'].render(prefix + text + " [NO RPG]", True, col)
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
                y += 45
            
            hint = F['main'].render("W/S = Select | SPACE = Buy", True, C['white'])
            screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, 480))
            
            ammo_txt = F['main'].render(f"Ammo: {p.ammo} | Rockets: {p.rockets}", True, C['neon'])
            screen.blit(ammo_txt, (SCREEN_W//2 - ammo_txt.get_width()//2, 520))
            
            cash_txt = F['main'].render(f"Cash: ${p.cash}", True, C['gold'])
            screen.blit(cash_txt, (SCREEN_W//2 - cash_txt.get_width()//2, 555))
        
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
        
        elif p.building_type == 'safe':
            screen.fill((20, 30, 20))
            
            title = F['big'].render("SAFE HOUSE", True, C['green'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 60))
            
            if not hasattr(p, 'safe_selection'):
                p.safe_selection = 0
            
            options = [
                ("Save Game", "FREE", True),
                ("Full Heal + Clear Heat", "$200", p.cash >= 200 and p.health < p.max_health),
            ]
            
            y = 220
            for i, (text, cost, available) in enumerate(options):
                selected = (p.safe_selection == i)
                prefix = "► " if selected else "  "
                col = C['green'] if selected and available else (C['white'] if available else C['red'])
                txt = F['main'].render(f"{prefix}{text} - {cost}", True, col)
                screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, y))
                y += 60
            
            # Status
            status = F['main'].render(f"Health: {p.health}/{p.max_health} | Wanted: {'★' * int(p.wanted)}", True, C['gold'])
            screen.blit(status, (SCREEN_W//2 - status.get_width()//2, 400))
            
            if self.has_save:
                save_info = F['small'].render("(Save data exists)", True, (100, 150, 100))
                screen.blit(save_info, (SCREEN_W//2 - save_info.get_width()//2, 450))
            
            hint = F['main'].render("W/S = Select | SPACE = Confirm", True, C['white'])
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
        weapon = p.current_weapon.upper()
        has_weapon = p.current_weapon != 'fists'
        
        # Check if player has the weapon
        weapon_owned = {
            'pistol': p.has_gun,
            'shotgun': p.has_shotgun,
            'uzi': p.has_uzi,
            'rifle': p.has_rifle,
            'rpg': p.has_rpg,
            'fists': True,
        }
        
        if not weapon_owned.get(p.current_weapon, False):
            weapon = "FISTS"
            has_weapon = False
        
        if p.current_weapon == 'rpg':
            if p.rockets > 0:
                weapon_col = C['red']
                ammo_str = f" [{p.rockets}]"
            else:
                weapon_col = C['red']
                ammo_str = " NO ROCKETS!"
        elif has_weapon:
            if p.ammo > 0:
                weapon_col = C['yellow']
                ammo_str = f" [{p.ammo}]"
            else:
                weapon_col = C['red']
                ammo_str = " EMPTY!"
        else:
            weapon_col = C['gray']
            ammo_str = ""
        
        screen.blit(F['small'].render(f"{weapon}{ammo_str}", True, weapon_col), (120, 10))
        
        # Weapon slots hint
        slots = []
        if p.has_gun: slots.append("1:Pistol")
        if p.has_shotgun: slots.append("2:Shotgun")
        if p.has_uzi: slots.append("3:Uzi")
        if p.has_rifle: slots.append("4:Rifle")
        if p.has_rpg: slots.append("5:RPG")
        if len(slots) > 1:
            slots_txt = F['tiny'].render(" | ".join(slots), True, (80, 80, 80))
            screen.blit(slots_txt, (120, 55))
        
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
        
        # Dead - with meme messages
        if not p.alive:
            death_msgs = [
                "WASTED", "SKILL ISSUE", "L + RATIO", "DOWN BAD",
                "GET REKT", "NO BITCHES?", "CAUGHT IN 4K", 
                "LITERALLY 1984", "FELL OFF", "NPC DEATH",
                "DIDNT ASK + RATIO", "COPE + SEETHE"
            ]
            # Use player kills as seed for consistent message until respawn
            msg_idx = (p.kills + int(p.respawn_timer / 30)) % len(death_msgs)
            dead = F['big'].render(death_msgs[msg_idx], True, C['red'])
            screen.blit(dead, (SCREEN_W//2 - dead.get_width()//2, SCREEN_H//2 - 50))
            resp = F['main'].render("skill issue detected... respawning...", True, C['white'])
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
        if p.inside or p.in_vehicle:
            return None
        
        px, py = p.center
        
        # Check for nearby vehicle first
        for vehicle in self.vehicles:
            if not vehicle.occupied and math.hypot(px - vehicle.x, py - vehicle.y) < 80:
                return f"{vehicle.vtype.upper()} (E to enter)"
        
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
        for rect, center in self.safe_houses:
            if math.hypot(px - center[0], py - center[1]) < 80:
                return "SAFE HOUSE"
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
            title = F['big'].render("LITERALLY HIM", True, C['gold'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 80))
            
            subtitle = F['main'].render("you did it. you're goated.", True, C['neon'])
            screen.blit(subtitle, (SCREEN_W//2 - subtitle.get_width()//2, 150))
            
            flex = F['main'].render(f"${self.win_goal} secured. W.", True, C['pink'])
            screen.blit(flex, (SCREEN_W//2 - flex.get_width()//2, 190))
        else:
            # Pause screen
            title = F['big'].render("AFK", True, C['white'])
            screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 100))
            
            pause_msg = F['small'].render("(touching grass rn brb)", True, (150, 150, 150))
            screen.blit(pause_msg, (SCREEN_W//2 - pause_msg.get_width()//2, 160))
        
        # Stats
        play_time = self.game_time // 60  # seconds
        minutes, seconds = divmod(play_time, 60)
        
        stats = [
            f"Time Grinding: {minutes}:{seconds:02d}",
            f"Bodies Dropped: {p.kills}",
            f"Gang Ops Packed: {p.gang_kills}",
            f"Bag Secured: ${p.total_earned}",
            f"Packs Sold: {p.total_drugs_sold}",
            f"Current Bag: ${p.cash}",
            f"Hoes Acquired: {len(self.hoes)}",
        ]
        
        y = 240
        for stat in stats:
            txt = F['main'].render(stat, True, C['white'])
            screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, y))
            y += 35
        
        # Instructions
        hint = F['small'].render("ESC to get back to it | Q to rage quit", True, (150, 150, 150))
        screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 80))
        
        # Goal progress
        progress = min(1.0, p.total_earned / self.win_goal)
        bar_w = 400
        pygame.draw.rect(screen, (40, 40, 50), (SCREEN_W//2 - bar_w//2, 520, bar_w, 30))
        pygame.draw.rect(screen, C['gold'], (SCREEN_W//2 - bar_w//2, 520, int(bar_w * progress), 30))
        pygame.draw.rect(screen, C['white'], (SCREEN_W//2 - bar_w//2, 520, bar_w, 30), 2)
        goal_txt = F['small'].render(f"Grind Progress: ${p.total_earned} / ${self.win_goal}", True, C['white'])
        screen.blit(goal_txt, (SCREEN_W//2 - goal_txt.get_width()//2, 555))
    
    def draw_mission_select(self):
        """Draw mission selection screen"""
        p = self.player
        
        # Darken background
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        title = F['big'].render("THE GRIND", True, C['neon'])
        screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 60))
        
        if self.active_mission:
            # Show active mission with abandon option
            active_txt = F['main'].render("CURRENT OBJECTIVE:", True, C['gold'])
            screen.blit(active_txt, (SCREEN_W//2 - active_txt.get_width()//2, 150))
            
            m = self.active_mission
            desc_txt = F['main'].render(m.description, True, C['white'])
            screen.blit(desc_txt, (SCREEN_W//2 - desc_txt.get_width()//2, 200))
            
            progress_txt = F['main'].render(f"Status: {m.get_progress_text()}", True, C['neon'])
            screen.blit(progress_txt, (SCREEN_W//2 - progress_txt.get_width()//2, 240))
            
            reward_txt = F['main'].render(f"Bag: ${m.reward}", True, C['gold'])
            screen.blit(reward_txt, (SCREEN_W//2 - reward_txt.get_width()//2, 280))
            
            hint = F['small'].render("X to give up (L) | TAB to close", True, (150, 150, 150))
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
    
    def draw_title_screen(self):
        """Draw the title screen"""
        # Background with animated elements
        screen.fill(C['dark_purple'])
        
        # Draw some decorative blood splatters
        for i in range(20):
            x = (i * 137 + self.game_time) % SCREEN_W
            y = (i * 89) % SCREEN_H
            size = 10 + (i % 15)
            pygame.draw.circle(screen, C['blood'], (x, y), size)
        
        # Title
        title = F['big'].render("BLOODBATH", True, C['red'])
        title_shadow = F['big'].render("BLOODBATH", True, (100, 0, 0))
        screen.blit(title_shadow, (SCREEN_W//2 - title.get_width()//2 + 4, 104))
        screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 100))
        
        subtitle = F['main'].render("R P G", True, C['gold'])
        screen.blit(subtitle, (SCREEN_W//2 - subtitle.get_width()//2, 180))
        
        # Rotating meme taglines
        taglines = [
            "no cap fr fr", "bussin respectfully", "it hits different",
            "caught in 4k", "main character energy", "based and pilled",
            "only in ohio", "its giving... crime", "slay bestie slay",
            "real ones know", "trust the process", "different breed"
        ]
        tagline_idx = (self.game_time // 120) % len(taglines)
        tag = F['small'].render(f"~ {taglines[tagline_idx]} ~", True, C['pink'])
        screen.blit(tag, (SCREEN_W//2 - tag.get_width()//2, 220))
        
        # Menu options
        options = ["START THAT GRIND", "HOW 2 PLAY", "TOUCH GRASS (quit)"]
        y = 320
        for i, option in enumerate(options):
            selected = (i == self.title_selection)
            col = C['gold'] if selected else C['white']
            prefix = "► " if selected else "  "
            txt = F['main'].render(prefix + option, True, col)
            screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, y))
            y += 50
        
        # Controls info (if selected)
        if self.title_selection == 1:
            controls = [
                "WASD - Move it move it",
                "Click - Pew pew (auto-aim on cops)",
                "E - Enter the building arc",
                "1-5 / Scroll - Switch that loadout",
                "TAB - Check the grind (missions)",
                "ESC - Take a breather",
            ]
            y = 480
            for ctrl in controls:
                txt = F['small'].render(ctrl, True, C['neon'])
                screen.blit(txt, (SCREEN_W//2 - txt.get_width()//2, y))
                y += 25
        
        # Version info
        ver = F['tiny'].render("v1.4 - Meme Update | no cap certified", True, (100, 100, 100))
        screen.blit(ver, (10, SCREEN_H - 25))
    
    def draw_day_night_overlay(self):
        """Apply day/night cycle lighting"""
        # Calculate time of day (0-1)
        time_ratio = self.time_of_day / self.day_length
        
        # Determine lighting based on time
        # 0.0-0.25: Night
        # 0.25-0.35: Dawn
        # 0.35-0.65: Day
        # 0.65-0.75: Dusk
        # 0.75-1.0: Night
        
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        
        if time_ratio < 0.25 or time_ratio > 0.75:
            # Night - blue tint
            alpha = 80
            overlay.fill((0, 0, 50, alpha))
        elif time_ratio < 0.35:
            # Dawn - orange/pink tint
            alpha = int(50 * (0.35 - time_ratio) / 0.1)
            overlay.fill((80, 40, 60, alpha))
        elif time_ratio > 0.65:
            # Dusk - orange tint
            alpha = int(50 * (time_ratio - 0.65) / 0.1)
            overlay.fill((80, 40, 20, alpha))
        else:
            # Day - no overlay
            return
        
        screen.blit(overlay, (0, 0))
    
    def run(self):
        running = True
        
        while running:
            dt = clock.tick(FPS) / 1000.0
            self.game_time += 1
            
            # Handle title screen
            if self.game_state == 'title':
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        running = False
                    if e.type == pygame.KEYDOWN:
                        if e.key == pygame.K_w or e.key == pygame.K_UP:
                            self.title_selection = (self.title_selection - 1) % 3
                        if e.key == pygame.K_s or e.key == pygame.K_DOWN:
                            self.title_selection = (self.title_selection + 1) % 3
                        if e.key == pygame.K_RETURN or e.key == pygame.K_SPACE:
                            if self.title_selection == 0:
                                self.game_state = 'playing'
                            elif self.title_selection == 2:
                                running = False
                        if e.key == pygame.K_ESCAPE:
                            running = False
                
                self.draw_title_screen()
                pygame.display.flip()
                continue
            
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
                        # E key - enter buildings OR vehicles
                        if self.player.in_vehicle:
                            self.exit_vehicle()
                        elif self.get_nearby_vehicle():
                            self.enter_vehicle()
                        else:
                            self.enter_building()
                    if e.key == pygame.K_f:
                        # F key - exit vehicle (alternative)
                        if self.player.in_vehicle:
                            self.exit_vehicle()
                    if e.key == pygame.K_SPACE:
                        if self.player.inside:
                            self.interact()
                        elif not self.player.in_vehicle:
                            self.melee()
                    if e.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
                    # Radio toggle (R key while in vehicle)
                    if e.key == pygame.K_r and self.player.in_vehicle:
                        self.current_station = (self.current_station + 1) % len(self.radio_stations)
                        station = self.radio_stations[self.current_station]
                        if station['name'] == 'OFF':
                            self.show_notification("Radio: OFF", 60)
                        else:
                            self.show_notification(f"Radio: {station['name']} ({station['genre']})", 90)
                    
                    # Weapon switching (1-5 keys)
                    p = self.player
                    if not p.inside:
                        if e.key == pygame.K_1 and p.has_gun:
                            p.current_weapon = 'pistol'
                            self.show_notification("Pistol", 30)
                        elif e.key == pygame.K_2 and p.has_shotgun:
                            p.current_weapon = 'shotgun'
                            self.show_notification("Shotgun", 30)
                        elif e.key == pygame.K_3 and p.has_uzi:
                            p.current_weapon = 'uzi'
                            self.show_notification("Uzi", 30)
                        elif e.key == pygame.K_4 and p.has_rifle:
                            p.current_weapon = 'rifle'
                            self.show_notification("Rifle", 30)
                        elif e.key == pygame.K_5 and p.has_rpg:
                            p.current_weapon = 'rpg'
                            self.show_notification("RPG", 30)
                    
                    # Menu navigation when inside buildings
                    if self.player.inside:
                        p = self.player
                        
                        # RIZZ BATTLE rhythm game
                        if p.building_type == 'strip' and len(p.rizz_sequence) > 0:
                            key_pressed = None
                            if e.key == pygame.K_w: key_pressed = 'W'
                            elif e.key == pygame.K_a: key_pressed = 'A'
                            elif e.key == pygame.K_s: key_pressed = 'S'
                            elif e.key == pygame.K_d: key_pressed = 'D'
                            
                            if key_pressed and p.rizz_index < len(p.rizz_sequence):
                                expected = p.rizz_sequence[p.rizz_index]
                                if key_pressed == expected:
                                    # CORRECT!
                                    p.rizz_combo += 1
                                    combo_bonus = min(p.rizz_combo, 10)
                                    points = 50 * combo_bonus
                                    p.rizz_score += points
                                    p.rizz_index += 1
                                    p.rizz_timer = 120
                                    
                                    # Meme messages based on combo
                                    messages = [
                                        "nice.", "sheesh!", "W RIZZ", "GYATT!", 
                                        "BUSSIN!", "NO CAP!", "SLAY!", "GOATED!",
                                        "OHIO RIZZ!", "SIGMA MODE!", "SKIBIDI!",
                                        "FANUM TAX!", "ONLY IN OHIO!", "BASED!"
                                    ]
                                    p.rizz_message = random.choice(messages) + f" +{points}"
                                    p.rizz_message_timer = 40
                                    
                                    # Check if completed sequence
                                    if p.rizz_index >= len(p.rizz_sequence):
                                        if p.rizz_score >= p.rizz_target:
                                            # RECRUIT SUCCESS
                                            hoe = Hoe(p.entry_pos[0] + random.randint(-50, 50),
                                                     p.entry_pos[1] + random.randint(-50, 50))
                                            self.hoes.append(hoe)
                                            p.cash += 100 + p.rizz_combo * 10
                                            p.rizz_message = "RIZZ GOD! +1 HOE!"
                                            p.rizz_message_timer = 90
                                        else:
                                            p.rizz_message = "NOT ENOUGH RIZZ... TRY AGAIN"
                                            p.rizz_message_timer = 90
                                        # Reset for next round
                                        p.rizz_sequence = [random.choice(['W', 'A', 'S', 'D']) for _ in range(8)]
                                        p.rizz_index = 0
                                        p.rizz_combo = 0
                                        p.rizz_score = 0
                                        p.rizz_timer = 120
                                else:
                                    # WRONG! Combo broken
                                    p.rizz_combo = 0
                                    fails = ["L + ratio", "no rizz detected", "down bad", 
                                             "skill issue", "cringe", "NPC behavior",
                                             "literally me fr fr", "caught in 4k"]
                                    p.rizz_message = random.choice(fails)
                                    p.rizz_message_timer = 40
                        
                        elif e.key == pygame.K_w or e.key == pygame.K_UP:
                            if p.building_type == 'gun':
                                p.gun_selection = (p.gun_selection - 1) % 7
                            elif p.building_type == 'dealer':
                                p.dealer_selection = (p.dealer_selection - 1) % 2
                            elif p.building_type == 'upgrade':
                                p.upgrade_selection = (p.upgrade_selection - 1) % 4
                            elif p.building_type == 'safe':
                                p.safe_selection = (p.safe_selection - 1) % 2
                        elif e.key == pygame.K_s or e.key == pygame.K_DOWN:
                            if p.building_type == 'gun':
                                p.gun_selection = (p.gun_selection + 1) % 7
                            elif p.building_type == 'dealer':
                                p.dealer_selection = (p.dealer_selection + 1) % 2
                            elif p.building_type == 'upgrade':
                                p.upgrade_selection = (p.upgrade_selection + 1) % 4
                            elif p.building_type == 'safe':
                                p.safe_selection = (p.safe_selection + 1) % 2
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if not self.paused:
                        shoot = True
                # Mouse wheel weapon cycling
                if e.type == pygame.MOUSEWHEEL and not self.player.inside:
                    p = self.player
                    weapons = []
                    if p.has_gun: weapons.append('pistol')
                    if p.has_shotgun: weapons.append('shotgun')
                    if p.has_uzi: weapons.append('uzi')
                    if p.has_rifle: weapons.append('rifle')
                    if p.has_rpg: weapons.append('rpg')
                    if len(weapons) > 0:
                        try:
                            idx = weapons.index(p.current_weapon)
                        except ValueError:
                            idx = 0
                        if e.y > 0:  # Scroll up
                            idx = (idx - 1) % len(weapons)
                        else:  # Scroll down
                            idx = (idx + 1) % len(weapons)
                        p.current_weapon = weapons[idx]
                        self.show_notification(weapons[idx].upper(), 30)
            
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
                if p.in_vehicle and p.current_vehicle:
                    # Vehicle driving controls
                    vehicle = p.current_vehicle
                    
                    # W/S for acceleration/brake
                    accel = (keys[pygame.K_w] or keys[pygame.K_UP]) - (keys[pygame.K_s] or keys[pygame.K_DOWN])
                    # A/D for steering
                    steer = (keys[pygame.K_d] or keys[pygame.K_RIGHT]) - (keys[pygame.K_a] or keys[pygame.K_LEFT])
                    
                    # Apply acceleration
                    if accel > 0:
                        vehicle.velocity = min(vehicle.velocity + 0.3, vehicle.max_speed)
                    elif accel < 0:
                        vehicle.velocity = max(vehicle.velocity - 0.5, -vehicle.max_speed * 0.5)
                    else:
                        # Friction
                        vehicle.velocity *= 0.97
                    
                    # Apply steering (only when moving)
                    if abs(vehicle.velocity) > 0.5:
                        vehicle.angle += steer * 0.04 * (vehicle.velocity / vehicle.max_speed)
                    
                    # Move vehicle
                    nx = vehicle.x + math.cos(vehicle.angle) * vehicle.velocity
                    ny = vehicle.y + math.sin(vehicle.angle) * vehicle.velocity
                    
                    # Check collision
                    if not self.collides(nx - vehicle.w//2, ny - vehicle.h//2, vehicle.w, vehicle.h):
                        vehicle.x = nx
                        vehicle.y = ny
                    else:
                        vehicle.velocity *= -0.5  # Bounce back
                        self.spawn_particles(vehicle.x, vehicle.y, 'spark', 5)
                    
                    # Keep in bounds
                    vehicle.x = max(vehicle.w, min(MAP_W*TILE - vehicle.w, vehicle.x))
                    vehicle.y = max(vehicle.h, min(MAP_H*TILE - vehicle.h, vehicle.y))
                    
                    # Update player position to match vehicle
                    p.x = vehicle.x - p.w//2
                    p.y = vehicle.y - p.h//2
                else:
                    # Normal on-foot movement
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
            
            # Day/night lighting
            self.draw_day_night_overlay()
            
            # Damage flash overlay
            if p.damage_flash > 0:
                flash = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
                alpha = int(100 * p.damage_flash / 10)
                flash.fill((255, 0, 0, alpha))
                screen.blit(flash, (0, 0))
            
            # Vehicle speed indicator
            if p.in_vehicle and p.current_vehicle:
                v = p.current_vehicle
                speed_txt = F['main'].render(f"{abs(int(v.velocity * 5))} MPH", True, C['neon'])
                screen.blit(speed_txt, (SCREEN_W//2 - speed_txt.get_width()//2, SCREEN_H - 90))
                
                # Radio display
                station = self.radio_stations[self.current_station]
                if station['name'] != 'OFF':
                    radio_txt = F['small'].render(f"♫ {station['name']} - {station['genre']}", True, C['gold'])
                else:
                    radio_txt = F['small'].render("♫ Radio OFF", True, (100, 100, 100))
                screen.blit(radio_txt, (SCREEN_W//2 - radio_txt.get_width()//2, SCREEN_H - 65))
                
                exit_hint = F['tiny'].render("E = Exit | R = Radio", True, (150, 150, 150))
                screen.blit(exit_hint, (SCREEN_W//2 - exit_hint.get_width()//2, SCREEN_H - 40))
            
            # Controls hint
            if not p.inside and not p.in_vehicle:
                hint = F['tiny'].render("WASD=Move | Click=Shoot | Space=Melee | E=Enter | TAB=Missions", True, (80, 80, 80))
                screen.blit(hint, (SCREEN_W//2 - hint.get_width()//2, SCREEN_H - 25))
            
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
