import numpy as np
from config import G, dt, g0



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
            force = (force_mag * force_dir)

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
class Spacecraft():
    def __init__(self, name, color, x, y, vx, vy, m, m_p, r, Isp, thrust): # Body object properties
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([vx, vy], dtype=float)
        self.acc = np.array([0.0, 0.0])
        self.m = m
        self.m_p = m_p
        self.total_mass = m + m_p
        self.r = r
        self.name = name
        self.color = color
        self.Isp = Isp
        self.thrust = thrust
# FORCE METHOD
    def gravity_force(self, other_bodies): # calculates the total force on a body
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
            force_mag = G * self.total_mass * other.m / r**2
            force_dir = r_vec / r
            force = (force_mag * force_dir)

            total_force += force
        return total_force
    
    def thrust_force(self, elapsed_simtime):
        thrust_vec = np.array([0.0,0.0])
        mdot = 0
        thrust = self.thrust
        Isp = self.Isp
        m = self.m # dry mass
        m_p = self.m_p # propellant mass
        m0 = m + m_p

        for burn in self.burns:
            burn_start = burn[0]
            dvx = burn[1]
            dvy = burn[2]

            dv_vec = np.array([dvx, dvy])
            dv_mag = np.linalg.norm(dv_vec)
            dir = dv_vec/dv_mag
            
            v_e = Isp * g0
            mf = m0 * np.exp(-dv_mag / v_e)
            m_fuel = m0 - mf
            mdot = thrust/v_e
            t_burn = m_fuel/mdot
            burn_end = burn_start + t_burn

            if burn_start <= elapsed_simtime < burn_end:
                thrust_vec = thrust * dir
                break
        return thrust_vec, mdot



# POSITION UPDATING
    def movement_update(self, bodies, elapsed_simtime):
        gravity_force = self.gravity_force(bodies)
        thrust_force, mdot = self.thrust_force(elapsed_simtime)

        self.total_mass = self.m + self.m_p
        acc_old = (gravity_force + thrust_force) / self.total_mass

        self.pos += self.vel * dt + .5 * acc_old * dt**2

        gravity_force = self.gravity_force(bodies)
        thrust_force, _ = self.thrust_force(elapsed_simtime)
        acc_new = (gravity_force + thrust_force) / self.total_mass

        self.acc = acc_new
        self.vel += .5 * (acc_old + acc_new) * dt

        self.m_p = self.m_p - mdot * dt
        self.total_mass = self.m_p + self.m

        print(self.pos)

        
