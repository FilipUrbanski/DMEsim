import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from util import (R_sphere, R_roller, roller_width, E_star, calculate_max_normal_force_simplified, mu_rubber, calculate_approximate_indentation, 
roller_ang_vel, max_allowed_contact_area, calculate_alpha, wizualizacja_nacisku)

#zmienne globalne
max_indentation = 5e-4
R_eff = (R_sphere * R_roller) / (R_sphere + R_roller)


roller_indentation_depths = {}

beta = 0.0  
angular_speed = 0.0  


max_normal_force, max_friction = calculate_max_normal_force_simplified(E_star, R_sphere, mu_rubber, max_indentation)

def render_text(position, text_string, font_size=20, font_color=(255,255,255)):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text_string, True, font_color, (0, 0, 0))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glWindowPos2d(*position)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    glDisable(GL_BLEND)

#pozycjonowanie etykiet
def render_text_3d(position3d, text_string, font_size=20, font_color=(255,255,255)):
    modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
    projection = glGetDoublev(GL_PROJECTION_MATRIX)
    viewport = glGetIntegerv(GL_VIEWPORT)

    screen_coords = gluProject(position3d[0], position3d[1], position3d[2], modelview, projection, viewport)

    render_text((screen_coords[0], screen_coords[1]), text_string, font_size, font_color)


def load_texture(image_path):
    texture_surface = pygame.image.load(image_path)
    texture_data = pygame.image.tostring(texture_surface, "RGBA", 1)
    width = texture_surface.get_width()
    height = texture_surface.get_height()

    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
    glGenerateMipmap(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, 0)

    return texture



def draw_roller(roller_radius, roller_height, lat, lng, sphere_radius, rotation_angle, texture, normal_force, angular_speed, beta, roller_number):
    glPushMatrix()
    x = sphere_radius * 1.05 * np.cos(lng) * np.sin(lat)
    y = sphere_radius * 1.05 * np.sin(lng) * np.sin(lat)
    z = sphere_radius * 1.05 * np.cos(lat)

    roller_axis_vector = np.array([x, y, z]) - np.array([0, 0, 0])  
    roller_axis_vector /= np.linalg.norm(roller_axis_vector) 

    y_axis_vector = np.array([0, 0, 1])

    dot_product = np.dot(roller_axis_vector, y_axis_vector)
    gamma = np.arccos(dot_product) #obliczani kąta gamma (w pracy prof. Kowalczuka i dr. Tatary kąt beta)

    gamma_degrees = np.degrees(gamma)

    glTranslatef(x, y, z)
    glRotatef(np.degrees(lng), 0, 0, 1) 
    glRotatef(-90, 1, 0, 0)  

    #implementcja rownan opisujacych model
    indentation_depth = calculate_approximate_indentation(normal_force, R_eff, E_star)
    contact_area = max_allowed_contact_area(R_sphere, indentation_depth)
    current_alpha = calculate_alpha(R_sphere, contact_area)

    roller_indentation_depths[roller_number] = indentation_depth

    sphere_ang_vel = angular_speed*180/np.pi
    roller_angular_velocity = roller_ang_vel(R_sphere, R_roller, gamma_degrees, current_alpha, sphere_ang_vel)

    force_label = f"DME {roller_number}: {abs(normal_force):.2f} N, {abs(roller_angular_velocity):.2f} Rad/s"
    label_position = (0 , 0, 0)
    render_text_3d(label_position, force_label) 

    rotation_angle =+ abs(roller_angular_velocity)
    glRotatef(np.degrees(rotation_angle), 0, 0, 1) 

    glBindTexture(GL_TEXTURE_2D, texture)
    glEnable(GL_TEXTURE_2D)
    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)
    gluCylinder(quadric, roller_radius, roller_radius, roller_height, 32, 1)
    glDisable(GL_TEXTURE_2D)
    glPopMatrix()


def create_rollers(radius, roller_radius, roller_height, camera_angle_x, camera_angle_y, rotation_angle, texture):
    glPushMatrix()
    glLoadIdentity()
    gluLookAt(5 * np.sin(np.radians(camera_angle_y)) * np.cos(np.radians(camera_angle_x)),
              5 * np.sin(np.radians(camera_angle_x)),
              5 * np.cos(np.radians(camera_angle_y)) * np.cos(np.radians(camera_angle_x)),
              0, 0, 0, 0, 1, 0)

    lat = np.pi / 2 
    for i in range(8):
        lng = 2 * np.pi * i / 8
        angle_difference = abs(lng - np.radians(beta))
        normal_force = max_normal_force * np.cos(angle_difference)  

        draw_roller(roller_radius, roller_height, lat, lng, radius, rotation_angle, texture, normal_force, angular_speed, beta, i + 1)
    
    glPopMatrix()

