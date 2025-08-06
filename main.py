# MODULES
import pygame
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
from config import G, dt, steps, fps_limit, scale

# BODY CLASS
class Body:
    def __init__(self, x, y, vx, vy, m, r, name, color): # Body object properties
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([vx, vy], dtype=float)
        self.acc = np.array([0.0, 0.0])
        self.m = m
        self.r = r
        self.name = name
        self.color = color

    def __repr__(self):
        return f"Body(name={self.name}, x={self.x}, y={self.y}, vx={self.vx}, vy={self.vy}, m={self.m}, r={self.r}, color={self.color})"


# FORCE METHOD
    def force_calc(self, other_bodies): # calculates the total force on a body
        total_force = np.array([0.0, 0.0])

        for other in other_bodies: # iterate through list of bodies
            if other is self:
                continue # skips self in list of bodies
            if other.m < 1e20:
                continue # skips objects below certain mass

            r_vec = other.pos - self.pos # new array finding difference between other and self positions
            r = np.linalg.norm(r_vec) # normalizing new array to scale total_force later (previously math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2))
            
            if r == 0:
                continue


            force_mag = G * self.m * other.m / r**2
            force_dir = r_vec / r
            force = force_mag * force_dir

            total_force += force

        return total_force

# MECHANICAL ENERGY METHOD
    def local_mech_e_calc(self, other_bodies):
        speed = np.linalg.norm(self.vel)
        self.kin_e = .5 * self.m * (speed**2)
        self.pot_e = 0
        
        for other in other_bodies: # iterate through list of bodies
            if other is self:
                continue # skips self in list of bodies

            r = np.linalg.norm(self.pos - other.pos)
            if r == 0:
                continue
            pot_e = -(G*self.m*other.m)/r
            self.pot_e += pot_e
        self.mech_e = self.kin_e + self.pot_e
        return self.mech_e


# POSITION UPDATING
    def movement_update(self, bodies):
        acc_old = self.force_calc(bodies) / self.m
        self.pos += self.vel * dt + .5 * acc_old * dt**2
        acc_new = self.force_calc(bodies) / self.m
        self.acc = acc_new
        self.vel += .5 * (acc_old + acc_new) * dt

# SPACECRAFT CLASS
class Spacecraft(Body):
    def __init__(self, x, y, vx, vy, m, r, name, color): # Body object properties
        super().__init__(x, y, vx, vy, m, r, name, color)

# MECHANICAL ENERGY
def mech_e_calc():
    total_kin = sum(.5* b.m * (b.vel[0]**2 + b.vel[1]**2) for b in bodies)
    total_pot = 0.0

    # CALCULATE POT_E FOR EACH PAIR OF OBJECTS UNIQUELY (NO DUPLICATING)
    for i, b1 in enumerate(bodies):
        for j in range(i+1, len(bodies)):
            b2 = bodies[j]
            r = np.linalg.norm(b1.pos - b2.pos)
            if r == 0:
                continue
            total_pot += -G * b1.m * b2.m / r

    return total_kin + total_pot 

# COLLISION HANDLING
def collision_handling():
    to_remove = []

    all_objects = bodies + spacecrafts
    for i, obj1 in enumerate(all_objects):
        for obj2 in all_objects[i+1:]:
            if obj1 is obj2:
                continue
            r = np.linalg.norm(obj1.pos - obj2.pos)
            if r <= (obj1.r + obj2.r):
                print(f"Collision: {obj1.name} hit {obj2.name}")
                if obj1.m > obj2.m:
                    to_remove.append(obj2)
                elif obj1.m < obj2.m:
                    to_remove.append(obj1)

    for obj in to_remove:
        if obj in bodies:
            bodies.remove(obj)
        elif obj in spacecrafts:
            spacecrafts.remove(obj)


# BODIES IN SIMULATION
bodies = []
with open("C:/Users/jacks/Documents/Astrodynamics Engine/Sim Presets/earth_system.csv", 'r') as file:
    lines = file.read().splitlines()
    for line in lines:
        x, y, vx, vy, m, r, name, color = line.split(",")
        body = Body(float(x.strip()), float(y.strip()), float(vx.strip()), float(vy.strip()), float(m.strip()), float(r.strip()), name.strip(), color.strip())
        bodies.append(body)

# SPACECRAFT IN SIMULATION
spacecrafts = []
with open("C:/Users/jacks/Documents/Astrodynamics Engine/Sim Presets/spacecraft.csv", 'r') as file:
    lines = file.read().splitlines()
    for line in lines:
        x, y, vx, vy, m, r, name, color = line.split(",")
        spacecraft = Spacecraft(float(x.strip()), float(y.strip()), float(vx.strip()), float(vy.strip()), float(m.strip()), float(r.strip()), name.strip(), color.strip())
        spacecrafts.append(spacecraft)




