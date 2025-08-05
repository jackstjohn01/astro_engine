import numpy as np

np.random.seed(42)  # For reproducibility

num_asteroids = 600

# Constants
G = 6.6743e-11  # gravitational constant
M_sun = 1.989e30  # mass of the Sun

# Asteroid belt roughly between 2.1 AU and 3.4 AU
AU = 1.496e11  # meters
r_min = 2.1 * AU
r_max = 3.4 * AU

lines = []
lines.append("x,y,vx,vy,mass,radius,name,color")

for i in range(1, num_asteroids + 1):
    # Random distance in asteroid belt
    r = np.random.uniform(r_min, r_max)
    
    # Random angle for position in radians (0 to 2pi)
    theta = np.random.uniform(0, 2*np.pi)
    
    # Cartesian coordinates
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    
    # Circular orbit velocity magnitude: v = sqrt(G*M_sun/r)
    v_mag = np.sqrt(G * M_sun / r)
    
    # Velocity direction perpendicular to radius vector for circular orbit
    vx = -v_mag * np.sin(theta)
    vy = v_mag * np.cos(theta)
    
    # Mass between 1e15 to 5e16 kg
    mass = np.random.uniform(1e15, 5e16)
    
    # Radius between 1 km to 5 km (in meters)
    radius = np.random.uniform(1e3, 5e3)
    
    # Name and color (gray shades)
    name = f"Asteroid {i}"
    gray_level = np.random.randint(80, 160)
    hex_color = f"#{gray_level:02x}{gray_level:02x}{gray_level:02x}"
    
    line = f"{x},{y},{vx},{vy},{mass},{radius},{name},{hex_color}"
    lines.append(line)

csv_output = "\n".join(lines)
print(csv_output)