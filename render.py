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
        self.relative_orientation = False  # Track if relative orientation is active

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
                    self.relative_orientation = False  # Reset relative orientation
                elif event.key == pygame.K_o:
                    # Orient camera relative to tracked object
                    if self.tracked_object is not None:
                        self._orient_relative_to_tracked()
                        self.relative_orientation = True
                elif event.key == pygame.K_p:
                    # Reset orientation to default
                    self.yaw = np.pi / 4
                    self.pitch = np.pi / 6
                    self.relative_orientation = False

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

    def _orient_relative_to_tracked(self):
        # Orient camera to look "down" the Z axis relative to tracked object
        self.pitch = -np.pi / 2
        self.yaw = 0

        if self.tracked_object is not None:
            # Project tracked object's position *without* offset and scale
            projected = self.project_3d_to_2d(self.tracked_object.pos)
            if projected is not None:
                # Set offset so that projected point maps exactly to screen center
                self.offset = np.array([self.screen_width / 2, self.screen_height / 2]) - projected * self.scale

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
        # Update axes length based on current scale
        self.update_axes()

        # Draw axes (X, Y, Z) lines only
        for start, end, color in self.axes.values():
            p1 = self._project_and_scale(start)
            p2 = self._project_and_scale(end)
            if p1 is not None and p2 is not None:
                pygame.draw.line(self.screen, color, p1.astype(int), p2.astype(int), 2)

    def draw_xy_plane(self):
        # Smaller size for XY plane (e.g., 1/4 of axis_len)
        plane_size = self.axis_len * 0.001

        corners_3d = [
            np.array([-plane_size, -plane_size, 0]),
            np.array([-plane_size,  plane_size, 0]),
            np.array([ plane_size,  plane_size, 0]),
            np.array([ plane_size, -plane_size, 0]),
        ]

        corners_2d = [self._project_and_scale(c) for c in corners_3d]

        if any(c is None for c in corners_2d):
            return

        points = [c.astype(int) for c in corners_2d]

        plane_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)

        # Gray color with low alpha for subtlety (e.g., 50 out of 255)
        gray_color = (150, 150, 150, 50)

        pygame.draw.polygon(plane_surface, gray_color, points)
        self.screen.blit(plane_surface, (0, 0))

    def draw_object(self, obj, valid_point_func, drawn_positions, drawn_labels):
        proj = self.project_3d_to_2d(obj.pos)
        if not valid_point_func(proj):
            return

        screen_pos = proj * self.scale + self.offset
        radius_px = max(2, int(obj.radius * self.scale))

        # Always draw the object circle (never skip)
        pygame.draw.circle(self.screen, pygame.Color(obj.color), screen_pos.astype(int), radius_px)
        drawn_positions.append(screen_pos)  # optional: keep if you want for future use

        # Draw label with shifting to avoid label-to-label overlap only
        label = self.font.render(obj.name, True, (255, 255, 255))
        label_rect = label.get_rect()

        # Start label position near the object circle
        base_label_pos = screen_pos + np.array([radius_px + 5, -radius_px])
        label_rect.topleft = base_label_pos.astype(int)

        shift_step = 2  # pixels to shift down on overlap

        # Shift label down until it doesn't collide with any other label
        while any(label_rect.colliderect(other_rect) for other_rect in drawn_labels):
            label_rect.move_ip(0, shift_step)

        # Draw label and add its rect for future collision checks
        self.screen.blit(label, label_rect.topleft)
        drawn_labels.append(label_rect)

    def draw(self, objects, step, dt):
        self.screen.fill((0, 0, 0))
        self.draw_xy_plane()
        self.draw_axes_and_grid()

        if self.tracked_object is not None:
            tracked_screen_pos = self._project_and_scale(self.tracked_object.pos)
            if tracked_screen_pos is not None:
                center_screen = np.array([self.screen_width / 2, self.screen_height / 2])
                self.offset += center_screen - tracked_screen_pos



        # Removed centering on tracked object so grid stays centered on origin

        def valid_point(p):
            return p is not None and p.shape == (2,) and not np.any(np.isnan(p)) and not np.any(np.isinf(p))

        # Redraw axes on top for clarity
        for start, end, color in self.axes.values():
            p1 = self._project_and_scale(start)
            p2 = self._project_and_scale(end)
            if valid_point(p1) and valid_point(p2):
                pygame.draw.line(self.screen, color, p1.astype(int), p2.astype(int), 2)

        drawn_positions = []
        drawn_labels = []

        for obj in sorted(objects, key=lambda o: o.mass):
            self.draw_object(obj, valid_point, drawn_positions, drawn_labels)

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

    def quit(self):
        pygame.quit()
