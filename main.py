import os
import random
import math
import pygame
from word_loader import load_words
from menu import draw_menu, handle_menu_event
from settings import draw_settings, handle_settings_event
from audio_manager import AudioManager


# ==================================================
# 1. KHOI TAO PYGAME VA AM THANH
# ==================================================
pygame.init() #khi chương trình dùng pygame, phải init để các module pygame sẵn sàng hoạt động như bàn phím, âm thanh,...

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) #lấy đường dẫn tuyệt đối đến thư mục đang chứa file hiện tại (main.py)
# os.path.abspath: đường dẫn tuyệt đối đến file (có chứa cả tên file)
# os.path.dirname: sau khi có đường dẫn tuyệt đối, không lấy tên file, chỉ lấy folder
SOUNDS_DIR = os.path.join(BASE_DIR, "sounds") # ghép thêm thư mục sounds vào để đến thư mục âm thanh
audio_manager = AudioManager(SOUNDS_DIR)

try:
    pygame.mixer.init() #khởi tạo module chuyên xử lý âm thanh của pygame, nếu khởi tạo thành công
    #thì đặt gán biến SOUND_ENABLED = True, không khởi tạo được module mixer thì gán SOUND_ENABLED = False và raise exception
    SOUND_ENABLED = True
except pygame.error as exc:
    SOUND_ENABLED = False
    print(f"Khong khoi tao duoc am thanh: {exc}")

# ==================================================
# 2. CAI DAT CUA SO GAME
# ==================================================
screen_info = pygame.display.Info() #lấy thông tin về màn hình hiện tại  (đơn vị là pixel), mục đích là để game nhận diện kích thước màn hình tự động
#không cần fix bất cứ giá trị cụ thể nào cho màn hình, và mỗi màn hình có 1 kích thước khác nhau.
WIDTH = screen_info.current_w   #lấy chiều rộng màn hình hiện tại
HEIGHT = screen_info.current_h  #lấy chiều cao màn hình hiện tại

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN) #tạo màn hình hiển thị game.
# WIDTH, HEIGHT: kích thước màn hình
# pygame.FULLSCREEN: yêu cầu chạy ở chế độ toàn màn hình. lưu vào biến screen để sau này còn tái sử dụng
pygame.display.set_caption("Chinese Archery")   #tên cửa sổ game

clock = pygame.time.Clock() #tạo đối tượng để kiểm soát tốc độ khung hình FPS của game
pygame.key.start_text_input()   #bật chế độ nhập văn bản vào bàn phím


# ==================================================
# 3. MAU SAC VA THONG SO
# ==================================================
WHITE = (245, 245, 255) #theo chuẩn RGB
BLACK = (25, 25, 35)
SKY = (10, 15, 45)

GROUND_COLOR = (91, 57, 39)
GROUND_TOP = (145, 100, 60)

GOLD = (255, 204, 90)
GREEN = (100, 255, 150)
RED = (255, 100, 100)

BROWN = (130, 76, 42)
DARK_BROWN = (65, 39, 30)

GROUND_HEIGHT = 100
GROUND_Y = HEIGHT - GROUND_HEIGHT

bow_x = WIDTH // 4
bow_y = GROUND_Y - 25

# Toc do muc tieu: cham hon phien ban ban dau
TARGET_SPEED = max(1.0, HEIGHT / 750)

# Toc do mui ten, don vi pixel/giay
ARROW_SPEED = 2000


# ==================================================
# 4. FONT CHU
# ==================================================
def load_font(size, paths):
    for path in paths: #truyen vao 1 thu muc nhieu file
        if os.path.isfile(path):    #tung duong dan neu la file thi return font cua file va size
            try:
                return pygame.font.Font(path, size)
            except (pygame.error, OSError): #neu co loi thi bo qua
                pass

    return pygame.font.Font(None, size)


vietnamese_font_paths = [
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/tahoma.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
]

chinese_font_paths = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simhei.ttf",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/arial.ttf",
]

target_font = load_font(30, chinese_font_paths)
input_font = load_font(25, vietnamese_font_paths)
ui_font = load_font(24, vietnamese_font_paths)


# ==================================================
# 5. DOC DU LIEU TU VUNG
# ==================================================
words_path = os.path.join(BASE_DIR, "data", "HSK5_words.txt")
words = load_words(words_path)

if not words:
    pygame.quit()
    raise ValueError(
        "Khong co tu vung. Hay kiem tra data/HSK5_words.txt"
    )


