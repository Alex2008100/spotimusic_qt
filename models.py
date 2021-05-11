"""
    Models, bruh
"""
class datasaver:
    
    def save_csv(self):
        pass

class Playlist:
    
    def __init__(self, title:str, songs:list):
        self.title = title
        self.songs = songs

class Song:
    
    def __init__(self, title:str, artist:str, album:str, path:str):
        self.title = title
        self.artist = artist
        self.album = album
        self.path = path
