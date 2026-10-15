
# -*- coding: utf-8 -*-
#!/usr/bin/env python

'''
╔════════════════════════════════════════════════════════════════════════════════
║  ☠️  FENIX EYE APK BUILDER SUITE v1.0  ☠️                                      
╠════════════════════════════════════════════════════════════════════════════════
║  Desarrollado por: 👉 Cristian M. Veliz Cano ✔       
║  Versión: V-01                                                                 
║  Propósito: Automatización de Builds Gradle para Android                       
╠════════════════════════════════════════════════════════════════════════════════
║  ✨ Compila APKs desde interfaz gráfica sin tocar consola ✨                   
╚════════════════════════════════════════════════════════════════════════════════

⚙️ Funcionalidades:
    📂 Selección de proyecto Android
    🧹 Clean (Limpiar build anterior)
    🔨 Build Debug (compilar APK de prueba)
    🔥 Build Release (compilar APK final)
    📱 Install ADB (instalar en dispositivo conectado)
    📊 Logs en tiempo real del proceso Gradle
    🔍 Detección automática de dispositivos

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⌨️ Atajos del Teclado:

📎 F1  → Información del software
📎 F11 → Está información
📎 Ctrl+K → Atajos de teclado
📎 Ctrl+O → Seleccionar proyecto
📎 Ctrl+L → Limpiar (Clean)
📎 Ctrl+D → Build Debug
📎 Ctrl+R → Build Release
📎 Ctrl+I → Install APK (ADB)
📎 ESC → Cerrar aplicación

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 Requisitos:
    ✔ Windows 10/11 (W7, Solo si Está Debidamente Configurada)
    ✔ Python 3.8+ --- (Solo si se ejecuta desde Codigo Fuente)
    ✔ PyQt5 instalado (Solo si se ejecuta desde Codigo Fuente)
    ✔ Android SDK/Gradle configurado
    ✔ Variables de entorno: JAVA_HOME, ANDROID_HOME

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
╔══════════════════════════════════════════════════════════════════╗
║  ☠️  FENIX EYE APK BUILDER v1.0  ☠️                              ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Compila proyectos Android que usen Gradle como sistema de build.║
║                                                                  ║
║  Compatible con:                                                 ║
║    • Proyectos Android Studio                                    ║
║    • Proyectos con build.gradle (Groovy)                         ║
║    • Proyectos con build.gradle.kts (Kotlin DSL)                 ║
║    • Cualquier estructura de carpetas válida para Gradle         ║
║                                                                  ║
║  REQUISITO OBLIGATORIO:                                          ║
║    El proyecto debe contener el archivo gradlew.bat              ║
║    en su carpeta raíz.                                           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

Alojado en MEGA:
https://mega.nz/file/O1sDmDgD#ZYDb883mQqcjSwVMcHO0eT1Ey5IKwrPS_jiDwiXlfJU

Proyectos Android:
https://mega.nz/file/ntFwETTb#sXVsCOKLbiOGbenponKHLui84tO_9m5aj0bboOxzr7k
'''

import re
import os
import sys
import subprocess
import webbrowser
import time
from datetime import datetime
from pathlib import Path as PathLib

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QListWidget, QLabel, 
    QFileDialog, QTextEdit, QVBoxLayout, QHBoxLayout, QLineEdit, QMessageBox, 
    QGroupBox, QGridLayout, QDialog, QShortcut, QProgressBar, QComboBox,
    QSplitter, QFrame)

from PyQt5.QtGui import QKeySequence, QIcon, QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer

##====================================================================================
# --- Clase para manejo de rutas ---
##====================================================================================
class Path():
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

##====================================================================================
# --- Worker Thread para procesos Gradle/ADB (No bloquea la UI) ---
##====================================================================================
class BuildWorker(QThread):
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    progress_signal = pyqtSignal(int)
    
    def __init__(self, command, cwd=None, env=None):
        super().__init__()
        self.command = command
        self.cwd = cwd
        self.env = env or os.environ.copy()
        self.process = None
        
    def run(self):
        try:
            self.log_signal.emit(f"☠️ Ejecutando: {' '.join(self.command)}")
            self.log_signal.emit(f"📁 Directorio: {self.cwd or os.getcwd()}")
            self.log_signal.emit("━" * 50)
            
            self.process = subprocess.Popen(
                self.command,
                cwd=self.cwd,
                env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                shell=True
            )
            
            full_output = []
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    line = line.rstrip()
                    full_output.append(line)
                    self.log_signal.emit(line)
                    # Detectar progreso
                    if "BUILD SUCCESSFUL" in line:
                        self.progress_signal.emit(100)
                    elif "BUILD FAILED" in line:
                        self.progress_signal.emit(0)
                        
            self.process.stdout.close()
            return_code = self.process.wait()
            
            if return_code == 0:
                self.finished_signal.emit(True, "\n".join(full_output))
            else:
                self.finished_signal.emit(False, "\n".join(full_output))
                
        except Exception as e:
            self.log_signal.emit(f"💀 ERROR: {str(e)}")
            self.finished_signal.emit(False, str(e))
            
    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.log_signal.emit("⚠️ Proceso detenido por usuario")

