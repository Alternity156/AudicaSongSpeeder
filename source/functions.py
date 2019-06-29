from subprocess import check_output

import os
import json
import struct
import midi

audica_songlist = ["addictedtoamemory.audica",
                   "adrenaline.audica",
                   "boomboom.audica",
                   "breakforme.audica",
                   "collider.audica",
                   "decodeme.audica",
                   "destiny.audica",
                   "gametime.audica",
                   "golddust.audica",
                   "hr8938cephei.audica",
                   "ifeellove.audica",
                   "iwantu.audica",
                   "lazerface.audica",
                   "overtime.audica",
                   "perfectexceeder.audica",
                   "popstars.audica",
                   "predator.audica",
                   "raiseyourweapon_noisia.audica",
                   "resistance.audica",
                   "smoke.audica",
                   "splinter.audica",
                   "synthesized.audica",
                   "thespace.audica",
                   "timeforcrime.audica",
                   "tothestars.audica",
                   "tutorial.audica"]
                 
class desc():
    
    songID = ""
    moggSong = ""
    title = ""
    artist = ""
    midiFile = ""
    fusionSpatialized = "fusion/guns/default/drums_default_spatial.fusion"
    fusionUnspatialized = "fusion/guns/default/drums_default_sub.fusion"
    sustainSongRight = ""
    sustainSongLeft = ""
    fxSong = ""
    tempo = 0.0
    songEndEvent = ""
    songEndPitchAdjust = 0.0
    prerollSeconds = 0.0
    previewStartSeconds = 0.0
    useMidiForCues = False
    hidden = False
    offset = 0
    author = ""
        
    def load_desc_file(self, file):
        f = open(file, 'r')
        desc_file = json.load(f)
        self.songID = desc_file["songID"]
        self.moggSong = desc_file["moggSong"]
        self.title = desc_file["title"]
        self.artist = desc_file["artist"]
        self.midiFile = desc_file["midiFile"]
        self.fusionSpatialized = desc_file["fusionSpatialized"]
        try:
            self.fusionUnspatialized = desc_file["fusionUnspatialized"]
        except:
            pass
        self.sustainSongRight = desc_file["sustainSongRight"]
        self.sustainSongLeft = desc_file["sustainSongLeft"]
        self.fxSong = desc_file["fxSong"]
        self.tempo = desc_file["tempo"]
        self.songEndEvent = desc_file["songEndEvent"][25:]
        try:
            self.songEndPitchAdjust = desc_file["songEndPitchAdjust"]
        except:
            pass
        self.prerollSeconds = desc_file["prerollSeconds"]
        try:
            self.previewStartSeconds = desc_file["previewStartSeconds"]
        except:
            pass
        self.useMidiForCues = desc_file["useMidiForCues"]
        self.hidden = desc_file["hidden"]
        try:
            self.offset = desc_file["offset"]
        except:
            pass
        try:
            self.author = desc_file["author"]
        except:
            pass
        f.close()
        
    def save_desc_file(self, file):
        line = "{\n"
        line = line + "\t\"songID\": " + json.dumps(self.songID) + ",\n"
        line = line + "\t\"moggSong\": " + json.dumps(self.moggSong) + ",\n"
        line = line + "\t\"title\": " + json.dumps(self.title) + ",\n"
        line = line + "\t\"artist\": " + json.dumps(self.artist) + ",\n"
        line = line + "\t\"midiFile\": " + json.dumps(self.midiFile) + ",\n"
        line = line + "\t\"fusionSpatialized\": " + json.dumps(self.fusionSpatialized) + ",\n"
        line = line + "\t\"fusionUnspatialized\": " + json.dumps(self.fusionUnspatialized) + ",\n"
        line = line + "\t\"sustainSongRight\": " + json.dumps(self.sustainSongRight) + ",\n"
        line = line + "\t\"sustainSongLeft\": " + json.dumps(self.sustainSongLeft) + ",\n"
        line = line + "\t\"fxSong\": " + json.dumps(self.fxSong) + ",\n"
        line = line + "\t\"tempo\": " + json.dumps(self.tempo) + ",\n"
        line = line + "\t\"songEndEvent\": " + json.dumps("event:/song_end/song_end_" + self.songEndEvent) + ",\n"
        line = line + "\t\"songEndPitchAdjust\": " + json.dumps(self.songEndPitchAdjust) + ",\n"
        line = line + "\t\"prerollSeconds\": " + json.dumps(self.prerollSeconds) + ",\n"
        line = line + "\t\"previewStartSeconds\": " + json.dumps(self.previewStartSeconds) + ",\n"
        line = line + "\t\"useMidiForCues\": " + json.dumps(self.useMidiForCues) + ",\n"
        line = line + "\t\"hidden\": " + json.dumps(self.hidden) + ",\n"
        line = line + "\t\"offset\": " + json.dumps(self.offset) + ",\n"
        line = line + "\t\"author\": " + json.dumps(self.author) + "\n"
        line = line + "}"
        
        f = open(file, "w")
        f.write(line)
        f.close()
        
def get_tempo(desc_input_file):
    desc_file = desc()
    desc_file.load_desc_file(desc_input_file)
    return desc_file.tempo
        
def save_new_desc(input_file, output_file, speed, tmpo):
    desc_file = desc()
    desc_file.load_desc_file(input_file)
    desc_file.songID = desc_file.songID + str(speed)
    desc_file.title = desc_file.title + " (" + str(speed) + "% Speed)"
    desc_file.tempo = str(tmpo)
    desc_file.save_desc_file(output_file)
    
def mogg2ogg(input_file, output_file):
    with open(input_file, "rb") as f:
        bytes = f.read()
        new_bytes = bytes[struct.unpack('<i', bytes[4] + bytes[5] + bytes[6] + bytes[7])[0]:]
        f = open(output_file, "wb")
        f.write(new_bytes)
    f.close()
    
def ogg2mogg(input_file, output_file):
    return check_output("ogg2mogg.exe \"" + input_file + "\" \"" + output_file + "\"")
    
def check_ffmpeg_install():
    print check_output("ffmpeg")
    
def change_audio_speed(input_file, output_file, scale):
    return check_output("ffmpeg -i \"" + input_file + "\" -filter:a \"atempo=" + scale + "\" \"" + output_file + "\"")
    
def change_midi_speed(input_file, output_file, tmpo):
    pattern = midi.read_midifile(input_file)
    for track in pattern:
        for event in track:
            if type(event) is midi.SetTempoEvent:
                event.set_bpm(float(tmpo))
                break
    midi.write_midifile(output_file, pattern)
    
def do_magic(input_file, output_file):
    return check_output("Plugins" + os.sep + "hmxaudio.exe \"" + input_file + "\" \"" + output_file + "\"")