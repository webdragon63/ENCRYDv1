import sys, os, subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog, QTextEdit, QCheckBox,
    QProgressBar, QFrame, QSizeGrip, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QPoint
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QBrush, QLinearGradient, QPen, QIcon
)

BIN_DIR = os.path.join(os.path.dirname(__file__), "output")
def get_bin(name):
    exe = os.path.join(BIN_DIR, name)
    if os.name == 'nt':
        exe += ".exe"
    return exe

class Worker(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)
    def __init__(self, args, password=None):
        super().__init__()
        self.args = args
        self.password = password
    def run(self):
        try:
            p = subprocess.Popen(
                self.args,
                stdin=subprocess.PIPE if self.password else None,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                bufsize=1, universal_newlines=True,
            )
            if self.password:
                p.stdin.write(self.password + "\n")
                p.stdin.flush()
            for line in p.stdout:
                self.output_signal.emit(line)
            code = p.wait()
            self.finished_signal.emit(code)
        except Exception as e:
            self.output_signal.emit(f"Error: {e}\n")
            self.finished_signal.emit(-1)

class MakeWorker(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(int)
    def run(self):
        try:
            p = subprocess.Popen(
                ["make"],
                cwd=os.path.dirname(__file__),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                bufsize=1, universal_newlines=True,
            )
            for line in p.stdout:
                self.output_signal.emit(line)
            code = p.wait()
            self.finished_signal.emit(code)
        except Exception as e:
            self.output_signal.emit(f"Make Error: {e}\n")
            self.finished_signal.emit(-1)

class NeonFrame(QFrame):
    def __init__(self, parent=None, color1="#00fff7", color2="#2dffae"):
        super().__init__(parent)
        self.setStyleSheet("background: rgba(24, 28, 32, 0.82); border-radius: 22px;")
        self.color1 = QColor(color1)
        self.color2 = QColor(color2)
        self._anim_val = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.animate)
        self._timer.start(30)
    def animate(self):
        self._anim_val = (self._anim_val + 4) % 360
        self.update()
    def paintEvent(self, event):
        super().paintEvent(event)
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        r = self.rect().adjusted(5,5,-5,-5)
        # Hi-tech glowing border: double neon gradient, animated
        grad_outer = QLinearGradient(r.topLeft(), r.bottomRight())
        grad_outer.setColorAt(0, self.color1.lighter(160))
        grad_outer.setColorAt(0.5, self.color2.lighter(180))
        grad_outer.setColorAt(1, self.color1.lighter(160))
        pen_outer = QPen(QBrush(grad_outer), 5)
        pen_outer.setCapStyle(Qt.RoundCap)
        pen_outer.setJoinStyle(Qt.RoundJoin)
        qp.setPen(pen_outer)
        qp.drawRoundedRect(r, 22, 22)
        # Animated dashed inner border
        grad_inner = QLinearGradient(r.topRight(), r.bottomLeft())
        grad_inner.setColorAt(0, self.color2.lighter(230))
        grad_inner.setColorAt(1, self.color1.lighter(230))
        pen_inner = QPen(QBrush(grad_inner), 2)
        pen_inner.setStyle(Qt.DotLine)
        pen_inner.setDashOffset(self._anim_val)
        qp.setPen(pen_inner)
        r_inner = r.adjusted(6,6,-6,-6)
        qp.drawRoundedRect(r_inner, 15, 15)
        # Optional: draw "corner widgets" for more hitec look
        for corner in [r_inner.topLeft(), r_inner.topRight(), r_inner.bottomLeft(), r_inner.bottomRight()]:
            qp.setBrush(QBrush(self.color1.lighter(180)))
            qp.setPen(Qt.NoPen)
            qp.drawEllipse(corner, 7, 7)