##====================================================================================
# --- CLASE PRINCIPAL ---
##====================================================================================
class FenixEyeAPKBuilder(QWidget):
    
    def __init__(self):
        super().__init__()
        
        self.project_path = None
        self.gradle_path = None
        self.apk_debug_path = None
        self.apk_release_path = None
        self.current_worker = None
        
        self.setWindowTitle("☠️ FENIX EYE APK BUILDER v1.0 ☠️")
        self.center_on_screen()
        
        # Icono
        self.setWindowIcon(QIcon(Path.resource_path("Ico\\1.ico")))
        
        self.init_ui()
        self.init_matrix_effect()
        self.add_log("☠️ FenixEye APK Builder iniciado")
        self.add_log("☠️ Listo para compilar")
        self.add_log("━" * 50)
        
    # ================================================
    # UI - Interfaz Hacker/Matrix
    # ================================================
    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #000000;
                color: #00ff41;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
            
            QPushButton {
                background-color: #0d1117;
                color: #00c3ff;
                border: 2px solid #00c3ff;
                border-radius: 4px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #00c3ff;
                color: #000000;
                border: 2px solid #00ff41;
            }
            
            QPushButton:pressed {
                background-color: #00ff41;
                color: #000000;
            }
            
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #555555;
                border: 2px solid #333333;
            }
            
            QLineEdit {
                background-color: #0d1117;
                color: #80ff00;
                border: 1px solid #00c3ff;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            
            QTextEdit {
                background-color: #0a0a0a;
                color: #00ff41;
                border: 1px solid #00c3ff;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            
            QGroupBox {
                border: 2px solid #00c3ff;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                color: #00c3ff;
                font-weight: bold;
                font-size: 12px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            
            QLabel {
                color: #00c3ff;
            }
            
            QListWidget {
                background-color: #0a0a0a;
                color: #80ff00;
                border: 1px solid #00c3ff;
                border-radius: 4px;
                font-size: 12px;
            }
            
            QProgressBar {
                border: 1px solid #00c3ff;
                border-radius: 4px;
                background-color: #0d1117;
                text-align: center;
                color: #00ff41;
            }
            
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00c3ff,
                    stop:0.5 #80ff00,
                    stop:1 #00ff41);
            }
            
            QComboBox {
                background-color: #0d1117;
                color: #00ff41;
                border: 1px solid #00c3ff;
                border-radius: 4px;
                padding: 5px;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #00c3ff;
            }
            
            QScrollBar:vertical {
                background-color: #0a0a0a;
                width: 12px;
                border: 1px solid #00c3ff;
            }
            
            QScrollBar::handle:vertical {
                background-color: #00c3ff;
                border-radius: 6px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #80ff00;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # ═══════════════════════════════════════════════════
        # TÍTULO MATRIX
        # ═══════════════════════════════════════════════════
        title_container = QFrame()
        title_container.setStyleSheet("""
            QFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #000000,
                    stop:0.5 #001100,
                    stop:1 #000000);
                border: 2px solid #00ff41;
                border-radius: 8px;
            }
        """)
        title_layout = QVBoxLayout(title_container)
        
        title = QLabel("☠️ FENIX EYE APK BUILDER ☠️")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #00ff41;
            font-size: 24px;
            font-weight: bold;
            font-family: 'Consolas', monospace;            
        """)
        ### text-shadow: 0 0 10px #00ff41;
        subtitle = QLabel("⚡ Automatización Gradle para Android ⚡")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            color: #00c3ff;
            font-size: 12px;
            font-family: 'Consolas', monospace;
        """)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        layout.addWidget(title_container)
        
        # ═══════════════════════════════════════════════════
        # SELECCIÓN DE PROYECTO
        # ═══════════════════════════════════════════════════
        project_group = QGroupBox("📁 PROYECTO ANDROID")
        project_layout = QHBoxLayout()
        
        self.project_input = QLineEdit()
        self.project_input.setPlaceholderText("Seleccione carpeta del proyecto...")
        self.project_input.setReadOnly(True)
        
        self.btn_select = QPushButton("🔍 EXAMINAR")
        self.btn_select.setFixedWidth(120)
        self.btn_select.clicked.connect(self.select_project)
        
        project_layout.addWidget(self.project_input)
        project_layout.addWidget(self.btn_select)
        project_group.setLayout(project_layout)
        layout.addWidget(project_group)
        
        # ═══════════════════════════════════════════════════
        # BOTONES DE ACCIÓN
        # ═══════════════════════════════════════════════════
        actions_group = QGroupBox("⚡ ACCIONES GRADLE")
        actions_layout = QGridLayout()
        
        self.btn_clean = QPushButton("🧹 CLEAN")
        self.btn_clean.setToolTip("Elimina carpeta build/ anterior")
        self.btn_clean.clicked.connect(self.gradle_clean)
        self.btn_clean.setEnabled(False)
        
        self.btn_debug = QPushButton("🔨 BUILD DEBUG")
        self.btn_debug.setToolTip("Compila APK de prueba (app-debug.apk)")
        self.btn_debug.clicked.connect(self.build_debug)
        self.btn_debug.setEnabled(False)
        
        self.btn_release = QPushButton("🔥 BUILD RELEASE")
        self.btn_release.setToolTip("Compila APK final (app-release.apk)")
        self.btn_release.clicked.connect(self.build_release)
        self.btn_release.setEnabled(False)
        
        self.btn_devices = QPushButton("📲 DISPOSITIVOS")
        self.btn_devices.setToolTip("Lista dispositivos Android conectados")
        self.btn_devices.clicked.connect(self.check_devices)
        
        self.btn_open_apk = QPushButton("📂 Open Directory \"APK\"")
        self.btn_open_apk.setToolTip("Abre el Directorio donde se haya Generado el APK")
        self.btn_open_apk.clicked.connect(self.open_apk)
        self.btn_open_apk.setEnabled(False)
        
        self.btn_install = QPushButton("📱 INSTALL ADB")
        self.btn_install.setToolTip("Instala APK en dispositivo conectado")
        self.btn_install.clicked.connect(self.install_apk)
        self.btn_install.setEnabled(False)
        
        actions_layout.addWidget(self.btn_clean, 0, 0)
        actions_layout.addWidget(self.btn_debug, 0, 1)
        actions_layout.addWidget(self.btn_release, 0, 2)
        actions_layout.addWidget(self.btn_devices, 1, 0)
        actions_layout.addWidget(self.btn_open_apk, 1, 1)
        actions_layout.addWidget(self.btn_install, 1, 2)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # ═══════════════════════════════════════════════════
        # BARRA DE PROGRESO
        # ═══════════════════════════════════════════════════
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        self.progress.setFormat("☠️ %p% ☠️")
        layout.addWidget(self.progress)
        
        # ═══════════════════════════════════════════════════
        # LOGS EN TIEMPO REAL (ESTILO TERMINAL)
        # ═══════════════════════════════════════════════════
        log_group = QGroupBox("📟 CONSOLA GRADLE")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group, stretch=1)
        
        # ═══════════════════════════════════════════════════
        # ESTADÍSTICAS
        # ═══════════════════════════════════════════════════
        stats_group = QGroupBox("📊 ESTADÍSTICAS")
        stats_layout = QGridLayout()
        
        self.lbl_project = QLabel("Proyecto: Ninguno")
        self.lbl_gradle = QLabel("Gradle: No detectado")
        self.lbl_apk_size = QLabel("Tamaño APK: --")
        self.lbl_build_time = QLabel("Tiempo build: --")
        self.lbl_status = QLabel("Estado: ☠️ INACTIVO")
        self.lbl_status.setStyleSheet("color: #ff4444; font-weight: bold;")
        
        stats_layout.addWidget(self.lbl_project, 0, 0)
        stats_layout.addWidget(self.lbl_gradle, 0, 1)
        stats_layout.addWidget(self.lbl_apk_size, 1, 0)
        stats_layout.addWidget(self.lbl_build_time, 1, 1)
        stats_layout.addWidget(self.lbl_status, 2, 0, 1, 2)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
##=========================================================================================        
        # ═══════════════════════════════════════════════════
        # ATAJOS DE TECLADO
        # ═══════════════════════════════════════════════════  
        # F1 - DEFINICION (Conpilación)
        QShortcut(QKeySequence('F1'), self).activated.connect(self.show_key_DEFINICION)
        # F11 - Info (APP)
        QShortcut(QKeySequence('F11'), self).activated.connect(self.show_app_info)
        # Ctrl+K - Atajos
        QShortcut(QKeySequence('Ctrl+K'), self).activated.connect(self.show_key_info)
        # Ctrl+O - Seleccionar proyecto
        QShortcut(QKeySequence('Ctrl+O'), self).activated.connect(self.select_project)
        # Ctrl+L - Clean
        QShortcut(QKeySequence('Ctrl+L'), self).activated.connect(self.gradle_clean)
        # Ctrl+D - Build Debug
        QShortcut(QKeySequence('Ctrl+D'), self).activated.connect(self.build_debug)
        # Ctrl+R - Build Release
        QShortcut(QKeySequence('Ctrl+R'), self).activated.connect(self.build_release)
        # Ctrl+I - Install
        QShortcut(QKeySequence('Ctrl+I'), self).activated.connect(self.install_apk)
        # ESC - Salir
        QShortcut(QKeySequence('Escape'), self).activated.connect(self.close)
        
        # Mostrar info al inicio
        QTimer.singleShot(500, self.show_app_info)

##=========================================================================================
    # ================================================
    # EFECTO MATRIX (Opcional - parpadeo sutil)
    # ================================================
    def init_matrix_effect(self):
        self.matrix_timer = QTimer(self)
        self.matrix_timer.timeout.connect(self.pulse_effect)
        self.matrix_timer.start(2000)
        self.pulse_state = True
        
    def pulse_effect(self):
        # Efecto sutil en el título
        pass  # Implementar si se desea animación
        
##=========================================================================================        
    # ================================================
    # MÉTODOS DE PROYECTO
    # ================================================
    def select_project(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            "☠️ Seleccionar Proyecto Android",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not folder:
            return
            
        self.project_path = folder
        self.project_input.setText(folder)
        self.lbl_project.setText(f"Proyecto: {os.path.basename(folder)}")
        
        # Verificar estructura Gradle
        gradlew = os.path.join(folder, "gradlew.bat")
        build_gradle = os.path.join(folder, "build.gradle.kts")
        
        if os.path.exists(gradlew):
            self.gradle_path = gradlew
            self.lbl_gradle.setText("Gradle: ✓ Detectado")
            self.lbl_gradle.setStyleSheet("color: #00ff41;")
            self.enable_buttons(True)
            self.add_log(f"✓ Proyecto cargado: {folder}")
            self.add_log(f"✓ Gradle wrapper detectado")
        else:
            self.lbl_gradle.setText("Gradle: ✗ No encontrado")
            self.lbl_gradle.setStyleSheet("color: #ff4444;")
            self.enable_buttons(False)
            QMessageBox.warning(
                self,
                "⚠️ Proyecto Inválido",
                "No se encontró gradlew.bat\n\n"
                "Seleccione la carpeta raíz de un proyecto Android válido."
            )
            
    def enable_buttons(self, enabled):
        self.btn_clean.setEnabled(enabled)
        self.btn_debug.setEnabled(enabled)
        self.btn_release.setEnabled(enabled)
        self.btn_install.setEnabled(enabled and self.apk_debug_path is not None)
        
    # ================================================
    # PROCESOS GRADLE
    # ================================================
    def gradle_clean(self):
        if not self.project_path:
            return
            
        self.add_log("━" * 50)
        self.add_log("🧹 INICIANDO CLEAN...")
        self.lbl_status.setText("Estado: 🧹 LIMPIANDO...")
        self.lbl_status.setStyleSheet("color: #00c3ff; font-weight: bold;")
        self.progress.setValue(10)
        
        cmd = [self.gradle_path, "clean"]
        self.run_gradle_command(cmd, "CLEAN")
        
    def build_debug(self):
        if not self.project_path:
            return
            
        self.add_log("━" * 50)
        self.add_log("🔨 INICIANDO BUILD DEBUG...")
        self.lbl_status.setText("Estado: 🔨 COMPILANDO DEBUG...")
        self.lbl_status.setStyleSheet("color: #80ff00; font-weight: bold;")
        self.progress.setValue(20)
        self.build_start_time = time.time()
        
        cmd = [self.gradle_path, "assembleDebug"]
        self.run_gradle_command(cmd, "DEBUG")
        
    def build_release(self):
        if not self.project_path:
            return
            
        self.add_log("━" * 50)
        self.add_log("🔥 INICIANDO BUILD RELEASE...")
        self.lbl_status.setText("Estado: 🔥 COMPILANDO RELEASE...")
        self.lbl_status.setStyleSheet("color: #ffaa00; font-weight: bold;")
        self.progress.setValue(20)
        self.build_start_time = time.time()
        
        cmd = [self.gradle_path, "assembleRelease"]
        self.run_gradle_command(cmd, "RELEASE")
        
    def run_gradle_command(self, cmd, build_type):
        # Detener worker anterior si existe
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
            self.current_worker.wait()
            
        # Configurar JAVA_HOME si existe
        env = os.environ.copy()
        
        self.current_worker = BuildWorker(cmd, self.project_path, env)
        self.current_worker.log_signal.connect(self.add_log)
        self.current_worker.progress_signal.connect(self.update_progress)
        self.current_worker.finished_signal.connect(lambda success, output: self.build_finished(success, output, build_type))
        self.current_worker.start()
        
    def update_progress(self, value):
        self.progress.setValue(value)
        
    def build_finished(self, success, output, build_type):
        elapsed = time.time() - getattr(self, 'build_start_time', time.time())
        
        if success:
            self.progress.setValue(100)
            self.lbl_status.setText(f"Estado: ✓ {build_type} COMPLETADO")
            self.lbl_status.setStyleSheet("color: #00ff41; font-weight: bold;")
            self.lbl_build_time.setText(f"Tiempo build: {elapsed:.1f}s")
            self.add_log("✓ BUILD SUCCESSFUL")
            
            # Buscar APK generado
            if build_type == "DEBUG":
                apk_path = os.path.join(
                    self.project_path,
                    "app", "build", "outputs", "apk", "debug", "app-debug.apk"
                )
                if os.path.exists(apk_path):
                    self.apk_debug_path = apk_path
                    size = os.path.getsize(apk_path) / (1024 * 1024)
                    self.lbl_apk_size.setText(f"Tamaño APK: {size:.2f} MB")
                    self.add_log(f"✓ APK generado: {apk_path}")
                    self.btn_install.setEnabled(True)
                    self.btn_open_apk.setEnabled(True)
                    
            elif build_type == "RELEASE":
                apk_path = os.path.join(
                    self.project_path,
                    "app", "build", "outputs", "apk", "release", "app-release.apk"
                )
                if os.path.exists(apk_path):
                    self.apk_release_path = apk_path
                    size = os.path.getsize(apk_path) / (1024 * 1024)
                    self.lbl_apk_size.setText(f"Tamaño APK: {size:.2f} MB")
                    self.add_log(f"✓ APK generado: {apk_path}")
                    self.btn_install.setEnabled(True)
                    self.btn_open_apk.setEnabled(True)
                    
        else:
            self.progress.setValue(0)
            self.lbl_status.setText("Estado: ✗ BUILD FAILED")
            self.lbl_status.setStyleSheet("color: #ff4444; font-weight: bold;")
            self.add_log("✗ BUILD FAILED")
            
            # Mostrar error resumido
            if "error" in output.lower():
                QMessageBox.critical(
                    self,
                    "💀 ERROR DE COMPILACIÓN",
                    "El build falló. Revise la consola para detalles."
                )

    # ================================================
    # OPEN APK  (Abre el Directorio donde Se Encuentra el app-release.apk)
    # ================================================
    def open_apk(self):
        """Abre la carpeta de capturas"""
        apk_debug = os.path.join(
            self.project_path,
                "app", "build", "outputs", "apk", "debug", "app-debug.apk"
            )

        apk_release = os.path.join(
            self.project_path,
                "app", "build", "outputs", "apk", "release", "app-release.apk"
            )

        if os.path.exists(apk_debug):

            apk_path = os.path.join(
                self.project_path,
                    "app", "build", "outputs", "apk", "debug", "app-debug.apk"
                    )

            path = os.path.abspath(apk_path)
            if sys.platform == 'win32':
                ###os.startfile(path)
                fpath, fname = os.path.split(path)
                webbrowser.open(f'{fpath}/')

            ##else:
            ##    import subprocess
            ##    subprocess.call(['xdg-open', path])

        if os.path.exists(apk_release):
            apk_path = os.path.join(
                self.project_path,
                    "app", "build", "outputs", "apk", "release"
                )

            if os.path.exists(apk_path):

                path = os.path.abspath(apk_path)
                if sys.platform == 'win32':
                    ###os.startfile(path)
                    fpath, fname = os.path.split(path)
                    webbrowser.open(f'{fpath}/')

                ##else:
                ##    import subprocess
                ##    subprocess.call(['xdg-open', path])
                
    # ================================================
    # ADB - INSTALACIÓN
    # ================================================
    def check_devices(self):
        self.add_log("━" * 50)
        self.add_log("📲 Buscando dispositivos...")
        
        cmd = ["adb", "devices"]
        self.run_adb_command(cmd, "DEVICES")
        
    def install_apk(self):
        if not self.apk_debug_path or not os.path.exists(self.apk_debug_path):
            QMessageBox.warning(
                self,
                "⚠️ APK No Encontrado",
                "Primero compile el APK Debug (Build Debug)"
            )
            return
            
        self.add_log("━" * 50)
        self.add_log(f"📱 Instalando: {os.path.basename(self.apk_debug_path)}")
        self.lbl_status.setText("Estado: 📱 INSTALANDO...")
        self.lbl_status.setStyleSheet("color: #00c3ff; font-weight: bold;")
        
        # -r = reinstalar, -d = permitir downgrade
        cmd = ["adb", "install", "-r", "-d", self.apk_debug_path]
        self.run_adb_command(cmd, "INSTALL")
        
    def run_adb_command(self, cmd, operation):
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
            self.current_worker.wait()
            
        self.current_worker = BuildWorker(cmd)
        self.current_worker.log_signal.connect(self.add_log)
        self.current_worker.finished_signal.connect(
            lambda success, output: self.adb_finished(success, output, operation)
        )
        self.current_worker.start()
        
    def adb_finished(self, success, output, operation):
        if operation == "INSTALL":
            if success and "Success" in output:
                self.lbl_status.setText("Estado: ✓ INSTALADO")
                self.lbl_status.setStyleSheet("color: #00ff41; font-weight: bold;")
                self.add_log("✓ Instalación exitosa")
                QMessageBox.information(
                    self,
                    "✓ ÉXITO",
                    "APK instalado correctamente en el dispositivo"
                )
            else:
                self.lbl_status.setText("Estado: ✗ ERROR INSTALACIÓN")
                self.lbl_status.setStyleSheet("color: #ff4444; font-weight: bold;")
                self.add_log("✗ Error de instalación")
                
        elif operation == "DEVICES":
            if "device" in output:
                self.add_log("✓ Dispositivo(s) detectado(s)")
            else:
                self.add_log("⚠️ No hay dispositivos conectados")
        
##=========================================================================================                
    # ================================================
    # UTILIDADES
    # ================================================
    def add_log(self, text):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{now}] {text}")
        # Auto-scroll al final
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def center_on_screen(self):
        screen = QApplication.primaryScreen().availableGeometry()
        w, h = 1200, 750
        x = (screen.width() - w) // 2
        y = (screen.height() - h) // 2+10
        self.setGeometry(x, y, w, h)
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            
    def closeEvent(self, event):
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
            self.current_worker.wait(2000)
        event.accept()
        
##=========================================================================================        
    # ================================================
    # DIÁLOGOS DE INFORMACIÓN
    # ================================================
    def show_app_info(self):
        dialog = AppInfoDialog(self)
        dialog.exec_()
        
    def show_key_info(self):
        dialog = KeyInfoDialog(self)
        dialog.exec_()
        
    def show_key_DEFINICION(self):
        dialog = KeyDEFINICION(self)
        dialog.exec_()

##====================================================================================
# DIÁLOGO DE INFORMACIÓN
##====================================================================================
class AppInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("☠️ INFORMACIÓN DEL SISTEMA")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(600, 500)
        self.setModal(True)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
            }
            QTextEdit {
                background-color: #0a0a0a;
                color: #00ff41;
                border: 2px solid #00c3ff;
                font-family: 'Consolas', monospace;
                font-size: 16px;
            }
            QPushButton {
                background-color: #0d1117;
                color: #00c3ff;
                border: 2px solid #00c3ff;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00c3ff;
                color: #000000;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("☠️ FENIX EYE APK BUILDER ☠️")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00ff41; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        info = QTextEdit()
        info.setReadOnly(True)
        info.setText("""
╔════════════════════════════════════════════════════════════
║  ☠️  FENIX EYE APK BUILDER SUITE v1.0  ☠️                  
╠════════════════════════════════════════════════════════════
║  Desarrollado Por: Cristian M. Veliz Cano                  
║  Versión: V-01                                             
║  Propósito: Automatización de Builds Gradle                
╠════════════════════════════════════════════════════════════
║ 
║ ⚙️ FUNCIONALIDADES:
║ 
║ 📂 Selección de proyecto Android
║     • Detecta automáticamente gradlew.bat
║     • Valida estructura del proyecto
║ 
║ 🧹 Clean (Ctrl+L)
║     • Elimina build/ anterior
║     • Limpia caché de Gradle
║ 
║ 🔨 Build Debug (Ctrl+D)
║     • Compila app-debug.apk
║     • Optimizado para pruebas
║ 
║ 🔥 Build Release (Ctrl+R)
║     • Compila app-release.apk
║     • Listo para distribución
║ 
║ 📱 Install ADB (Ctrl+I)
║     • Instala APK en dispositivo
║     • Requiere USB Debugging activado
║ 
║ 📊 Logs en tiempo real
║     • Salida de Gradle completa
║     • Detección de errores
║ 
╠════════════════════════════════════════════════════════════
║ 
║ ⚡ REQUISITOS DEL SISTEMA:
║ 
║ ✔ Windows 10/11 (W7, Solo si Está Debidamente Configurada)
║ ✔ Python 3.8+ --- (Solo si se ejecuta desde Codigo Fuente)
║ ✔ PyQt5 instalado (Solo si se ejecuta desde Codigo Fuente)
║ ✔ Android SDK configurado
║ ✔ JAVA_HOME definido
║ ✔ Dispositivo con USB Debugging (para install)
║ 
╠════════════════════════════════════════════════════════════
║ 
║ ⌨️ ATAJOS DE TECLADO:
║ 
║ F1          → DEFINICION: ¿GRADLE/ KOTLIN DSL?
║ F11         → Está información
║ Ctrl+K      → Atajos de teclado
║ Ctrl+O      → Seleccionar proyecto
║ Ctrl+L      → Clean
║ Ctrl+D      → Build Debug
║ Ctrl+R      → Build Release
║ Ctrl+I      → Install APK
║ ESC         → Salir
║ 
╠════════════════════════════════════════════════════════════
║ 
║ 📁 FLUJO DE TRABAJO RECOMENDADO:
║ 
║ 1. Seleccionar carpeta del proyecto (Ctrl+O)
║ 2. Verificar que Gradle esté detectado
║ 3. Opcional: Clean (Ctrl+L)
║ 4. Build Debug (Ctrl+D)
║ 5. Conectar dispositivo USB
║ 6. Install APK (Ctrl+I)
║ 
╠════════════════════════════════════════════════════════════
║ 
║ ☠️ LICENCIA: MIT License
║ ☠️ CÓDIGO LIBRE - USO EDUCATIVO
║ 
╚════════════════════════════════════════════════════════════
        """)
        layout.addWidget(info)
        
        btn = QPushButton("☠️ CERRAR ☠️")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)

