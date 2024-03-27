import numpy as np
import scipy as sp
import sympy as smp
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.integrate import quad
from scipy.integrate import cumulative_trapezoid

# Define the range for angular velocity
sphere_ang_vel = np.linspace(0, 10, 100)    # From 0 to 10 rad/s
alfa = 9                                    # Angular half-width of the roll
beta = 1                                   # Working angle 
applied_force = 20                          # Force excerted by sphere onto the roller 

# Fixed Geometrical Dimensions
R_sphere = 30  # Radius of the sphere in units (30 units)
R_roller = 3   # Radius of the roller in units (3 units)

# modulus of elasticity (E_rubber), Poisson's ratio (nu_rubber), coefficient of friction (mu), wear coefficient (k_wear), and hardness.
rubber_types = {
    "Naturalna": (0.05, 0.5, 0.65, 5e-7, 60),
    "Nitryl": (0.05, 0.49, 0.5, 1e-6, 65),
    "Silikon": (0.03, 0.495, 0.45, 5e-7, 55),
    "EPDM": (0.05, 0.5, 0.6, 7.5e-7, 60),
    "Butyl": (0.05, 0.5, 0.6, 5e-7, 65)
}

#roller angular velocity function; based on (6) in Sphere Drive and Control System for Haptic Interaction with Physical, Virtual and Augmented Reality
def roller_ang_vel(sphere_radius, roller_radius, beta, alpha, sphere_angular_velocity):
    numerator = -sphere_angular_velocity*(np.cos(beta+alpha) - np.cos(beta - alpha))
    denominator = (roller_radius/sphere_radius + np.cos(alpha))*2*alpha - 2*np.sin(alpha)
    return numerator/denominator

wr = roller_ang_vel(R_sphere, R_roller, beta, alfa, 3) 
print(wr)

def roller_wear(sphere_ang_vel, time, R_sphere, R_roller, alpha, beta, rubber_type):
    k_wear, hardness = rubber_types[rubber_type][3], rubber_types[rubber_type][4]
    wr = roller_ang_vel(R_sphere, R_roller, beta, alpha, sphere_ang_vel)

    def sliding_distance(t):
        vsphere = R_sphere * sphere_ang_vel  # Linear velocity of the sphere
        vroller = R_roller * wr              # Linear velocity of the roller
        return abs(vsphere - vroller)

    total_sliding_distance, _ = quad(sliding_distance, 0, time)

    wear_volume = k_wear * applied_force * total_sliding_distance / hardness
    return wear_volume
 

def plot_wear_comparison_fixed(max_time, max_ang_vel, R_sphere, R_roller, alpha, beta):
    times = np.linspace(0, max_time, 50)
    ang_velocities = np.linspace(0, max_ang_vel, 50)
    T, V = np.meshgrid(times, ang_velocities)

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')

    plot_surfaces = {}

    for rubber_type, color in zip(rubber_types.keys(), ['blue', 'green', 'red', 'cyan', 'magenta']):
        Wear = np.array([roller_wear(v, t, R_sphere, R_roller, alpha, beta, rubber_type) 
                         for v, t in zip(np.ravel(V), np.ravel(T))])
        Wear = Wear.reshape(T.shape)
        plot_surfaces[rubber_type] = ax.plot_surface(T, V, Wear, color=color, alpha=0.5)

    ax.set_xlabel('Czas (s)')
    ax.set_ylabel('Prędkość kątowa sfery(rad/s)')
    ax.set_zlabel('Ilość zużytego materiału (mm^3)')
    ax.set_title('Zużycie materiału w zależności od prędkości i czasu')

    legend_elements = [plt.Line2D([0], [0], color=color, lw=4, label=rubber_type) for rubber_type, color in zip(rubber_types.keys(), ['blue', 'green', 'red', 'cyan', 'magenta'])]
    ax.legend(handles=legend_elements)

    plt.show()

plot_wear_comparison_fixed(20, 10, R_sphere, R_roller, alfa, beta)