# ==================================================
# 6. TRANG THAI GAME
# ==================================================
# Trang hien tai
current_screen = "menu"

# Cau hinh mac dinh
settings = {
    "level": "HSK5",
    "content_type": "words",
    "translation_mode": "zh_to_vi",
    "target_speed": "normal"
}

# Cac vung bam tren giao dien
play_button = None
settings_buttons = None
back_button = None
start_button = None

score = 0
answer_text = ""

feedback = ""
feedback_color = WHITE

current_word = None
target_x = 0
target_y = -60

game_over = False
show_word_meaning = False  # Hien nghia tu truoc khi Game Over

arrows = []
particles = []

stars = [
    (
        random.randint(0, WIDTH),
        random.randint(0, max(1, GROUND_Y - 50)),
        random.choice([1, 1, 1, 2]),
    )
    for _ in range(120)
]



def new_target():
    global current_word, target_x, target_y

    current_word = random.choice(words)
    target_x = random.randint(60, max(60, WIDTH - 60))
    target_y = -60

    # Tao truoc am thanh cho tu vua xuat hien
    audio_manager.prepare_pronunciation(current_word["chinese"])


new_target()


# ==================================================
# 7. VE PHONG CANH
# ==================================================
def draw_background():
    screen.fill(SKY)

    for x, y, size in stars:
        pygame.draw.circle(
            screen,
            (180, 190, 230),
            (x, y),
            size,
        )

    pygame.draw.rect(
        screen,
        GROUND_COLOR,
        (0, GROUND_Y, WIDTH, GROUND_HEIGHT),
    )

    pygame.draw.line(
        screen,
        GROUND_TOP,
        (0, GROUND_Y),
        (WIDTH, GROUND_Y),
        4,
    )


# ==================================================
# 8. VE CUNG
# ==================================================
def draw_bow():
    upper_points = [
        (bow_x, bow_y),
        (bow_x + 17, bow_y - 22),
        (bow_x + 25, bow_y - 48),
        (bow_x + 22, bow_y - 76),
        (bow_x + 10, bow_y - 103),
        (bow_x - 8, bow_y - 125),
        (bow_x - 22, bow_y - 132),
    ]

    lower_points = [
        (bow_x, bow_y),
        (bow_x + 17, bow_y + 22),
        (bow_x + 25, bow_y + 48),
        (bow_x + 22, bow_y + 76),
        (bow_x + 10, bow_y + 103),
        (bow_x - 8, bow_y + 125),
        (bow_x - 22, bow_y + 132),
    ]

    upper_tip = upper_points[-1]
    lower_tip = lower_points[-1]

    pygame.draw.lines(
        screen, DARK_BROWN, False, upper_points, 13
    )
    pygame.draw.lines(
        screen, BROWN, False, upper_points, 7
    )

    pygame.draw.lines(
        screen, DARK_BROWN, False, lower_points, 13
    )
    pygame.draw.lines(
        screen, BROWN, False, lower_points, 7
    )

    # Day cung
    pygame.draw.line(
        screen,
        (225, 220, 195),
        upper_tip,
        lower_tip,
        2,
    )

    # Tay cam
    pygame.draw.line(
        screen,
        (220, 160, 75),
        (bow_x, bow_y - 13),
        (bow_x, bow_y + 13),
        15,
    )

    pygame.draw.line(
        screen,
        DARK_BROWN,
        (bow_x, bow_y - 13),
        (bow_x, bow_y + 13),
        3,
    )

    pygame.draw.circle(
        screen, GOLD, (bow_x, bow_y), 5
    )


# ==================================================
# 9. VE MUI TEN
# ==================================================
def draw_arrow(x1, y1, x2, y2):
    pygame.draw.line(
        screen,
        (225, 205, 160),
        (int(x1), int(y1)),
        (int(x2), int(y2)),
        4,
    )

    angle = math.atan2(y2 - y1, x2 - x1)

    head_length = 17
    head_angle = math.radians(27)

    left = (
        x2 - head_length * math.cos(angle - head_angle),
        y2 - head_length * math.sin(angle - head_angle),
    )

    right = (
        x2 - head_length * math.cos(angle + head_angle),
        y2 - head_length * math.sin(angle + head_angle),
    )

    pygame.draw.polygon(
        screen,
        (245, 240, 220),
        [(x2, y2), left, right],
    )


