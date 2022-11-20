# LoRaVegaManager class

from PySide6.QtCore import Slot, QUrl
from PySide6.QtNetwork import QAbstractSocket
from PySide6.QtWebSockets import QWebSocket
from PySide6.QtWidgets import QLabel

from controls import *


class LoRaVegaManager(QGroupBox):

    def __init__(self, addr='127.0.0.1', port='8002', user='root', password='123'):
        super().__init__()
        self.url = None
        self.password = None
        self.user = None
        self.setTitle('LoRa Vega manager')
        # add layouts
        vbox = QVBoxLayout(self)
        layout = QGridLayout()
        vbox.addLayout(layout)
        #
        self.connected = 0  # indicates if client is connected to server (1) or not (0)
        self.addr = addr  # remote address
        self.port = port  # remote port
        self.auth = 0  # no auth
        self.token = ''  # auth token
        self.sock = QWebSocket()
        self.sock.connected.connect(self.sock_connected)
        self.sock.disconnected.connect(self.sock_disconnected)
        self.sock.stateChanged.connect(self.state_changed)
        self.sock.error.connect(self.sock_error)

        # Line 0
        # socket status label
        self.socket_status = QLabel('Disconnected')
        self.socket_status.setStyleSheet('color: red;')
        self.socket_status.setMinimumWidth(100)
        self.socket_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.socket_status, 0, 3)

        # Line 1
        # controls for Server IP address
        self.url_label = QLabel('Server IP address: ')
        self.url_label.setMinimumWidth(100)
        self.url_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.url_label, 1, 1)
        #
        self.url_field = QLineEdit(addr)
        self.url_field.setMinimumWidth(100)
        self.url_field.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.url_field, 1, 2)
        #
        self.open_btn = QPushButton('Connect')
        self.open_btn.setStyleSheet('background-color: #00dd00;')
        layout.addWidget(self.open_btn, 1, 3)
        self.open_btn.clicked.connect(self.open)

        # Line 2
        # create controls for Server port
        self.port_label = QLabel('Server port: ')
        self.port_label.setMinimumWidth(90)
        self.port_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.port_label, 2, 1)
        #
        self.port_field = QLineEdit(port)
        self.port_field.setMinimumWidth(100)
        self.port_field.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.port_field, 2, 2)
        #
        self.close_btn = QPushButton('Disconnect')
        self.close_btn.setStyleSheet('background-color: red;')
        layout.addWidget(self.close_btn, 2, 3)
        self.close_btn.clicked.connect(self.close)

        # Line3
        # empty label
        self.empty_label = QLabel(' ')
        self.empty_label.setMinimumWidth(100)
        layout.addWidget(self.empty_label, 3, 3)

        # Line4
        # auth status label
        self.auth_status = QLabel('No auth')
        self.auth_status.setStyleSheet('color: red;')
        self.auth_status.setMinimumWidth(100)
        self.auth_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.auth_status, 4, 3)

        # Line5
        # create controls for user name
        self.user_label = QLabel('User: ')
        self.user_label.setMinimumWidth(90)
        self.user_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.user_label, 5, 1)
        #
        self.user_field = QLineEdit(user)
        self.user_field.setMinimumWidth(100)
        self.user_field.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.user_field, 5, 2)
        #
        self.open_auth = QPushButton('Auth req')
        self.open_auth.setStyleSheet('background-color: #44d5cc;')
        layout.addWidget(self.open_auth, 5, 3)
        self.open_auth.clicked.connect(self.auth_req)

        # Line 6
        # create controls for Password
        self.pass_label = QLabel('Password: ')
        self.pass_label.setMinimumWidth(90)
        self.pass_label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.pass_label, 6, 1)
        #
        self.pass_field = QLineEdit(password)
        self.pass_field.setMinimumWidth(100)
        self.pass_field.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pass_field, 6, 2)
        #
        self.close_auth = QPushButton('Auth close')
        self.close_auth.setStyleSheet('background-color: red;')
        layout.addWidget(self.close_auth, 6, 3)
        self.close_auth.clicked.connect(self.auth_close)

        # create log monitor
        self.log_monitor = LogMonitor()
        vbox.addWidget(self.log_monitor)

    def open(self):
        if self.connected == 0:
            self.addr = self.url_field.text()
            self.port = self.port_field.text()
            self.url = 'ws://' + self.addr + ':' + self.port
            print('Url: ', self.url)
            if self.addr:
                self.sock.open(QUrl(self.url))
            else:
                self.socket_status.setText('Please enter Url')
                self.socket_status.setStyleSheet('color: red;')

    def close(self):
        if self.connected:
            self.sock.close()

    def auth_req(self):
        if self.connected and self.auth == 0:
            self.user = self.user_field.text()
            self.password = self.pass_field.text()
            auth_req_msg = '{"cmd":"auth_req","login":"' + self.user + '","password":"' + self.password + '"}'
            print('auth_req_msg: ', auth_req_msg)
            self.sock.sendTextMessage(auth_req_msg)

    def auth_close(self):
        if self.auth:
            auth_close_msg = '{"cmd":"close_auth_req","token":"' + self.token + '"}'
            print('auth_close_msg: ', auth_close_msg)
            self.sock.sendTextMessage(auth_close_msg)

    @Slot()
    def sock_connected(self):
        self.socket_status.setText('Connected')
        self.socket_status.setStyleSheet('color: #00dd00;')  # green
        self.connected = 1

    @Slot()
    def sock_disconnected(self):
        self.socket_status.setText('Disconnected')
        self.socket_status.setStyleSheet('color: red;')
        self.connected = 0
        self.auth = 0
        self.token = ''
        self.auth_status.setText('No auth')
        self.auth_status.setStyleSheet('color: red;')
        self.log_monitor.log.insertPlainText('Lora manager: No auth\r')
        self.log_monitor.log.ensureCursorVisible()

    @Slot()
    def state_changed(self, state):
        if state == QAbstractSocket.SocketState.UnconnectedState:
            curr_state = 'Disconnected'
        elif state == QAbstractSocket.SocketState.HostLookupState:
            curr_state = 'Host Lookup...'
        elif state == QAbstractSocket.SocketState.ConnectingState:
            curr_state = 'Connecting...'
        elif state == QAbstractSocket.SocketState.ConnectedState:
            curr_state = 'Connected'
        elif state == QAbstractSocket.SocketState.BoundState:
            curr_state = 'Bound'
        elif state == QAbstractSocket.SocketState.ClosingState:
            curr_state = 'Closing...'
        else:
            curr_state = str(self.sock.state())
        self.log_monitor.log.insertPlainText('WebSocket: ' + curr_state + '\r')
        self.log_monitor.log.ensureCursorVisible()

    def sock_error(self):
        err = self.sock.error()
        if err == QAbstractSocket.ConnectionRefusedError:
            err_msg = 'Connection Refused Error'
        elif err == QAbstractSocket.RemoteHostClosedError:
            err_msg = 'Remote Host Closed Error'
        elif err == QAbstractSocket.HostNotFoundError:
            err_msg = 'Host Not Found Error'
        elif err == QAbstractSocket.SocketAccessError:
            err_msg = 'Socket Access Error'
        elif err == QAbstractSocket.SocketResourceError:
            err_msg = 'Socket Resource Error'
        elif err == QAbstractSocket.SocketTimeoutError:
            err_msg = 'Socket Timeout Error'
        elif err == QAbstractSocket.DatagramTooLargeError:
            err_msg = 'Datagram Too Large Error'
        elif err == QAbstractSocket.NetworkError:
            err_msg = 'Network Error'
        elif err == QAbstractSocket.AddressInUseError:
            err_msg = 'Address In Use Error'
        elif err == QAbstractSocket.SocketAddressNotAvailableError:
            err_msg = 'Socket Address Not Available Error'
        elif err == QAbstractSocket.UnsupportedSocketOperationError:
            err_msg = 'Unsupported Socket Operation Error'
        elif err == QAbstractSocket.ProxyAuthenticationRequiredError:
            err_msg = 'Proxy Authentication Required Error'
        elif err == QAbstractSocket.SslHandshakeFailedError:
            err_msg = 'Ssl Handshake Failed Error'
        elif err == QAbstractSocket.UnfinishedSocketOperationError:
            err_msg = 'Unfinished Socket Operation Error'
        elif err == QAbstractSocket.ProxyConnectionRefusedError:
            err_msg = 'Proxy Connection Refused Error'
        elif err == QAbstractSocket.ProxyConnectionClosedError:
            err_msg = 'Proxy Connection Closed Error'
        elif err == QAbstractSocket.ProxyConnectionTimeoutError:
            err_msg = 'Proxy Connection Timeout Error'
        elif err == QAbstractSocket.ProxyNotFoundError:
            err_msg = 'Proxy Not Found Error'
        elif err == QAbstractSocket.ProxyProtocolError:
            err_msg = 'Proxy Protocol Error'
        elif err == QAbstractSocket.OperationError:
            err_msg = 'Operation Error'
        elif err == QAbstractSocket.SslInternalError:
            err_msg = 'SslInternalError'
        elif err == QAbstractSocket.SslInvalidUserDataError:
            err_msg = 'Ssl Invalid User Data Error'
        elif err == QAbstractSocket.TemporaryError:
            err_msg = 'Temporary Error'
        elif err == QAbstractSocket.UnknownSocketError:
            err_msg = 'Unknown Socket Error'
        self.log_monitor.log.insertPlainText('WebSocket: ' + err_msg + '\r')
        self.log_monitor.log.ensureCursorVisible()
