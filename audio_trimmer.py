from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivy.uix.gridlayout import GridLayout
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivy.uix.image import Image
from kivymd.uix.slider.slider import MDSlider
from kivymd.uix.textfield import MDTextField
from kivy.clock import Clock
import pygame
import io
from pydub import AudioSegment



class MainApp(MDApp):
    def build(self):
        screen = MDScreen(md_bg_color="white")
        self.minutes = 0
        self.seconds = 0
        self.start_over = False

        # Add Logo
        screen.add_widget(Image(source="hu.png", pos_hint={"center_x": 0.5, "center_y": 0.75}, size_hint_x=0.7,
                                allow_stretch=False))

        self.duration_label = MDLabel(text="Enter the duration", halign="center", size_hint=(0.8, 1),
                                      pos_hint={"center_x": 0.5, "center_y": 0.6})

        screen.add_widget(self.duration_label)
        # Enter duration
        self.duration = MDTextField(text="", halign="center", size_hint=(0.1, 1),
                                    pos_hint={"center_x": 0.5, "center_y": 0.5}, font_size=38)

        screen.add_widget(self.duration)
        button = MDFillRoundFlatButton(text="SET DURATION", font_size=22, pos_hint={"center_x": 0.5, "center_y": 0.3},
                                       on_press=self.getDuration)
        screen.add_widget(button)

        # Error message
        self.message = MDLabel(text="", halign="center", size_hint=(0.8, 1),
                               pos_hint={"center_x": 0.5, "center_y": 0.4})
        screen.add_widget(self.message)

        self.audio_state = "stopped"

        # Audio Slider
        self.slider = MDSlider(min=0, value=0, color="#00a2ff", pos_hint={"center_x": 0.5, "center_y": 0.2}, hint=False,
                               hint_bg_color="white", track_color_inactive="red", track_color_disabled="grey",
                               disabled=True)
        screen.add_widget(self.slider)

        # checking duration
        self.check_time = MDLabel(text="00:00/00:00", halign="center", size_hint=(0.8, 1),
                               pos_hint={"center_x": 0.5, "center_y": 0.14})

        screen.add_widget(self.check_time)
        # Audio player
        self.play_button = MDIconButton(icon="play", disabled=True, pos_hint={"center_x": 0.45, "center_y": 0.06},
                                        on_press=self.play_audio)

        self.stop_button = MDIconButton(icon="stop", disabled=True, pos_hint={"center_x": 0.55, "center_y": 0.06},
                                        on_press=self.stop_audio)

        screen.add_widget(self.play_button)
        screen.add_widget(self.stop_button)

        self.updater = None
        return screen

    def getDuration(self, instance):
        try:
            duration = int(self.duration.text)
            if duration > 25:
                self.message.text = "Enter a duration not more than 25 minutes"
            elif duration:
                self.message.text = "Successfully set duration"
                # importing file from location by giving its path
                sound = AudioSegment.from_mp3("HUAudio25min.mp3")
                # Selecting Portion we want to cut
                StrtMin = 0
                StrtSec = 0
                EndMin = duration
                EndSec = 0
                # Time to milliseconds conversion
                StrtTime = StrtMin * 60 * 1000 + StrtSec * 1000
                EndTime = EndMin * 60 * 1000 + EndSec * 1000

                # Opening file and extracting portion of it
                # Saving file in required location
                if EndMin == 25:
                    # Play 20 minutes one
                    self.play_button.disabled = False
                    self.stop_button.disabled = False
                    self.slider.disabled = False
                    self.audio = AudioSegment.from_file("HUAudio25min.mp3")
                    self.audio_length = self.audio.duration_seconds
                    self.minutes, self.seconds = divmod(self.audio_length, 60)
                    self.seconds2 = str(int(self.seconds)).zfill(2)
                    self.check_time.text = f"00:00/{int(self.minutes)}:{self.seconds2}"

                elif EndMin < 25:
                    sound[StrtTime:EndTime].fade_out(7000).fade_out(5000).export("convertedaudio.mp3",
                                                                                 format="mp3")
                    self.play_button.disabled = False
                    self.stop_button.disabled = False
                    self.slider.disabled = False

        except ValueError:
            self.message.text = "A valid number was not entered"

    def play_audio(self, button):
        if self.audio_state == "stopped":
            pygame.init()
            pygame.mixer.init()
            if int(self.duration.text) == 25:
                self.audio = AudioSegment.from_file("HUAudio25min.mp3")
                with open("HUAudio25min.mp3", "rb") as f:
                    mp3_file = io.BytesIO(f.read())
                pygame.mixer.music.load(mp3_file)
            else:
                self.audio = AudioSegment.from_file("convertedaudio.mp3")
                with open("HUAudio25min.mp3", "rb") as f:
                    mp3_file = io.BytesIO(f.read())
                pygame.mixer.music.load(mp3_file)

            self.play_button.icon = "pause"
            self.audio_state = 'playing'

            self.audio_length = self.audio.duration_seconds
            pygame.mixer.music.play()
            self.slider.max = self.audio_length

        elif self.audio_state == 'playing':
            self.play_button.icon = "play"
            self.audio_state = "paused"
            pygame.mixer.music.pause()

        elif self.audio_state == "paused":
            self.play_button.icon = "pause"
            self.audio_state = 'playing'
            pygame.mixer.music.unpause()

        if self.updater is None:
            # schedule updates to the slider
            self.updater = Clock.schedule_interval(self.update_slider, 0.5)

        elif (self.updater is not None) and self.start_over:
            self.updater = Clock.schedule_interval(self.update_slider, 0.5)

        elif (self.updater is not None) and self.audio_state == "paused":
            self.updater = Clock.schedule_interval(self.update_slider, 0.5)

    def update_slider(self, instance):
        if pygame.mixer.music.get_busy():
            current_position = pygame.mixer.music.get_pos() / 1000
            self.minutescount, self.secondscount = divmod(current_position, 60)
            self.secondscount2 = "{:02d}".format(int(self.secondscount))
            self.minutescount2 = str(int(self.minutescount)).zfill(2)
            self.check_time.text = f"{int(self.minutescount2)}:{self.secondscount2}/{int(self.minutes)}:{self.seconds2}"
            self.slider.value = current_position
        else:
            self.updater.cancel()
            self.play_button.icon = "play"

    def stop_audio(self, instance):
        pygame.mixer.music.stop()
        self.audio_state = "stopped"
        self.start_over = True
        self.check_time.text = f"00:00/{int(self.minutes)}:{self.seconds2}"



if __name__ == "__main__":
    MainApp().run()
