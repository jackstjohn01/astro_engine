import pygame
import numpy as np

class PygameRenderer:
    def __init__(self, scale, screen_width=800, screen_height=600):
        pygame.init()
        self.font = pygame.font.SysFont(None, 14)
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        pygame.display.set_caption('Orbital Simulation')
        self.clock = pygame.time.Clock()

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.offset = np.array([screen_width / 2, screen_height / 2], dtype=float)
        self.scale = scale
        self.min_scale = 1e-15
        self.max_scale = 3.5e4
        self.zoom_sensitivity = 1.1

        self.camera_distance = 2e13
        self.tracked_object = None

        # Rotation angles in radians
        self.yaw = np.pi / 4
        self.pitch = np.pi / 6
        self.rotating = False
        self.last_mouse_pos_rot = None

        self.axis_len = self.camera_distance * 4
        self.update_axes()

    def update_axes(self):
        base_len = 1e11  # a reasonable default length in world units
        zoom_factor = 1 / self.scale
        # Clamp axis length between some min and max values depending on zoom
        self.axis_len = np.clip(base_len * zoom_factor, 1e9, 1e13)

        self.axes = {
            'x': (np.array([-self.axis_len, 0, 0]), np.array([self.axis_len, 0, 0]), (200, 80, 80)),
            'y': (np.array([0, -self.axis_len, 0]), np.array([0, self.axis_len, 0]), (80, 200, 80)),
            'z': (np.array([0, 0, -self.axis_len]), np.array([0, 0, self.axis_len]), (80, 80, 200)),
        }


    def handle_events(self, objects):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Right click starts rotation
                    self.rotating = True
                    self.last_mouse_pos_rot = np.array(pygame.mouse.get_pos(), dtype=float)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:
                    self.rotating = False

            elif event.type == pygame.MOUSEMOTION:
                if self.rotating and self.last_mouse_pos_rot is not None:
                    current_pos = np.array(pygame.mouse.get_pos(), dtype=float)
                    delta = current_pos - self.last_mouse_pos_rot
                    sensitivity = 0.005
                    self.yaw += delta[0] * sensitivity
                    self.pitch += delta[1] * sensitivity
                    max_pitch = np.pi/2 - 0.01
                    self.pitch = np.clip(self.pitch, -max_pitch, max_pitch)
                    self.last_mouse_pos_rot = current_pos

            elif event.type == pygame.MOUSEWHEEL:
                # Project origin before zoom
                origin_screen_before = self._project_and_scale(np.zeros(3))
                
                # Update scale with zoom limits
                if event.y > 0:
                    self.scale = min(self.scale * self.zoom_sensitivity, self.max_scale)
                elif event.y < 0:
                    self.scale = max(self.scale / self.zoom_sensitivity, self.min_scale)

                # Project origin after zoom
                origin_screen_after = self._project_and_scale(np.zeros(3))

                # Adjust offset to keep origin fixed under zoom
                if origin_screen_before is not None and origin_screen_after is not None:
                    self.offset += origin_screen_before - origin_screen_after

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self._cycle_tracked_object(objects, -1)
                elif event.key == pygame.K_RIGHT:
                    self._cycle_tracked_object(objects, 1)
                elif event.key == pygame.K_r:
                    self._reset_view()

        return True

    def _cycle_tracked_object(self, objects, direction):
        if not objects:
            self.tracked_object = None
            return
        if self.tracked_object in objects:
            idx = objects.index(self.tracked_object)
            idx = (idx + direction) % len(objects)
        else:
            idx = 0
        self.tracked_object = objects[idx]

    def _reset_view(self):
        self.tracked_object = None
        self.offset = np.array([self.screen_width/2, self.screen_height/2], dtype=float)
        self.yaw = np.pi/4
        self.pitch = np.pi/6

    def rotate_point(self, pos):
        pos = np.array(pos, dtype=float)

        pitch = -self.pitch  # flip pitch for intuitive control

        cos_p = np.cos(pitch)
        sin_p = np.sin(pitch)
        cos_y = np.cos(self.yaw)
        sin_y = np.sin(self.yaw)

        forward = np.array([cos_p*cos_y, cos_p*sin_y, sin_p])
        up = np.array([0, 0, 1])
        right = np.cross(up, forward)
        right /= np.linalg.norm(right) + 1e-15  # avoid divide by zero
        up = np.cross(forward, right)

        rot_matrix = np.column_stack((right, up, forward))
        rotated = rot_matrix.T @ pos
        return rotated

    def project_3d_to_2d(self, pos3d):
        rotated = self.rotate_point(pos3d)
        x, y, z = rotated
        z_cam = z + self.camera_distance

        near_plane = self.camera_distance * 0.001
        if z_cam < near_plane:
            return None

        factor = self.camera_distance / z_cam
        return np.array([x * factor, -y * factor])

    def _project_and_scale(self, pos3d):
        projected = self.project_3d_to_2d(pos3d)
        if projected is None or np.any(np.isnan(projected)) or np.any(np.isinf(projected)):
            return None
        return projected * self.scale + self.offset

    def draw_axes_and_grid(self):
        def nice_number(value):
            if value <= 0:
                return 0
            exponent = np.floor(np.log10(value))
            fraction = value / 10**exponent
            if fraction < 2:
                nice_frac = 1
            elif fraction < 5:
                nice_frac = 2
            else:
                nice_frac = 5
            return nice_frac * 10**exponent

        desired_pixels = 100
        world_size_per_pixel = 1 / self.scale if self.scale != 0 else 1e10
        grid_size = nice_number(desired_pixels * world_size_per_pixel)
        max_lines = 30

        # Draw axes
        for start, end, color in self.axes.values():
            p1 = self._project_and_scale(start)
            p2 = self._project_and_scale(end)
            if p1 is not None and p2 is not None:
                pygame.draw.line(self.screen, color, p1.astype(int), p2.astype(int), 2)

        # Draw XY grid
        for i in range(-max_lines, max_lines + 1):
            start_x = self._project_and_scale(np.array([-grid_size * max_lines, i * grid_size, 0]))
            end_x = self._project_and_scale(np.array([grid_size * max_lines, i * grid_size, 0]))
            start_y = self._project_and_scale(np.array([i * grid_size, -grid_size * max_lines, 0]))
            end_y = self._project_and_scale(np.array([i * grid_size, grid_size * max_lines, 0]))

            if start_x is not None and end_x is not None:
                pygame.draw.line(self.screen, (40, 40, 40), start_x.astype(int), end_x.astype(int), 1)
            if start_y is not None and end_y is not None:
                pygame.draw.line(self.screen, (40, 40, 40), start_y.astype(int), end_y.astype(int), 1)

    def draw(self, objects, step, dt):
        self.screen.fill((0, 0, 0))

        self.draw_axes_and_grid()

        # Center on tracked object if any
        if self.tracked_object is not None:
            obj_proj = self.project_3d_to_2d(self.tracked_object.pos)
            if obj_proj is not None and not np.any(np.isnan(obj_proj)) and not np.any(np.isinf(obj_proj)):
                screen_center = np.array(self.screen.get_size()) / 2
                obj_screen = obj_proj * self.scale + self.offset
                self.offset += screen_center - obj_screen

        def valid_point(p):
            return p is not None and p.shape == (2,) and not np.any(np.isnan(p)) and not np.any(np.isinf(p))

        # Redraw axes on top for clarity
        for start, end, color in self.axes.values():
            p1 = self._project_and_scale(start)
            p2 = self._project_and_scale(end)
            if valid_point(p1) and valid_point(p2):
                pygame.draw.line(self.screen, color, p1.astype(int), p2.astype(int), 2)

        # Draw objects
        for obj in objects:
            self._draw_object(obj, valid_point)

        # Info texts
        width_px = self.screen.get_size()[0]
        km_per_pixel = 1 / self.scale / 1000 if self.scale != 0 else 0
        screen_km = width_px * km_per_pixel
        zoom_text = self.font.render(f"Width: {screen_km:.2f} km", True, (255, 255, 255))

        sim_time = step * dt
        sim_text = self.font.render(
            f"Sim time: {sim_time:.2f} secs, {sim_time/60/60/24:.2f} days, {sim_time/60/60/24/365:.2f} yrs",
            True, (255, 255, 255)
        )

        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))

        self.screen.blit(zoom_text, (10, 10))
        self.screen.blit(sim_text, (10, 50))
        self.screen.blit(fps_text, (10, 70))

        pygame.display.flip()
        self.clock.tick(60)

    def _draw_object(self, obj, valid_point_func):
        proj = self.project_3d_to_2d(obj.pos)
        if not valid_point_func(proj):
            return

        screen_pos = proj * self.scale + self.offset
        radius_px = max(2, int(obj.radius * self.scale))

        pygame.draw.circle(self.screen, pygame.Color(obj.color), screen_pos.astype(int), radius_px)
        label = self.font.render(obj.name, True, (255, 255, 255))
        label_pos = screen_pos + np.array([radius_px + 5, -radius_px])
        self.screen.blit(label, label_pos.astype(int))

    def quit(self):
        pygame.quit()
