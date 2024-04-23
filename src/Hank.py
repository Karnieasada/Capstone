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

mouse_listener = None

start_time = None

unreleased_keys = []

input_events = []

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
        self.record_model.setRootPath(os.path.dirname(os.path.abspath(sys.argv[0])))
        self.ui.record_treeView.setModel(self.record_model)
        self.ui.record_treeView.setRootIndex(self.record_model.index("Recordings"))
        self.ui.recordButton.clicked.connect(self.record_OnClick)
        self.ui.clearButton.clicked.connect(self.clear_run_OnCLick)

        # Defining the UI components for the Play Tab.
        self.play_model = QtWidgets.QFileSystemModel()
        self.play_model.setRootPath(os.path.dirname(os.path.abspath(sys.argv[0])))
        self.ui.play_tab_treeView.setModel(self.play_model)
        self.ui.play_tab_treeView.setRootIndex(self.play_model.index("Recordings"))
        self.ui.play_Tab_Button.clicked.connect(self.play_OnClick)
        self.ui.play_Tab_Clear.clicked.connect(self.clear_play_OnClear)

        # Defining the UI components for the Edit Tab.
        self.edit_model = QtWidgets.QFileSystemModel()
        self.edit_model.setRootPath(os.path.dirname(os.path.abspath(sys.argv[0])))
        self.ui.edit_Tab_TreeView.setModel(self.edit_model)
        self.ui.edit_Tab_TreeView.setRootIndex(self.edit_model.index("Recordings"))
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
        filepath = os.path.join(os.path.dirname(
            os.path.abspath(sys.argv[0])),
            'Recordings',
            '{}.json'.format(filename)
        )
        with open(filepath, 'w') as outfile:
            json.dump(input_events, outfile, indent=4)

        input_events = []

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
        # Grabbing the filename through the current index of the treeview file model.
        filename = self.play_model.fileName(self.ui.play_tab_treeView.currentIndex())
        self.ui.playMessage.setText('Playing ' + filename)
        # If no file selected warn the user and stop playback
        if filename == "":
            window = QtWidgets.QMessageBox()
            window.setIcon(QtWidgets.QMessageBox.Warning)
            window.setWindowTitle("Error")
            window.setText("No File Selected")
            window.setStandardButtons(QtWidgets.QMessageBox.Ok)
            window.exec_()

        # If a file is selected ask for delay timer to allow the user to get ready for playback start.
        elif filename != "":
            window = QtWidgets.QDialog()
            delay, val = QtWidgets.QInputDialog.getInt(
                window, 'Delay', 'Enter delay:', min=0, max=10)

            if val:
                for i in range(0, delay):
                    sleep(1)
                # Spin up thread and begin playback.
                t2 = threading.Thread(target=self.playback_Start, args=(filename,))
                t2.start()

    # Function starting the playback.
    def playback_Start(self, filename):
        self.initialize_PyDirectInput()
        self.play_Actions(filename)
        self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)
        self.ui.playMessage.setText('Finished')
        self.ui.play_Tab_textBrowser.append("Done")

    # Initializing Pydirectinput and setting its pause to 0.
    def initialize_PyDirectInput(self):
        # Set the pause between actions to 0.
        pydirectinput.PAUSE = 0.0

    # Function for iterating through the Json file and performing the actions.
    def play_Actions(self, filename):
        filepath = os.path.join(os.path.dirname(
            os.path.abspath(sys.argv[0])),
            'Recordings',
            filename
        )
        with open(filepath, 'r') as jsonfile:
            # Loading all the Json actions into an array.
            data = json.load(jsonfile)

            for index, action in enumerate(data):

                if action['button'] == 'Key.esc':
                    break
                # If the action in the array is keydown press the key.
                if action['type'] == 'keypressed':
                    key = convertKey(action['button'])
                    pydirectinput.keyDown(key)
                    self.ui.play_Tab_textBrowser.append('keydown on {0}'.format(key))
                    self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)
                # If the action is to release the key release the key.
                elif action['type'] == 'keyreleased':
                    key = convertKey(action['button'])
                    pydirectinput.keyUp(key)
                    self.ui.play_Tab_textBrowser.append('keyup on {0}'.format(key))
                    self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)
                # If the action is a click, click the mouse button listed in the array.
                # Move to the next mouse click screen position and wait for click release action.
                # This is to allow for recorded drag events to be performed as they were recorded.
                elif action['type'] == 'click':
                    key = convertKey(action['button'])
                    endpos = data[index + 1]
                    movetime = endpos['time'] - action['time']
                    pydirectinput.mouseDown(action['pos'][0], action['pos'][1], button=key)
                    pydirectinput.moveTo(endpos['pos'][0], endpos['pos'][1], duration=movetime)
                    self.ui.play_Tab_textBrowser.append('click {} on {}'.format(key, action['pos']))
                    self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)
                # If action is to release the mouse release the mouse at position given.
                elif action['type'] == 'clickreleased':
                    key = convertKey(action['button'])
                    pydirectinput.mouseUp(action['pos'][0], action['pos'][1], button=key, duration=0.25)
                    self.ui.play_Tab_textBrowser.append('click {} released on {}'.format(key, action['pos']))
                    self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)

                # Try to read the next action until no more actions are listed then break the loop in case
                # of any index error or end of file.
                try:
                    next_action = data[index + 1]
                except IndexError:
                    break
                # Calculate the time of the playback.
                elapsed_time = next_action['time'] - action['time']
                # Pausing between actions in order to play the recording back in sync with the recording.
                if elapsed_time >= 0:
                    self.ui.play_Tab_textBrowser.append('sleeping for {}'.format(elapsed_time))
                    self.ui.play_Tab_textBrowser.moveCursor(QtGui.QTextCursor.End)
                    sleep(elapsed_time)
                else:
                    sleep(0)

    # Clear the playback text window if the user wants to.
    def clear_play_OnClear(self):
        self.ui.play_Tab_textBrowser.clear()
        self.ui.playMessage.setText("")

    """
    This section contains all the functions related to the edit tab.
    """
    # Function controlling the loading of the actions Json file and populating the table to see and edit the file.
    def edit_Load_OnClick(self):
        # If no data in the table get filename from file model and open the file.
        if self.ui.edit_Tab_DataTable.rowCount() == 0:
            filename = self.edit_model.fileName(self.ui.edit_Tab_TreeView.currentIndex())
            # If no file is selected prompt the use to select a file.
            if filename == "":
                window = QtWidgets.QMessageBox()
                window.setIcon(QtWidgets.QMessageBox.Warning)
                window.setWindowTitle("Error")
                window.setText("No File Selected")
                window.setStandardButtons(QtWidgets.QMessageBox.Ok)
                window.exec_()
            # If the filename is valid continue and open the file.
            else:
                filepath = os.path.join(os.path.dirname(
                    os.path.abspath(sys.argv[0])),
                    'Recordings',
                    filename
                )
        
                with open(filepath, 'r') as jsonfile:
                    # Open the file and dump the data into and array.
                    data = json.load(jsonfile)
                    self.ui.edit_Tab_DataTable.setRowCount(len(data))
                    row = 0
                    # Iterate through the data and populate the table based on the action taken.
                    # If and elif are used to check the action so the position cells are either filled or left as none
                    # values.
                    for action in data:
                        if action['type'] == 'keypressed':
                            self.ui.edit_Tab_DataTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(action['time'])))
                            self.ui.edit_Tab_DataTable.setItem(row, 1, QtWidgets.QTableWidgetItem(action['type']))
                            self.ui.edit_Tab_DataTable.setItem(row, 2, QtWidgets.QTableWidgetItem(action['button']))
                            self.ui.edit_Tab_DataTable.setItem(
                                row, 3, QtWidgets.QTableWidgetItem(str('none')))
                            self.ui.edit_Tab_DataTable.setItem(
                                row, 4, QtWidgets.QTableWidgetItem(str('none')))
                        elif action['type'] == 'keyreleased':
                            self.ui.edit_Tab_DataTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(action['time'])))
                            self.ui.edit_Tab_DataTable.setItem(row, 1, QtWidgets.QTableWidgetItem(action['type']))
                            self.ui.edit_Tab_DataTable.setItem(row, 2, QtWidgets.QTableWidgetItem(action['button']))
                            self.ui.edit_Tab_DataTable.setItem(
                                row, 3, QtWidgets.QTableWidgetItem(str('none')))
                            self.ui.edit_Tab_DataTable.setItem(
                                row, 4, QtWidgets.QTableWidgetItem(str('none')))
                        elif action['type'] == 'click':
                            self.ui.edit_Tab_DataTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(action['time'])))
                            self.ui.edit_Tab_DataTable.setItem(row, 1, QtWidgets.QTableWidgetItem(action['type']))
                            self.ui.edit_Tab_DataTable.setItem(row, 2, QtWidgets.QTableWidgetItem(action['button']))
                            self.ui.edit_Tab_DataTable.setItem(
                                row, 3, QtWidgets.QTableWidgetItem(str(action['pos'][0])))
                            self.ui.edit_Tab_DataTable.setItem(
                                row, 4, QtWidgets.QTableWidgetItem(str(action['pos'][1])))
                        elif action['type'] == 'clickreleased':
                            self.ui.edit_Tab_DataTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(action['time'])))
                            self.ui.edit_Tab_DataTable.setItem(row, 1, QtWidgets.QTableWidgetItem(action['type']))
                            self.ui.edit_Tab_DataTable.setItem(row, 2, QtWidgets.QTableWidgetItem(action['button']))
                            self.ui.edit_Tab_DataTable.setItem(
                                row, 3, QtWidgets.QTableWidgetItem(str(action['pos'][0])))
                            self.ui.edit_Tab_DataTable.setItem(
                                row, 4, QtWidgets.QTableWidgetItem(str(action['pos'][1])))
                        row = row + 1

        # Making sure that if there is data already in the table the user clears the data and before loading
        # another file.
        elif self.ui.edit_Tab_DataTable.rowCount() > 0:
            window = QtWidgets.QMessageBox()
            window.setIcon(QtWidgets.QMessageBox.Warning)
            window.setWindowTitle("Error")
            window.setText("Data already loaded in table. Clear Data to load another file.")
            window.setStandardButtons(QtWidgets.QMessageBox.Ok)
            window.exec_()

    # Function controlling the save button used for saving the loaded data in the table.
    def edit_Save_OnClick(self):
        # Making sure there actually data in the table first.
        if self.ui.edit_Tab_DataTable.rowCount() == 0:
            window = QtWidgets.QMessageBox()
            window.setIcon(QtWidgets.QMessageBox.Warning)
            window.setWindowTitle("Error")
            window.setText("No Data To Save")
            window.setStandardButtons(QtWidgets.QMessageBox.Ok)
            window.exec_()
        # If there is data in the table prompt the user to rename the file or cancel and keep the filename.
        else:
            window = QtWidgets.QDialog()
            filename, val = QtWidgets.QInputDialog.getText(
                window, 'Save', 'Enter file name or click cancel to keep filename:')
            # If ok is clicked and filename not blank then read through the table based on the action
            if val:
                if filename == "":
                    window = QtWidgets.QMessageBox()
                    window.setIcon(QtWidgets.QMessageBox.Warning)
                    window.setWindowTitle("Error")
                    window.setText("No file name given. Please enter a valid file name.")
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
                        # Make sure if the action is a key press that we leave position null.
                        if self.ui.edit_Tab_DataTable.item(r, 1).text() == 'keypressed':
                            pos = None
                            actions.append({
                                'time': float(time_),
                                'type': type_,
                                'button': button,
                                'pos': pos
                            })
                        elif self.ui.edit_Tab_DataTable.item(r, 1).text() == 'keyreleased':
                            pos = None
                            actions.append({
                                'time': float(time_),
                                'type': type_,
                                'button': button,
                                'pos': pos
                            })
                        # If the action is a click we make sure we keep the position value.
                        elif self.ui.edit_Tab_DataTable.item(r, 1).text() == 'click':
                            pos = [int(posX), int(posY)]
                            actions.append({
                                'time': float(time_),
                                'type': type_,
                                'button': button,
                                'pos': pos
                            })
                        elif self.ui.edit_Tab_DataTable.item(r, 1).text() == 'clickreleased':
                            pos = [int(posX), int(posY)]
                            actions.append({
                                'time': float(time_),
                                'type': type_,
                                'button': button,
                                'pos': pos
                            })
                    filepath = os.path.join(os.path.dirname(
                        os.path.abspath(sys.argv[0])),
                        'Recordings',
                        '{}.json'.format(filename)
                    )
                    # Rewrite the file with the new given filename.
                    with open(filepath, 'w') as outfile:
                        json.dump(actions, outfile, indent=4)
                    # Take the old filename and delete the old file.
                    old_Filename = self.edit_model.fileName(self.ui.edit_Tab_TreeView.currentIndex())
                    old_Path = os.path.join(os.path.dirname(
                        os.path.abspath(sys.argv[0])),
                        'Recordings',
                        old_Filename
                    )
                    os.remove(old_Path)
                    # After the file is writen and saved then clear the data table and reset the header labels.
                    self.ui.edit_Tab_DataTable.clear()
                    self.ui.edit_Tab_DataTable.setRowCount(0)
                    self.ui.edit_Tab_DataTable.setHorizontalHeaderLabels(["Time", "Type", "Button", "Pos X", "Pos Y"])

            # If cancel is pressed we iterate through the table and rewrite the file and keep the same name.
            # Using the same method as above to either keep positional values or Leave them Null.
            else:
                row = self.ui.edit_Tab_DataTable.rowCount()
                actions = []
                for r in range(row):
                    time_ = self.ui.edit_Tab_DataTable.item(r, 0).text()
                    type_ = self.ui.edit_Tab_DataTable.item(r, 1).text()
                    button = self.ui.edit_Tab_DataTable.item(r, 2).text()
                    posX = self.ui.edit_Tab_DataTable.item(r, 3).text()
                    posY = self.ui.edit_Tab_DataTable.item(r, 4).text()
                    if self.ui.edit_Tab_DataTable.item(r, 1).text() == 'keypressed':
                        pos = None
                        actions.append({
                            'time': float(time_),
                            'type': type_,
                            'button': button,
                            'pos': pos
                        })
                    elif self.ui.edit_Tab_DataTable.item(r, 1).text() == 'keyreleased':
                        pos = None
                        actions.append({
                            'time': float(time_),
                            'type': type_,
                            'button': button,
                            'pos': pos
                        })
                    elif self.ui.edit_Tab_DataTable.item(r, 1).text() == 'click':
                        pos = [int(posX), int(posY)]
                        actions.append({
                            'time': float(time_),
                            'type': type_,
                            'button': button,
                            'pos': pos
                        })
                    elif self.ui.edit_Tab_DataTable.item(r, 1).text() == 'clickreleased':
                        pos = [int(posX), int(posY)]
                        actions.append({
                            'time': float(time_),
                            'type': type_,
                            'button': button,
                            'pos': pos
                        })
                filename = self.edit_model.fileName(self.ui.edit_Tab_TreeView.currentIndex())
                filepath = os.path.join(os.path.dirname(
                    os.path.abspath(sys.argv[0])),
                    'Recordings',
                    filename
                )
                with open(filepath, 'w') as outfile:
                    json.dump(actions, outfile, indent=4)
                # After the file is writen and saved then clear the data table and reset the header labels.
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
    app.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(
                    os.path.abspath(sys.argv[0])),
                    'hank.ico')))
    Trainer = Hank()
    Trainer.show()
    sys.exit(app.exec_())
