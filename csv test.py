import numpy as np
import csv


# BODY CLASS
class Body:
    def __init__(self, x, y, vx, vy, m, radius, name, color): # Body object properties
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([vx, vy], dtype=float)
        self.acc = np.array([0.0, 0.0])
        self.m = m
        self.radius = radius
        self.name = name
        self.color = color

        def __repr__(self):
         return f"Body(name={self.name}, x={self.x}, y={self.y}, vx={self.vx}, vy={self.vy}, m={self.m}, radius={self.radius}, color={self.color})"


# FORCE METHOD
    def force_calc(self, other_bodies): # calculates the total force on a body
        total_force = np.array([0.0, 0.0])

        for other in other_bodies: # iterate through list of bodies
            if other is self:
                continue # skips self in list of bodies
            if other.m < 1e20:
                continue

            r_vec = other.pos - self.pos # new array finding difference between other and self positions
            r = np.linalg.norm(r_vec) # normalizing new array to scale total_force later (previously math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2))
            
            if r == 0:
                continue


            force_mag = G * self.m * other.m / r**2
            force_dir = r_vec / r
            force = force_mag * force_dir

            total_force += force

            if r <= other.radius:
                print("Collision")
                bodies.remove(self)
                del self

        return total_force

# LOCAL MECHANICAL ENERGY METHOD
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
    def __init__(self, x, y, vx, vy, m, radius, name, color): # Body object properties
        super().__init__(x, y, vx, vy, m, radius, name, color)
    def burn(self):
        if step == trigger_stepA:
            self.vel += burn_conditionA