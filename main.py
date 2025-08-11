# IMPORTS
from datetime import datetime
import numpy as np

from config import dt, steps, fps_limit, render_step, g0
from object_handling import bodies, spacecrafts
from render import PygameRenderer
from sim_funcs import mech_e_calc, collision_handling



# SETUP
renderer = PygameRenderer()
mech_e_initial = mech_e_calc()
step = 0


# SIMULATION LOOP
while renderer.handle_events() and step < steps:
    elapsed_simtime = dt * step

    # PHYSICS HANDLING
    for body in bodies:
        body.movement_update(bodies)
    for spacecraft in spacecrafts:
        spacecraft.movement_update(bodies, dt)
        if step % 10:
            print(spacecraft.vel)

    collision_handling()


    '''if step % 1000 == 0:
        energy = mech_e_calc()
        mech_e_diff = energy - mech_e_initial
        mech_e_error = np.abs(mech_e_diff) / np.abs(mech_e_initial) * 100'''

    # RENDERING
    if step % render_step == 0:
        renderer.draw(bodies, spacecrafts, step, dt)
    step += 1
    renderer.clock.tick(fps_limit)
renderer.quit()


elapsed_simtime = dt * step
# OUTPUTS
if elapsed_simtime < 60:
    print(f"Simtime elapsed (s): {elapsed_simtime:.2f}")
elif elapsed_simtime < 3600:
    minutes = elapsed_simtime / 60
    print(f"Simtime elapsed (min): {minutes:.2f}")
elif elapsed_simtime < 86400:
    hours = elapsed_simtime / 3600
    print(f"Simtime elapsed (hr): {hours:.2f}")
else:
    days = elapsed_simtime / 86400
    print(f"Simtime elapsed (day): {days:.2f}")



