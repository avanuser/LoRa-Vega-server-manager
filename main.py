# Qt Python LoRa Vega Management program

import json
import sys

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QApplication, QMainWindow

from controls import *
from lora_vega_manager import LoRaVegaManager

###############################################################

term_title = 'Qt LoRa Vega Manager'

win_min_height = 500
win_min_width = 600

term_min_width = 400

# Names of notebook's tables
tab1Name = 'Basic'
tab2Name = 'Etc'

def_btn_fg_color = 'black'
def_btn_bg_color = '#eeeeee'
btn_font_family = 'Titillium'
btn_font_size = '12px'

auth_req = '{"cmd": "auth_req","login": "root","password": "123"}'
ping_req = '{"cmd": "ping_req"}'
get_users_req = '{"cmd": "get_users_req"}'
server_info_req = '{"cmd": "server_info_req"}'
get_device_appdata_req = '{"cmd": "get_device_appdata_req"}'
get_gateways_req = '{"cmd": "get_gateways_req"}'

###############################################################

# Tab button [0,1,2,3]:
# 0 - label of the button
# 1 - command to send
# 2 - foreground color
# 3 - background color

# --------------- TAB1 BUTTONS ---------------
T1_0 = [['ping_req', ping_req, '', ''],
        ['get_users_req', get_users_req, '', ''],
        ['server_info_req', server_info_req, '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', '']]

T1_1 = [['get_device_appdata_req', get_device_appdata_req, '', ''],
        ['get_gateways_req', get_gateways_req, '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', '']]

T1_2 = [['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', '']]

T1 = [T1_0, T1_1, T1_2]

# --------------- TAB2 BUTTONS ---------------
T2_0 = [['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', '']]

T2_1 = [['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', '']]

T2_2 = [['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', ''],
        ['', '', '', '']]

T2 = [T2_0, T2_1, T2_2]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.jsn = None
        self.setWindowTitle(term_title)
        self.statusBar().showMessage('Welcome!')
        #
        self.cnt = 0  # used to count '{' and '}' in data stream
        self.msg = ''
        # central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        hbox = QHBoxLayout(central_widget)
        vbox1 = QVBoxLayout()
        hbox.addLayout(vbox1)
        # create term
        self.term = QTextEdit()
        self.term.setReadOnly(True)
        self.term.setMinimumWidth(term_min_width)
        self.term.setStyleSheet("""
                background-color: #101010;
                color: #FFFFFF;
                font-family: Titillium;
                font-size: 12px;
                """)
        self.clr_btn = QPushButton('Clear term')
        self.clr_btn.setStyleSheet('background-color: #101010; color: #eeeeee;')
        self.clr_btn.clicked.connect(self.clear_term)
        # 
        vbox1.addWidget(self.term)
        vbox1.addWidget(self.clr_btn)
        # create vbox2
        vbox2 = QVBoxLayout()
        # add side panel to main window
        hbox.addLayout(vbox2)
        # create WebSocket client and bind handlers
        self.lora_vega_manager = LoRaVegaManager(addr='127.0.0.1', port='8002')
        self.lora_vega_manager.sock.textMessageReceived.connect(self.on_rx)
        # create send_any_cmd
        self.send_any_cmd = SendAny()
        self.send_any_cmd.any_btn.clicked.connect(self.send_any)
        # create notebook
        self.notebook = Notebook()
        # add tables to the notebook
        self.notebook.add_tab_btn(tab1Name, T1, self.send)
        self.notebook.add_tab_btn(tab2Name, T2, self.send)
        # add controls and notebook to side panel
        vbox2.addWidget(self.lora_vega_manager)
        vbox2.addWidget(self.send_any_cmd)
        vbox2.addWidget(self.notebook)

    def send(self, btn):
        cmd_to_send = btn.get_cmd()
        if cmd_to_send:
            if isinstance(cmd_to_send, str):  # if type of cmd_to_send is a <string>
                self.lora_vega_manager.sock.sendTextMessage(cmd_to_send)

    def send_any(self):
        if self.lora_vega_manager.connected:
            data = self.send_any_cmd.any_field.text()
            self.lora_vega_manager.sock.sendTextMessage(data)

    @Slot()
    def on_rx(self, rx_msg):
        jsn = None
        try:
            self.term.insertPlainText(rx_msg)
            self.term.insertPlainText('\r\r')
            self.term.ensureCursorVisible()
        except Exception:
            print('on_rx: something went wrong!')
        for i in rx_msg:
            if i == '{':
                self.cnt = self.cnt + 1
                self.msg = self.msg + i
            elif i == '}':
                self.cnt = self.cnt - 1
                self.msg = self.msg + i
                if self.cnt == 0:
                    self.jsn = self.msg
                    self.msg = ''
                    try:
                        jsn = json.loads(self.jsn)
                    except Exception:
                        print('on_rx: error decoding JSON!')
                    if jsn:
                        self.parse_msg(jsn)
            else:
                if self.cnt:
                    self.msg = self.msg + i

    def parse_msg(self, msg):
        if msg.get('cmd', '') == 'auth_resp':
            if msg.get('status'):
                self.lora_vega_manager.token = msg.get('token', '')
                if len(self.lora_vega_manager.token) == 32:
                    self.lora_vega_manager.auth = 1
                    self.lora_vega_manager.auth_status.setText('Auth OK')
                    self.lora_vega_manager.auth_status.setStyleSheet('color: #44d5cc;')
                    print('token: ', self.lora_vega_manager.token)
                    self.lora_vega_manager.log_monitor.log.insertPlainText('Lora manager: Auth OK!\r')
                    self.lora_vega_manager.log_monitor.log.ensureCursorVisible()
        elif msg.get('cmd', '') == 'close_auth_resp':
            if msg.get('status'):
                self.lora_vega_manager.auth = 0
                self.lora_vega_manager.auth_status.setText('No auth')
                self.lora_vega_manager.auth_status.setStyleSheet('color: red;')
                self.lora_vega_manager.log_monitor.log.insertPlainText('Lora manager: No auth\r')
                self.lora_vega_manager.log_monitor.log.ensureCursorVisible()
        err = msg.get('err_string', '')
        if err:
            self.lora_vega_manager.log_monitor.log.insertPlainText('Lora manager: ' + err + '\r')
            self.lora_vega_manager.log_monitor.log.ensureCursorVisible()

    def clear_term(self):
        self.term.clear()  # clear terminal

    def closeEvent(self, event):
        self.lora_vega_manager.close()
        event.accept()


def main():
    app = QApplication([])
    main_win = MainWindow()
    main_win.resize(win_min_width, win_min_height)
    main_win.show()
    sys.exit(app.exec())  # PySide6
    # sys.exit(app.exec_())  # PySide2


if __name__ == '__main__':
    main()