def draw_aiming_arrow():
    dx = target_x - bow_x
    dy = target_y - bow_y

    distance = math.hypot(dx, dy)

    if distance == 0:
        return

    length = 75

    end_x = bow_x + dx / distance * length
    end_y = bow_y + dy / distance * length

    draw_arrow(
        bow_x,
        bow_y,
        end_x,
        end_y,
    )


# ==================================================
# 10. O NHAP DAP AN
# ==================================================
def draw_answer_box():
    box_width = min(340, WIDTH // 3)
    box_height = 48

    box_x = WIDTH - box_width - 30
    box_y = GROUND_Y + (GROUND_HEIGHT - box_height) // 2

    pygame.draw.rect(
        screen,
        (245, 242, 232),
        (box_x, box_y, box_width, box_height),
        border_radius=8,
    )

    pygame.draw.rect(
        screen,
        GOLD,
        (box_x, box_y, box_width, box_height),
        width=2,
        border_radius=8,
    )

    shown_text = answer_text
    max_width = box_width - 28

    while (
        shown_text
        and input_font.size(shown_text)[0] > max_width
    ):
        shown_text = shown_text[1:]

    text_surface = input_font.render(
        shown_text, True, BLACK
    )

    text_x = box_x + 12
    text_y = box_y + (
        box_height - text_surface.get_height()
    ) // 2

    screen.blit(text_surface, (text_x, text_y))

    # Con tro nhap lieu
    cursor_x = text_x + text_surface.get_width() + 2

    if cursor_x < box_x + box_width - 8:
        pygame.draw.line(
            screen,
            BLACK,
            (cursor_x, box_y + 10),
            (cursor_x, box_y + box_height - 10),
            2,
        )


# ==================================================
# 11. HIEU UNG PHAO HOA
# ==================================================
def create_explosion(x, y):
    for _ in range(32):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(80, 280)

        particles.append({
            "x": float(x),
            "y": float(y),
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed,
            "life": random.uniform(0.35, 0.8),
            "max_life": 0.8,
            "color": random.choice([
                GOLD,
                (255, 120, 100),
                (120, 220, 255),
                WHITE,
                (170, 120, 255),
            ]),
        })


def update_and_draw_particles(dt):
    remaining = []

    for particle in particles:
        particle["x"] += particle["vx"] * dt
        particle["y"] += particle["vy"] * dt
        particle["vy"] += 180 * dt
        particle["life"] -= dt

        if particle["life"] > 0:
            radius = max(
                1,
                int(
                    4 * particle["life"]
                    / particle["max_life"]
                ),
            )

            pygame.draw.circle(
                screen,
                particle["color"],
                (
                    int(particle["x"]),
                    int(particle["y"]),
                ),
                radius,
            )

            remaining.append(particle)

    particles[:] = remaining


# ==================================================
# 12. KIEM TRA DAP AN
# ==================================================

def check_answer():
    global answer_text, feedback, feedback_color, score

    if not answer_text.strip() or game_over:
        return

    user_answer = answer_text.strip().casefold()

    meanings = current_word.get("meanings", [])

    correct = any(
        user_answer == meaning.strip().casefold()
        for meaning in meanings
    )

    # Luu lai tu dang tra loi
    word_to_speak = current_word["chinese"]

    # Xoa o nhap sau moi lan nhan Enter
    answer_text = ""

    if correct:
        feedback = "Chinh xac!"
        feedback_color = GREEN
        score += 1

        arrows.append({
            "start_x": float(bow_x),
            "start_y": float(bow_y),
            "end_x": float(target_x),
            "end_y": float(target_y),
            "x": float(bow_x),
            "y": float(bow_y),
            "progress": 0.0,

            # Luu tu cua muc tieu nay vao mui ten
            "chinese": word_to_speak,
        })

        # Tao muc tieu moi ngay lap tuc
        new_target()

    else:
        audio_manager.play_effect_then_speak(
            "wrong",
            word_to_speak
        )

        feedback = "Sai roi!"
        feedback_color = RED


# ==================================================
# 13. HIEN NGHIA TU VUNG TRUOC GAME OVER
# ==================================================
def draw_word_meaning():
    # Lop nen toi trong suot
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 8, 25, 235))
    screen.blit(overlay, (0, 0))

    panel_width = min(820, WIDTH - 50)
    panel_height = min(500, HEIGHT - 50)
    panel_x = (WIDTH - panel_width) // 2
    panel_y = (HEIGHT - panel_height) // 2

    pygame.draw.rect(
        screen,
        (25, 35, 65),
        (panel_x, panel_y, panel_width, panel_height),
        border_radius=20,
    )
    pygame.draw.rect(
        screen,
        GOLD,
        (panel_x, panel_y, panel_width, panel_height),
        width=3,
        border_radius=20,
    )

    title_surface = ui_font.render(
        "Tu ban vua bo lo", True, GOLD
    )
    screen.blit(
        title_surface,
        title_surface.get_rect(center=(WIDTH // 2, panel_y + 48)),
    )

    chinese_surface = target_font.render(
        current_word.get("chinese", ""), True, WHITE
    )
    screen.blit(
        chinese_surface,
        chinese_surface.get_rect(center=(WIDTH // 2, panel_y + 120)),
    )

    meaning_title = ui_font.render(
        "Nghia tieng Viet:", True, (180, 200, 235)
    )
    screen.blit(
        meaning_title,
        meaning_title.get_rect(center=(WIDTH // 2, panel_y + 175)),
    )

    meanings = current_word.get("meanings", [])
    if isinstance(meanings, str):
        meanings = [meanings]
    meanings = [str(m).strip() for m in meanings if str(m).strip()]

    max_text_width = panel_width - 70
    y = panel_y + 220
    line_height = ui_font.get_linesize() + 5

    for meaning in meanings:
        # Tu dong xuong dong voi nghia dai.
        remaining = meaning.split()
        line = ""
        lines = []
        for word in remaining:
            candidate = f"{line} {word}".strip()
            if ui_font.size(candidate)[0] <= max_text_width:
                line = candidate
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)

        for line in lines:
            if y > panel_y + panel_height - 75:
                break
            surface = ui_font.render(line, True, WHITE)
            screen.blit(
                surface,
                surface.get_rect(center=(WIDTH // 2, y)),
            )
            y += line_height

        if y > panel_y + panel_height - 75:
            break

    prompt = ui_font.render(
        "Nhan Enter de tiep tuc", True, GOLD
    )
    screen.blit(
        prompt,
        prompt.get_rect(
            center=(WIDTH // 2, panel_y + panel_height - 32)
        ),
    )


# ==================================================
# 14. VONG LAP GAME
# ==================================================
running = True

while running:
    dt = min(clock.tick(60) / 1000.0, 0.05)

    # ----------------------------------------------
    # Xu ly su kien ban phim
    # ----------------------------------------------

    # ----------------------------------------------
    # Xu ly su kien
    # ----------------------------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            # Chi xu ly phim khi dang choi game
            elif current_screen == "game":

                if event.key == pygame.K_RETURN:

                    if show_word_meaning:
                        show_word_meaning = False
                        game_over = True

                    elif game_over:
                        score = 0
                        game_over = False
                        show_word_meaning = False
                        arrows.clear()
                        particles.clear()
                        answer_text = ""
                        feedback = ""
                        feedback_color = WHITE
                        new_target()

                    else:
                        if answer_text.strip():
                            # Kiem tra dap an nhu logic cu
                            check_answer()

                elif (
                        event.key == pygame.K_BACKSPACE
                        and not game_over
                        and not show_word_meaning
                ):
                    answer_text = answer_text[:-1]
        # Nhan van ban Unicode
        elif event.type == pygame.TEXTINPUT:

            if (
                current_screen == "game"
                and not game_over
                and not show_word_meaning
            ):
                answer_text += event.text

        # Xu ly click chuot tren Menu
        if current_screen == "menu":

            if play_button is not None:
                action = handle_menu_event(event, play_button)

                if action == "settings":
                    current_screen = "settings"

        # Xu ly click chuot tren Settings
        elif current_screen == "settings":

            if settings_buttons is not None:

                action = handle_settings_event(
                    event,
                    settings_buttons,
                    back_button,
                    start_button,
                    settings
                )

                if action == "menu":
                    current_screen = "menu"

                elif action == "game":

                    # Chuyen toc do duoc chon thanh toc do gameplay
                    speed_levels = {
                        "slow": 0.7,
                        "normal": 1.0,
                        "fast": 1.5
                    }

                    TARGET_SPEED = (
                        max(1.0, HEIGHT / 750)
                        * speed_levels[settings["target_speed"]]
                    )

                    # Reset trang thai game khi bat dau
                    score = 0
                    answer_text = ""
                    feedback = ""
                    feedback_color = WHITE
                    game_over = False
                    show_word_meaning = False

                    arrows.clear()
                    particles.clear()

                    new_target()

                    # Bat che do nhap van ban Unicode
                    pygame.key.start_text_input()

                    current_screen = "game"

    # ----------------------------------------------
    # Hien thi Menu hoac Settings
    # ----------------------------------------------
    if current_screen == "menu":

        play_button = draw_menu(screen, WIDTH, HEIGHT)

        pygame.display.flip()
        continue

    elif current_screen == "settings":

        (
            settings_buttons,
            back_button,
            start_button
        ) = draw_settings(
            screen,
            WIDTH,
            HEIGHT,
            settings
        )

        pygame.display.flip()
        continue

    audio_manager.update()
    # ----------------------------------------------
    # Cap nhat muc tieu
    # ----------------------------------------------
    if not game_over and not show_word_meaning:
        target_y += TARGET_SPEED * dt * 60

        target_surface = target_font.render(
            current_word["chinese"],
            True,
            WHITE,
        )

        target_rect = target_surface.get_rect(
            center=(target_x, int(target_y))
        )

        if target_rect.bottom >= GROUND_Y:
            # Tam dung game va cho nguoi choi xem nghia truoc.
            show_word_meaning = True
            answer_text = ""

    # ----------------------------------------------
    # Cap nhat mui ten
    # Phat hit.mp3 khi mui ten cham muc tieu
    # ---------------------------------------------
    remaining_arrows = []

    for arrow in arrows:
        dx = arrow["end_x"] - arrow["start_x"]
        dy = arrow["end_y"] - arrow["start_y"]

        distance = math.hypot(dx, dy)

        if distance > 0:
            arrow["progress"] += (
                    ARROW_SPEED * dt / distance
            )

        t = min(arrow["progress"], 1.0)

        arrow["x"] = arrow["start_x"] + dx * t
        arrow["y"] = arrow["start_y"] + dy * t

        if t >= 1.0:
            audio_manager.play_effect_then_speak(
                "hit",
                arrow["chinese"]
            )

            create_explosion(
                arrow["end_x"],
                arrow["end_y"],
            )

        else:
            remaining_arrows.append(arrow)

    arrows = remaining_arrows

    # ----------------------------------------------
    # Ve man hinh
    # ----------------------------------------------
    draw_background()

    if not game_over and not show_word_meaning:
        target_surface = target_font.render(
            current_word["chinese"],
            True,
            WHITE,
        )

        target_rect = target_surface.get_rect(
            center=(target_x, int(target_y))
        )

        screen.blit(target_surface, target_rect)

        draw_bow()
        draw_aiming_arrow()

    # Ve cac mui ten dang bay
    for arrow in arrows:
        draw_arrow(
            arrow["start_x"],
            arrow["start_y"],
            arrow["x"],
            arrow["y"],
        )

    # Ve phao hoa
    update_and_draw_particles(dt)

    # Diem so
    score_surface = ui_font.render(
        f"Score: {score}",
        True,
        GOLD,
    )

    screen.blit(score_surface, (30, 25))

    # Phan hoi dung/sai
    if feedback:
        feedback_surface = ui_font.render(
            feedback,
            True,
            feedback_color,
        )

        screen.blit(feedback_surface, (30, 65))

    # O nhap dap an, man hinh nghia, hoac Game Over
    if show_word_meaning:
        draw_word_meaning()

    elif not game_over:
        draw_answer_box()

    else:
        over_surface = target_font.render(
            "GAME OVER",
            True,
            RED,
        )

        over_rect = over_surface.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 - 30)
        )

        screen.blit(over_surface, over_rect)

        score_surface_over = ui_font.render(
            f"Score: {score}", True, GOLD
        )
        score_rect_over = score_surface_over.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 20)
        )
        screen.blit(score_surface_over, score_rect_over)

        restart_surface = ui_font.render(
            "Enter = choi lai",
            True,
            WHITE,
        )

        restart_rect = restart_surface.get_rect(
            center=(WIDTH // 2, HEIGHT // 2 + 65)
        )

        screen.blit(restart_surface, restart_rect)

    pygame.display.flip()


# ==================================================
# 14. DONG GAME
# ==================================================
pygame.key.stop_text_input()

audio_manager.stop()

pygame.quit()