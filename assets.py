"""
assets.py – Image loader + numpy character sprites.

Two stickman characters:
  - Boy  : blue shirt, short hair, trousers
  - Girl : pink shirt, longer hair/skirt, ponytail

Each has 4 directions × 2 walk frames = 8 surfaces per gender.
"""

import os
import numpy as np
import pygame
from constants import SCREEN_W, SCREEN_H, TILE

FRAME_W = 32
FRAME_H = 40    # slightly taller so detail fits


# ── surface helpers ───────────────────────────────────────────────────────────

def _surf(arr: np.ndarray) -> pygame.Surface:
    arr_c = np.ascontiguousarray(arr)
    return pygame.image.frombuffer(
        arr_c.tobytes(), (arr_c.shape[1], arr_c.shape[0]), "RGBA"
    ).convert_alpha()


def _canvas(h, w):
    return np.zeros((h, w, 4), dtype=np.uint8)


def _fill(arr, r1, c1, r2, c2, rgba):
    arr[r1:r2, c1:c2] = rgba


def _circle(arr, cy, cx, r, rgba):
    """Draw a filled circle into the numpy array."""
    for y in range(max(0, cy - r), min(arr.shape[0], cy + r + 1)):
        for x in range(max(0, cx - r), min(arr.shape[1], cx + r + 1)):
            if (y - cy) ** 2 + (x - cx) ** 2 <= r ** 2:
                arr[y, x] = rgba


# ── colours ───────────────────────────────────────────────────────────────────

SKIN  = (255, 200, 155, 255)
SKIN_D= (230, 175, 130, 255)   # slightly darker for side/back
WHITE = (255, 255, 255, 255)
BLACK = (20,  20,  20,  255)

BOY_HAIR   = ( 60,  35,  10, 255)
BOY_SHIRT  = ( 70, 120, 200, 255)
BOY_TROUSER= ( 40,  60, 130, 255)
BOY_SHOE   = ( 30,  20,  10, 255)

GIRL_HAIR  = (180,  80,  30, 255)
GIRL_SHIRT = (220,  80, 140, 255)
GIRL_SKIRT = (180,  50, 110, 255)
GIRL_SHOE  = (160,  40,  80, 255)
GIRL_SOCK  = (255, 230, 240, 255)


# ── Boy frames ────────────────────────────────────────────────────────────────

