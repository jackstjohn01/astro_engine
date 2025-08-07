# IMPORTS
from datetime import datetime
import numpy as np

from config import dt, steps, fps_limit, render_step
from object_handling import bodies, spacecrafts
from render import PygameRenderer
from sim_funcs import mech_e_calc, collision_handling



# SETUP
renderer = PygameRenderer()
mech_e_initial = mech_e_calc()
step = 0
startTime = datetime.now()


# SIMULATION LOOP
while renderer.handle_events() and step < steps:

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

    # RENDERING
    if step % render_step == 0:
        renderer.draw(bodies, spacecrafts, step, dt, mech_e_error)
    step += 1
    renderer.clock.tick(fps_limit)
renderer.quit()



# OUTPUTS
print("Elapsed time: " + str(datetime.now() - startTime))
print("Dts elapsed: " + str(dt*step))

mech_e_final = energy
mech_e_diff = mech_e_final - mech_e_initial
mech_e_error = np.abs(mech_e_diff) / np.abs(mech_e_initial) * 100
print("System energy error = " + str(mech_e_error) + "%")


