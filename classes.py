import numpy as np
from config import G, dt



# BODY CLASS
class Body:
    def __init__(self, name, color, x, y, vx, vy, mass, radius): # Body object properties
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([vx, vy], dtype=float)
        self.acc = np.array([0.0, 0.0])
        self.m = mass
        self.r = radius
        self.name = name
        self.color = color

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
            force = (force_mag * force_dir)

            total_force += force

        return total_force

# POSITION UPDATING
    def movement_update(self, bodies):
        acc_old = self.force_calc(bodies) / self.m
        self.pos += self.vel * dt + .5 * acc_old * dt**2
        acc_new = self.force_calc(bodies) / self.m
        self.acc = acc_new
        self.vel += .5 * (acc_old + acc_new) * dt