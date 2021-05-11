from multiprocessing import Process
from pydub import AudioSegment
import pyaudio, wave, os

class playsound:
    __instance__ = None

    def __init__(self):
        if playsound.__instance__ == None:
            playsound.__instance__ = self
        else:
            raise Exception('Two playsound instances')
    @staticmethod
    def instance():
        if not playsound.__instance__:
            playsound()
        return playsound.__instance__

    def set_file(self, dir:str):
        self.pa = pyaudio.PyAudio()
        self.process = None
        self.current_file = wave.open(dir)
        self.stream_out = self.pa.open(
            rate=self.current_file.getframerate(),
            channels=self.current_file.getnchannels(),
            format=self.pa.get_format_from_width(self.current_file.getsampwidth()),
            output=True,
            frames_per_buffer=1024)
        self.data = self.current_file.readframes(1024)
    
    def __loop_wav(self):
        while self.data and self.playing:
            self.stream_out.write(self.data)
            print('Hah')
            self.data = self.current_file.readframes(1024)

    def play(self):
        if not self.process:
            self.process = Process(target=self.__loop_wav)
            self.playing = True
            self.process.start()
        else:
            self.playing = False
            self.process.join()
            del self.process
            self.playing = True
            self.play()

    def stop(self):
        self.playing = False
        self.process.join()
        self.current_file = None

    def pause(self):
        self.playing = False