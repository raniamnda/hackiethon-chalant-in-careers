"""
game.py – Central state machine.
Gender is selected on intro screen and used to build the correct character sprite.
"""

import pygame
from constants import SCREEN_W, SCREEN_H
from assets import load_world_map, build_player_frames, load_interior, build_coin_icon
from player import Player
from world_map import WorldMap
from scenes import (IntroScene, WorldScene, AICareerScene,
                    ClinicChoiceScene, RealEstateChoiceScene)


class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        # ── State (set before assets so gender is available) ──────────────────
        self.player_name = "Hero"
        self.gender      = "boy"     # default — overwritten by intro screen
        self.coins       = 0

        # ── Assets ────────────────────────────────────────────────────────────
        self.bg_surface = load_world_map()
        self.coin_icon  = build_coin_icon()
        self.interiors  = {
            "clinic":     load_interior("clinic"),
            "hotel":      load_interior("hotel"),
            "realestate": load_interior("realestate"),
        }

        # Player frames start as boy — rebuilt when gender is confirmed
        self.player_frames = build_player_frames("boy")

        # ── World ─────────────────────────────────────────────────────────────
        self.world_map = WorldMap(self.bg_surface)
        self.player    = Player(
            self.player_frames,
            start_x = SCREEN_W // 2,
            start_y = SCREEN_H // 2,
        )

        self.current_scene = IntroScene(self.screen)
        self.debug         = False

    # ── public ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.debug = not self.debug
            return
        result = self.current_scene.handle_event(event)
        if result:
            self._transition(result)

    def update(self, dt):
        self.current_scene.update(dt)

    def draw(self):
        self.current_scene.draw(debug=self.debug)

    # ── transitions ───────────────────────────────────────────────────────────

    def _transition(self, result):
        action, payload = result

        if action == "world":
            self.player_name = payload.get("player_name", "Hero")
            self.coins       = payload.get("coins", 0)

            # Rebuild player sprite if gender changed
            new_gender = payload.get("gender", "boy")
            if new_gender != self.gender:
                self.gender        = new_gender
                self.player_frames = build_player_frames(self.gender)
                self.player.frames = self.player_frames
                print(f"[game] Character switched to: {self.gender}")

            self._go_world()

        elif action == "enter_building":
            building = payload["building"]
            if building == "clinic":
                self._play_music("clinic.mp3")
                self.current_scene = ClinicChoiceScene(self.screen, self.player_name)
            elif building == "hotel":
                self._play_music("hotel.mp3")
                self.current_scene = AICareerScene(
                    self.screen, "hotel", self.player_name, self.coins,
                    interior=self.interiors["hotel"])
            elif building in ("house1", "house2", "house3"):
                self._play_music("realestate.mp3")
                preselect = {"house1": 0, "house2": 1, "house3": 2}[building]
                self.current_scene = RealEstateChoiceScene(
                    self.screen, self.player_name, preselect=preselect)

        elif action == "start_career":
            role_key     = payload.get("role_key", "hotel")
            house_index  = payload.get("house_index", 0)
            interior_key = (
                "clinic"     if role_key in ("doctor", "psychologist") else
                "realestate" if role_key == "realestate" else
                "hotel"
            )
            # Play role-specific music
            music_file = {
                "doctor":       "clinic.mp3",
                "psychologist": "clinic.mp3",
                "hotel":        "hotel.mp3",
                "realestate":   "realestate.mp3",
            }.get(role_key, "world.mp3")
            self._play_music(music_file)
            self.current_scene = AICareerScene(
                self.screen, role_key, self.player_name, self.coins,
                interior=self.interiors[interior_key],
                house_index=house_index)

        elif action == "back_to_world":
            self.coins += payload.get("earned", 0)
            self._go_world()

    def _play_music(self, filename: str):
        """Play a lofi background track on loop."""
        import os
        path = os.path.join("music", filename)
        try:
            if not pygame.mixer.get_init():
                print("[music] Mixer not initialised — skipping")
                return
            if not os.path.exists(path):
                print(f"[music] File not found: {path}")
                return
            # Don't restart the same track if already playing
            current = getattr(self, "_current_track", None)
            if current == path and pygame.mixer.music.get_busy():
                return
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
            self._current_track = path
            print(f"[music] Now playing: {path}")
        except Exception as e:
            print(f"[music] Error playing {path}: {e}")

    def _go_world(self):
        self._play_music("world.mp3")
        self.current_scene = WorldScene(
            screen      = self.screen,
            world_map   = self.world_map,
            player      = self.player,
            player_name = self.player_name,
            coins       = self.coins,
        )
