import os.path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QFileDialog, QBoxLayout
from qfluentwidgets import FluentIcon as Fi, PrimaryPushButton, \
    StrongBodyLabel, ProgressBar, TextEdit, CheckBox
from qfluentwidgets import (SubtitleLabel, LineEdit, ToolButton)

from misc.BsaChecker import BsaChecker
from misc.Config import cfg
from prefab.InfoBar import show_result_toast


class CheckFileScreen(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('CheckFileScreen')
        self.layout = QVBoxLayout(self)

        # Subsection Setup
        self.setup_title = SubtitleLabel(self.tr('ba2 checkup setup'), self)
        self.top_layout = QHBoxLayout()

        # Folder chooser
        self.folder_layout = QVBoxLayout()
        self.folder_label = StrongBodyLabel(self.tr('Fallout 4 mod folder'), self)
        self.folder_layout_inner = QHBoxLayout()
        self.folder_input = LineEdit(self)
        self.folder_button = ToolButton(Fi.FOLDER, self)

        # Deep scan
        self.deep_scan_title = StrongBodyLabel(self.tr('Deep scan'), self)
        self.deep_scan_checkbox = CheckBox(self.tr('Enable'), self)
        self.deep_scan_layout = QVBoxLayout()

        # Start button
        self.start_layout = QHBoxLayout()
        self.start_button = PrimaryPushButton(Fi.SEND_FILL, self.tr('Start'), self)

        # Results
        self.preview_title = SubtitleLabel(self.tr('Results'), self)
        self.results_box = TextEdit(self)
        self.preview_progress = ProgressBar()

        # Hint on top of the preview table
        self.preview_hint_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight, self.results_box)
        self.preview_hint = SubtitleLabel(self.tr('Select or drag \'n drop a folder here to get started'), self)

        self.__setup_interface()

        self.checker = None
        self.first_output = True

    def __setup_interface(self):
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Setup section
        self.layout.addWidget(self.setup_title, 0, Qt.AlignmentFlag.AlignLeft)

        # Folder chooser
        self.folder_input.setPlaceholderText(self.tr('Fallout 4 mod folder'))
        self.folder_input.returnPressed.connect(self.__check_folder)
        # Open a folder chooser when clicking
        self.folder_button.clicked.connect(self.__open_folder)

        self.folder_layout_inner.addWidget(self.folder_input)
        self.folder_layout_inner.addWidget(self.folder_button)
        self.folder_layout.addWidget(self.folder_label)
        self.folder_layout.addLayout(self.folder_layout_inner)

        # Deep scan
        self.deep_scan_checkbox.setToolTip(self.tr('In addition to reading the content of the ba2 files,\n'
                                                   'this will also extract the ba2 files to a temporary\n'
                                                   'location to check for errors. Usually not necessary.'))
        self.deep_scan_layout.addWidget(self.deep_scan_title)
        self.deep_scan_layout.addWidget(self.deep_scan_checkbox)

        # Start button
        self.start_button.setMaximumWidth(300)
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.__check_files)
        self.start_layout.addWidget(self.start_button)

        # Top layout
        self.top_layout.addLayout(self.folder_layout)
        self.top_layout.addSpacing(15)
        self.top_layout.addLayout(self.deep_scan_layout)

        self.layout.addLayout(self.top_layout)
        self.layout.addSpacing(10)
        self.layout.addLayout(self.start_layout)

        self.layout.addWidget(self.preview_title)
        self.results_box.setReadOnly(True)
        self.results_box.setFontPointSize(10)
        self.layout.addWidget(self.results_box)

        # Hide the progress bar in the beginning
        sp = self.preview_progress.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.preview_progress.setSizePolicy(sp)
        self.preview_progress.setHidden(True)
        self.layout.addWidget(self.preview_progress)

        # Leave some space for the title bar
        self.layout.setContentsMargins(60, 42, 60, 10)

        # Drag and drop
        self.preview_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_hint_layout.addWidget(self.preview_hint, 0, Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)

        self.setLayout(self.layout)

    def __check_files(self):
        self.results_box.clear()
        self.results_box.append(self.tr('Checking ba2 files...'))
        self.preview_progress.setHidden(False)
        self.preview_progress.setValue(0)
        self.preview_progress.setError(False)

        # deep scan
        if self.deep_scan_checkbox.isChecked():
            self.checker = BsaChecker(self, self.folder_input.text(), True)
        else:
            # normal scan
            self.checker = BsaChecker(self, self.folder_input.text(), False)
        self.checker.done_processing.connect(self.__show_results)
        self.checker.issue_found.connect(self.__update_output)
        self.checker.start()
        self.checker.finished.connect(self.__check_finished)

    def __check_finished(self):
        del self.checker
        self.results_box.append(self.tr('Done!'))

    def __update_output(self, text):
        if self.first_output:
            self.results_box.clear()
            self.first_output = False

            self.results_box.append(self.tr('The following files did not pass the check:'))
            self.results_box.append(text)
        else:
            self.results_box.append(text)

    def __show_results(self, results):
        show_result_toast(results, 'check')

    def __check_folder(self):
        folder = self.folder_input.text()
        if not os.path.isdir(folder):
            self.start_button.setEnabled(False)
            return
        self.start_button.setEnabled(True)
        self.preview_hint.setText('')
        cfg.set(cfg.saved_dir, folder)

    def __open_folder(self):
        self.folder_input.setText(QFileDialog.getExistingDirectory(self, self.tr('Open your Fallout 4 mod folder'),
                                                                   options=QFileDialog.Option.ShowDirsOnly |
                                                                           QFileDialog.Option.DontResolveSymlinks))
        self.__check_folder()

        # Drag and drop

    def dragEnterEvent(self, event):
        self.preview_hint.setText(self.tr('Drop your Fallout 4 mod folder here'))
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.preview_hint.setText(self.tr('Select or drag \'n drop a folder here to get started'))

    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        if len(files) == 1 and os.path.isdir(files[0]):
            self.folder_input.setText(files[0])
            self.preview_hint.setText('')
            self.__check_folder()