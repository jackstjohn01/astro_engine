# IMPORTS
import numpy as np
from render import PygameRenderer

# CONSTANTS/SETTINGS
G = 6.6743E-11
scale = 2e-9
dt = .001
steps = 500000000
fps_limit = 0
render_step = 10
mass_threshold = 1e20




# INTEGRATORS
class Integrator:
    def __init__(self, force_calc, dt):
        self.force_calc = force_calc
        self.dt = dt
        self.time = 0.0
        self.steps = 0

    def velocity_verlet(self, objects):
        dt = self.dt

        # 1)
        a0_list = [self.force_calc.accel_calc(o, objects) for o in objects]

        # 2)
        for o, a0 in zip(objects, a0_list):
            o.pos += o.vel * dt + .5 * a0 * dt * dt

        # 3)
        a1_list = [self.force_calc.accel_calc(o, objects) for o in objects]

        # 4)
        for o, acc0, acc in zip(objects, a0_list, a1_list):
            o.vel += .5 * (acc0 + acc) * dt
            o.acc = acc
 
    def euler(self, obj, objects):   # legacy only
        obj.pos += obj.vel * dt
        obj.vel += obj.acc * dt
        obj.acc = self.force_calc.accel_calc(obj, objects)

    def step(self, objects):
        self.velocity_verlet(objects)
        self.steps += 1
        self.time += self.dt

# FORCE
class ForceCalculator:
    def __init__(self, G, mass_threshold):
        self.G = G
        self.mass_threshold = mass_threshold
    
    def gravity_force(self, target_object, other_objects): # calculates the total force on a body
        total_force = np.array([0.0, 0.0, 0.0])

        for other in other_objects: # iterate through list of objects
            if other is target_object:
                continue # skips self in list of objects
            if other.mass < self.mass_threshold:
                continue # skips objects below certain mass

            r_vec = other.pos - target_object.pos # new array finding difference between other and self positions
            r = np.linalg.norm(r_vec) # normalizing new array to scale total_force later (previously math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2))
            
            if r == 0:
                continue            

            force_mag = self.G * target_object.mass * other.mass / r**2
            force_dir = r_vec / r
            force = (force_mag * force_dir)

            total_force += force
    

        return total_force
    
    def accel_calc(self, obj, objects):
        return self.gravity_force(obj, objects) / obj.mass

# CELESTIAL BODY
class CelestialBody:
    def __init__(self, name, color, x, y, z, vx, vy, vz, mass, radius): # Body object properties
        self.pos = np.array([x, y, z], dtype=float)
        self.vel = np.array([vx, vy, vz], dtype=float)
        self.acc = np.array([0.0, 0.0, 0.0])
        self.mass = mass
        self.radius = radius
        self.name = name
        self.color = color
        self.momentum = self.vel * self.mass

# ENVIRONMENT MANAGER
class EnvironmentBuilder:
    def __init__(self):
        self.objects = []
    
    def build_solar_system(self):  # Aug 12 2025
        sun     = CelestialBody("Sun",     "#FFBB00", -614529066.354, -815946659.518, 22627052.3456, 12.7801684586, -2.34188402066, -0.23932935572, 1.98841e+30, 695700000)
        earth   = CelestialBody("Earth",   "#0062FF", 1.1414738e+11, -9.98583366e+10, 28102512.01, 18990.741, 22425.074, -2.810768222, 5.972e+24, 6371000)
        moon    = CelestialBody("Moon",    "#FFFFFF", 1.14516863e+11, -9.99007525e+10, 31151231.42, 19086.972, 23474.89, 92.82801134, 7.34767309e+22, 1737530)
        mercury = CelestialBody("Mercury", "#FF0000", 53230431404.1, -9265716120.34, -5606570719.26, -1864.69260574, 50301.2129353, 4282.88184459, 3.302e+23, 2439400)
        venus   = CelestialBody("Venus",   "#FFE18E", 71166974302.9, 79975639873.6, -3009245430.23, -26276.1537275, 23107.7969704, 1834.1327547, 4.8685e+24, 6051840)
        mars    = CelestialBody("Mars",    "#B6330B", -210830569865, -115691527477, 2770264083.16, 12539.1308396, -19192.0533707, -709.556950214, 6.4171e+23, 3389920)
        jupiter = CelestialBody("Jupiter", "#A6580F", -96148717754.2, 765205750582, -1021965745.02, -13117.3951661, -1007.83462229, 297.659815321, 1.89819e+27, 69911000)
        saturn  = CelestialBody("Saturn",  "#BEA356", 1.4265952e+12, -80480290838.6, -55401015863.7, 9.82542531117, 9622.45369707, -167.160657046, 5.6834e+26, 58232000)
        uranus  = CelestialBody("Uranus",  "#8BFFE6", 1.5496433e+12, 2.472949e+12, -10891473771.4, -5820.82969388, 3298.65019124, 87.5180485606, 8.6813e+25, 25362000)
        neptune = CelestialBody("Neptune", "#0A53C0", 4.4694316e+12, 9728532010.05, -103202940335, -47.1631912158, 5467.16695312, -112.1975635, 1.02409e+26, 24624000)
        pluto   = CelestialBody("Pluto",   "#36007C", 2.8179929e+12, -4.4578989e+12, -338110000562, 4732.21269598, 1699.67007978, -1532.21073632, 1.307e+22, 1188300)
        halley   = CelestialBody("1P/Halley",   "#FF00AA", -2.9284347e+12, 4.098427e+12, -1.481409e+12, 862.702925997, 347.069572537, 178.848657089, 2.2e+14, 9333.3)
        self.objects.extend([sun, mercury, venus, earth, moon, mars, jupiter, saturn, uranus, neptune, pluto, halley])

    def momentum_test(self):
        m1 = CelestialBody("m1", "#FF0000", 0, 0, 0, 0, 0, 0, 10, 1)
        m2 = CelestialBody("m2", "#0000FF", 10, 0, 0, -1, 0, 0, 5, 1)
        self.objects.extend([m1, m2])