##====================================================================================
# DIÁLOGO DE ATAJOS
##====================================================================================
class KeyInfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⌨️ ATAJOS DE TECLADO")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
            }
            QTextEdit {
                background-color: #0a0a0a;
                color: #00c3ff;
                border: 2px solid #00ff41;
                font-family: 'Consolas', monospace;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0d1117;
                color: #00ff41;
                border: 2px solid #00ff41;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ff41;
                color: #000000;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("⌨️ COMANDOS RÁPIDOS ⌨️")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00c3ff; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        keys = QTextEdit()
        keys.setReadOnly(True)
        keys.setText("""
╔══════════════════════════════════════════════════════════════╗
║  ATAJO      ║  ACCIÓN                                        ║
╠══════════════════════════════════════════════════════════════╣
║  F1         ║  DEFINICION: ¿GRADLE/ KOTLIN DSL?              ║
║  F11        ║  Información del sistema                       ║
║  Ctrl+K     ║  Mostrar atajos                                ║
║  Ctrl+O     ║  Seleccionar proyecto                          ║
║  Ctrl+L     ║  Gradle Clean                                  ║
║  Ctrl+D     ║  Build Debug APK                               ║
║  Ctrl+R     ║  Build Release APK                             ║
║  Ctrl+I     ║  Install APK (ADB)                             ║
║  ESC        ║  Cerrar aplicación                             ║
║══════════════════════════════════════════════════════════════╝
║                                                              ║ 
║ 📌 TIPS:                                                     ║
║                                                              ║
║ • Seleccione la carpeta raíz del proyecto Android            ║
║   (donde está el archivo gradlew.bat)                        ║
║                                                              ║
║ • Build Debug es más rápido, ideal para pruebas              ║
║                                                              ║
║ • Build Release genera APK optimizado                        ║
║                                                              ║
║ • Install requiere:                                          ║
║   - Dispositivo conectado por USB                            ║
║   - USB Debugging activado en el móvil                       ║
║   - Drivers ADB instalados                                   ║
║                                                              ║
║ • Los logs aparecen en tiempo real en la consola             ║
║                                                              ║
║ • Si el build falla, revise los mensajes de error            ║
║   en la consola para diagnosticar                            ║
║                                                              ║
║══════════════════════════════════════════════════════════════╝
║                                                              ║
║ 📍 O Bien:                                                   ║
║                                                              ║
║ • Puede Cimplemente, abrir, el Directorio directamente       ║
║   donde se encuentra el Archivo: → "app-debug.apk"           ║
║                                                              ║
║                             "O"                              ║
║                                                              ║
║ • Puede Cimplemente, abrir, el Directorio directamente       ║
║   donde se encuentra el Archivo: → "app-debug.apk"           ║
║                                                              ║
║         ═════════════════════════════════════════            ║
║                                                              ║
║ • Dependiendo, que Archivo, se haya Generado                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """)
        layout.addWidget(keys)
        
        btn = QPushButton("⌨️ CERRAR ⌨️")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)

