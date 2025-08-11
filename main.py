# IMPORTS
import numpy as np
from render import PygameRenderer

# CONSTANTS/SETTINGS
G = 6.6743E-11
scale = 1e-5
dt = .1
steps = 50000000
fps_limit = 0
render_step = 50


# ===================================================================

# BODY CLASS
class Body:
    def __init__(self, name, color, x, y, vx, vy, mass, radius): # Body object properties
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([vx, vy], dtype=float)
        self.acc = np.array([0.0, 0.0])
        self.mass = mass
        self.radius = radius
        self.name = name
        self.color = color

# FORCE METHOD
    def force_calc(self, other_bodies): # calculates the total force on a body
        total_force = np.array([0.0, 0.0])

        for other in other_bodies: # iterate through list of bodies
            if other is self:
                continue # skips self in list of bodies
            if other.mass < 1e20:
                continue # skips objects below certain mass

            r_vec = other.pos - self.pos # new array finding difference between other and self positions
            r = np.linalg.norm(r_vec) # normalizing new array to scale total_force later (previously math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2))
            
            if r == 0:
                continue            

            force_mag = G * self.mass * other.mass / r**2
            force_dir = r_vec / r
            force = (force_mag * force_dir)

            total_force += force

        return total_force

# POSITION UPDATING
    def movement_update(self, bodies):
        acc_old = self.force_calc(bodies) / self.mass
        self.pos += self.vel * dt + .5 * acc_old * dt**2
        acc_new = self.force_calc(bodies) / self.mass
        self.acc = acc_new
        self.vel += .5 * (acc_old + acc_new) * dt


# INSTANTIATION
Earth = Body("Earth", '#0000FF', 0, 0, 0, 0, 5.972e+24, 6371000)
Moon = Body("Moon", "#FFFFFF", 384400000, 0, 0, 1023, 7.34767309e+22, 1.74e+6)

bodies = [Earth, Moon]


# ===================================================================


# COLLISION HANDLING
def collision_handling():
    to_remove = []

    all_objects = bodies
    for i, obj1 in enumerate(all_objects):
        for obj2 in all_objects[i+1:]:
            if obj1 is obj2:
                continue
            r = np.linalg.norm(obj1.pos - obj2.pos)
            if r <= (obj1.radius + obj2.radius):
                print(f"Collision: {obj1.name} hit {obj2.name}")
                if obj1.m > obj2.m:
                    to_remove.append(obj2)
                elif obj1.m < obj2.m:
                    to_remove.append(obj1)

    for obj in to_remove:
        if obj in bodies:
            bodies.remove(obj)



# ===================================================================


# SETUP
renderer = PygameRenderer(scale)
step = 0


# SIMULATION LOOP
while renderer.handle_events() and step < steps:

    # PHYSICS HANDLING
    for body in bodies:
        body.movement_update(bodies)

    collision_handling()

    # RENDERING
    if step % render_step == 0:
        renderer.draw(bodies, step, dt)
    step += 1
    renderer.clock.tick(fps_limit)
renderer.quit()



