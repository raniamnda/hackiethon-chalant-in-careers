"""
CareerQuest – Main entry point
Run with:  python main.py
Requires:  pip install pygame numpy
"""

import pygame
from constants import SCREEN_W, SCREEN_H, FPS, TITLE
from game import Game


def main():
    pygame.init()

    # Initialise mixer explicitly before anything else
    try:
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        print("[music] Mixer initialised OK")
    except Exception as e:
        print(f"[music] Mixer failed to init: {e} — game will run without sound")

    pygame.display.set_caption(TITLE)
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    clock  = pygame.time.Clock()

    game = Game(screen)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)

        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.mixer.music.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
