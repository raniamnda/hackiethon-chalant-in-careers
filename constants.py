"""
constants.py – All magic numbers live here.
Building zones measured from world_map.png (897x671) scaled to 960x640.
"""

# ── Window ────────────────────────────────────────────────────────────────────
SCREEN_W   = 960
SCREEN_H   = 640
FPS        = 60
TITLE      = "Chalant in Careers"

# ── Colours (RGB) ─────────────────────────────────────────────────────────────
C_BLACK      = (  0,   0,   0)
C_WHITE      = (255, 255, 255)
C_BG         = ( 30,  30,  50)
C_PANEL      = ( 15,  15,  35, 220)
C_BORDER     = (245, 197,  24)
C_TEXT       = (240, 236, 226)
C_TEXT_DIM   = (160, 155, 145)
C_GREEN      = ( 74, 222, 128)
C_RED        = (248, 113, 113)
C_BLUE       = ( 96, 165, 250)
C_PINK       = (244, 114, 182)
C_PURPLE     = (167, 139, 250)
C_YELLOW     = (253, 224,  71)
C_GRASS      = ( 80, 160,  70)
C_PATH       = (180, 160, 120)
C_SKY        = (100, 180, 240)

# ── Player ────────────────────────────────────────────────────────────────────
PLAYER_SPEED   = 180      # px / second
PLAYER_SIZE    = 28

# ── Scenes ────────────────────────────────────────────────────────────────────
SCENE_INTRO       = "intro"
SCENE_WORLD       = "world"
SCENE_CLINIC      = "clinic"
SCENE_HOTEL       = "hotel"
SCENE_REALESTATE  = "realestate"
SCENE_RESULT      = "result"

# ── Building bounding boxes (x, y, w, h) at 960x640 ──────────────────────────
#
#   Original image: 897x671  →  scale_x=1.0702  scale_y=0.9538
#
#   Layout:
#     Top-left  big pink building  = Clinic   (biggest)
#     Top-right green building     = Hotel    (medium, door on left side)
#     Bottom row 3 small houses    = Real Estate house 1, 2, 3
#
BLDG_CLINIC      = (  58,  17, 422, 281)
BLDG_HOTEL       = ( 524,  17, 310, 281)
BLDG_HOUSE1      = (   0, 357, 139, 205)
BLDG_HOUSE2      = ( 165, 357, 262, 205)
BLDG_HOUSE3      = ( 412, 357, 197, 205)

# ── Entry trigger zones (x, y, w, h) — player must stand here to enter ───────
# y values set so labels appear clearly above each door
ZONE_CLINIC      = ( 199, 290, 140,  55)   # clinic door, front centre
ZONE_HOTEL       = ( 534, 280,  80,  55)   # hotel door, left side of top-right building
ZONE_HOUSE1      = (  39, 517,  60,  55)
ZONE_HOUSE2      = ( 252, 517,  87,  55)
ZONE_HOUSE3      = ( 478, 517,  65,  55)

# ── Dialogue ──────────────────────────────────────────────────────────────────
MAX_TURNS    = 7
WAGE_GREAT   = 500
WAGE_OK      = 250
WAGE_POOR    = 100

# ── Tile (kept for compatibility) ─────────────────────────────────────────────
TILE         = 32
MAP_COLS     = 30
MAP_ROWS     = 20
