from PyQt5 import QtCore, QtGui, QtWidgets
import models, csv, warnings, sys, music_tag as mstag, pygame.mixer as mixer, pygame

class Controller(QtCore.QObject):
    #Singleton stuff
    __instance__ = None

    def __init__(self):
        if Controller.__instance__ == None:
            Controller.__instance__ = self
        else:
            raise Exception('Two controller instances')
    @staticmethod
    def instance():
        if not Controller.__instance__:
            Controller()
        return Controller.__instance__

    #Actual class
    def startup(self):
        with open('data/songs.csv', mode='r') as file:
            reader = csv.reader(file, delimiter=',')
            self.songs = {}
            for row in reader:
                self.songs[int(row[0])] = models.Song(row[1], row[2], row[3], row[4])
        with open('data/playlists.csv', mode='r') as file:
            reader = csv.reader(file, delimiter=';')
            self.playlists = {0: models.Playlist('all', list(range(len(self.songs))))}
            reader = list(reader)
            for counter in range(0, len(reader), 2):
                self.playlists[reader[counter][0]] = models.Playlist(reader[counter][1], [int(id) for id in reader[counter+1]])

    def get_song_id(self, r_song:models.Song):
        for song in self.songs.items():
            if song[1] == r_song:
                return song[0]
        raise Exception('No id excecption')

    def get_playlist_id(self, r_playlist:models.Playlist):
        for playlist in self.playlists.items():
            if playlist[1] == r_playlist:
                return playlist[0]
        raise Exception('No id excecption')

    def save_songs(self):
        with open('data/songs.csv', mode='w+') as file:
            writer = csv.writer(file, delimiter=',')
            counter = 0
            for song in self.songs.items():
                song = song[1]
                writer.writerow([counter, song.title, song.artist, song.album, song.path])
                counter += 1

    def save_playlists(self):
        with open('data/playlists.csv', mode='w+',) as file:
            writer = csv.writer(file, delimiter=';')
            counter = 1
            for playlist in self.playlists.items():
                if not playlist[0] == 0:
                    playlist = playlist[1]
                    writer.writerows([[counter, playlist.title], playlist.songs])
                    counter += 1


    def add_song(self, data:list, dir:str):
        self.songs[len(self.songs)] = models.Song(data[0], data[1], data[2], dir)
        self.playlists[0].songs.append(len(self.songs)-1)

    def edit_song(self, song:models.Song):
        new_data = EditSongDlg(song.path).getResults()
        if new_data:
            self.songs[self.get_song_id(song)] = models.Song(new_data[0], new_data[1], new_data[2], song.path)
        self.window.render_songs()

    def remove_song(self, song:models.Song):
        song_id = self.get_song_id(song)
        for id in range(song_id+1, len(self.songs)-1):
            print("from:{} to:{}".format(id, id-1))
            self.songs[id] = self.songs[id-1]
        if self.songs[len(self.songs)-1]:
            del self.songs[len(self.songs)-1]
        for playlist in self.playlists.items():
            print(playlist[1].songs)
            if song_id in playlist[1].songs:
                playlist[1].songs.remove(song_id)
        self.window.render_songs()

    def add_playlist(self, title:str, data:list):
        self.playlists[len(self.playlists)] = models.Playlist(title, data)

    def edit_playlist(self, playlist):
        new_data = EditPlaylistDlg(playlist.title).getResults()
        if new_data:
            self.playlists[self.get_playlist_id(playlist)] = models.Playlist(new_data[0], new_data[1])
        self.window.render_playlists()
        self.window.render_songs()

    def remove_playlist(self, playlist):
        del self.playlists[self.get_playlist_id(playlist)]
        self.window.render_playlists()
        self.window.render_songs()

controller = Controller()
controller.startup()
pygame.init()

