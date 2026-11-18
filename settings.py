
import pygame


WHITE = (245, 245, 255)
GOLD = (255, 204, 90)
SKY = (10, 15, 45)
BUTTON_COLOR = (65, 85, 125)
BUTTON_HOVER = (100, 125, 175)
DISABLED_COLOR = (55, 60, 75)


def draw_option(screen, font, text, rect, selected, enabled=True):
    """Ve mot nut lua chon."""

    mouse_pos = pygame.mouse.get_pos()

    if not enabled:
        color = DISABLED_COLOR
    elif selected:
        color = (65, 115, 85)
    elif rect.collidepoint(mouse_pos):
        color = BUTTON_HOVER
    else:
        color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=8
    )

    border_color = GOLD if selected else WHITE

    pygame.draw.rect(
        screen,
        border_color,
        rect,
        width=2,
        border_radius=8
    )

    text_surface = font.render(text, True, WHITE)

    screen.blit(
        text_surface,
        text_surface.get_rect(center=rect.center)
    )


def draw_settings(screen, width, height, settings):
    """Ve trang cai dat."""

    screen.fill(SKY)

    title_font = pygame.font.Font(None, 65)
    label_font = pygame.font.Font(None, 30)
    option_font = pygame.font.Font(None, 27)
    button_font = pygame.font.Font(None, 34)
    note_font = pygame.font.Font(None, 23)

    title = title_font.render(
        "GAME SETTINGS",
        True,
        GOLD
    )

    screen.blit(
        title,
        title.get_rect(center=(width // 2, 65))
    )

    # Cac nhom lua chon
    groups = [
        ("Level", "level", ["HSK5", "HSK6"]),
        ("Content", "content_type", ["Words", "Sentences"]),
        (
            "Translation",
            "translation_mode",
            ["Chinese -> Vietnamese", "Vietnamese -> Chinese"]
        ),
        ("Target speed", "target_speed", ["Slow", "Normal", "Fast"])
    ]

    # Tao cac nut va luu lai Rect de xu ly su kien
    buttons = {}

    y = 145

    for group_name, key, options in groups:

        label = label_font.render(
            group_name,
            True,
            WHITE
        )

        screen.blit(label, (width // 2 - 330, y))

        buttons[key] = []

        if key == "translation_mode":
            button_width = 240
            gap = 15
        elif key == "target_speed":
            button_width = 130
            gap = 15
        else:
            button_width = 180
            gap = 20

        total_width = (
            len(options) * button_width
            + (len(options) - 1) * gap
        )

        start_x = width // 2 - total_width // 2

        for index, option in enumerate(options):

            rect = pygame.Rect(
                start_x + index * (button_width + gap),
                y + 35,
                button_width,
                48
            )

            # Chuyen ten hien thi thanh gia tri luu trong settings
            if key == "content_type":
                value = option.lower()

            elif key == "translation_mode":
                value = (
                    "zh_to_vi"
                    if index == 0
                    else "vi_to_zh"
                )

            elif key == "target_speed":
                value = ["slow", "normal", "fast"][index]

            else:
                value = option

            # Cac lua chon chua duoc ket noi voi gameplay
            enabled = not (
                (key == "level" and value == "HSK6")
                or (key == "content_type" and value == "sentences")
                or (key == "translation_mode" and value == "vi_to_zh")
            )

            draw_option(
                screen,
                option_font,
                option,
                rect,
                settings[key] == value,
                enabled
            )

            buttons[key].append({
                "rect": rect,
                "value": value,
                "enabled": enabled
            })

        y += 115

    # Ghi chu ve pham vi ho tro hien tai
    note = note_font.render(
        "Current version: HSK5 vocabulary, Chinese -> Vietnamese",
        True,
        GOLD
    )

    screen.blit(
        note,
        note.get_rect(center=(width // 2, height - 125))
    )

    # Nut BACK
    back_rect = pygame.Rect(
        width // 2 - 170,
        height - 75,
        140,
        50
    )

    draw_option(
        screen,
        button_font,
        "BACK",
        back_rect,
        False
    )

    # Nut START
    start_rect = pygame.Rect(
        width // 2 + 30,
        height - 75,
        140,
        50
    )

    draw_option(
        screen,
        button_font,
        "START",
        start_rect,
        False
    )

    return buttons, back_rect, start_rect


def handle_settings_event(event, buttons, back_rect, start_rect, settings):
    """Xu ly cac thao tac tren trang Settings."""

    if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
        return None

    # Nhan BACK
    if back_rect.collidepoint(event.pos):
        return "menu"

    # Nhan START
    if start_rect.collidepoint(event.pos):
        return "game"

    # Nhan cac lua chon
    for key, option_list in buttons.items():

        for option in option_list:

            if (
                option["enabled"]
                and option["rect"].collidepoint(event.pos)
            ):
                settings[key] = option["value"]
                return None

    return None
