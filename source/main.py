import kivy
kivy.require('1.10.1')

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.core.window import Window
from kivy.config import Config

from zipfile import ZipFile
from threading import Thread

import os
import re
import shutil

import functions

Config.set('input', 'mouse', 'mouse,disable_multitouch') #red dots problem fix maybe?
Config.set('graphics', 'fullscreen', 0)
Config.set('graphics', 'borderless', 0)
Config.set('graphics', 'height', 288)
Config.set('graphics', 'width', 512)
Config.set('graphics','resizable',0)
Config.write()

class IntInput(TextInput):

    pat = re.compile('[^0-9]')
    def insert_text(self, substring, from_undo=False):
        pat = self.pat
        s = re.sub(pat, '', substring)
        return super(IntInput, self).insert_text(s, from_undo=from_undo)

class MainApp(FloatLayout):
    
    speed_label = Label(text="Speed: ", pos=(-230,130))
    speed_input = IntInput(text="100", pos=(50,260), size_hint=(.1,.1))
    speed_percent_label = Label(text="%", pos=(-147,130))
    
    filename_label = Label(text="Drag and drop an .audica file...", pos=(0,0))
    
    status_label = Label(text="", pos=(0,-50))
    
    start_button = Button(text="START", pos=(200,0), size_hint=(.2,.2))
    
    ##
    
    selected_file = ""
    
    magician_mode = False
    
    tempo = 0

    def __init__(self, **kwargs):
        super(MainApp, self).__init__(**kwargs)
        
        self.add_widget(self.speed_input)
        self.add_widget(self.speed_label)
        self.add_widget(self.speed_percent_label)
        self.add_widget(self.filename_label)
        self.add_widget(self.status_label)
        self.add_widget(self.start_button)
        
        Window.bind(on_dropfile=self.dropfile_handle)
        
        self.start_button.bind(on_release=lambda i:Thread(target=self.start_button_handler).start())
        
    def start_button_handler(self):
        if int(self.speed_input.text) == 100:
            self.status_label.text = "Speed must not be set to 100%"
            return
        if int(self.speed_input.text) < 50 or int(self.speed_input.text) > 200:
            self.status_label.text = "Speed must be between 50% and 200%"
            return
        if self.selected_file[-7:] != ".audica":
            self.status_label.text = "No .audica file selected"
            return
        self.process_song()
            
    def process_song(self):
        self.start_button.disabled = True
        self.status_label.text = "Preparing the process..."
        new_songID = self.selected_file.split(os.sep)[-1][:-7] + self.speed_input.text
        if os.path.exists(new_songID):
            shutil.rmtree(new_songID)
        if os.path.exists("temp"):
            shutil.rmtree("temp")
        os.mkdir(new_songID)
        os.mkdir("temp")
        audica_file = ZipFile(self.selected_file)
        audica_file.extractall("temp")
        song_files = [f for f in os.listdir("temp") if os.path.isfile(os.path.join("temp", f))]
        for song_file in song_files:
            if song_file[-4:] == ".mid":
                self.status_label.text = "Creating MIDI file with new tempo..."
                self.tempo = self.percentage(int(self.speed_input.text), float(functions.get_tempo("temp" + os.sep + "song.desc")))
                functions.change_midi_speed("temp" + os.sep + song_file, new_songID + os.sep + song_file, self.tempo)
                break
        for song_file in song_files:
            if song_file[-9:] == ".moggsong" or song_file[-5:] == ".cues":
                self.status_label.text = "Moving " + song_file + "..."
                shutil.move("temp" + os.sep + song_file, new_songID + os.sep + song_file)
            if song_file[-5:] == ".mogg":
                self.status_label.text = "Modifying " + song_file + " with new tempo..."
                if self.magician_mode == True:
                    functions.do_magic("temp" + os.sep + song_file, "temp" + os.sep + song_file[:-5] + ".ogg")
                else:
                    functions.mogg2ogg("temp" + os.sep + song_file, "temp" + os.sep + song_file[:-5] + ".ogg")
                functions.change_audio_speed("temp" + os.sep + song_file[:-5] + ".ogg", "temp" + os.sep + song_file[:-5] + "new.ogg", str(float(int(self.speed_input.text)/100.0)))
                functions.ogg2mogg("temp" + os.sep + song_file[:-5] + "new.ogg", new_songID + os.sep + song_file)
            if song_file[-5:] == ".desc":
                self.status_label.text = "Modifying the song.desc file..."
                functions.save_new_desc("temp" + os.sep + song_file, new_songID + os.sep + song_file, self.speed_input.text, self.tempo)
        self.status_label.text = "Creating new .audica file with the new files..."
        if os.path.exists("OUTPUT"):
            if os.path.isfile("OUTPUT" + os.sep + new_songID + ".audica"):
                os.remove("OUTPUT" + os.sep + new_songID + ".audica")
        else:
            os.mkdir("OUTPUT")
        new_files = [f for f in os.listdir(new_songID) if os.path.isfile(os.path.join(new_songID, f))]
        f = ZipFile("OUTPUT" + os.sep + new_songID + ".audica", "w")
        for file in new_files:
            f.write(new_songID + os.sep + file, file)
        f.close()
        self.status_label.text = "Cleaning temp files..."
        shutil.rmtree("temp")
        shutil.rmtree(new_songID)
        self.status_label.text = "DONE! Your new audica file should be in the OUTPUT folder!"
        self.tempo = 0
        self.start_button.disabled = False
            
    def percentage(self, percent, whole):
        return (percent * whole) / 100.0
            
    def not_a_magician(self):
        self.status_label.text = "You are not a magician..."
        self.filename_label.text = "Drag and drop an .audica file..."
        self.selected_file = ""
        self.magician_mode = False
        
    def dropfile_handle(self, instance, file):
        if file.split(os.sep)[-1] in functions.audica_songlist:
            if os.path.isfile("Plugins" + os.sep + "hmxaudio.exe"):
                if os.path.isfile("Plugins" + os.sep + "HmxAudioPlugin.dll"):
                    if os.path.isfile("Plugins" + os.sep + "fmodstudio64.dll"):
                        if os.path.isfile("Plugins" + os.sep + "fmod64.dll"):
                            self.selected_file = file
                            self.filename_label.text = file.split(os.sep)[-1]
                            self.status_label.text = "Magician mode enabled!"
                            self.magician_mode = True
                        else:
                            self.not_a_magician()
                    else:
                        self.not_a_magician()
                else:
                    self.not_a_magician()
            else:
                self.not_a_magician()
        elif file[-7:] == ".audica":
            self.selected_file = file
            self.status_label.text = ""
            self.filename_label.text = file.split(os.sep)[-1]
            self.magician_mode = False
        else:
            self.selected_file = ""
            self.filename_label.text = "Drag and drop an .audica file..."
            self.status_label.text = ""
            self.magician_mode = False

class MyApp(App):

    def build(self):
        self.title = "Audica Song Speeder"
        return MainApp()


if __name__ == '__main__':
    MyApp().run()