import coolerspace as cs
import sys

path = sys.argv[1]
shape_y = int(sys.argv[2])
shape_x = int(sys.argv[3])

# Inputs
s1 = cs.create_input("scattering1", [shape_y, shape_x], cs.ScatteringSpectrum)
s2 = cs.create_input("scattering2", [shape_y, shape_x], cs.ScatteringSpectrum)

a1 = cs.create_input("absorption1", [shape_y, shape_x], cs.AbsorptionSpectrum)
a2 = cs.create_input("absorption2", [shape_y, shape_x], cs.AbsorptionSpectrum)

d1 = cs.create_input("density1", [shape_y, shape_x, 1], cs.Matrix)
d2 = cs.create_input("density2", [shape_y, shape_x, 1], cs.Matrix)

light = cs.create_input("light", [shape_y, shape_x], cs.LightSpectrum)

# Pigment creation
p1 = cs.Pigment(s1, a1)
p2 = cs.Pigment(s2, a2)

# Mix
mixed = cs.mix(d1, p1, d2, p2)

# Cast to reflectance
reflectance = cs.ReflectanceSpectrum(mixed)

# Reflect lights off pigment reflectance
reflected = cs.LightSpectrum(cs.Matrix(light) * cs.Matrix(reflectance))

# Convert to sRGB
image = cs.sRGB(reflected)

# Compilation
cs.create_output(image)
cs.compile(path)