def _boy_frame(facing: str, foot: int) -> pygame.Surface:
    H, W = FRAME_H, FRAME_W
    a = _canvas(H, W)

    # ── shared: head ──────────────────────────────────────────────────────────
    _circle(a, 7, W//2, 6, SKIN)

    # hair depending on facing
    if facing == "up":
        _fill(a, 0, W//2-6, 5, W//2+6, BOY_HAIR)
    elif facing in ("left", "right"):
        _fill(a, 0, W//2-6, 4, W//2+6, BOY_HAIR)
        _fill(a, 4, W//2-6, 7, W//2+2, BOY_HAIR)
    else:  # down
        _fill(a, 0, W//2-6, 5, W//2+6, BOY_HAIR)

    # eyes
    if facing == "down":
        a[8, W//2-3] = BLACK
        a[8, W//2+2] = BLACK
    elif facing == "up":
        pass
    elif facing == "left":
        a[8, W//2-5] = BLACK
    else:
        a[8, W//2+4] = BLACK

    # ── body / shirt ──────────────────────────────────────────────────────────
    _fill(a, 14, W//2-5, 24, W//2+5, BOY_SHIRT)

    # ── arms ──────────────────────────────────────────────────────────────────
    if foot == 0:
        _fill(a, 14, W//2-9, 22, W//2-5, BOY_SHIRT)   # left arm
        _fill(a, 14, W//2+5, 22, W//2+9, BOY_SHIRT)   # right arm
    else:
        _fill(a, 15, W//2-9, 23, W//2-5, BOY_SHIRT)
        _fill(a, 15, W//2+5, 23, W//2+9, BOY_SHIRT)

    # hands
    _circle(a, 22 if foot==0 else 23, W//2-7, 2, SKIN)
    _circle(a, 22 if foot==0 else 23, W//2+7, 2, SKIN)

    # ── legs ──────────────────────────────────────────────────────────────────
    if foot == 0:
        _fill(a, 24, W//2-5, 36, W//2,   BOY_TROUSER)
        _fill(a, 24, W//2,   34, W//2+5, BOY_TROUSER)
        _fill(a, 36, W//2-5, 40, W//2,   BOY_SHOE)
        _fill(a, 34, W//2,   38, W//2+5, BOY_SHOE)
    else:
        _fill(a, 24, W//2-5, 34, W//2,   BOY_TROUSER)
        _fill(a, 24, W//2,   36, W//2+5, BOY_TROUSER)
        _fill(a, 34, W//2-5, 38, W//2,   BOY_SHOE)
        _fill(a, 36, W//2,   40, W//2+5, BOY_SHOE)

    return _surf(a)


# ── Girl frames ───────────────────────────────────────────────────────────────

def _girl_frame(facing: str, foot: int) -> pygame.Surface:
    H, W = FRAME_H, FRAME_W
    a = _canvas(H, W)

    # ── head ──────────────────────────────────────────────────────────────────
    _circle(a, 7, W//2, 6, SKIN)

    # hair — longer, with ponytail hint
    if facing == "up":
        _fill(a, 0, W//2-7, 5, W//2+7, GIRL_HAIR)
        _fill(a, 5, W//2-7, 14, W//2-5, GIRL_HAIR)   # long side hair left
        _fill(a, 5, W//2+5, 14, W//2+7, GIRL_HAIR)   # long side hair right
    elif facing == "left":
        _fill(a, 0, W//2-7, 5, W//2+7, GIRL_HAIR)
        _fill(a, 5, W//2-7, 14, W//2-4, GIRL_HAIR)
        # ponytail right side
        _fill(a, 2, W//2+5, 10, W//2+9, GIRL_HAIR)
    elif facing == "right":
        _fill(a, 0, W//2-7, 5, W//2+7, GIRL_HAIR)
        _fill(a, 5, W//2+4, 14, W//2+7, GIRL_HAIR)
        _fill(a, 2, W//2-9, 10, W//2-5, GIRL_HAIR)
    else:  # down
        _fill(a, 0, W//2-7, 5, W//2+7, GIRL_HAIR)
        _fill(a, 5, W//2-7, 14, W//2-5, GIRL_HAIR)
        _fill(a, 5, W//2+5, 14, W//2+7, GIRL_HAIR)
        # ponytail top
        _fill(a, 0, W//2+3, 4,  W//2+7, GIRL_HAIR)

    # eyes + lashes
    if facing == "down":
        a[8, W//2-3] = BLACK
        a[8, W//2+2] = BLACK
        a[7, W//2-3] = BLACK   # lash
        a[7, W//2+2] = BLACK
    elif facing == "left":
        a[8, W//2-5] = BLACK
        a[7, W//2-5] = BLACK
    elif facing == "right":
        a[8, W//2+4] = BLACK
        a[7, W//2+4] = BLACK

    # ── body / shirt ──────────────────────────────────────────────────────────
    _fill(a, 14, W//2-5, 22, W//2+5, GIRL_SHIRT)

    # ── arms ──────────────────────────────────────────────────────────────────
    if foot == 0:
        _fill(a, 14, W//2-9, 21, W//2-5, GIRL_SHIRT)
        _fill(a, 14, W//2+5, 21, W//2+9, GIRL_SHIRT)
    else:
        _fill(a, 15, W//2-9, 22, W//2-5, GIRL_SHIRT)
        _fill(a, 15, W//2+5, 22, W//2+9, GIRL_SHIRT)

    _circle(a, 21 if foot==0 else 22, W//2-7, 2, SKIN)
    _circle(a, 21 if foot==0 else 22, W//2+7, 2, SKIN)

    # ── skirt ─────────────────────────────────────────────────────────────────
    # A-line skirt: wider at bottom
    _fill(a, 22, W//2-5, 32, W//2+5, GIRL_SKIRT)
    _fill(a, 26, W//2-7, 32, W//2+7, GIRL_SKIRT)   # flare

    # ── legs / socks / shoes ──────────────────────────────────────────────────
    if foot == 0:
        _fill(a, 32, W//2-4, 37, W//2,   GIRL_SOCK)
        _fill(a, 32, W//2,   37, W//2+4, GIRL_SOCK)
        _fill(a, 37, W//2-5, 40, W//2,   GIRL_SHOE)
        _fill(a, 37, W//2,   40, W//2+5, GIRL_SHOE)
    else:
        _fill(a, 32, W//2-4, 37, W//2,   GIRL_SOCK)
        _fill(a, 32, W//2,   37, W//2+4, GIRL_SOCK)
        _fill(a, 35, W//2-5, 39, W//2,   GIRL_SHOE)
        _fill(a, 37, W//2,   40, W//2+5, GIRL_SHOE)

    return _surf(a)


# ── Frame builder ─────────────────────────────────────────────────────────────

def build_player_frames(gender: str = "boy") -> dict:
    """
    Returns { "down": [surf0, surf1], "left": [...], "right": [...], "up": [...] }
    gender: "boy" or "girl"
    """
    draw_fn = _boy_frame if gender == "boy" else _girl_frame
    frames  = {}
    for facing in ("down", "up", "left", "right"):
        frames[facing] = [
            draw_fn(facing, 0),
            draw_fn(facing, 1),
        ]
    print(f"[assets] Using numpy {gender} character sprite")
    return frames


# ── World map ─────────────────────────────────────────────────────────────────

def _fallback_surface(w, h, colour, label=""):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((*colour, 200))
    pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2)
    if label:
        try:
            font = pygame.font.SysFont("monospace", 13, bold=True)
            txt  = font.render(label, True, (255, 255, 255))
            surf.blit(txt, (w//2 - txt.get_width()//2, h//2 - txt.get_height()//2))
        except Exception:
            pass
    return surf


def _load(path, fw, fh, fc, label="", alpha=True):
    if os.path.exists(path):
        try:
            img = pygame.image.load(path)
            return img.convert_alpha() if alpha else img.convert()
        except pygame.error as e:
            print(f"[assets] Could not load {path}: {e}")
    else:
        print(f"[assets] Missing file: {path}  (using placeholder)")
    return _fallback_surface(fw, fh, fc, label)


def load_world_map() -> pygame.Surface:
    surf = _load("images/world_map.png", SCREEN_W, SCREEN_H,
                 (100, 130, 100), "world_map.png", alpha=False)
    if surf.get_size() != (SCREEN_W, SCREEN_H):
        surf = pygame.transform.scale(surf, (SCREEN_W, SCREEN_H))
    return surf


def load_interior(name: str) -> pygame.Surface:
    paths = {
        "clinic":     "images/interior_clinic.png",
        "hotel":      "images/interior_hotel.png",
        "realestate": "images/interior_realestate.png",
    }
    colours = {
        "clinic":     (200, 220, 230),
        "hotel":      (220, 200, 180),
        "realestate": (210, 230, 200),
    }
    surf = _load(paths.get(name, ""), SCREEN_W, SCREEN_H,
                 colours.get(name, (180, 180, 180)), name, alpha=False)
    if surf.get_size() != (SCREEN_W, SCREEN_H):
        surf = pygame.transform.scale(surf, (SCREEN_W, SCREEN_H))
    return surf


def build_coin_icon(size=20) -> pygame.Surface:
    arr = np.zeros((size, size, 4), dtype=np.uint8)
    cx, cy, r = size//2, size//2, size//2-1
    for y in range(size):
        for x in range(size):
            if (x-cx)**2+(y-cy)**2 <= r**2:
                arr[y,x] = (245,197,24,255)
            if (x-cx)**2+(y-cy)**2 <= (r-3)**2:
                arr[y,x] = (200,150,10,255)
    return _surf(arr)
