"""
scenes.py – One class per scene. The Game object swaps between them.
"""

import numpy as np
import pygame
from constants import *
from ui import (FontCache, Button, TypewriterText, InputBox,
                draw_panel, draw_text, draw_wrapped_text, wrap_text)
from dialogue import (CLINIC_DOCTOR, CLINIC_PSYCH, HOTEL_SCRIPT,
                      REALESTATE_SCRIPTS, get_score_rating, get_feedback)


# ─────────────────────────────────────────────────────────────────────────────
# IntroScene
# ─────────────────────────────────────────────────────────────────────────────

class IntroScene:
    def __init__(self, screen):
        self.screen  = screen
        W, H         = SCREEN_W, SCREEN_H
        self.title_y = -80
        self.alpha   = 0

        self.input   = InputBox(pygame.Rect(W//2 - 160, H//2 + 20, 320, 40),
                                placeholder="Enter your name…")
        self.confirm = Button(pygame.Rect(W//2 - 80, H//2 + 80, 160, 44),
                              "Start", colour=(60, 140, 80))
        self.gender  = "boy"
        self.btn_boy  = Button(pygame.Rect(W//2 - 130, H//2 - 40, 110, 36),
                               "Boy",  colour=(60, 100, 180))
        self.btn_girl = Button(pygame.Rect(W//2 + 20,  H//2 - 40, 110, 36),
                               "Girl", colour=(180, 80, 140))
        self.error   = ""

        rng = np.random.default_rng(7)
        self.stars        = rng.integers(0, [SCREEN_W, SCREEN_H], size=(120, 2))
        self.star_bright  = rng.random(120)

    def handle_event(self, event):
        result = self.input.handle_event(event)
        if result:
            return self._try_confirm(result)
        if self.confirm.handle_event(event):
            return self._try_confirm(self.input.text.strip())
        if self.btn_boy.handle_event(event):
            self.gender = "boy"
        if self.btn_girl.handle_event(event):
            self.gender = "girl"
        return None

    def _try_confirm(self, name):
        if not name:
            self.error = "Please enter a name first!"
            return None
        return ("world", {"player_name": name, "gender": self.gender, "coins": 0})

    def update(self, dt):
        self.title_y = min(60, self.title_y + 200 * dt)
        self.alpha   = min(255, self.alpha + 300 * dt)
        self.input.update(dt)

    def draw(self, debug=False):
        s = self.screen
        s.fill(C_BG)
        for i, (sx, sy) in enumerate(self.stars):
            b = int(self.star_bright[i] * 200 + 55)
            s.set_at((int(sx), int(sy)), (b, b, b))

        W, H = SCREEN_W, SCREEN_H
        font_big = FontCache.get(38, bold=True)
        font_med = FontCache.get(18)
        font_sm  = FontCache.get(14)

        title = font_big.render("Chalant in Careers", True, C_BORDER)
        s.blit(title, (W//2 - title.get_width()//2, int(self.title_y)))
        sub = font_sm.render("Discover your calling. Master your role.", True, C_TEXT_DIM)
        s.blit(sub, (W//2 - sub.get_width()//2, int(self.title_y) + 50))

        panel_rect = pygame.Rect(W//2 - 200, H//2 - 90, 400, 240)
        draw_panel(s, panel_rect)
        label = font_med.render("Who are you?", True, C_TEXT)
        s.blit(label, (W//2 - label.get_width()//2, H//2 - 80))

        self.btn_boy.draw(s)
        self.btn_girl.draw(s)
        sel = font_sm.render(f"Selected: {self.gender.capitalize()}", True, C_YELLOW)
        s.blit(sel, (W//2 - sel.get_width()//2, H//2 - 5))
        self.input.draw(s)
        self.confirm.draw(s)

        if self.error:
            err = font_sm.render(self.error, True, C_RED)
            s.blit(err, (W//2 - err.get_width()//2, H//2 + 132))


# ─────────────────────────────────────────────────────────────────────────────
# WorldScene
# ─────────────────────────────────────────────────────────────────────────────

class WorldScene:
    def __init__(self, screen, world_map, player, player_name, coins):
        self.screen      = screen
        self.world_map   = world_map
        self.player      = player
        self.player_name = player_name
        self.coins       = coins

        self.near_zone   = None
        self.prompt_anim = 0.0

        self.f_hud  = FontCache.get(15, bold=True)
        self.f_sm   = FontCache.get(13)
        self.f_hint = FontCache.get(14)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_e, pygame.K_RETURN):
            if self.near_zone:
                return ("enter_building", {"building": self.near_zone})
        return None

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)
        self.near_zone   = self.world_map.zone_at(self.player.feet_rect)
        self.prompt_anim += dt * 3

    def draw(self, debug=False):
        s = self.screen

        # 1 — background map
        self.world_map.draw(s)

        # 2 — building labels
        self.world_map.draw_labels(s)

        # 3 — debug zone overlay (toggle with F1)
        if debug:
            self.world_map.draw_debug_zones(s)

        # 4 — player
        self.player.draw(s)
        if debug:
            self.player.draw_debug(s)

        # 5 — entry prompt
        if self.near_zone:
            offset = int(np.sin(self.prompt_anim) * 5)
            prompt = self.f_hint.render("Press  [E]  to enter", True, C_WHITE)
            px = SCREEN_W // 2 - prompt.get_width() // 2
            py = SCREEN_H - 72 + offset
            draw_panel(s, pygame.Rect(px - 14, py - 8,
                                      prompt.get_width() + 28,
                                      prompt.get_height() + 16))
            s.blit(prompt, (px, py))

        # 6 — HUD bar
        hud = pygame.Rect(0, 0, SCREEN_W, 36)
        draw_panel(s, hud, bg=(10, 10, 25, 210), border=(50, 50, 90), radius=0)
        name_s = self.f_hud.render(f"  {self.player_name}", True, C_TEXT)
        s.blit(name_s, (8, 8))
        coin_s = self.f_hud.render(f"Coins: {self.coins}", True, C_YELLOW)
        s.blit(coin_s, (SCREEN_W - coin_s.get_width() - 16, 8))
        ctrl = self.f_sm.render("WASD / Arrow keys | E = enter | F1 = debug", True, C_TEXT_DIM)
        s.blit(ctrl, (SCREEN_W // 2 - ctrl.get_width() // 2, 10))


# ─────────────────────────────────────────────────────────────────────────────
# CareerScene  (conversation engine — same for all roles)
# ─────────────────────────────────────────────────────────────────────────────

class CareerScene:
    CHAT_X  = 20;  CHAT_Y = 80;  CHAT_W = 580;  CHAT_H = 390
    RIGHT_X = 622; RIGHT_W = 318

    def __init__(self, screen, script, player_name, coins, interior=None):
        self.screen      = screen
        self.script      = script
        self.player_name = player_name
        self.coins       = coins
        self.interior    = interior   # background surface or None

        self.turn      = 0
        self.score     = 0
        self.max_score = len(script["turns"]) * 2

        intro_raw       = script["intro"].replace("{name}", player_name)
        self.typewriter = TypewriterText(intro_raw, speed=50)
        self.phase      = "intro"
        self.npc_tw     = None
        self.choice_btns = []
        self.result_data = None
        self.chat_log    = []

        self.f_title = FontCache.get(17, bold=True)
        self.f_body  = FontCache.get(14)
        self.f_sm    = FontCache.get(13)

        self._end_btn = Button(
            pygame.Rect(self.RIGHT_X, SCREEN_H - 58, self.RIGHT_W, 42),
            "End Session", colour=(130, 45, 45))

    # ── helpers ───────────────────────────────────────────────────────────────

    def _start_npc_turn(self):
        self.npc_tw      = TypewriterText(self.script["turns"][self.turn]["npc"], speed=45)
        self.phase       = "npc"
        self.choice_btns = []

    def _advance_to_choices(self):
        self.phase = "choice"
        self.chat_log.append((self.script["npc_name"],
                               self.script["turns"][self.turn]["npc"]))
        self._build_choice_buttons()

    def _build_choice_buttons(self):
        self.choice_btns = []
        for i, (text, pts) in enumerate(self.script["turns"][self.turn]["choices"]):
            btn = Button(
                pygame.Rect(self.RIGHT_X, 102 + i * 90, self.RIGHT_W, 82),
                text, colour=(38, 58, 108), font_size=12)
            btn._pts = pts
            self.choice_btns.append(btn)

    def _player_chose(self, text, pts):
        self.score += pts
        self.chat_log.append((self.player_name, text))
        self.turn += 1
        if self.turn >= len(self.script["turns"]):
            self._end_session()
        else:
            self._start_npc_turn()

    def _end_session(self):
        self.phase = "result"
        label, wage, col = get_score_rating(self.score, self.max_score)
        fb = get_feedback(self.score, self.max_score, self.script["role"])
        self.result_data = {"label": label, "wage": wage, "col": col,
                             "feedback": fb, "score": self.score, "max": self.max_score}

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if self.phase == "intro":
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if not self.typewriter.done: self.typewriter.skip()
                else: self._start_npc_turn()

        elif self.phase == "npc":
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if not self.npc_tw.done: self.npc_tw.skip()
                else: self._advance_to_choices()

        elif self.phase == "choice":
            for btn in self.choice_btns:
                if btn.handle_event(event):
                    self._player_chose(btn.text, btn._pts)
                    return None
            if self._end_btn.handle_event(event):
                self._end_session()

        elif self.phase == "result":
            if not hasattr(self, "_back_btn"):
                self._make_back_btn()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return ("back_to_world", {"earned": self.result_data["wage"]})
            if self._back_btn.handle_event(event):
                return ("back_to_world", {"earned": self.result_data["wage"]})

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.phase != "result":
                return ("back_to_world", {"earned": 0})
        return None

    def _make_back_btn(self):
        self._back_btn = Button(
            pygame.Rect(SCREEN_W//2 - 120, SCREEN_H - 80, 240, 46),
            "Return to Map", colour=(45, 115, 55))

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt):
        if self.phase == "intro": self.typewriter.update(dt)
        elif self.phase == "npc" and self.npc_tw: self.npc_tw.update(dt)

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self, debug=False):
        s = self.screen

        # Background — interior image or solid colour
        if self.interior:
            s.blit(self.interior, (0, 0))
            # dim overlay so text is readable
            dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            dim.fill((0, 0, 20, 160))
            s.blit(dim, (0, 0))
        else:
            s.fill(C_BG)

        # Header
        draw_panel(s, pygame.Rect(0, 0, SCREEN_W, 68), bg=(8, 8, 28, 245), radius=0)
        role_s = self.f_title.render(self.script["role"], True, C_BORDER)
        s.blit(role_s, (16, 10))
        set_s = self.f_sm.render(self.script["setting"], True, C_TEXT_DIM)
        s.blit(set_s, (16, 36))
        ctx_s = self.f_sm.render(self.script["context"], True, C_BLUE)
        s.blit(ctx_s, (SCREEN_W//2 - ctx_s.get_width()//2, 50))
        turn_s = self.f_sm.render(
            f"Turn {self.turn}/{len(self.script['turns'])}   Score: {self.score}/{self.max_score}",
            True, C_TEXT_DIM)
        s.blit(turn_s, (SCREEN_W - turn_s.get_width() - 16, 10))

        if self.phase != "result":
            self._draw_chat(s)
            self._draw_right(s)
        else:
            self._draw_result(s)

    def _draw_chat(self, s):
        cr = pygame.Rect(self.CHAT_X, self.CHAT_Y, self.CHAT_W, self.CHAT_H)
        draw_panel(s, cr)
        f  = self.f_sm
        y  = cr.y + 10
        mw = cr.w - 28

        for speaker, text in self.chat_log[-13:]:
            is_player = speaker == self.player_name
            col = C_GREEN if is_player else C_BLUE
            lbl = f.render(f"{speaker}:", True, col)
            s.blit(lbl, (cr.x + 10, y)); y += lbl.get_height() + 2
            for line in wrap_text(text, f, mw - 10):
                ls = f.render(line, True, C_TEXT)
                if y + ls.get_height() < cr.bottom - 28:
                    s.blit(ls, (cr.x + 20, y))
                y += ls.get_height() + 2
            y += 6

        if self.phase == "intro" and self.typewriter:
            for line in wrap_text(self.typewriter.visible, f, mw - 10):
                ls = f.render(line, True, C_YELLOW)
                if y + ls.get_height() < cr.bottom - 28:
                    s.blit(ls, (cr.x + 10, y))
                y += ls.get_height() + 3
            hint_col = C_WHITE if self.typewriter.done else C_TEXT_DIM
            hint = f.render("Click or press any key to continue...", True, hint_col)
            s.blit(hint, (cr.x + 10, cr.bottom - 24))

        elif self.phase == "npc" and self.npc_tw:
            lbl = f.render(f"{self.script['npc_name']}:", True, C_BLUE)
            s.blit(lbl, (cr.x + 10, y)); y += lbl.get_height() + 2
            for line in wrap_text(self.npc_tw.visible, f, mw - 10):
                ls = f.render(line, True, C_TEXT)
                if y + ls.get_height() < cr.bottom - 28:
                    s.blit(ls, (cr.x + 20, y))
                y += ls.get_height() + 3
            if self.npc_tw.done:
                hint = f.render("Click to choose your response...", True, C_TEXT_DIM)
                s.blit(hint, (cr.x + 10, cr.bottom - 24))

    def _draw_right(self, s):
        rr = pygame.Rect(self.RIGHT_X - 8, self.CHAT_Y, self.RIGHT_W + 8, SCREEN_H - self.CHAT_Y - 10)
        draw_panel(s, rr)

        if self.phase == "choice":
            lbl = self.f_body.render("Your response:", True, C_BORDER)
            s.blit(lbl, (self.RIGHT_X, self.CHAT_Y + 12))
            for btn in self.choice_btns:
                btn.draw(s)
            hint = self.script["turns"][self.turn].get("hint", "")
            if hint:
                hr = pygame.Rect(self.RIGHT_X, 390, self.RIGHT_W, 64)
                draw_panel(s, hr, bg=(15, 40, 15, 210), border=(74, 222, 128))
                draw_wrapped_text(s, f"Tip: {hint}", self.f_sm, C_GREEN, hr.inflate(-12, -10))
            self._end_btn.draw(s)
        else:
            info = self.f_sm.render("Conversation in progress...", True, C_TEXT_DIM)
            s.blit(info, (self.RIGHT_X, self.CHAT_Y + 20))
            esc = self.f_sm.render("[ESC] Exit without pay", True, (160, 70, 70))
            s.blit(esc, (self.RIGHT_X, SCREEN_H - 70))

    def _draw_result(self, s):
        if not hasattr(self, "_back_btn"):
            self._make_back_btn()
        rd  = self.result_data
        col = {"green": C_GREEN, "yellow": C_YELLOW, "red": C_RED}.get(rd["col"], C_WHITE)
        pr  = pygame.Rect(SCREEN_W//2 - 285, 75, 570, SCREEN_H - 175)
        draw_panel(s, pr)
        y = pr.y + 22

        title = self.f_title.render("Session Complete!", True, C_BORDER)
        s.blit(title, (SCREEN_W//2 - title.get_width()//2, y)); y += 42

        rating = FontCache.get(22, bold=True).render(rd["label"], True, col)
        s.blit(rating, (SCREEN_W//2 - rating.get_width()//2, y)); y += 48

        sc = self.f_body.render(f"Score: {rd['score']} / {rd['max']}", True, C_TEXT)
        s.blit(sc, (SCREEN_W//2 - sc.get_width()//2, y)); y += 38

        ws = FontCache.get(18, bold=True).render(f"Coins earned: {rd['wage']}", True, C_YELLOW)
        s.blit(ws, (SCREEN_W//2 - ws.get_width()//2, y)); y += 46

        fb_lbl = self.f_body.render("Feedback:", True, C_BORDER)
        s.blit(fb_lbl, (pr.x + 32, y)); y += 30
        for line in rd["feedback"]:
            fl = self.f_sm.render(f"  - {line}", True, C_TEXT)
            s.blit(fl, (pr.x + 32, y)); y += 26

        y += 10
        note = self.f_sm.render("Press [Enter] or click below to return", True, C_TEXT_DIM)
        s.blit(note, (SCREEN_W//2 - note.get_width()//2, y))
        self._back_btn.draw(s)


# ─────────────────────────────────────────────────────────────────────────────
# ClinicChoiceScene
# ─────────────────────────────────────────────────────────────────────────────

class ClinicChoiceScene:
    def __init__(self, screen, player_name):
        self.screen      = screen
        self.player_name = player_name
        W, H = SCREEN_W, SCREEN_H
        self.btn_doc  = Button(pygame.Rect(W//2 - 220, H//2 + 20, 200, 56),
                               "Doctor",      colour=(55, 125, 185))
        self.btn_psy  = Button(pygame.Rect(W//2 + 20,  H//2 + 20, 200, 56),
                               "Psychologist",colour=(115, 55, 165))
        self.btn_back = Button(pygame.Rect(W//2 - 80,  H//2 + 100,160, 42),
                               "<- Back",         colour=(75, 75, 75))
        self.f_title = FontCache.get(22, bold=True)
        self.f_body  = FontCache.get(14)

    def handle_event(self, event):
        if self.btn_doc.handle_event(event):
            return ("start_career", {"script": CLINIC_DOCTOR, "role_key": "doctor"})
        if self.btn_psy.handle_event(event):
            return ("start_career", {"script": CLINIC_PSYCH,  "role_key": "psychologist"})
        if self.btn_back.handle_event(event):
            return ("back_to_world", {})
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return ("back_to_world", {})
        return None

    def update(self, dt): pass

    def draw(self, debug=False):
        s = self.screen
        s.fill(C_BG)
        W, H = SCREEN_W, SCREEN_H
        draw_panel(s, pygame.Rect(W//2 - 300, H//2 - 120, 600, 290))
        title = self.f_title.render("The Clinic", True, C_BORDER)
        s.blit(title, (W//2 - title.get_width()//2, H//2 - 110))
        sub = self.f_body.render("Choose your role:", True, C_TEXT)
        s.blit(sub, (W//2 - sub.get_width()//2, H//2 - 60))
        self.btn_doc.draw(s); self.btn_psy.draw(s); self.btn_back.draw(s)
        f12 = FontCache.get(12)
        d1 = f12.render("Diagnose & treat physical conditions", True, C_TEXT_DIM)
        d2 = f12.render("Support mental health & wellbeing",   True, C_TEXT_DIM)
        s.blit(d1, (W//2 - 220, H//2 + 82))
        s.blit(d2, (W//2 + 20,  H//2 + 82))


# ─────────────────────────────────────────────────────────────────────────────
# RealEstateChoiceScene
# ─────────────────────────────────────────────────────────────────────────────

class RealEstateChoiceScene:
    _HOUSES = [
        ("House 1", "Starter Cottage - $480k",  (45, 95, 55)),
        ("House 2", "Family Home - $720k",      (45, 95, 55)),
        ("House 3", "Luxury Estate - $1.45M",   (45, 95, 55)),
    ]

    def __init__(self, screen, player_name, preselect=None):
        self.screen      = screen
        self.player_name = player_name
        W, H = SCREEN_W, SCREEN_H
        self.btns = []
        for i, (label, desc, col) in enumerate(self._HOUSES):
            self.btns.append(Button(
                pygame.Rect(W//2 - 310 + i * 215, H//2 + 10, 195, 60),
                label, colour=col))
        self.btn_back = Button(pygame.Rect(W//2 - 80, H//2 + 100, 160, 42),
                               "<- Back", colour=(75, 75, 75))
        self.f_title = FontCache.get(20, bold=True)

        # If player walked directly into house1/2/3, auto-highlight that button
        self.preselect = preselect

    def handle_event(self, event):
        for i, btn in enumerate(self.btns):
            if btn.handle_event(event):
                return ("start_career", {
                    "role_key":    "realestate",
                    "house_index": i,   # 0=starter, 1=family, 2=luxury
                })
        if self.btn_back.handle_event(event):
            return ("back_to_world", {})
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return ("back_to_world", {})
        return None

    def update(self, dt): pass

    def draw(self, debug=False):
        s = self.screen
        s.fill(C_BG)
        W, H = SCREEN_W, SCREEN_H
        draw_panel(s, pygame.Rect(W//2 - 335, H//2 - 120, 670, 290))
        title = self.f_title.render("The Avenue - Choose a Property", True, C_BORDER)
        s.blit(title, (W//2 - title.get_width()//2, H//2 - 108))
        f12 = FontCache.get(12)
        for i, btn in enumerate(self.btns):
            btn.draw(s)
            desc = self._HOUSES[i][1]
            dl = f12.render(desc, True, C_TEXT_DIM)
            s.blit(dl, (W//2 - 310 + i * 215, H//2 + 76))
        self.btn_back.draw(s)


# ─────────────────────────────────────────────────────────────────────────────
# AICareerScene  – live AI conversation with scrollable chat + expanded input
# ─────────────────────────────────────────────────────────────────────────────

class AICareerScene:
    CHAT_X  = 20;  CHAT_Y = 80;  CHAT_W = 640;  CHAT_H = 400
    INPUT_Y = 492; INPUT_H = 60
    RIGHT_X = 672; RIGHT_W = SCREEN_W - 672 - 10

    ROLE_META = {
        "doctor":       ("Doctor",           "The Clinic - Consultation Room",
                         "Your patient is waiting. Greet them and begin the consultation."),
        "psychologist": ("Psychologist",      "The Clinic - Therapy Room",
                         "Your client is here for their first session. Make them feel safe."),
        "hotel":        ("Hotel Front Desk",  "The Grand Hotel - Reception",
                         "A guest has just arrived. Welcome them warmly."),
        "realestate":   ("Real Estate Agent", "The Avenue",
                         "Your buyer has arrived. Show them what the property has to offer."),
    }
    NPC_NAMES = {
        "doctor": "Mr. Tan", "psychologist": "Mei",
        "hotel": "Ms. Rivera", "realestate": "Client",
    }

    def __init__(self, screen, role, player_name, coins, interior=None, house_index=0):
        from ai_model import AIConversation
        self.screen      = screen
        self.role        = role
        self.player_name = player_name
        self.coins       = coins
        self.interior    = interior

        # Start AI generation in background
        self.ai          = AIConversation(role, player_name, house_index=house_index)

        # Scene state
        self.briefing    = ""
        self.phase       = "loading"
        self._load_t     = 0.0
        self.chat_log    = []
        self.result_data = None
        self.turn        = 0

        # Metadata
        meta = self.ROLE_META.get(role, ("Career", "Scene", ""))
        self.role_label, self.setting, self.context = meta
        self._npc_name   = self.NPC_NAMES.get(role, "NPC")

        # UI state
        self.briefing_tw   = None
        self._input_text   = ""
        self._input_cursor = 0.0
        self._max_chars    = 200
        self._scroll_y     = 0
        self._total_chat_h = 0
        self._scroll_speed = 30
        self._think_t      = 0.0
        self._think_dot    = 0

        self.end_btn = Button(
            pygame.Rect(self.RIGHT_X, SCREEN_H - 60, self.RIGHT_W, 42),
            "End Session", colour=(130, 45, 45))
        self._back_btn = Button(
            pygame.Rect(SCREEN_W//2 - 120, SCREEN_H - 80, 240, 46),
            "Return to Map", colour=(45, 115, 55))

        self.f_title = FontCache.get(17, bold=True)
        self.f_body  = FontCache.get(14)
        self.f_sm    = FontCache.get(13)

    # ── scroll ────────────────────────────────────────────────────────────────

    def _clamp_scroll(self):
        max_scroll = max(0, self._total_chat_h - (self.CHAT_H - 10))
        self._scroll_y = max(0, min(self._scroll_y, max_scroll))

    def _scroll_to_bottom(self):
        self._scroll_y = 0

    # ── input ─────────────────────────────────────────────────────────────────

    def _handle_key(self, event):
        if event.key == pygame.K_RETURN and not (pygame.key.get_mods() & pygame.KMOD_SHIFT):
            val = self._input_text.strip()
            self._input_text = ""
            return val if val else None
        elif event.key == pygame.K_BACKSPACE:
            self._input_text = self._input_text[:-1]
        elif event.unicode and len(self._input_text) < self._max_chars:
            self._input_text += event.unicode
        return None

    # ── events ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if self.phase == "loading":
            return None   # ignore all input while loading

        if self.phase == "briefing":
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                if self.briefing_tw and not self.briefing_tw.done:
                    self.briefing_tw.skip()
                else:
                    self.chat_log.append((self._npc_name, self.ai.opener, C_BLUE))
                    self._scroll_to_bottom()
                    self.phase = "typing"
            return None

        elif self.phase == "typing":
            if event.type == pygame.MOUSEWHEEL:
                self._scroll_y -= event.y * self._scroll_speed
                self._clamp_scroll()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return ("back_to_world", {"earned": 0})
                submitted = self._handle_key(event)
                if submitted:
                    self._player_send(submitted)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.end_btn.rect.collidepoint(event.pos):
                    self._force_end()

        elif self.phase == "thinking":
            if event.type == pygame.MOUSEWHEEL:
                self._scroll_y -= event.y * self._scroll_speed
                self._clamp_scroll()

        elif self.phase == "result":
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return ("back_to_world", {"earned": self.result_data["wage"]})
            if self._back_btn.handle_event(event):
                return ("back_to_world", {"earned": self.result_data["wage"]})

        return None

    def _player_send(self, text):
        self.chat_log.append((self.player_name, text, C_GREEN))
        self.turn += 1
        self.ai.send(text)
        self._scroll_to_bottom()
        self.phase = "thinking"

    def _force_end(self):
        self._set_result("needs_improvement", "Session ended early — always complete the full conversation!", 0, "Keep Practising")

    def _set_result(self, rating, feedback, wage, label):
        self.phase = "result"
        col_map = {"outstanding": "green", "okay": "yellow", "needs_improvement": "red"}
        self.result_data = {
            "label": label, "wage": wage,
            "col": col_map.get(rating, "yellow"),
            "feedback": feedback, "turns": self.turn,
        }

    # ── update ────────────────────────────────────────────────────────────────

    def update(self, dt):
        if self.phase == "loading":
            self._load_t += dt
            if self.ai.loaded:
                # Character is ready — build briefing typewriter and switch phase
                self.briefing    = self.ai.briefing
                self.briefing_tw = TypewriterText(self.briefing, speed=80)
                # Update NPC name from generated character
                char = getattr(self.ai, "_char", {})
                self._npc_name = (
                    char.get("name") or
                    char.get("buyer_name") or
                    self.NPC_NAMES.get(self.role, "NPC")
                )
                self.phase = "briefing"
            return
        if self.phase == "briefing":
            if self.briefing_tw:
                self.briefing_tw.update(dt)
        elif self.phase == "typing":
            self._input_cursor += dt
        elif self.phase == "thinking":
            self._think_t  += dt * 2.5
            self._think_dot = int(self._think_t) % 4
            if self.ai.ready:
                npc_text, done, wage, label, feedback = self.ai.get_result()
                self.chat_log.append((self._npc_name, npc_text, C_BLUE))
                self._scroll_to_bottom()
                if done:
                    self._set_result(
                        "outstanding" if wage == 500 else
                        "okay"        if wage == 250 else
                        "needs_improvement",
                        feedback, wage, label)
                else:
                    self.phase = "typing"

    # ── draw ─────────────────────────────────────────────────────────────────

    def draw(self, debug=False):
        s = self.screen
        if self.interior:
            s.blit(self.interior, (0, 0))
            dim = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            dim.fill((0, 0, 20, 155))
            s.blit(dim, (0, 0))
        else:
            s.fill(C_BG)

        # Header
        draw_panel(s, pygame.Rect(0, 0, SCREEN_W, 68), bg=(8, 8, 28, 245), radius=0)
        s.blit(self.f_title.render(self.role_label, True, C_BORDER), (16, 10))
        s.blit(self.f_sm.render(self.setting, True, C_TEXT_DIM), (16, 36))
        ctx = self.f_sm.render(self.context, True, C_BLUE)
        s.blit(ctx, (SCREEN_W//2 - ctx.get_width()//2, 50))
        turn_s = self.f_sm.render(f"Turn {self.turn}/7", True, C_TEXT_DIM)
        s.blit(turn_s, (SCREEN_W - turn_s.get_width() - 80, 10))
        ai_s = self.f_sm.render("AI", True, C_GREEN)
        s.blit(ai_s, (SCREEN_W - ai_s.get_width() - 16, 10))

        if self.phase == "loading":
            self._draw_loading(s)
        elif self.phase == "briefing":
            self._draw_briefing(s)
        elif self.phase in ("typing", "thinking"):
            self._draw_chat(s)
            self._draw_input(s)
            self._draw_right(s)
        elif self.phase == "result":
            self._draw_result(s)

    def _draw_loading(self, s):
        """Spinner shown while AI generates the character in background."""
        cr = pygame.Rect(self.CHAT_X, self.CHAT_Y,
                         self.CHAT_W + self.RIGHT_W + 12, self.CHAT_H + 80)
        draw_panel(s, cr)
        f = self.f_sm
        # Spinner dots
        dots = "." * (int(self._load_t * 3) % 4)
        lines = [
            "Preparing your scenario" + dots,
            "",
            "The AI is generating a unique character for you.",
            "This takes a few seconds...",
            "",
            "Please wait.",
        ]
        y = cr.y + cr.h // 2 - len(lines) * 12
        for line in lines:
            if line:
                surf = f.render(line, True, C_YELLOW if "Preparing" in line else C_TEXT_DIM)
                s.blit(surf, (cr.x + cr.w//2 - surf.get_width()//2, y))
            y += 26

    def _draw_briefing(self, s):
        cr = pygame.Rect(self.CHAT_X, self.CHAT_Y,
                         self.CHAT_W + self.RIGHT_W + 12, self.CHAT_H + 80)
        draw_panel(s, cr)
        f  = self.f_sm
        lh = f.get_height() + 5   # line height with spacing
        y  = cr.y + 14
        mw = cr.w - 32

        # Split visible text by newline FIRST, then word-wrap each line
        visible = self.briefing_tw.visible
        raw_lines = visible.split("\n")

        for raw_line in raw_lines:
            if raw_line.strip() == "":
                # Blank line — add a small gap
                y += lh // 2
            else:
                # Colour based on content
                if raw_line.startswith("[ GAME MASTER"):
                    col = C_YELLOW
                elif raw_line.startswith("[ YOUR GOAL"):
                    col = C_BORDER
                elif raw_line.startswith("  -"):
                    col = C_TEXT_DIM
                elif raw_line.startswith("  "):
                    col = C_TEXT
                else:
                    col = C_TEXT

                # Word-wrap long lines within the panel width
                for wrapped in (wrap_text(raw_line, f, mw) or [raw_line]):
                    if y + lh < cr.bottom - 30:
                        ls = f.render(wrapped, True, col)
                        s.blit(ls, (cr.x + 14, y))
                    y += lh

        hint_col = C_WHITE if self.briefing_tw.done else C_TEXT_DIM
        hint = f.render("Click or press any key to start...", True, hint_col)
        s.blit(hint, (cr.x + 14, cr.bottom - 26))

    def _draw_chat(self, s):
        cr  = pygame.Rect(self.CHAT_X, self.CHAT_Y, self.CHAT_W, self.CHAT_H)
        draw_panel(s, cr)
        f   = self.f_sm
        lh  = f.get_height() + 3
        mw  = cr.w - 28

        # Build line list
        all_lines = []
        for speaker, text, col in self.chat_log:
            all_lines.append((f"{speaker}:", col, False))
            for ln in wrap_text(text, f, mw - 10):
                all_lines.append((ln, C_TEXT, True))
            all_lines.append(("", C_TEXT, True))

        if self.phase == "thinking":
            dots = "." * self._think_dot
            all_lines.append((f"{self._npc_name} is typing{dots}", C_TEXT_DIM, False))

        self._total_chat_h = len(all_lines) * lh + 20
        self._clamp_scroll()

        # Clip and draw
        s.set_clip(pygame.Rect(cr.x+1, cr.y+1, cr.w-2, cr.h-2))
        y = cr.bottom - 10 - self._total_chat_h + self._scroll_y + 10
        for text, col, indent in all_lines:
            dy = int(y)
            if text and cr.y <= dy <= cr.bottom - lh:
                surf = f.render(text, True, col)
                s.blit(surf, (cr.x + (20 if indent else 10), dy))
            y += lh
        s.set_clip(None)

        # Scrollbar
        if self._total_chat_h > cr.h:
            bh  = max(20, int(cr.h * cr.h / self._total_chat_h))
            ms  = self._total_chat_h - cr.h
            by  = cr.y + int((ms - self._scroll_y) / ms * (cr.h - bh))
            pygame.draw.rect(s, (60,60,90),  pygame.Rect(cr.right-6, cr.y, 5, cr.h), border_radius=3)
            pygame.draw.rect(s, C_BORDER,    pygame.Rect(cr.right-6, by,  5, bh),    border_radius=3)
            hint = f.render("^ scroll", True, C_TEXT_DIM)
            s.blit(hint, (cr.right - hint.get_width() - 10, cr.y + 4))

    def _draw_input(self, s):
        ir  = pygame.Rect(self.CHAT_X, self.INPUT_Y, self.CHAT_W, self.INPUT_H)
        pygame.draw.rect(s, (20,20,45), ir, border_radius=6)
        bcol = C_BORDER if self.phase == "typing" else (60,60,80)
        pygame.draw.rect(s, bcol, ir, 2, border_radius=6)

        if self.phase == "typing":
            display = self._input_text + ("|" if int(self._input_cursor*2)%2==0 else "")
            col = C_WHITE
        else:
            display = "Waiting for response…"
            col = C_TEXT_DIM

        f    = self.f_sm
        mw   = ir.w - 16
        lines = (wrap_text(display, f, mw) or [""])[-2:]
        y = ir.y + (ir.h - len(lines) * (f.get_height()+2)) // 2
        for ln in lines:
            s.blit(f.render(ln, True, col), (ir.x+8, y))
            y += f.get_height() + 2

        counter = f.render(f"{len(self._input_text)}/{self._max_chars}", True, C_TEXT_DIM)
        s.blit(counter, (ir.right - counter.get_width()-6, ir.bottom - counter.get_height()-4))
        if self.phase == "typing" and self._input_text:
            hint = f.render("Enter ↵ to send", True, C_TEXT_DIM)
            s.blit(hint, (ir.x+8, ir.bottom - hint.get_height()-4))

    def _draw_right(self, s):
        rr = pygame.Rect(self.RIGHT_X, self.CHAT_Y, self.RIGHT_W, SCREEN_H - self.CHAT_Y - 10)
        draw_panel(s, rr)
        f = self.f_sm
        y = rr.y + 14

        tip_t = f.render("💡 Tips", True, C_BORDER)
        s.blit(tip_t, (rr.x+10, y)); y += tip_t.get_height() + 10

        tips = {
            "doctor":       ["Greet your patient warmly","Ask open questions",
                             "Listen before advising","Explain what you're doing","Reassure the patient"],
            "psychologist": ["Create a safe space","Validate feelings first",
                             "Use open questions","Reflect back what they say","Don't rush to solutions"],
            "hotel":        ["Greet Ms. Rivera warmly","Use her name",
                             "Be proactive","Offer specifics","Anticipate her needs"],
            "realestate":   ["Ask what they need first","Be specific about the property",
                             "Acknowledge the bathroom","Use market comparables","Close with a next step"],
        }.get(self.role, [])

        for tip in tips:
            ts = f.render(f"• {tip}", True, C_TEXT_DIM)
            if y + ts.get_height() < rr.y + 210:
                s.blit(ts, (rr.x+10, y))
            y += ts.get_height() + 7

        y = max(y+10, rr.y+220)
        bw  = rr.w - 20
        pct = self.turn / 7
        pygame.draw.rect(s, (40,40,60), pygame.Rect(rr.x+10, y, bw, 10), border_radius=4)
        if pct > 0:
            col = C_GREEN if pct < 0.6 else C_YELLOW if pct < 0.86 else C_RED
            pygame.draw.rect(s, col, pygame.Rect(rr.x+10, y, int(bw*pct), 10), border_radius=4)
        y += 18
        pg = f.render(f"Progress: {self.turn}/7 messages", True, C_TEXT_DIM)
        s.blit(pg, (rr.x+10, y)); y += pg.get_height() + 16

        st = f.render("[ Scoring ]", True, C_BORDER)
        s.blit(st, (rr.x+10, y)); y += st.get_height() + 8
        for line, col in [("Outstanding  500 coins", C_GREEN),
                          ("Solid Work   250 coins", C_YELLOW),
                          ("Keep Practising 100 coins", C_RED)]:
            ls = f.render(line, True, col)
            s.blit(ls, (rr.x+10, y)); y += ls.get_height() + 6

        self.end_btn.draw(s)
        esc = f.render("[ESC] Exit (no pay)", True, (150,65,65))
        s.blit(esc, (rr.x+10, SCREEN_H-70))

    def _draw_result(self, s):
        rd   = self.result_data
        band = rd["col"]   # "green", "yellow", "red"
        col  = {"green": C_GREEN, "yellow": C_YELLOW, "red": C_RED}.get(band, C_WHITE)

        pr = pygame.Rect(SCREEN_W//2-300, 70, 600, SCREEN_H-160)
        draw_panel(s, pr)
        y = pr.y + 24

        # Title varies by band
        title_text = {
            "green":  "Session Complete!",
            "yellow": "Session Complete!",
            "red":    "Session Complete!",
        }.get(band, "Session Complete!")
        title = self.f_title.render(title_text, True, C_BORDER)
        s.blit(title, (SCREEN_W//2 - title.get_width()//2, y)); y += 46

        # Rating label — larger, coloured, no emoji
        rating = FontCache.get(22, bold=True).render(rd["label"], True, col)
        s.blit(rating, (SCREEN_W//2 - rating.get_width()//2, y)); y += 52

        # Turns
        ts = self.f_body.render(f"Turns completed: {rd['turns']} / 7", True, C_TEXT)
        s.blit(ts, (SCREEN_W//2 - ts.get_width()//2, y)); y += 38

        # Coins earned
        ws = FontCache.get(18, bold=True).render(f"Coins earned: {rd['wage']}", True, C_YELLOW)
        s.blit(ws, (SCREEN_W//2 - ws.get_width()//2, y)); y += 52

        # Feedback header varies by band
        fb_header = {
            "green":  "What you did well:",
            "yellow": "How to improve:",
            "red":    "Keep Practising:",
        }.get(band, "Feedback:")
        fl = self.f_body.render(fb_header, True, col)
        s.blit(fl, (pr.x+32, y)); y += 30

        # Feedback text
        fb = rd.get("feedback") or "Keep practising your communication skills!"
        for line in wrap_text(fb, self.f_sm, pr.w-64):
            ls = self.f_sm.render(line, True, C_TEXT)
            s.blit(ls, (pr.x+40, y)); y += ls.get_height() + 5

        # Extra encouragement line for needs_improvement
        if band == "red":
            y += 10
            enc = self.f_sm.render("Try again — focus on greeting warmly and asking questions.", True, C_RED)
            for line in wrap_text("Try again — focus on greeting warmly and asking questions.", self.f_sm, pr.w-64):
                ls = self.f_sm.render(line, True, C_RED)
                s.blit(ls, (pr.x+40, y)); y += ls.get_height() + 4

        y += 18
        note = self.f_sm.render("Press [Enter] or click below to return", True, C_TEXT_DIM)
        s.blit(note, (SCREEN_W//2 - note.get_width()//2, y))
        self._back_btn.draw(s)