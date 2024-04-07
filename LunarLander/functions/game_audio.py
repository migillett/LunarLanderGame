from pygame import mixer
from os import path, listdir
import random


class GameAudio:
    def __init__(self, absolute_path: str):
        self.mixer: mixer = mixer

        self.audio_path = path.join(absolute_path, 'assets', 'audio')

        self.music_path: str = path.join(
            self.audio_path, 'main-theme.mp3')

        self.victory_sfx = mixer.Sound(
            path.join(self.audio_path, 'victory', 'VictorySmall.wav'))

        self.alarm_sfx = mixer.Sound(
            path.join(self.audio_path, 'alarm.wav'))
        self.alarm_sfx.set_volume(0.5)

        self.thruster_sfx = mixer.Sound(
            path.join(self.audio_path, 'Wind.wav'))

        self.alarm_channel = self.mixer.Channel(1)
        self.thruster_channel = self.mixer.Channel(2)

        self.mixer.music.load(
            path.join(self.audio_path, 'main-theme.mp3'))

    def pick_random_audio(self, audio_directory: str) -> str:
        audio_files = [x for x in listdir(audio_directory) if x.endswith('.wav')]  # noqa
        return path.join(audio_directory, random.choice(audio_files))

    def play_music(self) -> None:
        self.mixer.music.play(-1)

    def play_victory(self) -> None:
        self.mixer.music.stop()
        self.mixer.Sound.play(self.victory_sfx)

    def play_crash(self) -> None:
        audio_path = self.pick_random_audio(
            path.join(self.audio_path, 'explosions'))
        explosion_sound = mixer.Sound(audio_path)

        self.mixer.music.stop()
        self.mixer.Sound.play(explosion_sound)

    def play_thruster(self) -> None:
        if not self.thruster_channel.get_busy():
            self.thruster_channel.play(self.thruster_sfx)

    def play_alarm(self) -> None:
        if not self.alarm_channel.get_busy():
            self.alarm_channel.play(self.alarm_sfx)