class RenderHandler(QtCore.QObject):

    finished_signal = QtCore.pyqtSignal()
    data_signal = QtCore.pyqtSignal(list)
    finished = True

    def render_playlists(self, listWidget):
        if not self.finished:
            warnings.warn('Attempt at double render')
            return None
        else:
            self.finished = False
            list_item = QtWidgets.QListWidgetItem(listWidget)
            for playlist in Controller.instance().playlists:
                item_widget = PlaylistWidget(playlist)
                listWidget.addItem(list_item)
                listWidget.setItemWidget(list_item, item_widget)
                list_item.setSizeHint(item_widget.sizeHint())
            self.finished = True
            self.finished_signal.emit()

    def render_songs(self, playlist, listWidget):
        if not self.finished:
            warnings.warn('Attempt at double render')
            return None
        else:
            self.finished = False
            list_item = QtWidgets.QListWidgetItem(listWidget)
            for id in playlist.songs:
                song = Controller.instance().songs[id]
                item_widget = SongWidget(song, Controller.instance().get_song_id(song))
                listWidget.songListWidget.addItem(list_item)
                listWidget.songListWidget.setItemWidget(list_item, item_widget)
                list_item.setSizeHint(item_widget.sizeHint())
            self.finished = True
            self.finished_signal.emit()

    @staticmethod
    def add_song_dlg():
        filenames = QtWidgets.QFileDialog.getOpenFileName(Controller.instance().window, 'Open audio file', 'home/', 'Audio files (*.mp3 *.wav)')
        return filenames

#Edit song dialog /////////////////////

class Ui_EditSong(object):
    def setupUi(self, Form, song_dir):
        Form.setObjectName("Form")
        Form.resize(300, 216)
        Form.setMaximumSize(QtCore.QSize(300, 184))
        self.song_dir = song_dir
        self.formLayout = QtWidgets.QFormLayout(Form)
        self.formLayout.setObjectName("formLayout")
        self.directoryLabel = QtWidgets.QLabel(Form)
        self.directoryLabel.setObjectName("directoryLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.directoryLabel)
        self.songDirectoryLabel = QtWidgets.QLabel(Form)
        self.songDirectoryLabel.setMaximumSize(QtCore.QSize(16777215, 30))
        self.songDirectoryLabel.setObjectName("songDirectoryLabel")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.songDirectoryLabel)
        self.titleLabel = QtWidgets.QLabel(Form)
        self.titleLabel.setObjectName("titleLabel")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.titleLabel)
        self.titleLine = QtWidgets.QLineEdit(Form)
        self.titleLine.setObjectName("titleLine")
        #
        self.titleLine.setText(mstag.load_file(self.song_dir)['title'].first)
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.titleLine)
        self.artistLabel = QtWidgets.QLabel(Form)
        self.artistLabel.setObjectName("artistLabel")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.artistLabel)
        self.artistLine = QtWidgets.QLineEdit(Form)
        self.artistLine.setObjectName("artistLine")
        #
        self.artistLine.setText(mstag.load_file(self.song_dir)['artist'].first)
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.artistLine)
        self.albumLabel = QtWidgets.QLabel(Form)
        self.albumLabel.setObjectName("albumLabel")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.albumLabel)
        self.albumLine = QtWidgets.QLineEdit(Form)
        self.albumLine.setObjectName("albumLine")
        #
        self.albumLine.setText(mstag.load_file(self.song_dir)['album'].first)
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.albumLine)
        self.addButton = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, Form)
        self.addButton.setObjectName("addButton")
        self.addButton.accepted.connect(self.accept)
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.addButton)
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.formLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.label)

        self.closeEvent = lambda event: self.reject()
        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.directoryLabel.setText(_translate("Form", "Directory:"))
        self.songDirectoryLabel.setText(_translate("Form", "{}".format(self.song_dir)))
        self.titleLabel.setText(_translate("Form", "Song title:"))
        self.artistLabel.setText(_translate("Form", "Artist:"))
        self.albumLabel.setText(_translate("Form", "Album:"))
        self.label.setText(_translate("Form", "You\'ll be able to edit it later"))

class EditSongDlg(QtWidgets.QDialog, Ui_EditSong):
    def __init__(self, song_dir):
        super().__init__()
        self.setupUi(self, song_dir)

    def getResults(self):
        if self.exec_()  == QtWidgets.QDialog.Accepted:
            # get all values
            title = self.titleLine.text()
            artist = self.artistLine.text()
            album = self.albumLine.text()
            if not title:
                title = 'Untitled'
            if not artist:
                artist = 'Unknown'
            if not album:
                album = 'Single'

            tag = mstag.load_file(self.song_dir)
            tag['title']=title
            tag['artist']=artist
            tag['album']=album
            return (title, artist, album)

#Edit playlist dialog /////////////////