#obsługa wywołania grafu wizualizacji nacisku
def handle_roller_press(roller_number, R_roller, roller_width):
    print(f"DME {roller_number} analizowane")
    if roller_number in roller_indentation_depths:
        indentation_depth = roller_indentation_depths[roller_number]
        wizualizacja_nacisku(R_roller, roller_width, indentation_depth, plot_size=(8,6))
    else:
        print(f"Brak danych dla DME {roller_number}")

#oświetlenie sceny
def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightfv(GL_LIGHT0, GL_POSITION, (1, 1, 1, 0))


def create_sphere_dl(radius, lats, longs, texture):
    display_list = glGenLists(1)
    glNewList(display_list, GL_COMPILE)
    glBindTexture(GL_TEXTURE_2D, texture)
    glEnable(GL_TEXTURE_2D)
    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)
    gluSphere(quadric, radius, lats, longs)
    glDisable(GL_TEXTURE_2D)
    glEndList()
    return display_list

def draw_sphere(radius, lats, longs, texture):
    glBindTexture(GL_TEXTURE_2D, texture)
    glEnable(GL_TEXTURE_2D)
    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)
    gluSphere(quadric, radius, lats, longs)
    for i in range(0, lats + 1):
        lat0 = np.pi * (-0.5 + float(i - 1) / lats)
        z0 = np.sin(lat0)
        zr0 = np.cos(lat0)

        lat1 = np.pi * (-0.5 + float(i) / lats)
        z1 = np.sin(lat1)
        zr1 = np.cos(lat1)
    
        glBegin(GL_QUAD_STRIP)
        for j in range(0, longs + 1):
            lng = 2 * np.pi * float(j - 1) / longs
            x = np.cos(lng)
            y = np.sin(lng)

            glNormal3f(x * zr0, y * zr0, z0)
            glVertex3f(x * zr0, y * zr0, z0)
            glNormal3f(x * zr1, y * zr1, z1)
            glVertex3f(x * zr1, y * zr1, z1)
        glEnd()
    glDisable(GL_TEXTURE_2D)

def main():
    global beta, angular_speed  

    pygame.init()
    pygame.font.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glEnable(GL_DEPTH_TEST)
    setup_lighting()
    glMatrixMode(GL_MODELVIEW)

    sphere_texture = load_texture('img/sfera_powierzchnia.jpg')
    roller_texture = load_texture('img/sfera_powierzchnia.jpg')

    sphere_dl = create_sphere_dl(R_sphere, 50, 50, sphere_texture)
    rotation_angle = 0
    camera_angle_x = 0
    camera_angle_y = 0

    clock = pygame.time.Clock()

    dragging = False
    last_mouse_pos = (0, 0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if pygame.K_0 <= event.key <= pygame.K_8:  #Obluga przyciskow do wywolywania wizualizacji styku DME - sfera
                    roller_number = event.key - pygame.K_0
                    handle_roller_press(roller_number, R_roller, roller_width)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging = True
                    last_mouse_pos = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    mouse_pos = pygame.mouse.get_pos()
                    dx = mouse_pos[0] - last_mouse_pos[0]
                    dy = mouse_pos[1] - last_mouse_pos[1]

                    camera_angle_y += dx * 0.1
                    camera_angle_x -= dy * 0.1

                    last_mouse_pos = mouse_pos

        keys = pygame.key.get_pressed() #przyciski odpowiadajace za predkosc sfery oraz jej kierunek obrotu
        if keys[pygame.K_a]:
            beta += 1
        if keys[pygame.K_d]:
            beta -= 1 
        if keys[pygame.K_w]:
            angular_speed += 0.01 
        if keys[pygame.K_s]:
            angular_speed -= 0.01 

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        gluLookAt(5 * np.sin(np.radians(camera_angle_y)) * np.cos(np.radians(camera_angle_x)),
                  5 * np.sin(np.radians(camera_angle_x)),
                  5 * np.cos(np.radians(camera_angle_y)) * np.cos(np.radians(camera_angle_x)),
                  0, 0, 0, 0, 1, 0)

        rotation_angle += angular_speed
        glRotatef(beta, 0, 0, 1)
        glRotatef(rotation_angle, 0, 1, 0) 
        glCallList(sphere_dl)
        glPushMatrix() 
        glCallList(sphere_dl)
        glPopMatrix()  
        glCallList(sphere_dl)

        create_rollers(R_sphere, R_roller, roller_width, camera_angle_x, camera_angle_y, rotation_angle, roller_texture)

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, display[0], 0, display[1])
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        render_text((10, 570), f"Gamma: {beta:.2f} deg")
        render_text((10, 550), f"Angular Speed: {angular_speed:.2f} rad/s")
        glPopMatrix()  
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()  
        glMatrixMode(GL_MODELVIEW)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()