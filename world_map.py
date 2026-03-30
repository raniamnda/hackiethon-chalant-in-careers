"""
world_map.py – Draws the world using a real background image.

The map is a single scaled image (images/world_map.png).
Buildings are already painted on it — no separate building sprites needed.
Entry zones are invisible rects defined in constants.py that trigger
the [E] enter prompt when the player walks into them.
"""

import pygame
from constants import (
    SCREEN_W, SCREEN_H,
    BLDG_CLINIC, BLDG_HOTEL, BLDG_HOUSE1, BLDG_HOUSE2, BLDG_HOUSE3,
    ZONE_CLINIC, ZONE_HOTEL, ZONE_HOUSE1, ZONE_HOUSE2, ZONE_HOUSE3,
    C_YELLOW, C_WHITE, C_RED, C_BLUE, C_GREEN,
)


# ── Zone registry ─────────────────────────────────────────────────────────────
#  Each entry:  key -> (zone_rect_tuple, building_rect_tuple, label, colour)
ZONES = {
    "clinic":     (ZONE_CLINIC,  BLDG_CLINIC,  "[ The Clinic ]",  C_RED),
    "hotel":      (ZONE_HOTEL,   BLDG_HOTEL,   "[ The Hotel ]",   C_BLUE),
    "house1":     (ZONE_HOUSE1,  BLDG_HOUSE1,  "[ House 1 ]",     C_GREEN),
    "house2":     (ZONE_HOUSE2,  BLDG_HOUSE2,  "[ House 2 ]",     C_GREEN),
    "house3":     (ZONE_HOUSE3,  BLDG_HOUSE3,  "[ House 3 ]",     C_GREEN),
}


class WorldMap:
    def __init__(self, background: pygame.Surface):
        """
        background: the pre-loaded & scaled world_map surface from assets.py
        """
        self.background = background
        self._label_font = None   # lazy-init after pygame.font is ready

    # ── public helpers ────────────────────────────────────────────────────────

    def zone_at(self, player_feet_rect: pygame.Rect):
        """
        Returns the zone key (str) if the player's feet rect overlaps any
        entry zone, otherwise None.
        """
        for key, (zone_xywh, *_) in ZONES.items():
            if pygame.Rect(zone_xywh).colliderect(player_feet_rect):
                return key
        return None

    # ── drawing ───────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface):
        """Blit the background image. No camera offset — map fills the screen."""
        screen.blit(self.background, (0, 0))

    def draw_labels(self, screen: pygame.Surface):
        """Draw building name labels over each building's door zone."""
        if self._label_font is None:
            self._label_font = pygame.font.SysFont("monospace", 13, bold=True)

        for key, (zone_xywh, bldg_xywh, label, colour) in ZONES.items():
            zx, zy, zw, zh = zone_xywh   # draw label above the DOOR ZONE
            text   = self._label_font.render(label, True, colour)
            shadow = self._label_font.render(label, True, (0, 0, 0))
            cx = zx + zw // 2 - text.get_width() // 2
            cy = zy - text.get_height() - 6

            # Clamp so label never goes off the top of the screen
            cy = max(36, cy)

            screen.blit(shadow, (cx + 1, cy + 1))
            screen.blit(text,   (cx,     cy))

    def draw_debug_zones(self, screen: pygame.Surface):
        """
        Draw entry zones as translucent overlays.
        Call this during development to verify zone positions,
        then remove the call when you're happy.
        """
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for key, (zone_xywh, bldg_xywh, label, colour) in ZONES.items():
            zr = pygame.Rect(zone_xywh)
            pygame.draw.rect(overlay, (*colour, 80),  zr)
            pygame.draw.rect(overlay, (*colour, 200), zr, 2)
        screen.blit(overlay, (0, 0))
