# render.py
import pygame
import numpy as np
from datetime import datetime
from config import scale as global_scale

class PygameRenderer:
    def __init__(self, screen_width=800, screen_height=600):
        pygame.init()
        self.font = pygame.font.SysFont('None', 14)
        self.screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
        pygame.display.set_caption('Orbital Simulation')
        self.clock = pygame.time.Clock()
        self.offset = np.array([screen_width // 2, screen_height // 2])
        self.dragging = False
        self.last_mouse_pos = None
        self.zoom_sensitivity = 1.1
        self.min_scale = 1e-15
        self.max_scale = 3.5e-4
        self.scale = global_scale
        self.screen_width = screen_width
        self.screen_height = screen_height

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.dragging = True
                    self.last_mouse_pos = np.array(pygame.mouse.get_pos())
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
            if event.type == pygame.MOUSEMOTION and self.dragging:
                current_mouse_pos = np.array(pygame.mouse.get_pos())
                delta = current_mouse_pos - self.last_mouse_pos
                self.offset += delta
                self.last_mouse_pos = current_mouse_pos
            if event.type == pygame.MOUSEWHEEL:
                zoom_point = np.array(pygame.mouse.get_pos())
                world_pos_before = (zoom_point - self.offset) / self.scale
                if event.y > 0:
                    self.scale *= self.zoom_sensitivity
                elif event.y < 0:
                    self.scale /= self.zoom_sensitivity
                self.scale = max(min(self.scale, self.max_scale), self.min_scale)
                self.offset = zoom_point - world_pos_before * self.scale
        return True

    def draw(self, bodies, step, dt):
        self.screen.fill((0, 0, 0))

        def draw_object(obj):
            pos = np.array([obj.pos[0], -obj.pos[1]]) * self.scale + self.offset
            screen_size = obj.r * self.scale
            draw_radius = max(2, int(screen_size))
            pygame.draw.circle(self.screen, pygame.Color(obj.color), pos.astype(int), draw_radius)
            label = self.font.render(obj.name, True, (255, 255, 255))
            label_pos = pos + np.array([draw_radius + 5, -draw_radius])
            self.screen.blit(label, label_pos.astype(float))

        for obj in bodies:
            draw_object(obj)

        # HUD
        width_pixels = self.screen.get_size()[0]
        zoom_inverse_km = (1 / self.scale / 1000)
        screen_width_km = width_pixels * zoom_inverse_km
        zoom_text = self.font.render(f"Width: {screen_width_km:.2f} km", True, (255, 255, 255))
        #energy_text = self.font.render(f"Energy error: {mech_e_error:.10f} %", True, (255, 255, 255))
        simtime = step * dt
        simtime_text = self.font.render(f"Sim time: {simtime:.2f} secs, {simtime/60/60/24:.2f} days, {simtime/60/60/24/365:.2f} yrs", True, (255, 255, 255))
        fps = self.clock.get_fps()
        fps_text = self.font.render(f"FPS: {fps:.2f}", True, (255, 255, 255))

        self.screen.blit(zoom_text, (10, 10))
        #self.screen.blit(energy_text, (10, 30))
        self.screen.blit(simtime_text, (10, 50))
        self.screen.blit(fps_text, (10, 70))

        pygame.display.flip()
        self.clock.tick()

    def quit(self):
        pygame.quit()