#Creado por Emmanuel Calvo ------>2024

import sys
import os
import json
import subprocess
from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import Image

BOOKS_FILE = "books.json"

class ScrollButton(QtWidgets.QPushButton):
    def __init__(self, direction, parent=None):
        super().__init__(parent)
        self.setFixedSize(15, 30)
        self.direction = direction
        self.setText('←' if direction == 'left' else '→')
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(52, 152, 219, 0.7);
                color: white;
                border-radius: 5px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(41, 128, 185, 0.9);
            }
            QPushButton:disabled {
                background-color: rgba(189, 195, 199, 0.5);
            }
        """)

class BookCarousel(QtWidgets.QWidget):
    def __init__(self, title):
        super().__init__()
        self.title = title
        self.setup_ui()
    def open_pdf(self, pdf_path):
        try:
            if sys.platform.startswith('win'):
                os.startfile(pdf_path)
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', pdf_path])
            else:  # linux
                subprocess.run(['xdg-open', pdf_path])
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Error al abrir PDF",
                f"No se pudo abrir el archivo PDF:\n{str(e)}",
                QtWidgets.QMessageBox.Ok
            )
            
    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        
        # Título de la sección
        title_label = QtWidgets.QLabel(self.title)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px;")
        layout.addWidget(title_label)
        
        # Contenedor horizontal para los botones y el área de scroll
        carousel_container = QtWidgets.QHBoxLayout()
        carousel_container.setSpacing(0)
        layout.addLayout(carousel_container)
        
        # Botón izquierdo
        self.left_button = ScrollButton('left')
        self.left_button.clicked.connect(self.scroll_left)
        self.left_button.setEnabled(False)
        carousel_container.addWidget(self.left_button)
        
        # Scroll Area
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedHeight(300)
        self.scroll_area.horizontalScrollBar().valueChanged.connect(self.update_buttons)
        carousel_container.addWidget(self.scroll_area)
        
        # Botón derecho
        self.right_button = ScrollButton('right')
        self.right_button.clicked.connect(self.scroll_right)
        carousel_container.addWidget(self.right_button)
        
        # Contenedor para los libros
        self.book_container = QtWidgets.QWidget()
        self.book_layout = QtWidgets.QHBoxLayout()
        self.book_layout.setSpacing(20)
        self.book_layout.setContentsMargins(20, 10, 20, 10)
        self.book_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.book_container.setLayout(self.book_layout)
        
        self.scroll_area.setWidget(self.book_container)

    def scroll_left(self):
        new_value = max(0, self.scroll_area.horizontalScrollBar().value() - 200)
        self.scroll_area.horizontalScrollBar().setValue(new_value)
        
    def scroll_right(self):
        new_value = min(
            self.scroll_area.horizontalScrollBar().maximum(),
            self.scroll_area.horizontalScrollBar().value() + 200
        )
        self.scroll_area.horizontalScrollBar().setValue(new_value)
    
    def update_buttons(self):
        scrollbar = self.scroll_area.horizontalScrollBar()
        self.left_button.setEnabled(scrollbar.value() > 0)
        self.right_button.setEnabled(scrollbar.value() < scrollbar.maximum())

    def add_book(self, book, parent):
        # Crear widget para el libro
        book_widget = QtWidgets.QWidget()
        book_widget.setFixedSize(200, 280)  # Cambiado de 180 a 200 para dar más espacio
        book_layout = QtWidgets.QVBoxLayout()
        book_layout.setSpacing(5)
        
        # Portada del libro
        cover_label = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap(book["img_path"])
        scaled_pixmap = pixmap.scaled(160, 180, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        cover_label.setPixmap(scaled_pixmap)
        cover_label.setAlignment(QtCore.Qt.AlignCenter)
        
        # Título del libro
        title_label = QtWidgets.QLabel(book["title"])
        title_label.setWordWrap(True)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 12px; 
            color: #34495e;
            margin-bottom: 5px;
            max-height: 30px;
        """)
        title_label.setMaximumHeight(40)
        
        # Contenedor para botones
        buttons_layout = QtWidgets.QHBoxLayout()
        buttons_layout.setSpacing(8)  # Espacio entre botones
        
        # Botón de estado
        status_button = QtWidgets.QPushButton("📋 ▼")
        status_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border-radius: 3px;
                padding: 5px;
                font-size: 11px;
                max-width: 50px;
                min-width: 40px;
                height: 25px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        status_button.setFixedWidth(45)
        
        status_menu = QtWidgets.QMenu()
        for status in ["Leído", "Pendiente", "Por Leer"]:
            action = QtWidgets.QAction(status, status_button)
            action.triggered.connect(lambda checked, s=status, b=book: parent.change_book_status(b, s))
            status_menu.addAction(action)
        
        status_button.setMenu(status_menu)
        
        # Botón de abrir PDF
        open_button = QtWidgets.QPushButton("📖")
        open_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 3px;
                padding: 5px;
                font-size: 11px;
                max-width: 30px;
                height: 25px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        open_button.setToolTip("Abrir PDF")
        open_button.clicked.connect(lambda: self.open_pdf(book["pdf_path"]))
        open_button.setFixedWidth(30)
        
        # Botón de eliminar
        delete_button = QtWidgets.QPushButton("🗑")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 3px;
                padding: 5px;
                font-size: 11px;
                max-width: 30px;
                height: 25px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_button.clicked.connect(lambda: parent.delete_book(book))
        delete_button.setFixedWidth(30)
        
        # Añadir todos los botones al layout
        buttons_layout.addWidget(status_button)
        buttons_layout.addWidget(open_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Ajustar los márgenes y espaciado del layout
        book_layout.setSpacing(5)
        book_layout.setContentsMargins(5, 5, 5, 5)
        
        book_layout.addWidget(cover_label)
        book_layout.addWidget(title_label)
        book_layout.addLayout(buttons_layout)
        book_widget.setLayout(book_layout)
        
        # Estilo para el widget del libro
        book_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #bdc3c7;
            }
            QWidget:hover {
                border: 2px solid #3498db;
            }
        """)
        
        self.book_layout.addWidget(book_widget)
        QtCore.QTimer.singleShot(100, self.update_buttons)
    
    def open_pdf(self, pdf_path):
        try:
            if sys.platform.startswith('win'):
                os.startfile(pdf_path)
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', pdf_path])
            else:  # linux
                subprocess.run(['xdg-open', pdf_path])
        except Exception as e:
            QtWidgets.QMessageBox.warning(
                self,
                "Error al abrir PDF",
                f"No se pudo abrir el archivo PDF:\n{str(e)}",
                QtWidgets.QMessageBox.Ok
            )

class BookManager(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biblioteca Virtual")
        #self.setGeometry(100, 100, 1200, 800)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        self.books = self.load_books()
        
        # Establecer estilo general
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f6fa;
                font-family: Arial;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                padding: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QScrollBar:vertical {
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background: #95a5a6;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QMessageBox {
                background-color: #f5f6fa;
            }
            QMessageBox QPushButton {
                min-width: 80px;
                padding: 5px;
            }
        """)
        
        self.setup_ui()
        self.showMaximized()
        
    def setup_ui(self):
        # Crear un widget scrolleable para todo el contenido
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout()
        scroll_layout.setSpacing(15)
        scroll_widget.setLayout(scroll_layout)
        
        # Header con botón de agregar y estadísticas
        header_layout = QtWidgets.QHBoxLayout()
        add_book_btn = QtWidgets.QPushButton("Agregar Libro")
        add_book_btn.clicked.connect(self.add_book)
        header_layout.addWidget(add_book_btn)
        
        self.stats_label = QtWidgets.QLabel()
        self.stats_label.setStyleSheet("font-size: 14px; color: #7f8c8d;")
        header_layout.addWidget(self.stats_label)
        scroll_layout.addLayout(header_layout)
        
        # Carruseles para cada sección
        self.read_carousel = BookCarousel("Libros Leídos")
        self.pending_carousel = BookCarousel("Libros Pendientes")
        self.to_read_carousel = BookCarousel("Libros por Leer")
        
        scroll_layout.addWidget(self.read_carousel)
        scroll_layout.addWidget(self.pending_carousel)
        scroll_layout.addWidget(self.to_read_carousel)
        
        # Configurar el scroll area principal
        main_scroll = QtWidgets.QScrollArea()
        main_scroll.setWidget(scroll_widget)
        main_scroll.setWidgetResizable(True)
        main_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        main_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        
        # Layout principal
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(main_scroll)
        self.setLayout(main_layout)
        
        # Mostrar libros y actualizar estadísticas
        self.display_books()
        self.update_stats()

    def load_books(self):
        if os.path.exists(BOOKS_FILE):
            with open(BOOKS_FILE, "r") as file:
                return json.load(file)
        return []
    
    def save_books(self):
        with open(BOOKS_FILE, "w") as file:
            json.dump(self.books, file, indent=4)
            
    def delete_book(self, book):
        reply = QtWidgets.QMessageBox.question(
            self,
            'Confirmar Eliminación',
            f'¿Estás seguro de que deseas eliminar "{book["title"]}"?',
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.books = [b for b in self.books if not (
                b["title"] == book["title"] and 
                b["pdf_path"] == book["pdf_path"]
            )]
            self.save_books()
            self.display_books()
            self.update_stats()
            
            QtWidgets.QMessageBox.information(
                self,
                "Libro Eliminado",
                f'Se ha eliminado "{book["title"]}" de tu biblioteca',
                QtWidgets.QMessageBox.Ok
            )
    
    def add_book(self):
        pdf_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Seleccionar Libro PDF", "", "PDF Files (*.pdf)"
        )
        if not pdf_path:
            return
        
        img_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Seleccionar Imagen de Portada", "", "Image Files (*.png *.jpg *.jpeg)"
        )
        if not img_path:
            return
        
        title, ok = QtWidgets.QInputDialog.getText(
            self, "Título del Libro", "Ingrese el título del libro:"
        )
        if not ok or not title:
            title = os.path.basename(pdf_path)
        
        new_book = {
            "title": title,
            "pdf_path": pdf_path,
            "img_path": img_path,
            "status": "Por Leer"
        }
        self.books.append(new_book)
        self.save_books()
        self.display_books()
        self.update_stats()
    
    def change_book_status(self, book, new_status):
        for b in self.books:
            if b["title"] == book["title"] and b["pdf_path"] == book["pdf_path"]:
                b["status"] = new_status
                break
        
        self.save_books()
        self.display_books()
        self.update_stats()
        
        QtWidgets.QMessageBox.information(
            self,
            "Estado Actualizado",
            f'"{book["title"]}" movido a {new_status}',
            QtWidgets.QMessageBox.Ok
        )
    
    def display_books(self):
        for i in reversed(range(self.read_carousel.book_layout.count())):
            self.read_carousel.book_layout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.pending_carousel.book_layout.count())):
            self.pending_carousel.book_layout.itemAt(i).widget().setParent(None)
        for i in reversed(range(self.to_read_carousel.book_layout.count())):
            self.to_read_carousel.book_layout.itemAt(i).widget().setParent(None)
        
        for book in self.books:
            if book["status"] == "Leído":
                self.read_carousel.add_book(book, self)
            elif book["status"] == "Pendiente":
                self.pending_carousel.add_book(book, self)
            else:
                self.to_read_carousel.add_book(book, self)
        
    def update_stats(self):
        read_count = len([b for b in self.books if b["status"] == "Leído"])
        pending_count = len([b for b in self.books if b["status"] == "Pendiente"])
        to_read_count = len([b for b in self.books if b["status"] == "Por Leer"])
        self.stats_label.setText(
            f"📚 Total: {len(self.books)} | ✓ Leídos: {read_count} | "
            f"⏳ Pendientes: {pending_count} | 📖 Por Leer: {to_read_count}"
    )

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = BookManager()
    window.show()
    sys.exit(app.exec_())