class TerminalOutput(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Fira Mono", 13))
        self.setStyleSheet("""
            background: #101215;
            color: #00fff7;
            border-radius: 12px;
            padding: 10px;
            selection-background-color: #38006e;
        """)
        self.setCursorWidth(2)
        self._scanline_timer = QTimer(self)
        self._scanline_timer.timeout.connect(self.repaint)
        self._scanline_timer.start(30)
    def paintEvent(self, event):
        super().paintEvent(event)
        qp = QPainter(self.viewport())
        h = self.viewport().height()
        w = self.viewport().width()
        qp.setOpacity(0.14)
        for y in range(0, h, 4):
            qp.fillRect(0, y, w, 2, QColor("#00fff7"))

class Sidebar(QWidget):
    tabChanged = pyqtSignal(int)
    def __init__(self, tabs):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(4,4,4,4)
        self.layout.setSpacing(12)
        self.buttons = []
        for idx, (name, icon) in enumerate(tabs):
            btn = QPushButton(icon + "  " + name)
            btn.setFont(QFont("Fira Mono", 13, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background: #101215;
                    color: #0FF;
                    border: 2px solid #222;
                    border-radius: 10px;
                    padding: 12px 10px;
                    text-align: left;
                }
                QPushButton:hover, QPushButton:checked {
                    background: #181C20;
                    color: #F0F;
                    border: 2px solid #0FF;
                }
            """)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, i=idx: self.change_tab(i))
            self.layout.addWidget(btn)
            self.buttons.append(btn)
        self.layout.addStretch()
        self.setFixedWidth(180)
        self.change_tab(0)
    def change_tab(self, idx):
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i==idx)
        self.tabChanged.emit(idx)

class BasePanel(QWidget):
    def __init__(self, title, icon, operation_fields, run_callback):
        super().__init__()
        neon = NeonFrame()
        vbox = QVBoxLayout(neon)
        vbox.setContentsMargins(24,24,24,24)
        head = QLabel(f"{icon}  <span style='font-size:22px;'>{title}</span>")
        head.setTextFormat(Qt.RichText)
        head.setStyleSheet("color: #fff; letter-spacing:3px; margin-bottom:12px;")
        head.setFont(QFont("Fira Mono", 18, QFont.Bold))
        vbox.addWidget(head)
        form = QFormLayout()
        self.fields = {}
        for label, field_type, *rest in operation_fields:
            field = None
            if field_type == "file":
                field = QLineEdit()
                field.setPlaceholderText("Choose file...")
                field.setMinimumHeight(35)
                field.setFont(QFont("Fira Mono", 12))
                field.setStyleSheet("""
                    background: #23242A;
                    color: #FFF;
                    border-radius: 7px;
                    border: 2px solid #2DFFAE;
                    padding-left: 10px;
                """)
                btn = QPushButton("FILE")
                btn.setMaximumWidth(40)
                btn.setMinimumHeight(35)
                btn.setStyleSheet("""
                    background:#101215;color:#0FF;
                    border-radius:7px;
                """)
                btn.clicked.connect(lambda _, f=field: self._pick_file(f, rest[0] if rest else "open"))
                h = QHBoxLayout(); h.setContentsMargins(0,0,0,0)
                h.addWidget(field); h.addWidget(btn)
                w = QWidget(); w.setLayout(h)
                form.addRow(label, w)
            elif field_type == "savefile":
                field = QLineEdit()
                field.setPlaceholderText("Choose save location...")
                field.setMinimumHeight(35)
                field.setFont(QFont("Fira Mono", 12))
                field.setStyleSheet("""
                    background: #23242A;
                    color: #FFF;
                    border-radius: 7px;
                    border: 2px solid #2DFFAE;
                    padding-left: 10px;
                """)
                btn = QPushButton("SAVE")
                btn.setMaximumWidth(40)
                btn.setMinimumHeight(35)
                btn.setStyleSheet("""
                    background:#101215;color:#0FF;
                    border-radius:7px;
                """)
                btn.clicked.connect(lambda _, f=field: self._pick_file(f, "save"))
                h = QHBoxLayout(); h.setContentsMargins(0,0,0,0)
                h.addWidget(field); h.addWidget(btn)
                w = QWidget(); w.setLayout(h)
                form.addRow(label, w)
            elif field_type == "password":
                field = QLineEdit()
                field.setEchoMode(QLineEdit.Password)
                field.setMinimumHeight(35)
                field.setFont(QFont("Fira Mono", 12))
                field.setStyleSheet("""
                    background: #23242A;
                    color: #FFF;
                    border-radius: 7px;
                    border: 2px solid #2DFFAE;
                    padding-left: 10px;
                """)
                cb = QCheckBox("👁 Show")
                cb.setStyleSheet("color: #0FF;")
                cb.setMinimumHeight(35)
                cb.stateChanged.connect(lambda x, f=field: f.setEchoMode(QLineEdit.Normal if x else QLineEdit.Password))
                h = QHBoxLayout(); h.setContentsMargins(0,0,0,0)
                h.addWidget(field); h.addWidget(cb)
                w = QWidget(); w.setLayout(h)
                form.addRow(label, w)
            else:
                field = QLineEdit()
                field.setMinimumHeight(35)
                field.setFont(QFont("Fira Mono", 12))
                field.setStyleSheet("""
                    background: #23242A;
                    color: #FFF;
                    border-radius: 7px;
                    border: 2px solid #2DFFAE;
                    padding-left: 10px;
                """)
                form.addRow(label, field)
            self.fields[label] = field
        vbox.addLayout(form)
        self.outterm = TerminalOutput()
        vbox.addWidget(self.outterm, 1)
        self.progress = QProgressBar()
        self.progress.setMaximum(0)
        self.progress.setMinimum(0)
        self.progress.setVisible(False)
        self.progress.setStyleSheet("""
            QProgressBar {
                background: #101215;
                border: 2px solid #0FF;
                border-radius: 8px;
                text-align: center;
                color: #0FF;
                font-size: 15px;
            }
            QProgressBar::chunk {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1FF7E0, stop:1 #2DFFAE
                );
                border-radius: 8px;
            }
        """)
        vbox.addWidget(self.progress)
        self.run_btn = QPushButton("▶ Run")
        self.run_btn.setFont(QFont("Fira Mono", 17, QFont.Bold))
        self.run_btn.setMinimumHeight(45)
        self.run_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0FF, stop:1 #1FF7E0);
                color: #181C20;
                border-radius: 14px;
                border: 2px solid #0FF;
                padding: 12px 30px;
                font-size: 17px;
            }
            QPushButton:hover {
                background: #1FF7E0;
                color: #fff;
                border: 2px solid #2DFFAE;
            }
        """)
        self.run_btn.clicked.connect(lambda: run_callback(self))
        vbox.addWidget(self.run_btn)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(neon)

    def _pick_file(self, field, mode):
        dlg = QFileDialog(self)
        dlg.setStyleSheet("""
            * { color: #fff; background: #23242A; }
            QLineEdit, QLabel, QTreeView, QListView, QHeaderView { color: #fff; background: #000000; }
            QPushButton { color: #fff; background: #101215; border-radius:6px;}
            QDialogButtonBox QPushButton { color: #fff; }
        """)
        if mode=="open":
            dlg.setFileMode(QFileDialog.ExistingFile)
            if dlg.exec_():
                files = dlg.selectedFiles()
                if files:
                    field.setText(files[0])
        else:
            dlg.setAcceptMode(QFileDialog.AcceptSave)
            if dlg.exec_():
                files = dlg.selectedFiles()
                if files:
                    field.setText(files[0])

    def log(self, msg):
        self.outterm.append(msg)
    def run_worker(self, args, password=None):
        self.outterm.clear()
        self.progress.setVisible(True)
        self.worker = Worker(args, password)
        self.worker.output_signal.connect(self.log)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()
    def on_finished(self, code):
        self.progress.setVisible(False)
        if code == 0:
            self.log("<span style='color:#0f0;'>\n[Success]</span>")
        else:
            self.log("<span style='color:#F77;'>\n[Failed. Exit code: %s]</span>"%code)

