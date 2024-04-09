# Import main needs for UI
from Bot import Ui_Trainer
from PyQt5 import QtCore, QtGui, QtWidgets
# Import needs for recording
from pynput import mouse, keyboard
# Import needs for playback
import pydirectinput
# Import various libraries for use in functions
import threading
from time import time, sleep
import json
import os
from KeyMap import convertKey
from PyQt5.QtCore import Qt

mouse_listener = None

start_time = None

unreleased_keys = []

input_events = []

"""
Need to think about if when the save is pressed on the edit tab then give the user the option to rename the file
or to keep the file name.
Like have a message box come up and they can either name the file or if they hit cancel they keep the file name the 
same.
"""
"""
Just need to work on the things from the save tab then need to do the testing part of the code. Like
make a couple of test runs of it playing a game or the ebay idea. Then we should be good.
"""
# Class for holding computer actions for the json file.
class Event_Type:
    Key_Pressed = "keypressed"
    Key_Released = "keyreleased"
    Click = "click"
    Click_Released = "clickreleased"


# Setting up the subclass of our main UI file and clarifying its components.
class Hank(QtWidgets.QMainWindow):
    def __init__(self):
        super(Hank, self).__init__()

        # Main setup for Hank.
        self.ui = Ui_Trainer()
        self.ui.setupUi(self)

        # Defining the UI components for Record Tab.
        self.record_model = QtWidgets.QFileSystemModel()
        self.record_model.setRootPath(os.path.dirname(__file__))
        self.ui.record_treeView.setModel(self.record_model)
        self.ui.record_treeView.setRootIndex(self.record_model.index("recordings"))
        self.ui.recordButton.clicked.connect(self.record_OnClick)
        self.ui.clearButton.clicked.connect(self.clear_run_OnCLick)

        # Defining the UI components for the Play Tab.
        self.play_model = QtWidgets.QFileSystemModel()
        self.play_model.setRootPath(os.path.dirname(__file__))
        self.ui.play_tab_treeView.setModel(self.play_model)
        self.ui.play_tab_treeView.setRootIndex(self.play_model.index("recordings"))
        self.ui.play_Tab_Button.clicked.connect(self.play_OnClick)
        self.ui.play_Tab_Clear.clicked.connect(self.clear_play_OnClear)

        # Defining the UI components for the Edit Tab.
        self.edit_model = QtWidgets.QFileSystemModel()
        self.edit_model.setRootPath(os.path.dirname(__file__))
        self.ui.edit_Tab_TreeView.setModel(self.edit_model)
        self.ui.edit_Tab_TreeView.setRootIndex(self.edit_model.index("recordings"))
        self.ui.edit_Tab_DataTable.setColumnCount(5)
        self.ui.edit_Tab_DataTable.setColumnWidth(0, 150)
        self.ui.edit_Tab_DataTable.setColumnWidth(2, 150)
        self.ui.edit_Tab_DataTable.setHorizontalHeaderLabels(["Time", "Type", "Button", "Pos X", "Pos Y"])
        self.ui.edit_Tab_Load_Button.clicked.connect(self.edit_Load_OnClick)
        self.ui.edit_Tab_Save_Button.clicked.connect(self.edit_Save_OnClick)
        self.ui.edit_Tab_Clear.clicked.connect(self.clear_Data_Table)

    """
    This section contains all the functions for the record tab.
    """
    def record_OnClick(self):
        # Set label texts to notify of the beginning of a record.
        self.ui.recordingMessage.setText("Starting Recording")
        self.ui.pressEscape.setText("Press Escape to end recording")

        # Create dialog windows for filename and delay which is used to give the user some time before the
        # start of the recording.
        window = QtWidgets.QDialog()
        filename, val = QtWidgets.QInputDialog.getText(
            window, 'Record', 'Enter file name:')
        delay, val2 = QtWidgets.QInputDialog.getInt(
            window, 'Delay', 'Enter delay:', min=0, max=10)
        if filename == "":
            filename, val = QtWidgets.QInputDialog.getText(
                window, 'Record', 'Please enter a filename'
            )
        if filename == "":
            val = False

        if val and val2:
            for i in range(0, delay):
                sleep(1)

            self.ui.recordingMessage.setText("GO")
            # Spinning up second thread to handle the recording.
            t1 = threading.Thread(target=self.recording_Start, args=(filename,))
            t1.start()
        else:
            self.ui.recordingMessage.setText("")
            self.ui.pressEscape.setText("")

    def recording_Start(self, filename):
        # Launching the listeners to record the actions.
        self.runListeners()
        self.ui.recordingMessage.setText("")
        self.ui.pressEscape.setText("")
        self.ui.record_textBrowser.append('Recording duration: {0} seconds'.format(self.elapsed_time()))
        self.ui.record_textBrowser.moveCursor(QtGui.QTextCursor.End)
        global input_events

        # Clearing input events and outputting the final Json file
        script_dir = os.path.dirname(__file__)
        filepath = os.path.join(
            script_dir,
            'recordings',
            '{}.json'.format(filename)
        )
        with open(filepath, 'w') as outfile:
            json.dump(input_events, outfile, indent=4)

    def elapsed_time(self):
        global start_time
        return time() - start_time

    # Recording events as they take place and storing them in the input array in Json format.
    def record_event(self, event_type, event_time, button, pos=None):
        if str(button) == 'Key.esc':
            return
        global input_events
        input_events.append({
            'time': event_time,
            'type': event_type,
            'button': str(button),
            'pos': pos
        })

        if event_type == Event_Type.Click:
            self.ui.record_textBrowser.append('{} on {} pos {} at {}'.format(event_type, button, pos, event_time))
            self.ui.record_textBrowser.moveCursor(QtGui.QTextCursor.End)
        elif event_type == Event_Type.Click_Released:
            self.ui.record_textBrowser.append('{} on {} pos {} at {}'.format(event_type, button, pos, event_time))
            self.ui.record_textBrowser.moveCursor(QtGui.QTextCursor.End)
        else:
            self.ui.record_textBrowser.append('{} on {} at {}'.format(event_type, button, event_time))
            self.ui.record_textBrowser.moveCursor(QtGui.QTextCursor.End)

    # Recording key press events
    def on_press(self, key):
        global unreleased_keys
        if key in unreleased_keys:
            return
        else:
            unreleased_keys.append(key)
        try:
            self.record_event(Event_Type.Key_Pressed, self.elapsed_time(), key.char)
        except AttributeError:
            self.record_event(Event_Type.Key_Pressed, self.elapsed_time(), key)

    # Recording key release events.
    def on_release(self, key):
        global unreleased_keys
        try:
            unreleased_keys.remove(key)
        except ValueError:
            self.ui.record_textBrowser.append('ERROR: {} not in unreleased_keys'.format(key))
            self.ui.record_textBrowser.moveCursor(QtGui.QTextCursor.End)

        try:
            self.record_event(Event_Type.Key_Released, self.elapsed_time(), key.char)
        except AttributeError:
            self.record_event(Event_Type.Key_Released, self.elapsed_time(), key)
        if key == keyboard.Key.esc:
            global mouse_listener
            mouse_listener.stop()
            return False

    # Recording click events
    def on_click(self, x, y, button, pressed):
        if pressed:
            self.record_event(Event_Type.Click, self.elapsed_time(), button, (x, y))
        else:
            self.record_event(Event_Type.Click_Released, self.elapsed_time(), button, (x, y))

    # Starts the listeners and binds the events to the functions of which to record said events.
    def runListeners(self):
        global mouse_listener
        mouse_listener = mouse.Listener(on_click=self.on_click, on_release=self.on_click)
        mouse_listener.start()
        mouse_listener.wait()

        with keyboard.Listener(
                on_press=self.on_press,
                on_release=self.on_release) as listener:
            global start_time
            start_time = time()
            listener.join()

    # Clear the text browser if the user wants.
    def clear_run_OnCLick(self):
        self.ui.record_textBrowser.clear()

    """
    This section contains all the functions related to the play tab.
    """
    def play_OnClick(self):
        filename = self.play_model.fileName(self.ui.play_tab_treeView.currentIndex())
        self.ui.playMessage.setText('Playing ' + filename)
        if filename == "":
            window = QtWidgets.QMessageBox()
            window.setIcon(QtWidgets.QMessageBox.Warning)
            window.setWindowTitle("Error")
            window.setText("No File Selected")
            window.setStandardButtons(QtWidgets.QMessageBox.Ok)
            window.exec_()

        window = QtWidgets.QDialog()
        delay, val = QtWidgets.QInputDialog.getInt(
            window, 'Delay', 'Enter delay:', min=0, max=10)

        if val:
            for i in range(0, delay):
                sleep(1)
            t2 = threading.Thread(target=self.playback_Start, args=(filename,))
            t2.start()

    def playback_Start(self, filename):
        self.initialize_PyDirectInput()
        self.play_Actions(filename)
        self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.ui.playMessage.setText('Finished')
        self.ui.play_Tab_textBrowser.append("Done")

    def initialize_PyDirectInput(self):
        # Set the pause between actions to 0.
        pydirectinput.PAUSE = 0.0

    """
    Also need to comment some things in this section.
    """
    def play_Actions(self, filename):
        script_dir = os.path.dirname(__file__)
        filepath = os.path.join(
            script_dir,
            'recordings',
            filename
        )
        with open(filepath, 'r') as jsonfile:

            data = json.load(jsonfile)

            for index, action in enumerate(data):

                if action['button'] == 'Key.esc':
                    break

                if action['type'] == 'keypressed':
                    key = convertKey(action['button'])
                    pydirectinput.keyDown(key)
                    self.ui.play_Tab_textBrowser.append('keydown on {0}'.format(key))
                    self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)
                elif action['type'] == 'keyreleased':
                    key = convertKey(action['button'])
                    pydirectinput.keyUp(key)
                    self.ui.play_Tab_textBrowser.append('keyup on {0}'.format(key))
                    self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)
                elif action['type'] == 'click':
                    key = convertKey(action['button'])
                    endpos = data[index + 1]
                    movetime = endpos['time'] - action['time']
                    pydirectinput.mouseDown(action['pos'][0], action['pos'][1], button=key)
                    pydirectinput.moveTo(endpos['pos'][0], endpos['pos'][1], duration=movetime)
                    self.ui.play_Tab_textBrowser.append('click {} on {}'.format(key, action['pos']))
                    self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)
                elif action['type'] == 'clickreleased':
                    key = convertKey(action['button'])
                    pydirectinput.mouseUp(action['pos'][0], action['pos'][1], button=key, duration=0.25)
                    self.ui.play_Tab_textBrowser.append('click {} released on {}'.format(key, action['pos']))
                    self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)

                try:
                    next_action = data[index + 1]
                except IndexError:
                    break
                elapsed_time = next_action['time'] - action['time']

                if elapsed_time >= 0:
                    self.ui.play_Tab_textBrowser.append('sleeping for {}'.format(elapsed_time))
                    self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)
                    sleep(elapsed_time)
                else:
                    sleep(0)

    def clear_play_OnClear(self):
        self.ui.play_Tab_textBrowser.clear()
        self.ui.playMessage.setText("")

    """
    This section contains all the functions related to the edit tab.
    """
    """
    Json editor is working need to think about allowing for file renaming and things like that.
    Also look at the top and work from there.
    """
    def edit_Load_OnClick(self):
        if self.ui.edit_Tab_DataTable.rowCount() == 0:
            filename = self.edit_model.fileName(self.ui.edit_Tab_TreeView.currentIndex())
            if filename == "":
                window = QtWidgets.QMessageBox()
                window.setIcon(QtWidgets.QMessageBox.Warning)
                window.setWindowTitle("Error")
                window.setText("No File Selected")
                window.setStandardButtons(QtWidgets.QMessageBox.Ok)
                window.exec_()
            else:
                script_dir = os.path.dirname(__file__)
                filepath = os.path.join(
                    script_dir,
                    'recordings',
                    filename
                )
        
                with open(filepath, 'r') as jsonfile:
                    data = json.load(jsonfile)
                    self.ui.edit_Tab_DataTable.setRowCount(len(data))
                    row = 0
                    for action in data:
                        self.ui.edit_Tab_DataTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(action['time'])))
                        self.ui.edit_Tab_DataTable.setItem(row, 1, QtWidgets.QTableWidgetItem(action['type']))
                        self.ui.edit_Tab_DataTable.setItem(row, 2, QtWidgets.QTableWidgetItem(action['button']))
                        self.ui.edit_Tab_DataTable.setItem(row, 3, QtWidgets.QTableWidgetItem(str(action['pos'][0])))
                        self.ui.edit_Tab_DataTable.setItem(row, 4, QtWidgets.QTableWidgetItem(str(action['pos'][1])))
                        row = row + 1

        elif self.ui.edit_Tab_DataTable.rowCount() > 0:
            window = QtWidgets.QMessageBox()
            window.setIcon(QtWidgets.QMessageBox.Warning)
            window.setWindowTitle("Error")
            window.setText("Data already loaded in table. Clear Data to load another file.")
            window.setStandardButtons(QtWidgets.QMessageBox.Ok)
            window.exec_()

    def edit_Save_OnClick(self):
        if self.ui.edit_Tab_DataTable.rowCount() == 0:
            window = QtWidgets.QMessageBox()
            window.setIcon(QtWidgets.QMessageBox.Warning)
            window.setWindowTitle("Error")
            window.setText("No Data To Save")
            window.setStandardButtons(QtWidgets.QMessageBox.Ok)
            window.exec_()
        else:
            row = self.ui.edit_Tab_DataTable.rowCount()
            actions = []
            for r in range(row):
                time_ = self.ui.edit_Tab_DataTable.item(r, 0).text()
                type_ = self.ui.edit_Tab_DataTable.item(r, 1).text()
                button = self.ui.edit_Tab_DataTable.item(r, 2).text()
                posX = self.ui.edit_Tab_DataTable.item(r, 3).text()
                posY = self.ui.edit_Tab_DataTable.item(r, 4).text()
                pos = [int(posX), int(posY)]
                actions.append({
                    'time': float(time_),
                    'type': type_,
                    'button': button,
                    'pos': pos
                })

            filename = self.model.fileName(self.ui.edit_Tab_TreeView.currentIndex())
            script_dir = os.path.dirname(__file__)
            filepath = os.path.join(
                script_dir,
                'recordings',
                filename
            )
            with open(filepath, 'w') as outfile:
                json.dump(actions, outfile, indent=4)

            self.ui.edit_Tab_DataTable.clear()
            self.ui.edit_Tab_DataTable.setRowCount(0)
            self.ui.edit_Tab_DataTable.setHorizontalHeaderLabels(["Time", "Type", "Button", "Pos X", "Pos Y"])

    def clear_Data_Table(self):
        self.ui.edit_Tab_DataTable.clear()
        self.ui.edit_Tab_DataTable.setRowCount(0)
        self.ui.edit_Tab_DataTable.setHorizontalHeaderLabels(["Time", "Type", "Button", "Pos X", "Pos Y"])


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Trainer = Hank()
    Trainer.show()
    sys.exit(app.exec_())
