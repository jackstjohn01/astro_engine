import math
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt


# CONSTANTS
G = 6.6743E-11
dt = .1
steps = 50000000
# 96000000 steps = apprx 8 hours real time
# 50000000 steps = apprx 58 days sim time


# BODY CLASS
class Body:
    def __init__(self, x, y, vx, vy, m, color): # Body object properties
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([vx, vy], dtype=float)
        self.acc = np.array([0.0, 0.0])
        self.m = m
        self.color = color

# FORCE METHOD
    def force_calc(self, other_bodies): # calculates the total force on a body
        total_force = np.array([0.0, 0.0])

        for other in other_bodies: # iterate through list of bodies
            if other is self:
                continue # skips self in list of bodies

            r_vec = other.pos - self.pos # new array finding difference between other and self positions
            r = np.linalg.norm(r_vec) # normalizing new array to scale total_force later (previously math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2))
            
            if r == 0:
                continue

            force_mag = G * self.m * other.m / r**2
            force_dir = r_vec / r
            force = force_mag * force_dir

            total_force += force

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
bodies = [Earth0, Satellite]





# PLOTTING
plt.ion()  # enables interactive mode
fig, ax = plt.subplots()
ax.set_facecolor('black')  # set background color

# Initial view size based on bodies
positions = np.array([body.pos for body in bodies])
min_pos = np.min(positions, axis=0)
max_pos = np.max(positions, axis=0)
padding = 1e7
ax.set_xlim(min_pos[0] - padding, max_pos[0] + padding)
ax.set_ylim(min_pos[1] - padding, max_pos[1] + padding)

plt.show()

x=0


# MOUSE SCROLLING
def on_scroll(event):
    base_scale = 1.1  # scroll speed
    cur_xlim = ax.get_xlim()
    cur_ylim = ax.get_ylim()

    xdata = event.xdata
    ydata = event.ydata
    if xdata is None or ydata is None:
        return  # outside the axes

    if event.button == 'up':
        scale_factor = 1 / base_scale
    elif event.button == 'down':
        scale_factor = base_scale
    else:
        scale_factor = 1

    new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
    new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

    relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
    rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])

    ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
    ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
    fig.canvas.draw_idle()
fig.canvas.mpl_connect('scroll_event', on_scroll)


startTime = datetime.now()


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
        body.movement_update(bodies)

    # PLOTTING LOOP
    if step % 10 == 0:  # plot every n steps because plotting is slower than computing
        x_vals = [body.pos[0] for body in bodies]
        y_vals = [body.pos[1] for body in bodies]
        colors = [body.color for body in bodies]
        # Subtract 20 from log10(m) to compress the range, then scale
        size = [max((np.log10(body.m) - 20) * 10, 5) for body in bodies]  # 10 is a scaling factor, 5 is min size
        graph = ax.scatter(x_vals, y_vals, c=colors, s=size)
        plt.pause(.001)  # pause to update the plot
        graph.remove()  # remove the previous scatter plot to avoid overplotting


print("Elapsed time: " + str(datetime.now() - startTime))

