"""
player.py – Movable character with 4-directional animation.
Movement uses NumPy for velocity normalisation.
The world map is now a single full-screen image so the player moves
within a fixed SCREEN_W x SCREEN_H boundary (no camera scroll needed).
"""

import numpy as np
import pygame
from constants import SCREEN_W, SCREEN_H, PLAYER_SPEED


class Player:
    def __init__(self, frames: dict, start_x: float, start_y: float):
        self.frames    = frames        # {"down": [surf0, surf1], ...}
        self.x         = float(start_x)
        self.y         = float(start_y)
        self.facing    = "down"
        self.foot      = 0             # 0 or 1 — walk frame index
        self.anim_t    = 0.0
        self.anim_spd  = 0.16          # seconds per step

        # Use frame size from the loaded sprite
        sample = frames["down"][0]
        self.w = sample.get_width()
        self.h = sample.get_height()

    # ── rects ─────────────────────────────────────────────────────────────────

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.w, self.h)

    @property
    def feet_rect(self) -> pygame.Rect:
        """Small rect at the bottom-centre of the sprite for zone detection."""
        fw = max(10, self.w - 12)
        return pygame.Rect(
            int(self.x) + (self.w - fw) // 2,
            int(self.y) + self.h - 10,
            fw, 10
        )

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt: float, keys):
        # Build velocity vector with NumPy
        vx, vy = 0.0, 0.0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]: vx = -1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: vx =  1.0
        if keys[pygame.K_UP]    or keys[pygame.K_w]: vy = -1.0
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]: vy =  1.0

        vel = np.array([vx, vy], dtype=np.float64)
        mag = np.linalg.norm(vel)

        if mag > 0:
            vel = (vel / mag) * PLAYER_SPEED * dt   # normalise then scale

            # Update facing direction
            if abs(vel[0]) >= abs(vel[1]):
                self.facing = "right" if vel[0] > 0 else "left"
            else:
                self.facing = "down" if vel[1] > 0 else "up"

            # Walk animation
            self.anim_t += dt
            if self.anim_t >= self.anim_spd:
                self.anim_t -= self.anim_spd
                self.foot = 1 - self.foot
        else:
            self.foot   = 0
            self.anim_t = 0.0

        # Apply movement, clamped to screen bounds
        self.x = float(np.clip(self.x + vel[0], 0, SCREEN_W - self.w))
        self.y = float(np.clip(self.y + vel[1], 0, SCREEN_H - self.h))

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self, surface: pygame.Surface):
        surf = self.frames[self.facing][self.foot]
        surface.blit(surf, (int(self.x), int(self.y)))

    # ── debug ─────────────────────────────────────────────────────────────────

    def draw_debug(self, surface: pygame.Surface):
        pygame.draw.rect(surface, (255, 0, 0),   self.rect,       1)
        pygame.draw.rect(surface, (0, 255, 255),  self.feet_rect,  1)
