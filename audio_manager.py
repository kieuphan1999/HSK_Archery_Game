
import os
import asyncio
import threading
import tempfile
import time

import pygame
import edge_tts


class AudioManager:

    def __init__(self, sounds_dir):
        self.sounds_dir = sounds_dir
        self.sound_enabled = False

        # Khoi tao pygame mixer
        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except pygame.error as exc:
            print(f"[AUDIO] Khong khoi tao duoc am thanh: {exc}")

        self.channel = None
        self.hit_sound = None
        self.wrong_sound = None

        # Cache am thanh TTS
        self.speech_cache = {}
        self.cache_lock = threading.Lock()

        # Trang thai phat am thanh
        self.pending_word = None
        self.pending_speech = None
        self.waiting_for_speech = False

        # Bien theo doi thoi gian
        self.effect_start_time = None
        self.effect_end_time = None
        self.waiting_logged = False

        if self.sound_enabled:
            self.channel = pygame.mixer.Channel(1)

            self.hit_sound = self.load_sound("hit.mp3", 0.6)
            self.wrong_sound = self.load_sound("wrong.mp3", 0.6)

            self.play_background_music()

    # -----------------------------------------
    # LOAD SOUND
    # -----------------------------------------
    def load_sound(self, filename, volume=0.5):
        path = os.path.join(self.sounds_dir, filename)

        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(volume)
            return sound

        except (pygame.error, OSError) as exc:
            print(f"[AUDIO] Khong tai duoc {filename}: {exc}")
            return None

    # -----------------------------------------
    # BACKGROUND MUSIC
    # -----------------------------------------
    def play_background_music(self):
        path = os.path.join(
            self.sounds_dir,
            "background.mp3"
        )

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)

        except pygame.error as exc:
            print(f"[AUDIO] Loi phat nhac nen: {exc}")

    # -----------------------------------------
    # PRELOAD CHINESE PRONUNCIATION
    # -----------------------------------------
    def prepare_pronunciation(self, chinese_text):

        if not self.sound_enabled or not chinese_text:
            return

        with self.cache_lock:

            # Tu da co trong cache hoac dang duoc tao
            if chinese_text in self.speech_cache:
                return

            self.speech_cache[chinese_text] = "loading"

        def worker():

            start_time = time.perf_counter()
            temp_path = None

            try:
                temp_file = tempfile.NamedTemporaryFile(
                    suffix=".mp3",
                    delete=False
                )

                temp_path = temp_file.name
                temp_file.close()

                async def generate():

                    communicator = edge_tts.Communicate(
                        text=chinese_text,
                        voice="zh-CN-XiaoxiaoNeural",
                        rate="+0%",
                        volume="+0%"
                    )

                    await communicator.save(temp_path)

                asyncio.run(generate())

                elapsed = time.perf_counter() - start_time

                with self.cache_lock:
                    self.speech_cache[chinese_text] = temp_path

            except Exception as exc:

                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

                with self.cache_lock:
                    self.speech_cache[chinese_text] = exc

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    # -----------------------------------------
    # PLAY EFFECT THEN SPEAK
    # -----------------------------------------
    def play_effect_then_speak(self, effect_name, chinese_text):

        if not self.sound_enabled:
            return

        self.pending_word = chinese_text
        self.pending_speech = None
        self.waiting_for_speech = True

        self.effect_start_time = time.perf_counter()
        self.effect_end_time = None
        self.waiting_logged = False

        if effect_name == "hit":
            sound = self.hit_sound
        else:
            sound = self.wrong_sound

        if sound is not None:
            self.channel.play(sound)
        else:
            self.effect_end_time = time.perf_counter()

    # -----------------------------------------
    # UPDATE - CALL IN GAME LOOP
    # -----------------------------------------
    def update(self):

        if not self.sound_enabled:
            return

        if not self.waiting_for_speech:
            return

        # Cho hieu ung hit/wrong ket thuc
        if self.channel.get_busy():
            return

        # Ghi nhan thoi diem hieu ung ket thuc
        if self.effect_end_time is None:

            self.effect_end_time = time.perf_counter()

            effect_duration = (
                self.effect_end_time - self.effect_start_time
            )

        # Lay file TTS cua dung tu
        if self.pending_speech is None:

            with self.cache_lock:
                result = self.speech_cache.get(self.pending_word)

            # File TTS chua tao xong
            if result is None or result == "loading":

                if not self.waiting_logged:
                    self.waiting_logged = True

                return

            # TTS tao that bai
            if isinstance(result, Exception):

                self.waiting_for_speech = False
                self.pending_word = None
                return

            try:
                load_start = time.perf_counter()

                self.pending_speech = pygame.mixer.Sound(result)
                self.pending_speech.set_volume(1.0)

                load_time = time.perf_counter() - load_start


            except (pygame.error, OSError) as exc:

                print(f"[TTS] Loi load am thanh: {exc}")

                self.waiting_for_speech = False
                self.pending_word = None
                return

        # Phat giong doc
        self.channel.play(self.pending_speech)

        speak_delay = (
            time.perf_counter() - self.effect_end_time
        )

        self.waiting_for_speech = False
        self.pending_word = None
        self.pending_speech = None

    # -----------------------------------------
    # STOP AND CLEAN UP
    # -----------------------------------------
    def stop(self):

        if self.sound_enabled:
            self.channel.stop()
            pygame.mixer.music.stop()

        # Xoa cac file TTS tam khi thoat game
        with self.cache_lock:

            for result in self.speech_cache.values():

                if isinstance(result, str) and os.path.exists(result):

                    try:
                        os.remove(result)
                    except OSError:
                        pass

            self.speech_cache.clear()
