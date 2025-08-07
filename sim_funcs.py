from object_handling import bodies, spacecrafts
from config import G
import numpy as np


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
    