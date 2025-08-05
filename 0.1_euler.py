import math
import datetime
import numpy as np
import matplotlib.pyplot as plt


# CONSTANTS
G = 6.6743E-11
dt = .2
steps = 500000



# BODY CLASS
class Body:
    def __init__(self, x, y, vx, vy, m, color): # Body object properties
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.m = m
        self.ax = 0.0
        self.ay = 0.0
        self.kin_e = 0.0
        self.pot_e = 0.0
        self.mech_e = 0.0
        self.color = color

# FORCE METHOD
    def force_calc(self, other_bodies): # calculates the total force on a body
        fx_total = 0.0
        fy_total = 0.0

        for other in other_bodies: # iterate through list of bodies
            if other is self:
                continue # skips self in list of bodies

            m1 = self.m
            m2 = other.m
            r = math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2)
            if r == 0:
                continue

            dx = (other.x - self.x)
            dy = (other.y - self.y)

            f = ((G * m1 * m2) / r**2)
            fx = f * (dx/r)
            fy = f * (dy/r)

            fx_total += fx
            fy_total += fy
        return fx_total, fy_total


# ACCEL METHOD
    def accel_calc(self, bodies): # updates a body's self.ax and .ay properties
        fx, fy = self.force_calc(bodies)
        self.ax = fx/self.m
        self.ay = fy/self.m

# LOCAL MECHANICAL ENERGY METHOD
    def local_mech_e_calc(self, other_bodies):
        v_total = math.sqrt((self.vx**2)+(self.vy**2))
        self.kin_e = .5 * self.m * (v_total**2)
        self.pot_e = 0
        
        for other in other_bodies: # iterate through list of bodies
            if other is self:
                continue # skips self in list of bodies

            r = math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2)
            if r == 0:
                continue
            pot_e = -(G*self.m*other.m)/r
            self.pot_e += pot_e
        self.mech_e = self.kin_e + self.pot_e
        return self.mech_e


# MOVEMENT METHOD
    def movement_loop(self): # updates a body's movement after accel_calc is called
        self.x = self.vx * dt + self.x
        self.y = self.vy * dt + self.y
        self.vx = self.ax * dt + self.vx
        self.vy = self.ay * dt + self.vy


# MECHANICAL ENERGY
def mech_e_calc():
    total_kin = sum(.5* b.m * (b.vx**2 + b.vy**2) for b in bodies)
    total_pot = 0.0

    # CALCULATE POT_E FOR EACH PAIR OF OBJECTS UNIQUELY (NO DUPLICATING)
    for i, b1 in enumerate(bodies):
        for j in range(i+1, len(bodies)):
            b2 = bodies[j]
            r = math.sqrt((b1.x - b2.x)**2 + (b1.y - b2.y)**2)
            if r == 0:
                continue
            total_pot += -G * b1.m * b2.m / r

    return total_kin + total_pot 



# x, y, vx, vy, m, color
# local earth
Satellite = Body(6778100, 0, 0, 7660, 400000, color='green')
Earth0 = Body(0, 0, 0, 0, 5.97219E+24, color='blue')
Asteroid = Body(0, 6.371e6 + 5.0e6, 3000, 0, 1.0e10, color='red')

# 3 body simulation example
Object1 = Body(0.0, 0.0, 0.0, 1000, 5e21, 'blue')              
Object2 = Body(0, 1.5e6, -1000, 0, 5e21, 'red')             
Object3 = Body(0, -1.5e6, -2000, 0, 8e22, 'green')   

# solar system
Sun = Body(0, 0, 0, 0, 1.989e30, '#f2831f')  # Sun
Mercury = Body(5.791e10, 0, 0, 47870, 3.30104e23, "#ff0000") # Mercury
Venus = Body(1.082e11, 0, 0, 35020, 4.867e24, '#e2c2a5') # Venus
Earth1 = Body(1.496e11, 0, 0, 29780, 5.972e24, '#3399ff')  # Earth
Moon = Body(1.496e11 + 3.844e8, 0, 0, 29780 + 1022, 7.34767309e22, '#cccccc')  # Moon
Mars = Body(2.279e11, 0, 0, 24077, 6.4171e23, '#f27c5f')  # Mars
Jupiter = Body(7.785e11, 0, 0, 13070, 1.8982e27, "#e85e30")  # Jupiter
Saturn = Body(1.429e12, 0, 0, 9690, 5.6834e26, '#f27c5f')  # Saturn
Uranus = Body(2.871e12, 0, 0, 6810, 8.6810e25, '#95bbbe')  # Uranus
Neptune = Body(4.495e12, 0, 0, 5430, 1.02413e26, '#647ba5')  # Neptune
Pluto = Body(5.906e12, 0, 0, 4700, 1.303e22, "#53035a")  # Pluto

# BODIES IN SIMULATION
bodies = [Object1, Object2, Object3]





# PLOTTING
plt.ion()  # enables interactive mode

plt.xlim(-6778100, 6778100)
plt.ylim(-6778100, 6778100)
plt.gca().set_facecolor('black')  # Set background color
plt.show()

x=0

# RUN LOOP
for step in range(steps):
    # ENERGY CONSERVATION
    print(mech_e_calc())
    if step == 0:
        mech_e_initial = mech_e_calc()
    if step == steps - 1:
        mech_e_final = mech_e_calc()
        mech_e_diff = mech_e_final - mech_e_initial
        mech_e_error = np.abs(mech_e_diff)/np.abs(mech_e_initial) * 100
        print("System energy error = " + str(mech_e_error) + "%")

    # PHYSICS LOOP
    for body in bodies:
        body.accel_calc(bodies)
    for body in bodies:
        body.movement_loop()

    # PLOTTING LOOP
    if step % 100 == 0:  # plot every n steps because plotting is slower than computing
        x_vals = [body.x for body in bodies]
        y_vals = [body.y for body in bodies]
        colors = [body.color for body in bodies]
        # Subtract 20 from log10(m) to compress the range, then scale
        size = [max((np.log10(body.m) - 20) * 10, 5) for body in bodies]  # 10 is a scaling factor, 5 is min size
        graph = plt.scatter(x_vals, y_vals, c=colors, s=size)
        plt.pause(.001)  # pause to update the plot
        graph.remove()  # remove the previous scatter plot to avoid overplotting




