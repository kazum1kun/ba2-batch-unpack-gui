from PySide6.QtCore import Qt, QUrl
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QFileDialog
from qfluentwidgets import FluentIcon as Fi
from qfluentwidgets import (SubtitleLabel, setFont, LargeTitleLabel, HyperlinkLabel, CaptionLabel, LineEdit, ToolButton,
                            TogglePushButton, TableWidget,
                            ToolTipFilter)

from PreviewTableModel import PreviewTableModel
from Utilities import *


class MainScreen(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('MainScreen')
        self.layout = QVBoxLayout(self)

        # Title of the app
        self.title_label = LargeTitleLabel('Batch BA2 Unpacker', self)

        # Subtitles
        self.subtitle_layout = QHBoxLayout(self)

        self.subtitle_label_1 = CaptionLabel(' by KazumaKuun | ', self)
        self.subtitle_label_2 = HyperlinkLabel(QUrl('https://www.nexusmods.com/fallout4/mods/1'), 'Nexus')
        self.subtitle_label_3 = CaptionLabel(' | ', self)
        self.subtitle_label_4 = HyperlinkLabel(QUrl('https://github.com/kazum1kun/ba2-batch-unpack'), 'GitHub')

        # Subsection Setup
        self.setup_title = SubtitleLabel('Setup', self)

        # Folder chooser
        self.chooser_layout = QHBoxLayout(self)
        self.folder_input = LineEdit(self)
        self.folder_button = ToolButton(Fi.FOLDER)

        # Threshold
        self.threshold_layout = QHBoxLayout(self)
        self.threshold_input = LineEdit(self)
        self.threshold_button = TogglePushButton(Fi.SYNC, 'Auto')

        # Subsection Preview
        self.preview_title = SubtitleLabel('Preview', self)

        # File table
        self.preview_table = TableWidget(self)

        self.setup_interface()

    def setup_interface(self):
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.title_label, 0, Qt.AlignmentFlag.AlignLeft)
        self.subtitle_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        setFont(self.subtitle_label_1, 14)
        self.subtitle_layout.addWidget(self.subtitle_label_1)
        self.subtitle_layout.addWidget(self.subtitle_label_2)
        self.subtitle_layout.addWidget(self.subtitle_label_3)
        self.subtitle_layout.addWidget(self.subtitle_label_4)

        self.layout.addLayout(self.subtitle_layout, 0)
        self.layout.addWidget(self.setup_title, 0, Qt.AlignmentFlag.AlignLeft)

        self.chooser_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.folder_input.setPlaceholderText('Fallout 4 mod directory')
        # Open a folder chooser when clicking
        self.folder_button.clicked.connect(self.open_folder)
        self.chooser_layout.addWidget(self.folder_input)
        self.chooser_layout.addWidget(self.folder_button)
        self.layout.addLayout(self.chooser_layout)

        self.threshold_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.threshold_input.setPlaceholderText('File size threshold')

        # Perform auto threshold calculation and disable user input box
        self.threshold_button.clicked.connect(self.auto_toggled)
        self.threshold_button.setToolTip('Automatically attempts to determine a\n'
                                         'threshold so that just enough BA2 are\n'
                                         'extracted to get under the BA2 limit')
        self.threshold_button.setToolTipDuration(5000)
        self.threshold_button.installEventFilter(ToolTipFilter(self.threshold_button))

        self.threshold_layout.addWidget(self.threshold_input)
        self.threshold_layout.addWidget(self.threshold_button)
        self.layout.addLayout(self.threshold_layout)

        self.layout.addWidget(self.preview_title, 0, Qt.AlignmentFlag.AlignLeft)

        # Tableview configs
        self.preview_table.setBorderVisible(True)
        self.preview_table.setBorderRadius(8)

        self.preview_table.setWordWrap(False)
        self.preview_table.setColumnCount(4)
        self.preview_table.setRowCount(20)

        self.preview_table.setHorizontalHeaderLabels(['File Name', 'File Size', '# Files', 'Path'])
        self.preview_table.resizeColumnsToContents()

        self.layout.addWidget(self.preview_table)

        # Leave some space for the title bar
        self.layout.setContentsMargins(10, 32, 10, 10)

    def open_folder(self):
        self.folder_input.setText(QFileDialog.getExistingDirectory(self, 'Open your Fallout 4 mod directory', options=
        QFileDialog.Option.ShowDirsOnly |
        QFileDialog.Option.DontResolveSymlinks))
        selected_folder = self.folder_input.text()
        ba2_paths = self.scan_ba2(selected_folder, ['main.ba2', 'scripts.ba2'])  ## TODO supply the real postfixes

        # Populate ba2 files and their properties
        ba2_dirs = [os.path.dirname(f) for f in ba2_paths]
        ba2_filenames = [os.path.basename(f) for f in ba2_paths]
        ba2_sizes = [readable_size(os.stat(f).st_size) for f in ba2_paths]
        ba2_num_files = [num_files_in_ba2('./bin/bsab.exe', f) for f in ba2_paths]
        ba2_ignored = [False for f in ba2_paths]

        self.preview_table.setModel(PreviewTableModel(ba2_dirs, ba2_filenames, ba2_sizes, ba2_num_files, ba2_ignored))

    def auto_toggled(self):
        # Disable threshold input if "Auto" is enabled
        self.threshold_input.setDisabled(self.threshold_input.isEnabled())
