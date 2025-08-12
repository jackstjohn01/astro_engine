# IMPORTS
import numpy as np
from render import PygameRenderer

# CONSTANTS/SETTINGS
G = 6.6743E-11
scale = 2e-9
dt = 100
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

# ENVIRONMENT MANAGER
class EnvironmentBuilder:
    def __init__(self):
        self.objects = []
    
    def build_solar_system(self):
        sun     = CelestialBody("Sun",     "#FFBB00", -614529066.354, -815946659.518, 12.7801684586, -2.34188402066, 1.98841e+30, 695700000)
        earth   = CelestialBody("Earth",   "#0000FF", 1.1414738e+11, -9.98583366e+10, 18990.741, 22425.074, 5.972e+24, 6371000)
        moon    = CelestialBody("Moon",    "#FFFFFF", 1.14516863e+11, -9.99007525e+10, 19086.972, 23474.89, 7.34767309e+22, 1737530)
        #mercury = CelestialBody("Mercury", "#4D2323", 3.155344199074432e+10, -5.693882536298677e+10, 3.286977437475324e+04, 2.602455558070761e+04, 3.302e+23, 2439400)
        #venus   = CelestialBody("Venus",   "#FFE18E", 9.734550332424313e+10, 4.743339899870563e+10, -1.545339281356930e+04, 3.132956163213875e+04, 4.8685e+24, 6051840)
       # mars    = CelestialBody("Mars",    "#B6330B", -2.238631954292564e+11, -9.091456886987776e+10, 1.002296479269221e+04, -2.037721994728289e+04, 6.4171e+23, 3389920)
        #jupiter = CelestialBody("Jupiter", "#A35308", -7.963414575382397e+10, 7.670754963765473e+11, -1.316050304962360e+04, -738.1110975861913, 1.89819e+27, 69911000)
       # saturn  = CelestialBody("Saturn",  "#BEA356", 1.427166571167729e+12, -9.130546181177369e+10, 76.11714419847609, 9620.882176202878, 5.6834e+26, 58232000)
      #  uranus  = CelestialBody("Uranus",  "#CDFFF4", 1.557307946542705e+12, 2.469762230835388e+12, -5823.196753297577, 3317.194211276365, 8.6813e+25, 25362000)
       # neptune = CelestialBody("Neptune", "#0A53C0", 4.470114269169979e+12, 3.927923557755202e+09, -52.30520831625361, 5470.802134455399, 1.02409e+26, 24624000)
      #  pluto   = CelestialBody("Pluto",   "#36007C", 2.812885215178998e+12, -4.459136259323923e+12, 4716.599497405087, 1678.836827667972, 1.307e+22, 1188300)
        self.objects.extend([sun, earth, moon])

# WORLD MANAGER
class World: # "scene manager"
    def __init__(self, integrator, force_calculator, environment_builder):
        self.objects = []
        self.integrator = integrator
        self.force_calculator = force_calculator
        self.environment_builder = environment_builder

    def add_object(self):
        self.environment_builder.build_solar_system()
        self.objects = self.environment_builder.objects
    
    # COLLISION HANDLING
    def collision_handling(self):
        to_remove = []
        for i, obj1 in enumerate(self.objects):
            for obj2 in self.objects[i+1:]:
                if obj1 is obj2:
                    continue
                r = np.linalg.norm(obj1.pos - obj2.pos)
                if r <= (obj1.radius + obj2.radius):
                    print(f"Collision: {obj1.name} hit {obj2.name}")
                    if obj1.mass > obj2.mass:
                        to_remove.append(obj2)
                    elif obj1.mass < obj2.mass:
                        to_remove.append(obj1)

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
while renderer.handle_events() and world.integrator.steps < steps:
    if integrator.steps == 0:
        world.add_object()
    world.step()

    # RENDERING
    if world.integrator.steps % render_step == 0:
        renderer.draw(world.objects, world.integrator.steps, dt)
    renderer.clock.tick(fps_limit)

    # OUTPUT
    if world.integrator.steps % 10000 == 0:
        energy = total_energy()
        print(f"Energy: {energy:.2e} J")

renderer.quit()



