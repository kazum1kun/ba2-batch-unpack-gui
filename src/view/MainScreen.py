import os.path

from PySide6.QtCore import Qt, QUrl, QModelIndex, QAbstractItemModel
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QFileDialog, QHeaderView, QBoxLayout, \
    QAbstractScrollArea
from qfluentwidgets import FluentIcon as Fi, IndeterminateProgressBar, TableView, PushButton, PrimaryPushButton, \
    BodyLabel, StrongBodyLabel, RoundMenu, Action, ProgressBar, InfoBarIcon, MessageBox
from qfluentwidgets import (SubtitleLabel, setFont, LargeTitleLabel, HyperlinkLabel, CaptionLabel, LineEdit, ToolButton,
                            TogglePushButton, TableWidget,
                            ToolTipFilter)
from qfluentwidgets.components.widgets.acrylic_label import AcrylicLabel
from humanize import naturalsize
from model.PreviewTableModel import *

from misc.Utilities import *


class MainScreen(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName('MainScreen')
        self.layout = QVBoxLayout(self)

        # Title of the app
        self.title_label = LargeTitleLabel('Unpackerr', self)

        # # Subtitles
        # self.subtitle_layout = QHBoxLayout(self)
        #
        # self.subtitle_label_1 = CaptionLabel(' by KazumaKuun | ', self)
        # self.subtitle_label_2 = HyperlinkLabel(QUrl('https://www.nexusmods.com/fallout4/mods/1'), 'Nexus')
        # self.subtitle_label_3 = CaptionLabel(' | ', self)
        # self.subtitle_label_4 = HyperlinkLabel(QUrl('https://github.com/kazum1kun/ba2-batch-unpack'), 'GitHub')

        # Subsection Setup
        self.setup_title = SubtitleLabel('Setup', self)
        self.setup_layout = QHBoxLayout(self)

        # Folder chooser
        self.folder_layout = QVBoxLayout(self)
        self.folder_layout_inner = QHBoxLayout(self)
        self.folder_label = StrongBodyLabel('Fallout 4 mod folder', self)
        self.folder_input = LineEdit(self)
        self.folder_button = ToolButton(Fi.FOLDER, self)

        # Threshold
        self.threshold_layout = QVBoxLayout(self)
        self.threshold_layout_inner = QHBoxLayout(self)
        self.threshold_label = StrongBodyLabel('Extraction size threshold', self)
        self.threshold_input = LineEdit(self)
        self.threshold_button = TogglePushButton(Fi.SYNC, 'Auto', self)

        # Start button
        self.start_layout = QHBoxLayout(self)
        self.start_button = PrimaryPushButton(Fi.SEND_FILL, 'Start', self)

        # Subsection Preview
        self.preview_title = SubtitleLabel('Preview', self)

        self.preview_progress = ProgressBar()

        # File table
        self.preview_table = TableView(self)

        # Hint on top of the preview table
        self.preview_hint_layout = QBoxLayout(QBoxLayout.Direction.LeftToRight, self.preview_table)
        self.preview_hint = SubtitleLabel('Select a folder to get started', self)

        # File related
        self.processor = None
        self.file_data: list[FileEntry] = []

        self.table_ready = False
        self.persistent_tooltip = None

        self.setup_interface()

    def setup_interface(self):
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.title_label, 0, Qt.AlignmentFlag.AlignLeft)

        # Setup section
        self.layout.addWidget(self.setup_title, 0, Qt.AlignmentFlag.AlignLeft)

        # Folder chooser
        self.folder_layout_inner.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.folder_input.setPlaceholderText('Fallout 4 mod directory')
        # Open a folder chooser when clicking
        self.folder_button.clicked.connect(self.open_folder)

        self.folder_layout_inner.addWidget(self.folder_input)
        self.folder_layout_inner.addWidget(self.folder_button)
        self.folder_layout.addWidget(self.folder_label)
        self.folder_layout.addLayout(self.folder_layout_inner)

        # Threshold
        self.threshold_layout_inner.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.threshold_input.setPlaceholderText('Threshold')
        self.threshold_input.textEdited.connect(self.threshold_changed)

        # Perform auto threshold calculation and disable user input box
        self.threshold_button.clicked.connect(self.auto_toggled)
        self.threshold_button.setToolTip('Automatically attempts to determine a\n'
                                         'threshold so just enough BA2 are\n'
                                         'extracted to get under the BA2 limit')
        self.threshold_button.installEventFilter(ToolTipFilter(self.threshold_button))

        self.threshold_layout_inner.addWidget(self.threshold_input)
        self.threshold_layout_inner.addWidget(self.threshold_button)
        self.threshold_layout_inner.addStretch(1)
        self.threshold_layout.addWidget(self.threshold_label)
        self.threshold_layout.addLayout(self.threshold_layout_inner)

        # Main setup layout
        self.setup_layout.addLayout(self.folder_layout, stretch=1)
        self.setup_layout.addSpacing(15)
        self.setup_layout.addLayout(self.threshold_layout)
        self.layout.addLayout(self.setup_layout)

        self.layout.addSpacing(10)

        # Start button
        self.start_button.setMaximumWidth(300)
        self.start_button.setEnabled(False)
        self.start_layout.addWidget(self.start_button)
        self.layout.addLayout(self.start_layout)

        self.layout.addWidget(self.preview_title, 0, Qt.AlignmentFlag.AlignLeft)

        self.setup_table()

        # Hide the progress bar in the beginning
        sp = self.preview_progress.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.preview_progress.setSizePolicy(sp)
        self.preview_progress.setHidden(True)
        self.layout.addWidget(self.preview_progress)

        # Leave some space for the title bar
        self.layout.setContentsMargins(60, 42, 60, 10)

    def setup_table(self):
        # Tableview configs
        self.preview_table.setBorderVisible(True)
        self.preview_table.setBorderRadius(8)

        self.preview_table.setWordWrap(False)
        vh = QHeaderView(Qt.Orientation.Vertical)
        vh.hide()
        self.preview_table.setVerticalHeader(vh)

        self.preview_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.preview_table.customContextMenuRequested.connect(self.table_custom_menu)

        sp = self.preview_table.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.preview_table.setSizePolicy(sp)

        self.layout.addWidget(self.preview_table)

        # Proxy model used by the table
        proxy_model = QSortFilterProxyModel()
        proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.preview_table.setModel(proxy_model)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        # Sorting
        self.preview_table.horizontalHeader().setSortIndicator(1, Qt.SortOrder.AscendingOrder)
        self.preview_table.setSortingEnabled(True)

        # Add the hint to the center of the table
        self.preview_hint_layout.addWidget(self.preview_hint, 0, Qt.AlignmentFlag.AlignCenter)

    def open_folder(self):
        self.folder_input.setText(QFileDialog.getExistingDirectory(self, 'Open your Fallout 4 mod directory',
                                                                   options=QFileDialog.Option.ShowDirsOnly |
                                                                           QFileDialog.Option.DontResolveSymlinks))

        selected_folder = self.folder_input.text()
        self.start_button.setDisabled(True)

        # Only process if the folder selected is not empty
        if selected_folder:
            qconfig.set(cfg.saved_dir, selected_folder)
            self.folder_button.setDisabled(True)
            # Animate the progress bar
            self.processor = BsaProcessor(selected_folder, './bin/bsab.exe', self)

            self.preview_hint.setHidden(True)
            # self.show_progress_persistent()

            self.processor.done_processing.connect(self.show_toast)
            self.processor.finished.connect(self.done_loading_ba2)
            self.processor.start()

    def auto_toggled(self):
        # Disable threshold input if "Auto" is enabled
        self.threshold_input.setDisabled(self.threshold_input.isEnabled())
        if self.threshold_button.isChecked():
            self.determine_threshold()
        else:
            self.threshold_input.clear()
            self.refresh_table(self.file_data)

    def refresh_table(self, data):
        model = PreviewTableModel(data)
        self.preview_table.model().setSourceModel(model)

        self.folder_button.setDisabled(False)
        self.table_ready = True
        self.check_start_ready()

    def done_loading_ba2(self):
        # Hide the progress bar again
        # self.preview_progress.stop()
        # self.preview_progress.setHidden(True)

        if self.threshold_button.isChecked():
            self.determine_threshold()
        else:
            self.refresh_table(self.file_data)
        self.adjust_column_size()
        # self.persistent_tooltip.deleteLater()

        del self.processor

    def adjust_column_size(self):
        total_width = self.preview_table.width()
        fs_col_width = 92
        num_col_width = 81

        self.preview_table.setColumnWidth(0, int((total_width - fs_col_width - num_col_width) * 0.45))
        self.preview_table.setColumnWidth(1, fs_col_width)
        self.preview_table.setColumnWidth(2, num_col_width)

    # Resize the columns of the table automatically on resize
    def resizeEvent(self, event):
        self.adjust_column_size()

    def show_toast(self, results):
        num_success = results[0]
        num_fail = results[1]
        auto_ignore = cfg.ignore_bad_files.value
        fail_message = f'Finished scanning ba2. {num_fail} files could not be opened'
        if auto_ignore:
            fail_message += ' and were automatically ignored.'
        else:
            fail_message += ' but will be processed anyways.'
        fail_message += f'\n{num_success} files were processed and ready to be extracted.'

        if num_fail > 0:
            warning_info = InfoBar(
                icon=InfoBarIcon.WARNING,
                title='Some files could not be loaded',
                content=fail_message,
                duration=10000,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )
            more_info_button = PushButton('Details', warning_info)
            more_info_button.clicked.connect(self.show_failed_files)
            warning_info.addWidget(more_info_button)
            warning_info.show()
        else:
            InfoBar.success(
                title='Great success',
                content=f'Finished scanning ba2. {num_success} files were processed and ready to be extracted.',
                duration=5000,
                position=InfoBarPosition.BOTTOM,
                parent=self
            )

    def threshold_changed(self):
        text = self.threshold_input.text()
        if not text:
            self.refresh_table(self.file_data)
            return
        threshold_byte = parse_size(text)
        filtered = self.get_filtered_files(threshold_byte)
        self.refresh_table(filtered)

    def table_custom_menu(self, pos):
        item_idx = self.preview_table.indexAt(pos)
        if not item_idx.isValid():
            return

        menu = RoundMenu()

        # Add actions one by one, Action inherits from QAction and accepts icons of type FluentIconBase
        menu.addAction(Action(Fi.REMOVE_FROM, 'Ignore', triggered=lambda: print(f'{item_idx.data()}')))
        menu.addAction(Action(Fi.LINK, 'Open', triggered=lambda: print("Cut successful")))

        menu.exec_(self.preview_table.viewport().mapToGlobal(pos))

    def show_failed_files(self):
        failed_files_text = '\n'.join(self.failed_files)
        box = MessageBox('The following files cannot be loaded', failed_files_text, parent=self)
        box.yesButton.setText('Ok')
        box.cancelButton.setText('Copy to clipboard')
        box.yesSignal.connect(box.deleteLater)
        box.cancelSignal.connect(
            lambda: QApplication.clipboard().setText(failed_files_text)
        )
        box.cancelSignal.connect(box.deleteLater)
        box.exec()

    def check_start_ready(self):
        table_nonempty = self.preview_table.model().rowCount() > 0
        self.start_button.setEnabled(self.table_ready and table_nonempty)

    def determine_threshold(self):
        if len(self.file_data) <= 235:
            if self.table_ready:
                self.auto_not_available()
            return

        threshold = self.file_data[-235].file_size
        self.threshold_input.setText(naturalsize(threshold))

        filtered = self.get_filtered_files(threshold)
        self.refresh_table(filtered)

    def get_filtered_files(self, threshold_byte):
        if threshold_byte != -1:
            # Persist the size info
            qconfig.set(cfg.saved_threshold, threshold_byte)
            return [entry for entry in self.file_data if entry.file_size <= threshold_byte]

    def auto_not_available(self):
        w = MessageBox('No unpacking necessary',
                       'It appears that you are not over the ba2 limit (yet). No ba2 unpacking is necessary. '
                       'To proceed please manually set a threshold.',
                       self)
        w.yesSignal.connect(self.threshold_button.click)
        w.yesButton.setText('Ok')
        w.cancelSignal.connect(QApplication.quit)
        w.cancelButton.setText('Exit Unpackrr')

        w.exec()