class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ENCRYD_v1")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(1250, 930)
        self.setMinimumSize(700, 400)
        neon = NeonFrame()
        neon.setStyleSheet("background: rgba(24,28,32,0.82); border-radius: 24px;")
        layout = QHBoxLayout(neon)
        layout.setContentsMargins(0,0,0,0)
        sidebar = Sidebar([
            ("Encrypt", "🔒"),
            ("Decrypt", "🔓"),
        ])
        layout.addWidget(sidebar)
        self.panels = []
        def make_panel(tab):
            if tab==0: # Encrypt
                return BasePanel("Encrypt", "🔒", [
                    ("Input file", "file"),
                    ("Output file", "savefile"),
                    ("Password", "password"),
                ], self.run_encrypt)
            elif tab==1: # Decrypt
                return BasePanel("Decrypt", "🔓", [
                    ("Encrypted file", "file"),
                    ("Output file", "savefile"),
                    ("Password", "password"),
                ], self.run_decrypt)
        self.stack = QWidget()
        self.stack_layout = QVBoxLayout(self.stack)
        self.stack_layout.setContentsMargins(0,0,0,0)
        self.stack_layout.setSpacing(0)
        for i in range(2):
            p = make_panel(i)
            self.panels.append(p)
            p.setVisible(i==0)
            self.stack_layout.addWidget(p)
        layout.addWidget(self.stack, 1)
        neon_layout = QVBoxLayout(self)
        neon_layout.setContentsMargins(20, 20, 20, 20)
        neon_layout.addWidget(neon)
        # Top bar with title and window controls
        toph = QHBoxLayout()
        self.dashboard = QLabel("""
<span style='color:#0FF;font-size:38px;font-weight:bold;'>ENCRYD_v1</span><br>
<span style='color:#2DFFAE;font-size:19px;'>  Made By WebDragon63</span>
""")
        self.dashboard.setAlignment(Qt.AlignCenter)
        self.dashboard.setStyleSheet("padding: 22px; letter-spacing:3px;")
        toph.addWidget(self.dashboard, 1)
        # Window control buttons (minimize, maximize/restore, close)
        btnbar = QHBoxLayout()
        btnbar.setSpacing(8)
        self.btn_min = QPushButton("—")
        self.btn_min.setFixedSize(32, 32)
        self.btn_min.setStyleSheet("background:#101215;color:#0FF;font-size:20px;border-radius:9px;")
        self.btn_min.clicked.connect(self.showMinimized)
        self.btn_max = QPushButton("▢")
        self.btn_max.setFixedSize(32, 32)
        self.btn_max.setStyleSheet("background:#101215;color:#0FF;font-size:18px;border-radius:9px;")
        self.btn_max.clicked.connect(self.toggle_fullscreen)
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(32, 32)
        self.btn_close.setStyleSheet("background:#101215;color:#F77;font-size:16px;border-radius:9px;")
        self.btn_close.clicked.connect(self.close)
        btnbar.addWidget(self.btn_min)
        btnbar.addWidget(self.btn_max)
        btnbar.addWidget(self.btn_close)
        toph.addLayout(btnbar)
        neon_layout.insertLayout(0, toph)
        sidebar.tabChanged.connect(self.set_tab)
        self.sizegrip = QSizeGrip(self)
        neon_layout.addWidget(self.sizegrip, 0, Qt.AlignBottom | Qt.AlignRight)
        # Build/Make button
        self.make_btn = QPushButton("🛠 Build C Binaries")
        self.make_btn.setFont(QFont("Fira Mono", 13, QFont.Bold))
        self.make_btn.setMinimumHeight(45)
        self.make_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0FF, stop:1 #1FF7E0);
                color: #181C20;
                border-radius: 10px;
                border: 2px solid #0FF;
                padding: 8px 16px;
                font-size: 17px;
            }
            QPushButton:hover {
                background: #1FF7E0;
                color: #000;
                border: 2px solid #2DFFAE;
            }
        """)
        self.make_btn.clicked.connect(self.run_make)
        neon_layout.addWidget(self.make_btn, 0, Qt.AlignTop)
        # Panel to show make output
        self.make_term = TerminalOutput()
        self.make_term.setFixedHeight(120)
        neon_layout.addWidget(self.make_term, 0, Qt.AlignTop)
        self._drag_active = False
        self._drag_pos = None

    def set_tab(self, idx):
        for i, p in enumerate(self.panels):
            p.setVisible(i==idx)

    def run_encrypt(self, panel):
        infile = panel.fields["Input file"].text()
        outfile = panel.fields["Output file"].text()
        password = panel.fields["Password"].text()
        if not (infile and outfile and password):
            panel.log("<span style='color:#F77;'>Please provide all fields.</span>")
            return
        # Always output .bin for encryption
        if not outfile.lower().endswith('.bin'):
            outfile += '.bin'
            panel.fields["Output file"].setText(outfile)
        args = [get_bin("encryptor"), infile, outfile]
        panel.run_worker(args, password=password)
    def run_decrypt(self, panel):
        infile = panel.fields["Encrypted file"].text()
        outfile = panel.fields["Output file"].text()
        password = panel.fields["Password"].text()
        if not (infile and outfile and password):
            panel.log("<span style='color:#F77;'>Please provide all fields.</span>")
            return
        args = [get_bin("decryptor"), infile, outfile]
        panel.run_worker(args, password=password)
    def run_make(self):
        self.make_term.clear()
        self.make_btn.setEnabled(False)
        self.make_worker = MakeWorker()
        self.make_worker.output_signal.connect(self.make_term.append)
        self.make_worker.finished_signal.connect(self.make_done)
        self.make_worker.start()
    def make_done(self, code):
        self.make_btn.setEnabled(True)
        if code == 0:
            self.make_term.append("<span style='color:#0f0;'>[Build Success]</span>")
        else:
            self.make_term.append("<span style='color:#F77;'>[Build Failed]</span>")
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    def mouseMoveEvent(self, event):
        if self._drag_active:
            self.move(event.globalPos() - self._drag_pos)
            event.accept()
    def mouseReleaseEvent(self, event):
        self._drag_active = False
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
            self.btn_max.setText("▢")
        else:
            self.showFullScreen()
            self.btn_max.setText("❐")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Fira Mono")
    if not font.exactMatch():
        font = QFont("Consolas")
    app.setFont(font)
    win = DashboardWindow()
    win.show()
    sys.exit(app.exec_())
