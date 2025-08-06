from classes import Body, Spacecraft

# BODIES IN SIMULATION
bodies = []
with open("C:/Users/jacks/Documents/Astrodynamics Engine/Sim Presets/earth_system.csv", 'r') as file:
    lines = file.read().splitlines()
    for line in lines:
        x, y, vx, vy, m, r, name, color = line.split(",")
        body = Body(float(x.strip()), float(y.strip()), float(vx.strip()), float(vy.strip()), float(m.strip()), float(r.strip()), name.strip(), color.strip())
        bodies.append(body)

# SPACECRAFT IN SIMULATION
spacecrafts = []
with open("C:/Users/jacks/Documents/Astrodynamics Engine/Sim Presets/spacecraft.csv", 'r') as file:
    lines = file.read().splitlines()
    for line in lines:
        x, y, vx, vy, m, r, name, color = line.split(",")
        spacecraft = Spacecraft(float(x.strip()), float(y.strip()), float(vx.strip()), float(vy.strip()), float(m.strip()), float(r.strip()), name.strip(), color.strip())
        spacecrafts.append(spacecraft)