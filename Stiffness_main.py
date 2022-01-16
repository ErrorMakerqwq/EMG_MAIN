# PyQt5 imports
#
from PyQt5.QtWidgets import (QWidget, QApplication, QVBoxLayout, QErrorMessage, QTabWidget, QStackedWidget, QTabBar)
from PyQt5.QtCore import QObject, pyqtSignal

# Miscellaneous imports
#
import sys
import time
#

from pymyolinux.core.myo import MyoDongle

from data_tools import DataTools


########################################################################################################################
########################################################################################################################
##### StiffnessGUI
########################################################################################################################
########################################################################################################################
class TopLevel(QWidget):
    """
        Main window containing all GUI components.
    """

    #
    # Used to cleanup background worker thread(s) (on exit)
    #
    class Exit(QObject):
        exitClicked = pyqtSignal()

    def closeEvent(self, event):
        self.close_event.exitClicked.emit()

    def __init__(self):
        super().__init__()

        self.close_event = self.Exit()  # Thread cleanup on exit
        self.close_event.exitClicked.connect(self.stop_background_workers)

        # Configurable
        self.worker_check_period = 1  # seconds

        self.init_ui()

    def init_ui(self):
        """
            Initializes the top-level tab widget and all sub tabs ("Data", "Training", "Testing")
        """
        self.setGeometry(0, 0, 1100, 800)
        self.setWindowTitle('Myo Tools')
        self.setObjectName("TopWidget")
        self.setStyleSheet("#TopWidget {background-color: white;}")

        #
        # Top-level layout
        #
        tools_layout = QVBoxLayout()
        self.tool_tabs = QTabWidget()

        # Fancy styling
        tab_widgets = self.tool_tabs.findChild(QStackedWidget)
        tab_widgets.setObjectName("TabWidgets")
        tools_layout.addWidget(self.tool_tabs)
        top_tabs = self.tool_tabs.findChild(QTabBar)
        top_tabs.setObjectName("TopTabs")
        self.tool_tabs.setStyleSheet(
            "QTabBar#TopTabs::tab {font-weight: bold; height:35px; width: 150px; border-radius: 3px; "
            "                   border: 2px solid #bbbbbb; background-color:#dddddd;}"
            "QStackedWidget#TabWidgets {background-color: #eeeeee;}")
        self.tool_tabs.currentChanged.connect(self.on_tab_changed)
        self.cur_index = 0

        self.data_tools_tab = DataTools(self.on_device_connected, self.on_device_disconnected,
                                        self.is_data_tools_open)

        self.tool_tabs.addTab(self.data_tools_tab, "Data Collection")
        # self.tool_tabs.addTab(self.online_training_tab, "Online Training")
        # self.tool_tabs.addTab(self.online_pred_tab, "Online Predictions")

        self.setLayout(tools_layout)
        self.show()

    def is_data_tools_open(self):
        return self.cur_index == 0

    def on_device_connected(self, address, rssi, battery_level):
        """
            Called on user initiated connection

        :param address: MAC address of connected Myo device
        """

    def on_device_disconnected(self, address):
        """
            Called on user initiated disconnect, or unexpected disconnect

        :param address: MAC address of disconnected Myo device
        """

    def on_tab_changed(self, value):
        """
            Intercepts a user attempting to switch tabs (to ensure a valid tab switch is taking place)

            value: Desired tab index to switch to
        """
        if self.cur_index == value:
            return
        valid_switch = False

        #
        # Determine if we can switch
        #
        data_tool_idx = 0

        if self.cur_index == data_tool_idx:
            #
            # Check for incomplete Myo search workers
            #
            waiting_on_search = False
            for worker in self.data_tools_tab.search_threads:
                if not worker.complete:
                    waiting_on_search = True
                    break

            if not waiting_on_search:

                #
                # Check for background data workers
                #

                # worker_running  = False
                # num_widgets     = self.data_tools_tab.ports_found.count()
                #
                # for idx in range(num_widgets):
                #     # Ignore port widgets (only interested in Myo device rows)
                #     list_widget = self.data_tools_tab.ports_found.item(idx)
                #     if hasattr(list_widget, "port_idx"):
                #         continue
                #
                #     myo_widget = self.data_tools_tab.ports_found.itemWidget(list_widget)
                #     if not (myo_widget.worker is None):
                #         if not myo_widget.worker.complete:
                #             worker_running = True
                #             break
                worker_running = False

                if not worker_running:

                    #
                    # Close the background video worker if appropriate
                    #

                    # if not self.data_tools_tab.gt_helper_open:
                    #     if not (self.data_tools_tab.gt_helper.worker is None):
                    #         self.data_tools_tab.gt_helper.stop_videos()
                    #
                    #         while not (self.data_tools_tab.gt_helper.worker.complete):
                    #             time.sleep(self.worker_check_period)
                    #
                    #     #
                    #     # IF we make it here, the switch is valid (for the case of the data tools tab)
                    #     #
                    #     valid_switch = True
                    # else:
                    #     self.warn_user("Please close GT Helper first.")

                    valid_switch = True

                else:
                    self.warn_user("Please close connection to Myo devices first.")
            else:
                self.warn_user("Please wait for Myo device search to complete first.")

        #
        # To control switching out of online training / testing
        #

        if valid_switch:
            self.cur_index = value
        else:
            self.tool_tabs.setCurrentIndex(self.cur_index)

    def stop_background_workers(self):
        """
            This function is called on (user click-initiated) exit of the main window.
        """
        self.data_tools_tab.stop_data_tools_workers()

    def warn_user(self, message):
        """
            Generates a pop-up warning message

        :param message: The text to display
        """
        self.warning = QErrorMessage()
        self.warning.showMessage(message)
        self.warning.show()


if __name__ == '__main__':
    gui = QApplication(sys.argv)
    top = TopLevel()

    # Event loop
    sys.exit(gui.exec_())
