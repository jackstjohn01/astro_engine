# IMPORTS
import numpy as np

from config import dt, steps, fps_limit, render_step
from objects import bodies
from render import PygameRenderer





# COLLISION HANDLING
def collision_handling():
    to_remove = []

    all_objects = bodies
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



# SETUP
renderer = PygameRenderer()
step = 0


# SIMULATION LOOP
while renderer.handle_events() and step < steps:
    elapsed_simtime = dt * step

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



