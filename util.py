import numpy as np

# Stałe i właściwości materiałów 
R_sphere = 1.52 
R_roller = 0.152 
roller_width = 0.072  
sphere_mass = 200  
g = 9.81 
mu_rubber = 0.8 
E_rubber = 75e6 
nu_rubber = 0.3  
max_indentation = 5e-4
E_star = E_rubber / (1 - nu_rubber ** 2)  

#wzor (4.5)
def calculate_alpha(R_sphere, contact_area):
    return 2*np.arccos(contact_area/(2*np.pi*R_sphere**2)-1)

#wzor 2.1
def roller_ang_vel(sphere_radius, roller_radius, beta, alpha,  sphere_angular_velocity):
    numerator = -sphere_angular_velocity * (np.cos(beta + alpha) - np.cos(beta - alpha))
    denominator = (roller_radius / sphere_radius + np.cos(alpha)) * 2 * alpha - 2 * np.sin(alpha)
    return numerator / denominator

#wzor (4.1)
def max_allowed_contact_area(R_sphere, max_indentation):
    max_area = 2*np.pi*R_sphere*max_indentation
    return max_area

#sprawdzenie maksymalnego dozwolonego nacisku
def max_allowable_pressure(youngs_modulus, max_indentation):
    return youngs_modulus * max_indentation

#wzory (4.4)
def calculate_max_normal_force_simplified(E, R_sphere, mu, max_indentation):
    area_contact = max_allowed_contact_area(R_sphere, max_indentation)
    max_pressure = max_allowable_pressure(E, max_indentation)
    normal_force = max_pressure * area_contact
    max_friction = mu * normal_force
    return normal_force, max_friction

#wzor (3.3)
def calculate_approximate_indentation(F, R_eff, E_star):
    delta = ((9 * F ** 2) / (16 * R_eff ** 2 * E_star ** 2)) ** (1 / 3) 
    return delta
    

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

def wizualizacja_nacisku(R_roller, roller_width, max_indentation, plot_size=(8, 6)):
    theta = np.linspace(0, 2 * np.pi, 200)
    z = np.linspace(-roller_width / 2, roller_width / 2, 100)
    Theta, Z = np.meshgrid(theta, z)

    X = R_roller * np.cos(Theta)
    Y = R_roller * np.sin(Theta)

    x2d = np.linspace(-R_roller*2, R_roller*2, 100)
    y2d = np.linspace(-roller_width / 2, roller_width / 2, 100)
    X2d, Y2d = np.meshgrid(x2d, y2d)
    wgl_2d = max_indentation - (X2d**2 + Y2d**2) / (2 * R_roller)
    wgl_2d[wgl_2d < 0] = 0

    Indentation_mapped = np.zeros_like(Z)
    for i in range(wgl_2d.shape[1]):
        Indentation_mapped[:, i] = np.interp(Z[:, i], y2d, wgl_2d[:, i])

    X -= Indentation_mapped * np.cos(Theta)
    Y -= Indentation_mapped * np.sin(Theta)

    fig = plt.figure(figsize=plot_size)
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, facecolors=plt.cm.viridis(Indentation_mapped / max_indentation), rstride=1, cstride=1)

    #skalowanie osi
    max_range = np.array([X.max()-X.min(), Y.max()-Y.min(), Z.max()-Z.min()]).max() / 2.0
    mid_x = (X.max()+X.min()) * 0.5
    mid_y = (Y.max()+Y.min()) * 0.5
    mid_z = (Z.max()+Z.min()) * 0.5
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

    ax.set_xlabel('Oś X(m)')
    ax.set_ylabel('Oś Y(m)')
    ax.set_zlabel('Oś Z(m)')
    ax.set_title('Pole styku sfery z DME')
    plt.show()


#wizualizacja_nacisku(R_roller=0.152, roller_width=0.072, max_indentation=5e-3)