class Ui_EditPlaylist(object):
    def setupUi(self, mainLayout, playlist_title:str=''):
        mainLayout.setObjectName("mainLayout")
        mainLayout.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(mainLayout)
        self.verticalLayout.setObjectName("verticalLayout")
        self.titleEdit = QtWidgets.QLineEdit(mainLayout)
        self.titleEdit.setObjectName("titleEdit")
        self.titleEdit.setText(playlist_title)
        self.verticalLayout.addWidget(self.titleEdit)
        self.songListWidget = QtWidgets.QListWidget(mainLayout)
        self.songListWidget.setObjectName("songListWidget")
        self.verticalLayout.addWidget(self.songListWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok, QtCore.Qt.Horizontal, mainLayout)
        self.buttonBox.setObjectName("buttonBox")
        #
        self.buttonBox.accepted.connect(self.accept)
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(mainLayout)
        QtCore.QMetaObject.connectSlotsByName(mainLayout)
        self.render_songs()

    def retranslateUi(self, mainLayout):
        _translate = QtCore.QCoreApplication.translate
        mainLayout.setWindowTitle(_translate("mainLayout", "Form"))
        self.titleEdit.setPlaceholderText(_translate("mainLayout", "Title (e.g. Never Gonna Give You Up)"))

    def render_songs(self):
        self.songListWidget.clear()
        self.checkboxes = {}
        for song in Controller.instance().songs.items():
            list_item = QtWidgets.QListWidgetItem(self.songListWidget)
            checkbox = QtWidgets.QCheckBox('{} : {}'.format(song[1].artist, song[1].title))
            self.checkboxes[Controller.instance().get_song_id(song[1])] = checkbox
            self.songListWidget.setItemWidget(list_item, checkbox)

class EditPlaylistDlg(QtWidgets.QDialog, Ui_EditPlaylist):
    def __init__(self, playlist_title=''):
        super().__init__()
        self.setupUi(self, playlist_title)
        self.render_songs()

    def getResults(self):
        if self.exec_()  == QtWidgets.QDialog.Accepted:
            # get all values
            title = self.titleEdit.text()
            selected_songs = []
            for data in self.checkboxes.items():
                if data[1].isChecked():
                    selected_songs.append(data[0])
            return (title, selected_songs)