# PYGAME WINDOW/SETUP
pygame.init()
font = pygame.font.SysFont('None', 14)
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption('Orbital Simulation')
clock = pygame.time.Clock()


# SCREEN POSITIONING/VIEWING 
offset = np.array([screen_width // 2, screen_height // 2])  # center of screen
dragging = False
last_mouse_pos = None
zoom_sensitivity = 1.1  # how fast you zoom in/out
min_scale = 1e-15 # how far you can zoom out
max_scale = 3.5e-4 # how far you can zoom in
running = True
step = 0
startTime = datetime.now()
render_step = 5





mech_e_initial = mech_e_calc()
# SIMULATION LOOP
while running and step < steps:
    # PHYSICS HANDLING
    for body in bodies:
        body.movement_update(bodies)
    for spacecraft in spacecrafts:
        spacecraft.movement_update(bodies)
    collision_handling()
    if step % 1000 == 0:
        energy = mech_e_calc()
        mech_e_diff = energy - mech_e_initial
        mech_e_error = np.abs(mech_e_diff) / np.abs(mech_e_initial) * 100



    # PYGAME HANDLING
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                dragging = True
                last_mouse_pos = np.array(pygame.mouse.get_pos())

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left release
                dragging = False

        if event.type == pygame.MOUSEMOTION and dragging:
            current_mouse_pos = np.array(pygame.mouse.get_pos())
            delta = current_mouse_pos - last_mouse_pos
            offset += delta  # move the camera offset
            last_mouse_pos = current_mouse_pos

        if event.type == pygame.MOUSEWHEEL:
            zoom_point = np.array(pygame.mouse.get_pos())  # where the mouse is pointing during zoom

            # Before scale change: translate screen to world
            world_pos_before = (zoom_point - offset) / scale

            if event.y > 0:  # scroll up = zoom in
                scale *= zoom_sensitivity
            elif event.y < 0:  # scroll down = zoom out
                scale /= zoom_sensitivity

            # Clamp zoom
            scale = max(min(scale, max_scale), min_scale)

            # After scale change: recalculate offset to zoom at mouse point
            offset = zoom_point - world_pos_before * scale

        if step % render_step == 0:
            pygame.display.flip()


    # PYGAME RENDERING
    screen.fill((0, 0, 0))  # black background
    
    # DRAW OBJECTS TO SCREEN
    def draw_object(obj):
        pos = np.array([obj.pos[0], -obj.pos[1]]) * scale + offset
        screen_size = obj.r * scale
        draw_radius = max(2, int(screen_size))
        pygame.draw.circle(screen, pygame.Color(obj.color), pos.astype(int), draw_radius)
        label = font.render(obj.name, True, (255, 255, 255))
        label_pos = pos + np.array([draw_radius + 5, -draw_radius])
        screen.blit(label, label_pos.astype(float))
    for body in bodies:
        draw_object(body)
    for spacecraft in spacecrafts:
        draw_object(spacecraft)


    # DISPLAY SCALE
    width_pixels = screen.get_size()[0]
    zoom_inverse_km = (1 / scale / 1000)
    screen_width_km = width_pixels * zoom_inverse_km
    zoom_text = font.render(f"Width: {screen_width_km:.2f} km", True, (255, 255, 255))
    screen.blit(zoom_text, (10, 10))

    # DISPLAY ENERGY ERROR
    energy_text = font.render(f"Energy error: {mech_e_error:.10f} %", True, (255, 255, 255))
    screen.blit(energy_text, (10, 30))

    # DISPLAY SIM TIME
    simtime = step * dt
    simtime_text = font.render(f"Sim time: {simtime:.2f} secs, {simtime/60/60/24:.2f} days, {simtime/60/60/24/365:.2f} yrs", True, (255, 255, 255))
    screen.blit(simtime_text, (10, 50)) 

    # DISPLAY FPS
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 70))


    pygame.display.flip() # flip y axis to make up positive
    clock.tick(fps_limit) # cap FPS
    step += 1


pygame.quit()
print("Elapsed time: " + str(datetime.now() - startTime))
print("Dts elapsed: " + str(dt*step))

mech_e_final = energy
mech_e_diff = mech_e_final - mech_e_initial
mech_e_error = np.abs(mech_e_diff) / np.abs(mech_e_initial) * 100
print("System energy error = " + str(mech_e_error) + "%")


