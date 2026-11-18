
import pygame


# Mau sac giao dien
WHITE = (245, 245, 255)
GOLD = (255, 204, 90)
SKY = (10, 15, 45)
DARK_BLUE = (25, 35, 65)
BUTTON_COLOR = (65, 85, 125)
BUTTON_HOVER = (100, 125, 175)


def draw_menu(screen, width, height):
    """Ve giao dien trang chu."""

    screen.fill(SKY)

    title_font = pygame.font.Font(None, 90)
    subtitle_font = pygame.font.Font(None, 32)
    button_font = pygame.font.Font(None, 45)

    # Tieu de game
    title = title_font.render(
        "CHINESE ARCHERY",
        True,
        GOLD
    )
    screen.blit(
        title,
        title.get_rect(center=(width // 2, height // 3))
    )

    # Gioi thieu
    subtitle = subtitle_font.render(
        "Learn Chinese through an archery game",
        True,
        WHITE
    )
    screen.blit(
        subtitle,
        subtitle.get_rect(center=(width // 2, height // 3 + 75))
    )

    # Nut PLAY
    button_width = 240
    button_height = 65

    play_button = pygame.Rect(
        (width - button_width) // 2,
        height // 2 + 70,
        button_width,
        button_height
    )

    mouse_pos = pygame.mouse.get_pos()

    color = (
        BUTTON_HOVER
        if play_button.collidepoint(mouse_pos)
        else BUTTON_COLOR
    )

    pygame.draw.rect(
        screen,
        color,
        play_button,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        GOLD,
        play_button,
        width=2,
        border_radius=12
    )

    play_text = button_font.render(
        "PLAY",
        True,
        WHITE
    )

    screen.blit(
        play_text,
        play_text.get_rect(center=play_button.center)
    )

    return play_button


def handle_menu_event(event, play_button):
    """Kiem tra nguoi choi co nhan nut PLAY khong."""

    if (
        event.type == pygame.MOUSEBUTTONDOWN
        and event.button == 1
        and play_button.collidepoint(event.pos)
    ):
        return "settings"

    return None
