"""
Professional PyQt5 GUI for Code Review Assistant
Main Window with tabs for different features
"""

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QTextEdit, QPushButton, QLabel, QFileDialog,
    QComboBox, QSplitter, QMessageBox, QProgressBar, QListWidget,
    QListWidgetItem, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCharFormat, QColor, QTextCursor

try:
    from groq import Groq
except ImportError:
    print("Groq not installed. Run: pip install groq")
    sys.exit(1)

from analyzers import AnalyzerFactory, Severity


class ReviewThread(QThread):
    """Background thread for code review to keep UI responsive"""
    finished = pyqtSignal(str, list, list)  # language, static_issues, ai_issues
    error = pyqtSignal(str)
    
    def __init__(self, analyzer_factory, code, filename=None, language=None):
        super().__init__()
        self.analyzer_factory = analyzer_factory
        self.code = code
        self.filename = filename
        self.language = language
    
    def run(self):
        try:
            lang, static, ai = self.analyzer_factory.analyze_code(
                self.code, 
                self.filename, 
                self.language
            )
            self.finished.emit(lang, static, ai)
        except Exception as e:
            self.error.emit(str(e))


class CodeReviewGUI(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('GROQ_API_KEY')
        self.current_file = None
        self.review_history = []
        
        if not self.api_key:
            QMessageBox.critical(
                self,
                "API Key Missing",
                "GROQ_API_KEY environment variable not set.\n\n"
                "Get your FREE key from https://console.groq.com/\n"
                "Then set it: setx GROQ_API_KEY \"your-key\""
            )
            sys.exit(1)
        
        # Initialize analyzer
        try:
            self.client = Groq(api_key=self.api_key)
            self.analyzer_factory = AnalyzerFactory(self.client)
        except Exception as e:
            QMessageBox.critical(self, "Initialization Error", str(e))
            sys.exit(1)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("AI Code Review Assistant - Dark Mode Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Add tabs
        tabs.addTab(self.create_review_tab(), "📝 Code Review")
        tabs.addTab(self.create_history_tab(), "📊 History")
        tabs.addTab(self.create_settings_tab(), "⚙️ Settings")
        tabs.addTab(self.create_about_tab(), "ℹ️ About")
        
        main_layout.addWidget(tabs)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Apply styling
        self.apply_styles()
    
    def create_review_tab(self):
        """Create the main code review tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Top control panel
        control_panel = QHBoxLayout()
        
        # File picker
        self.file_label = QLabel("No file selected")
        load_file_btn = QPushButton("📁 Load File")
        load_file_btn.clicked.connect(self.load_file)
        
        # Language selector
        lang_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            "Auto-detect",
            "Python",
            "JavaScript",
            "TypeScript",
            "Java",
            "C++",
            "Go",
            "Rust"
        ])
        
        # Review button
        self.review_btn = QPushButton("🔍 Review Code")
        self.review_btn.clicked.connect(self.start_review)
        self.review_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666666;
            }
        """)
        
        control_panel.addWidget(self.file_label)
        control_panel.addWidget(load_file_btn)
        control_panel.addStretch()
        control_panel.addWidget(lang_label)
        control_panel.addWidget(self.language_combo)
        control_panel.addWidget(self.review_btn)
        
        layout.addLayout(control_panel)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress_bar)
        
        # Splitter for code and results
        splitter = QSplitter(Qt.Horizontal)
        
        # Code input area
        code_group = QGroupBox("Code to Review")
        code_layout = QVBoxLayout()
        self.code_edit = QTextEdit()
        self.code_edit.setPlaceholderText("Paste your code here or load a file...")
        self.code_edit.setFont(QFont("Consolas", 10))
        code_layout.addWidget(self.code_edit)
        
        # Code actions
        code_actions = QHBoxLayout()
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.code_edit.clear)
        paste_btn = QPushButton("Paste")
        paste_btn.clicked.connect(lambda: self.code_edit.setText(QApplication.clipboard().text()))
        code_actions.addWidget(clear_btn)
        code_actions.addWidget(paste_btn)
        code_actions.addStretch()
        code_layout.addLayout(code_actions)
        
        code_group.setLayout(code_layout)
        splitter.addWidget(code_group)
        
        # Results area
        results_group = QGroupBox("Review Results")
        results_layout = QVBoxLayout()
        
        self.results_list = QListWidget()
        results_layout.addWidget(self.results_list)
        
        # Stats
        self.stats_label = QLabel("No issues yet")
        self.stats_label.setStyleSheet("font-size: 12px; color: #b0b0b0;")
        results_layout.addWidget(self.stats_label)
        
        results_group.setLayout(results_layout)
        splitter.addWidget(results_group)
        
        splitter.setSizes([600, 600])
        layout.addWidget(splitter)
        
        return widget
    
    def create_history_tab(self):
        """Create the history tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Review History")
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)
        
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)
        
        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.clicked.connect(self.clear_history)
        layout.addWidget(clear_history_btn)
        
        return widget
    
    def create_settings_tab(self):
        """Create the settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        label = QLabel("Settings")
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)
        
        # Options
        self.auto_save_check = QCheckBox("Auto-save reports")
        self.show_info_check = QCheckBox("Show INFO level issues")
        self.show_info_check.setChecked(True)
        self.static_analysis_check = QCheckBox("Enable fast static analysis")
        self.static_analysis_check.setChecked(True)
        
        layout.addWidget(self.auto_save_check)
        layout.addWidget(self.show_info_check)
        layout.addWidget(self.static_analysis_check)
        layout.addStretch()
        
        return widget
    
    def create_about_tab(self):
        """Create the about tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        about_text = QLabel(
            "<h2>AI Code Review Assistant</h2>"
            "<p><b>Version:</b> 2.0 Professional</p>"
            "<p><b>Powered by:</b> Groq (Llama 3.3 70B)</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Language-specific expert analysis</li>"
            "<li>Fast static code scanning</li>"
            "<li>AI-powered deep review</li>"
            "<li>Professional desktop interface</li>"
            "</ul>"
            "<p><b>Supported Languages:</b><br>"
            "Python, JavaScript, TypeScript, Java, C++, Go, Rust</p>"
            "<p><b>API:</b> 100% FREE via Groq</p>"
            "<p><b>GitHub:</b> github.com/Virtual0410/Code-review-ai</p>"
        )
        about_text.setWordWrap(True)
        about_text.setTextFormat(Qt.RichText)
        layout.addWidget(about_text)
        layout.addStretch()
        
        return widget
    
    def load_file(self):
        """Load a code file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select Code File",
            "",
            "Code Files (*.py *.js *.jsx *.ts *.tsx *.java *.cpp *.c *.go *.rs);;All Files (*.*)"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    code = f.read()
                
                self.code_edit.setText(code)
                self.current_file = filename
                self.file_label.setText(f"File: {os.path.basename(filename)}")
                self.statusBar().showMessage(f"Loaded: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error Loading File", str(e))
    
    def start_review(self):
        """Start code review in background thread"""
        code = self.code_edit.toPlainText().strip()
        
        if not code:
            QMessageBox.warning(self, "No Code", "Please enter or load code to review")
            return
        
        # Disable UI during review
        self.review_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.statusBar().showMessage("Analyzing code...")
        
        # Get language
        lang_text = self.language_combo.currentText()
        language = None if lang_text == "Auto-detect" else lang_text.lower()
        
        # Start review thread
        self.review_thread = ReviewThread(
            self.analyzer_factory,
            code,
            self.current_file,
            language
        )
        self.review_thread.finished.connect(self.display_results)
        self.review_thread.error.connect(self.review_error)
        self.review_thread.start()
    
    def display_results(self, language, static_issues, ai_issues):
        """Display review results"""
        # Re-enable UI
        self.review_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Combine issues
        all_issues = static_issues + ai_issues
        
        # Clear previous results
        self.results_list.clear()
        
        # Display issues
        if not all_issues:
            item = QListWidgetItem("✅ No issues found! Code looks good.")
            item.setForeground(QColor("#4caf50"))  # Bright green for dark mode
            self.results_list.addItem(item)
            self.stats_label.setText("No issues detected")
            self.statusBar().showMessage("Review complete - No issues found")
            return
        
        # Count by severity
        severity_counts = {}
        for issue in all_issues:
            sev = issue.severity.name
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        # Add issues to list
        for issue in sorted(all_issues, key=lambda x: list(Severity).index(x.severity)):
            # Skip INFO if disabled
            if issue.severity == Severity.INFO and not self.show_info_check.isChecked():
                continue
            
            line_info = f" (Line {issue.line_number})" if issue.line_number else ""
            item_text = f"{issue.severity.value} [{issue.category}] {issue.message}{line_info}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, issue)  # Store issue object
            
            # Color code by severity (dark mode compatible)
            if issue.severity == Severity.CRITICAL:
                item.setForeground(QColor("#ff4444"))  # Bright red
            elif issue.severity == Severity.HIGH:
                item.setForeground(QColor("#ff9800"))  # Bright orange
            elif issue.severity == Severity.MEDIUM:
                item.setForeground(QColor("#ffeb3b"))  # Bright yellow
            elif issue.severity == Severity.LOW:
                item.setForeground(QColor("#4caf50"))  # Bright green
            else:
                item.setForeground(QColor("#2196f3"))  # Bright blue
            
            self.results_list.addItem(item)
        
        # Update stats
        stats_parts = []
        for sev in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
            if sev in severity_counts:
                stats_parts.append(f"{sev}: {severity_counts[sev]}")
        
        stats_text = f"Language: {language.title()} | Found {len(all_issues)} issue(s) | " + " | ".join(stats_parts)
        self.stats_label.setText(stats_text)
        self.statusBar().showMessage(f"Review complete - {len(all_issues)} issues found")
        
        # Add to history
        self.review_history.append({
            'language': language,
            'issues': len(all_issues),
            'file': self.current_file or 'Pasted Code'
        })
        self.update_history()
    
    def show_issue_details(self, item):
        """Show detailed info for selected issue"""
        issue = item.data(Qt.UserRole)
        
        if not issue:
            return
        
        details = f"<h3>{issue.severity.value} - {issue.category}</h3>"
        details += f"<p><b>Issue:</b> {issue.message}</p>"
        
        if issue.line_number:
            details += f"<p><b>Line:</b> {issue.line_number}</p>"
        
        if issue.suggestion:
            details += f"<p><b>💡 Suggestion:</b> {issue.suggestion}</p>"
        
        self.details_text.setHtml(details)
    
    def review_error(self, error_msg):
        """Handle review error"""
        self.review_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.statusBar().showMessage("Review failed")
        QMessageBox.critical(self, "Review Error", f"Review failed:\n{error_msg}")
    
    def update_history(self):
        """Update history tab"""
        self.history_list.clear()
        for entry in self.review_history[-10:]:  # Last 10
            text = f"{entry['file']} ({entry['language']}) - {entry['issues']} issues"
            self.history_list.addItem(text)
    
    def clear_history(self):
        """Clear review history"""
        self.review_history.clear()
        self.history_list.clear()
        self.statusBar().showMessage("History cleared")
    
    def apply_styles(self):
        """Apply dark mode styling"""
        self.setStyleSheet("""
            /* Main Window */
            QMainWindow {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            
            /* Central Widget */
            QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            
            /* Tab Widget */
            QTabWidget::pane {
                border: 1px solid #3a3a3a;
                background-color: #252525;
            }
            
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #b0b0b0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            
            QTabBar::tab:selected {
                background-color: #252525;
                color: #ffffff;
                border-bottom: 2px solid #4CAF50;
            }
            
            QTabBar::tab:hover {
                background-color: #3a3a3a;
            }
            
            /* Group Box */
            QGroupBox {
                font-weight: bold;
                border: 2px solid #3a3a3a;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #252525;
                color: #e0e0e0;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #4CAF50;
            }
            
            /* Text Edit */
            QTextEdit {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: #e0e0e0;
                selection-background-color: #4CAF50;
                selection-color: #ffffff;
            }
            
            QTextEdit:focus {
                border: 1px solid #4CAF50;
            }
            
            /* List Widget */
            QListWidget {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                background-color: #2d2d2d;
                color: #e0e0e0;
                outline: none;
            }
            
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3a3a3a;
            }
            
            QListWidget::item:selected {
                background-color: #3a3a3a;
                color: #ffffff;
            }
            
            QListWidget::item:hover {
                background-color: #353535;
            }
            
            /* Buttons */
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                border: 1px solid #3a3a3a;
                background-color: #2d2d2d;
                color: #e0e0e0;
                font-weight: 500;
            }
            
            QPushButton:hover {
                background-color: #3a3a3a;
                border: 1px solid #4a4a4a;
            }
            
            QPushButton:pressed {
                background-color: #252525;
            }
            
            QPushButton:disabled {
                background-color: #1e1e1e;
                color: #666666;
                border: 1px solid #2a2a2a;
            }
            
            /* Labels */
            QLabel {
                color: #e0e0e0;
                background-color: transparent;
            }
            
            /* ComboBox */
            QComboBox {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                padding: 5px 10px;
                background-color: #2d2d2d;
                color: #e0e0e0;
                selection-background-color: #4CAF50;
            }
            
            QComboBox:hover {
                border: 1px solid #4a4a4a;
            }
            
            QComboBox::drop-down {
                border: none;
                padding-right: 10px;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #e0e0e0;
                margin-right: 5px;
            }
            
            QComboBox QAbstractItemView {
                border: 1px solid #3a3a3a;
                background-color: #2d2d2d;
                color: #e0e0e0;
                selection-background-color: #4CAF50;
                selection-color: #ffffff;
            }
            
            /* Progress Bar */
            QProgressBar {
                border: 1px solid #3a3a3a;
                border-radius: 3px;
                background-color: #2d2d2d;
                text-align: center;
                color: #e0e0e0;
            }
            
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
            
            /* Status Bar */
            QStatusBar {
                background-color: #252525;
                color: #b0b0b0;
                border-top: 1px solid #3a3a3a;
            }
            
            /* Checkboxes */
            QCheckBox {
                color: #e0e0e0;
                spacing: 8px;
            }
            
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3a3a3a;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            
            QCheckBox::indicator:checked {
                background-color: #4CAF50;
                border-color: #4CAF50;
            }
            
            QCheckBox::indicator:hover {
                border-color: #4a4a4a;
            }
            
            /* Splitter */
            QSplitter::handle {
                background-color: #3a3a3a;
            }
            
            QSplitter::handle:horizontal {
                width: 2px;
            }
            
            QSplitter::handle:vertical {
                height: 2px;
            }
            
            /* ScrollBar */
            QScrollBar:vertical {
                border: none;
                background-color: #2d2d2d;
                width: 12px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #4a4a4a;
                min-height: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #5a5a5a;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar:horizontal {
                border: none;
                background-color: #2d2d2d;
                height: 12px;
                margin: 0px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #4a4a4a;
                min-width: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #5a5a5a;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)


def main():
    """Run the application"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = CodeReviewGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