# Main window /////////////////////////

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(966, 772)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.listsLayout = QtWidgets.QHBoxLayout()
        self.listsLayout.setObjectName("listsLayout")
        self.playlistWidget = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playlistWidget.sizePolicy().hasHeightForWidth())
        self.playlistWidget.setSizePolicy(sizePolicy)
        self.playlistWidget.setObjectName("playlistWidget")
        self.listsLayout.addWidget(self.playlistWidget)
        self.songListWidget = QtWidgets.QListWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.songListWidget.sizePolicy().hasHeightForWidth())
        self.songListWidget.setSizePolicy(sizePolicy)
        self.songListWidget.setMinimumSize(QtCore.QSize(0, 300))
        self.songListWidget.setObjectName("songListWidget")
        self.listsLayout.addWidget(self.songListWidget)
        self.verticalLayout.addLayout(self.listsLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_2.setContentsMargins(0, -1, -1, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.dataLayout = QtWidgets.QHBoxLayout()
        self.dataLayout.setObjectName("dataLayout")
        self.buttonLayout = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonLayout.sizePolicy().hasHeightForWidth())
        self.buttonLayout.setSizePolicy(sizePolicy)
        self.buttonLayout.setObjectName("buttonLayout")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.buttonLayout)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.stopButton = QtWidgets.QPushButton(self.buttonLayout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stopButton.sizePolicy().hasHeightForWidth())
        self.stopButton.setSizePolicy(sizePolicy)
        self.stopButton.setObjectName("stopButton")
        #
        self.stopButton.clicked.connect(self.stop_song)
        self.verticalLayout_5.addWidget(self.stopButton)
        self.pauseButton = QtWidgets.QPushButton(self.buttonLayout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pauseButton.sizePolicy().hasHeightForWidth())
        self.pauseButton.setSizePolicy(sizePolicy)
        self.pauseButton.setObjectName("pauseButton")
        #
        self.pauseButton.clicked.connect(self.pause_song)
        self.verticalLayout_5.addWidget(self.pauseButton)
        self.playButton = QtWidgets.QPushButton(self.buttonLayout)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.playButton.sizePolicy().hasHeightForWidth())
        self.playButton.setSizePolicy(sizePolicy)
        self.playButton.setObjectName("playButton")
        #
        self.playButton.clicked.connect(self.play_song)
        self.verticalLayout_5.addWidget(self.playButton)
        self.dataLayout.addWidget(self.buttonLayout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.titleLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.titleLabel.sizePolicy().hasHeightForWidth())
        self.titleLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(15)
        self.titleLabel.setFont(font)
        self.titleLabel.setScaledContents(True)
        self.titleLabel.setWordWrap(True)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout_3.addWidget(self.titleLabel)
        self.artistLabel = QtWidgets.QLabel(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.artistLabel.sizePolicy().hasHeightForWidth())
        self.artistLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.artistLabel.setFont(font)
        self.artistLabel.setObjectName("artistLabel")
        self.verticalLayout_3.addWidget(self.artistLabel)
        self.dataLayout.addLayout(self.verticalLayout_3)
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.horizontalSlider.sizePolicy().hasHeightForWidth())
        self.horizontalSlider.setSizePolicy(sizePolicy)
        self.horizontalSlider.setMinimumSize(QtCore.QSize(150, 0))
        self.horizontalSlider.setMinimum(1)
        self.horizontalSlider.setMaximum(100)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setInvertedControls(False)
        self.horizontalSlider.setTickPosition(QtWidgets.QSlider.TicksBothSides)
        self.horizontalSlider.setTickInterval(5)
        self.horizontalSlider.setObjectName("horizontalSlider")
        #
        self.horizontalSlider.valueChanged.connect(self.volume_change)
        self.dataLayout.addWidget(self.horizontalSlider)
        self.verticalLayout_2.addLayout(self.dataLayout)
        self.verticalLayout.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 966, 30))
        self.menubar.setObjectName("menubar")
        self.menuAdd = QtWidgets.QMenu(self.menubar)
        self.menuAdd.setObjectName("menuAdd")
        MainWindow.setMenuBar(self.menubar)
        self.actionAdd_song = QtWidgets.QAction(MainWindow)
        self.actionAdd_song.setObjectName("actionAdd_song")
        #
        self.actionAdd_song.triggered.connect(self.add_song)
        self.actionAdd_playlist = QtWidgets.QAction(MainWindow)
        self.actionAdd_playlist.setObjectName("actionAdd_playlist")
        #
        self.actionAdd_playlist.triggered.connect(self.add_playlist)
        self.menuAdd.addAction(self.actionAdd_song)
        self.menuAdd.addAction(self.actionAdd_playlist)
        self.menubar.addAction(self.menuAdd.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.retranslateUi(MainWindow)
        self.render_playlists()
        self.render_songs()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        Controller.instance().window = self

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.stopButton.setText(_translate("MainWindow", "Stop"))
        self.pauseButton.setText(_translate("MainWindow", "Pause"))
        self.playButton.setText(_translate("MainWindow", "Play"))
        self.titleLabel.setText(_translate("MainWindow", "Title"))
        self.artistLabel.setText(_translate("MainWindow", "Artist"))
        self.menuAdd.setTitle(_translate("MainWindow", "Files"))
        self.actionAdd_song.setText(_translate("MainWindow", "Add song"))
        self.actionAdd_playlist.setText(_translate("MainWindow", "Add playlist"))

    def render_playlists(self):
        self.playlistWidget.clear()
        for playlist in Controller.instance().playlists.items():
            list_item = QtWidgets.QListWidgetItem(self.playlistWidget)
            list_item.setData(QtCore.Qt.EditRole, playlist[1])
            self.playlistWidget.itemClicked.connect(lambda item: self.render_songs())
            item_widget = PlaylistWidget(playlist[1])
            self.playlistWidget.addItem(list_item)
            self.playlistWidget.setItemWidget(list_item, item_widget)
            list_item.setSizeHint(item_widget.sizeHint())

    def render_songs(self):
        self.songListWidget.clear()
        playlist = self.playlistWidget.currentItem()
        if playlist:
            playlist = playlist.data(QtCore.Qt.DisplayRole)
        else:
            playlist = Controller.instance().playlists[0]
        for id in playlist.songs:
            list_item = QtWidgets.QListWidgetItem(self.songListWidget)
            self.songListWidget.itemDoubleClicked.connect(lambda item: self.play_song(id))
            song = Controller.instance().songs[id]
            item_widget = SongWidget(song, Controller.instance().get_song_id(song))
            self.songListWidget.addItem(list_item)
            self.songListWidget.setItemWidget(list_item, item_widget)
            list_item.setSizeHint(item_widget.sizeHint())

    def volume_change(self):
        mixer.music.pause()
        mixer.music.set_volume(self.horizontalSlider.value()/100)
        mixer.music.unpause()

    def add_song(self):
        song = RenderHandler.add_song_dlg()[0]
        if song:
            values = EditSongDlg(song).getResults()
            if values:
                Controller.instance().add_song(values, song)
                self.render_songs()
    def add_playlist(self):
        values = EditPlaylistDlg().getResults()
        if values:
            Controller.instance().add_playlist(values[0], values[1])
            self.render_playlists()

    def play_song(self, song_id:int):
        Controller.instance().selected_song = song_id
        mixer.init()
        mixer.music.load(Controller.instance().songs[song_id].path)
        self.volume_change()
        mixer.music.play(-1, 0)
        self.titleLabel.setText(Controller.instance().songs[song_id].title)
        self.artistLabel.setText(Controller.instance().songs[song_id].artist)

    def stop_song(self):
        mixer.music.stop()
        Controller.instance().selected_song = None

    def pause_song(self):
        if self.pauseButton.text() == 'Pause':
            mixer.music.pause()
            self.pauseButton.setText('Unpause')
        else:
            mixer.music.unpause()
            self.pauseButton.setText('Pause')

    def closeEvent(self, event):
        Controller.instance().save_songs()
        Controller.instance().save_playlists()
        event.accept()

#Widgets

class PlaylistWidget(QtWidgets.QWidget):
    def __init__(self, playlist: models.Playlist, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setGeometry(QtCore.QRect(0, 0, 211, 41))
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(10, 2, 5, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.playlistName = QtWidgets.QLabel(self)
        self.playlistName.setText(playlist.title)
        self.playlistName.setObjectName("playlistName")
        self.horizontalLayout.addWidget(self.playlistName)

        if playlist.title == 'All':
            self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.customContextMenuRequested.connect(lambda point:self.popMenu.exec_(self.mapToGlobal(point)))

        self.popMenu = QtWidgets.QMenu(self)
        self.editAction = QtWidgets.QAction('Edit', self)
        self.editAction.triggered.connect(lambda: Controller.instance().edit_playlist(playlist))
        self.removeAction = QtWidgets.QAction('Remove', self)
        self.removeAction.triggered.connect(lambda: Controller.instance().remove_playlist(playlist))
        self.popMenu.addAction(self.editAction)
        self.popMenu.addAction(self.removeAction)

class SongWidget(QtWidgets.QWidget):
    def __init__(self, song: models.Song, song_id, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        self.setGeometry(QtCore.QRect(0, 0, 211, 41))
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.horizontalLayout.setContentsMargins(10, 2, 5, 2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.titleLabel = QtWidgets.QLabel(self)
        self.titleLabel.setText('{}: {}'.format(song_id, song.title))
        self.titleLabel.setObjectName("titleLabel")
        self.horizontalLayout.addWidget(self.titleLabel)

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.artistLabel = QtWidgets.QLabel(self)
        self.artistLabel.setText(song.artist)
        self.artistLabel.setObjectName("artistLabel")
        self.verticalLayout.addWidget(self.artistLabel)
        self.albumLabel = QtWidgets.QLabel(self)
        self.albumLabel.setText(song.album)
        self.albumLabel.setObjectName("albumLabel")
        self.verticalLayout.addWidget(self.albumLabel)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(lambda point:self.popMenu.exec_(self.mapToGlobal(point)))

        self.popMenu = QtWidgets.QMenu(self)
        self.editAction = QtWidgets.QAction('Edit', self)
        self.editAction.triggered.connect(lambda: Controller.instance().edit_song(song))
        self.removeAction = QtWidgets.QAction('Remove', self)
        self.removeAction.triggered.connect(lambda: Controller.instance().remove_song(song))
        self.popMenu.addAction(self.editAction)
        self.popMenu.addAction(self.removeAction)

        self.horizontalLayout.setStretch(0, 1)
