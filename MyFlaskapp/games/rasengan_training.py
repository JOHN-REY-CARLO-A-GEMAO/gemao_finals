import tkinter as tk
from tkinter import Canvas
import random
import math
from base_game import BaseNarutoGame

class RasenganTrainingGame(BaseNarutoGame):
    """Naruto Rasengan Training Game - Spin the rasengan with correct timing"""
    
    def __init__(self): # Removed root parameter
        super().__init__("Rasengan Training", 800, 600) # BaseNarutoGame handles root
        
        # Game specific variables
        self.rasengan_power = 0
        self.spin_speed = 0
        self.target_power = 75
        self.power_zone_min = 70
        self.power_zone_max = 80
        self.is_spinning = False
        self.spin_angle = 0
        self.particles = []
        self.success_count = 0
        
        self.setup_game_canvas()
        
    def setup_game_canvas(self):
        """Setup the game canvas"""
        self.canvas = Canvas(self.game_frame, 
                           width=780, 
                           height=400,
                           bg='#1a1a2e',
                           highlightthickness=2,
                           highlightbackground=self.colors['primary'])
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw Naruto's hand
        self.draw_naruto_hand()
        
        # Power meter
        self.draw_power_meter()
        
        # Instructions
        self.canvas.create_text(390, 30, 
                               text="Click and hold to spin the Rasengan!",
                               fill='white',
                               font=('Arial', 14, 'bold'),
                               tags='instruction')
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.start_spin)
        self.canvas.bind('<ButtonRelease-1>', self.release_spin)
        
    def draw_naruto_hand(self):
        """Draw Naruto's hand holding rasengan"""
        # Hand
        self.hand = self.canvas.create_oval(350, 250, 450, 350,
                                           fill='#FDBCB4',
                                           outline='black',
                                           width=2,
                                           tags='hand')
        
        # Rasengan base
        self.rasengan_base = self.canvas.create_oval(375, 275, 425, 325,
                                                    fill='#4169E1',
                                                    outline='white',
                                                    width=2,
                                                    tags='rasengan_base')
        
    def draw_power_meter(self):
        """Draw power meter"""
        # Meter background
        self.canvas.create_rectangle(50, 100, 150, 300,
                                    fill='#333333',
                                    outline='white',
                                    width=2,
                                    tags='meter_bg')
        
        # Power zone (target area)
        self.canvas.create_rectangle(50, 120, 150, 300 - int(self.power_zone_min/100 * 200),
                                    fill='#00FF00',
                                    outline='',
                                    tags='power_zone')

        self.canvas.create_rectangle(50, 300 - int(self.power_zone_max/100 * 200), 150, 300 - int(self.power_zone_min/100 * 200),
                                    fill='#FFFF00', # Warning zone
                                    outline='',
                                    tags='power_zone_warning')
        
        # Power level
        self.power_bar = self.canvas.create_rectangle(50, 300, 150, 300,
                                                    fill='#FF0000',
                                                    outline='',
                                                    tags='power_bar')
        
        # Labels
        self.canvas.create_text(100, 80,
                               text="POWER",
                               fill='white',
                               font=('Arial', 12, 'bold'))
        
        self.canvas.create_text(100, 320,
                               text=f"Target: {self.target_power}%",
                               fill='white',
                               font=('Arial', 10))
        
    def start_spin(self, event):
        """Start spinning the rasengan"""
        if not self.is_running:
            return
            
        self.is_spinning = True
        self.rasengan_power = 0
        self.spin_speed = 2
        self.particles = []
        
    def release_spin(self, event):
        """Release and check rasengan power"""
        if not self.is_spinning:
            return
            
        self.is_spinning = False
        
        # Check if power is in target zone
        if self.power_zone_min <= self.rasengan_power <= self.power_zone_max:
            self.successful_rasengan()
        else:
            self.failed_rasengan()
            
    def successful_rasengan(self):
        """Handle successful rasengan"""
        self.update_score(50)
        self.success_count += 1
        
        # Show success effect
        self.show_success_effect()
        
        # Increase difficulty
        if self.success_count % 3 == 0:
            self.update_level()
            self.target_power = min(95, 75 + self.level * 5)
            self.power_zone_min = self.target_power - 5
            self.power_zone_max = self.target_power + 5
            self.canvas.delete('target_text')
            self.canvas.create_text(100, 320,
                                   text=f"Target: {self.target_power}%",
                                   fill='white',
                                   font=('Arial', 10),
                                   tags='target_text')
        
        self.show_naruto_message("Success!", f"Perfect Rasengan! +50 points")
        
    def failed_rasengan(self):
        """Handle failed rasengan"""
        self.update_lives(-1)
        self.show_failure_effect()
        
    def update_rasengan(self):
        """Update rasengan animation and power"""
        if self.is_spinning:
            # Increase power
            self.rasengan_power = min(100, self.rasengan_power + self.spin_speed)
            self.spin_speed = min(10, self.spin_speed + 0.1)
            
            # Update power bar
            bar_height = (self.rasengan_power / 100) * 200
            self.canvas.coords(self.power_bar, 50, 300 - bar_height, 150, 300)
            
            # Change color based on power
            if self.power_zone_min <= self.rasengan_power <= self.power_zone_max:
                self.canvas.itemconfig(self.power_bar, fill='#00FF00')
            elif self.rasengan_power > self.power_zone_max:
                self.canvas.itemconfig(self.power_bar, fill='#FF0000')
            else:
                self.canvas.itemconfig(self.power_bar, fill='#FFFF00')
            
            # Spin animation
            self.spin_angle += 15
            self.draw_spinning_rasengan()
            
            # Create particles
            if random.random() < 0.3:
                self.create_particle()
                
        # Update particles
        self.update_particles()
        
    def draw_spinning_rasengan(self):
        """Draw spinning rasengan effect"""
        self.canvas.delete('rasengan_spin')
        
        center_x, center_y = 400, 300
        
        # Draw spinning chakra
        for i in range(4):
            angle = math.radians(self.spin_angle + i * 90)
            x1 = center_x + math.cos(angle) * 20
            y1 = center_y + math.sin(angle) * 20
            x2 = center_x + math.cos(angle) * 35
            y2 = center_y + math.sin(angle) * 35
            
            self.canvas.create_line(x1, y1, x2, y2,
                                   fill='#00BFFF',
                                   width=3,
                                   tags='rasengan_spin')
            
        # Central sphere
        size = 25 + math.sin(self.spin_angle * 0.1) * 5
        self.canvas.create_oval(center_x - size, center_y - size,
                               center_x + size, center_y + size,
                               fill='#87CEEB',
                               outline='white',
                               width=2,
                               tags='rasengan_spin')
        
    def create_particle(self):
        """Create chakra particle"""
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        
        particle = {
            'x': 400,
            'y': 300,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'life': 30,
            'id': None
        }
        
        particle['id'] = self.canvas.create_oval(
            particle['x'] - 3, particle['y'] - 3,
            particle['x'] + 3, particle['y'] + 3,
            fill='#00FFFF',
            outline='',
            tags='particle'
        )
        
        self.particles.append(particle)
        
    def update_particles(self):
        """Update particle positions"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.canvas.delete(particle['id'])
                self.particles.remove(particle)
            else:
                # Fade effect
                alpha = particle['life'] / 30
                size = 3 * alpha
                self.canvas.coords(particle['id'],
                                 particle['x'] - size, particle['y'] - size,
                                 particle['x'] + size, particle['y'] + size)
                
    def show_success_effect(self):
        """Show success effect"""
        for i in range(10):
            x = random.randint(350, 450)
            y = random.randint(250, 350)
            star = self.canvas.create_polygon(
                x, y - 8, x + 4, y, x + 8, y,
                x + 4, y + 4, x, y + 8, x - 4, y + 4,
                x - 8, y, x - 4, y,
                fill='#FFD700',
                outline='orange',
                tags='effect'
            )
            self.root.after(1000, lambda s=star: self.canvas.delete(s))
            
    def show_failure_effect(self):
        """Show failure effect"""
        self.canvas.create_text(400, 200,
                               text="FAILED!",
                               fill='#FF0000',
                               font=('Arial', 24, 'bold'),
                               tags='effect')
        self.root.after(1000, lambda: self.canvas.delete('effect'))
        
    def start_game(self):
        """Start the game"""
        self.is_running = True
        self.score = 0
        self.lives = 3
        self.level = 1
        self.success_count = 0
        self.target_power = 75
        self.power_zone_min = 70
        self.power_zone_max = 80
        
        self.update_score(0)
        self.update_lives(0)
        self.level_label.config(text="Level: 1")
        
        self.game_loop()
        
    def pause_game(self):
        """Pause the game"""
        self.is_running = False
        
    def reset_game(self):
        """Reset the game"""
        self.is_running = False
        self.is_spinning = False
        self.rasengan_power = 0
        self.spin_speed = 0
        self.spin_angle = 0
        self.particles = []
        self.success_count = 0
        
        # Clear effects
        self.canvas.delete('rasengan_spin')
        self.canvas.delete('particle')
        self.canvas.delete('effect')
        
        # Reset power bar
        self.canvas.coords(self.power_bar, 50, 300, 150, 300)
        
        # Reset stats
        self.score = 0
        self.lives = 3
        self.level = 1
        self.target_power = 75
        self.power_zone_min = 70
        self.power_zone_max = 80
        
        self.update_score(0)
        self.update_lives(0)
        self.level_label.config(text="Level: 1")
        
    def game_loop(self):
        """Main game loop"""
        if not self.is_running:
            return
            
        self.update_rasengan()
        self.root.after(50, self.game_loop)