##====================================================================================
# DIÁLOGO DE DEFINICION F1
##====================================================================================
class KeyDEFINICION(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⌨️ DEFINICION F1")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #000000;
            }
            QTextEdit {
                background-color: #0a0a0a;
                color: #00c3ff;
                border: 2px solid #00ff41;
                font-family: 'Consolas', monospace;
                font-size: 16px;
            }
            QPushButton {
                background-color: #0d1117;
                color: #00ff41;
                border: 2px solid #00ff41;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ff41;
                color: #000000;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("⌨️ DEFINICION ⌨️")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #00c3ff; font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        keys = QTextEdit()
        keys.setReadOnly(True)
        keys.setText("""
╔═════════════════════════════════════════════════
║  ¿QUÉ ES ANDROID SDK / GRADLE / KOTLIN DSL?                
╠═════════════════════════════════════════════════
║                                                                  
║ Android SDK (Software Development Kit):                          
║ Es el conjunto de herramientas que Google 
║ proporciona para crear aplicaciones Android. 
║ Incluye compiladores, emuladores, librerías 
║ y utilidades necesarias.                               
║                                                                  
║ Gradle:                                                          
║ Es el sistema de automatización de builds 
║ que Android usa desde 2013. Se encarga de:                                       
║   • Compilar el código Kotlin/Java                               
║   • Procesar recursos (XML, imágenes)                            
║   • Empaquetar todo en el archivo APK                            
║   • Gestionar dependencias (librerías)                           
║                                                                  
║ Kotlin DSL:                                                      
║ Es Gradle escrito con sintaxis de Kotlin en
║ lugar de Groovy.     
║ Desde 2018 Android lo recomienda como opción 
║ por defecto.        
║                                                                  
║ Diferencia:                                                      
║   • build.gradle    = Sintaxis Groovy 
║     (más antigua)              
║   • build.gradle.kts = Sintaxis Kotlin 
║     (más moderna, recomendada)
║                                                                  
║ Ambos funcionan igual. Solo cambia el lenguaje 
║ de configuración. 
║                                                                  
╠═════════════════════════════════════════════════
║                                                                  
║ Este software SOLO funciona si su proyecto 
║ tiene:                
║   ✓ Archivo gradlew.bat 
║     (o gradlew en Linux/Mac)                 
║   ✓ Archivo build.gradle o 
║     build.gradle.kts                      
║   ✓ Carpeta app/src/main/                                        
║                                                                  
║ Si su proyecto usa Maven, Bazel u otro 
║ sistema, este software "NO podrá compilarlo".
╚═════════════════════════════════════════════════

☠️ FENIX EYE APK BUILDER v1.0:

╔═════════════════════════════════════════════════
║  ☠️  FENIX EYE APK BUILDER v1.0  ☠️                              
╠═════════════════════════════════════════════════
║                                                                  
║  Compila proyectos Android que usen Gradle como 
║  sistema de build.
║                                                                  
║  Compatible con:                                                 
║    • Proyectos Android Studio                                    
║    • Proyectos con build.gradle (Groovy)                         
║    • Proyectos con build.gradle.kts (Kotlin DSL)                 
║    • Cualquier estructura de carpetas válida 
║      para Gradle         
║                                                                  
║  REQUISITO OBLIGATORIO:                                          
║    El proyecto debe contener el archivo 
║    gradlew.bat, en su carpeta raíz.                                           
║                                                                  
╚═════════════════════════════════════════════════
        """)
        layout.addWidget(keys)
        
        btn = QPushButton("⌨️ CERRAR ⌨️")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)

##====================================================================================
# RUN
##====================================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Fuente monoespaciada global
    font = QFont("Consolas", 10)
    font.setStyleHint(QFont.Monospace)
    app.setFont(font)
    
    window = FenixEyeAPKBuilder()
    window.show()
    sys.exit(app.exec_())
##====================================================================================
##====================================================================================