# WORLD MANAGER
class World: # "scene manager"
    def __init__(self, integrator, force_calculator, environment_builder):
        self.objects = []
        self.integrator = integrator
        self.force_calculator = force_calculator
        self.environment_builder = environment_builder

    def add_object(self):
        self.environment_builder.momentum_test()
        self.objects = self.environment_builder.objects
    
    # COLLISION HANDLING
    def collision_handling(self):
        to_remove = []

        for i, obj1 in enumerate(self.objects): # pair up objects
            for obj2 in self.objects[i+1:]:
                if obj1 is obj2:
                    continue

                r = np.linalg.norm(obj1.pos - obj2.pos) # detect collision
                if r <= (obj1.radius + obj2.radius):
                    print(f"Collision: {obj1.name} hit {obj2.name}")
                    

                    if obj1.mass > obj2.mass:
                        to_remove.append(obj2)
                        obj1.mass += obj2.mass
                        obj1.momentum += obj2.momentum
                        obj1.vel = obj1.momentum/obj1.mass
                        print(obj1.vel)
                    elif obj1.mass < obj2.mass:
                        to_remove.append(obj1)
                        obj2.mass += obj1.mass
                        obj2.momentum += obj1.momentum
                        obj2.vel = obj2.momentum/obj2.mass
                        print(obj2.vel)

        for obj in to_remove:
            if obj in self.objects:
                self.objects.remove(obj)

    def step(self):
        self.integrator.step(self.objects)
        self.collision_handling()



# INSTANTIATION
environment_builder = EnvironmentBuilder()
force_calculator = ForceCalculator(G=G, mass_threshold=mass_threshold)
integrator = Integrator(dt=dt, force_calc=force_calculator)
world = World(integrator, force_calculator, environment_builder)








# ENERGY
def total_energy(): # takes a "snapshot" of the system's energy when called
    KE = 0.0
    PE = 0.0

    for object in world.objects:
        KE += .5 * object.mass * (np.linalg.norm(object.vel) ** 2)
    for index, obj1 in enumerate(world.objects):
        for obj2 in world.objects[index + 1:]:
            distance = np.linalg.norm(obj1.pos - obj2.pos)
            PE += -(G * obj1.mass * obj2.mass) / distance
    energy = KE + PE
    return energy





renderer = PygameRenderer(scale)


# SIMULATION LOOP
running = True
while running and world.integrator.steps < steps:
    running = renderer.handle_events(world.objects)
    
    if integrator.steps == 0: # things to do once
        world.add_object()
        energy_i = total_energy()
    
    world.step()

    # RENDERING
    if world.integrator.steps % render_step == 0:
        renderer.draw(world.objects, world.integrator.steps, dt)
    
    renderer.clock.tick(fps_limit)

    # OUTPUT
    if world.integrator.steps % 5000 == 0: # do every x steps
        energy_f = total_energy()
        print(f"Energy error: {(np.abs(energy_f-energy_i)/np.abs(energy_i))*100:.2e}% ")

renderer.quit()
energy_f = total_energy()
print(f"Final energy error: {(np.abs(energy_f-energy_i)/np.abs(energy_i))*100:.2e}% ")


