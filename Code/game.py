from IPython.lib import backgroundjobs as bg
import ipywidgets as widgets
from IPython.display import display
import time


# --------------------------------------
# ---
# --------------------------------------

jobs = bg.BackgroundJobManager()

RUNNING = 0
PAUSED = 1
END = 2

class Game:
    gameStatus = RUNNING
    state = None
    messages = None

    def __init__(self, showDisplay = True, updateTime = 0.2):
        self.SLEEP_TIME = updateTime
        self.display = showDisplay
        if self.display:
            pauseButton = widgets.Button(description='Run',
                                    disabled=False,
                                    button_style='info',
                                    tooltip='Change game status',
                                    icon='check',
                                    width = '120px')
            pauseButton.on_click(lambda b: self.setGameStatus(b))
            stepButton = widgets.Button(description='Step',
                                    disabled=False,
                                    button_style='info',
                                    tooltip='Next State',
                                    icon='check',
                                    width = '120px')
            stepButton.on_click(lambda b: self.gameStep())
            stopButton = widgets.Button(description='Stop',
                                    disabled=False,
                                    button_style='info',
                                    tooltip='Stop game',
                                    icon='check',
                                    width = '120px')
            stopButton.on_click(lambda b: self.stopGame())
            self.messages = widgets.Label(value="")
            self.layout = widgets.HBox([self.setBoardView(),
                                widgets.VBox([self.setStateView(),
                                                self.setActionButtons(),
                                                pauseButton,
                                                stepButton,
                                                stopButton,
                                                self.messages
                                                ])
                                ])
            display(self.layout)
            self.thread = jobs.new('self.playGame()')
        else: 
            self.gameStatus = RUNNING
            self.playGame()

    def setGameStatus(self,button):
        if self.gameStatus==RUNNING:
            self.gameStatus = PAUSED
            button.description = 'Run'
        else:
            self.gameStatus = RUNNING
            button.description = 'Pause'

    def stopGame(self):
        if self.display: jobs.flush()
        #self.layout.close()
        self.gameStatus = END

    def playGame(self):
        while True:
            if self.gameStatus==END:
                break
            elif self.gameStatus==RUNNING:
                self.gameStep()
            if self.display: time.sleep(self.SLEEP_TIME)
