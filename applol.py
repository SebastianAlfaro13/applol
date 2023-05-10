import sys
import sqlite3
from PyQt5.QtMultimedia import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

IMAGES = {
    "Hierro": "assets/images/season-2019-iron-1.png",
    "Bronce": "assets/images/season-2019-bronze-1.png",
    "Plata": "assets/images/season-2019-silver-1.png",
    "Oro": "assets/images/season-2019-gold-1.png",
    "Platino": "assets/images/season-2019-platinum-1.png",
    "Diamante": "assets/images/season-2019-diamond-1.png",
    "Maestro": "assets/images/season-2019-master-1.png",
    "Gran Maestro": "assets/images/season-2019-grandmaster-1.png",
    "Retador": "assets/images/season-2019-challenfer-1.png"
}


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Administrador de cuentas de invocador"
        self.left = 100
        self.top = 100
        self.width = 800
        self.height = 600

        self.conn = sqlite3.connect("cuentas_lol.db")
        self.cursor = self.conn.cursor()

        self.create_table()

        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.main_container = QWidget(self)
        self.main_container.setGeometry(0, 0, self.width, self.height)
        self.setCentralWidget(self.main_container)

        layout = QVBoxLayout()
        # Icono de aplicación
        self.setWindowIcon(QIcon("icono.png"))
        
        #Centrar ventana de app y bloquear redimensión
        self.setFixedSize(self.width, self.height)
        self.show()
        screen_center = QDesktopWidget().availableGeometry().center()
        self.move(int(screen_center.x() - self.width/2), int(screen_center.y() - self.height/2 - 50))

        # Widgets y layout de la parte superior
        top_layout = QHBoxLayout()

        self.edit_cuenta = QLineEdit()
        self.edit_cuenta.setPlaceholderText("Cuenta")
        top_layout.addWidget(self.edit_cuenta)

        self.edit_contraseña = QLineEdit()
        self.edit_contraseña.setPlaceholderText("Contraseña")
        top_layout.addWidget(self.edit_contraseña)

        self.edit_nickname = QLineEdit()
        self.edit_nickname.setPlaceholderText("Nickname")
        top_layout.addWidget(self.edit_nickname)

        self.combo_liga = QComboBox()
        self.combo_liga.addItems(["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Maestro", "Gran Maestro", "Retador"])
        top_layout.addWidget(self.combo_liga)

        self.combo_servidor = QComboBox()
        self.combo_servidor.addItems(["LAS", "BRAZIL"])
        top_layout.addWidget(self.combo_servidor)

        btn_agregar = QPushButton("Agregar")
        btn_agregar.clicked.connect(self.agregar_cuenta)
        top_layout.addWidget(btn_agregar)

        # Widgets y layout de la parte inferior
        bottom_layout = QHBoxLayout()

        self.combo_filtrar_servidor = QComboBox()
        self.combo_filtrar_servidor.addItems(["Todos", "LAS", "BRAZIL"])
        bottom_layout.addWidget(self.combo_filtrar_servidor)

        self.combo_filtrar_liga = QComboBox()
        self.combo_filtrar_liga.addItems(["Todas", "Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Maestro", "Gran Maestro", "Retador"])
        bottom_layout.addWidget(self.combo_filtrar_liga)

        btn_filtrar = QPushButton("Filtrar")
        btn_filtrar.clicked.connect(self.filtrar_cuentas)
        bottom_layout.addWidget(btn_filtrar)

        btn_modificar = QPushButton("Modificar")
        btn_modificar.clicked.connect(self.abrir_dialogo_modificar_cuenta)
        bottom_layout.addWidget(btn_modificar)

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self.eliminar_cuenta)
        bottom_layout.addWidget(btn_eliminar)

        self.btn_sonido = QPushButton("Activar sonido")
        self.btn_sonido.setCheckable(True)
        self.btn_sonido.setChecked(False)
        self.btn_sonido.toggled.connect(self.control_sonido)
        bottom_layout.addWidget(self.btn_sonido)

       # Crear la tabla de cuentas
        self.table = CustomTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Cuenta", "Contraseña", "Nickname", "Liga", "Servidor"])
        self.table.verticalHeader().setVisible(False)

        # Ocultar la columna "ID"
        self.table.setColumnHidden(5, True)

        header = self.table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignCenter)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(50)

        # Aplicar estilo al texto de la tabla
        font = QFont("Cambria", 12, QFont.Bold)
        self.table.setFont(font)


        # Añadir los layouts a la ventana principal
        layout.addLayout(top_layout)
        layout.addWidget(self.table)
        layout.addLayout(bottom_layout)

        self.main_container.setLayout(layout)

        self.cargar_cuentas()

        # Cambiar el color de los bordes internos de la aplicación
        self.setStyleSheet("QTableWidget { border: 2px solid white; }")

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS cuentas (id INTEGER PRIMARY KEY, cuenta TEXT, contraseña TEXT, nickname TEXT, liga TEXT, servidor TEXT)''')
        self.conn.commit()

    def agregar_cuenta(self):
        cuenta = self.edit_cuenta.text()
        contraseña = self.edit_contraseña.text()
        nickname = self.edit_nickname.text()
        liga = self.combo_liga.currentText()
        servidor = self.combo_servidor.currentText()

        if not cuenta or not contraseña or not nickname:
            QMessageBox.warning(self, "Campos vacíos", "Por favor, complete todos los campos.")
        else:
            self.cursor.execute('''INSERT INTO cuentas (cuenta, contraseña, nickname, liga, servidor) VALUES (?, ?, ?, ?, ?)''', (cuenta, contraseña, nickname, liga, servidor))
            self.conn.commit()
            self.edit_cuenta.clear()
            self.edit_contraseña.clear()
            self.edit_nickname.clear()
            self.cargar_cuentas()

    def cargar_cuentas(self):
        # Limpia la tabla antes de volver a cargar los datos.
        self.table.setRowCount(0)
        # Realiza una consulta SELECT para obtener todas las filas de la tabla 'cuentas'
        self.cursor.execute('''SELECT * FROM cuentas''')
        # Recupera todas las filas de la consulta anterior y las almacena en la variable 'cuentas'
        cuentas = self.cursor.fetchall()
        # Itera sobre cada fila en 'cuentas'
        for cuenta in cuentas:
            # Obtiene la posición de la fila en la tabla
            row_position = self.table.rowCount()
            # Inserta una nueva fila en la tabla en la posición 'row_position'
            self.table.insertRow(row_position)

            # Itera sobre los primeros 5 elementos de la fila actual
            for i in range(5):
                # Crea un nuevo objeto QTableWidgetItem con el valor actual de 'cuenta[i+1]'
                item = QTableWidgetItem(str(cuenta[i+1]))
                # Crea una fuente con negrita y tamaño de fuente de 12
                font = QFont()
                font.setBold(True)
                font.setPointSize(12)
                # Establece la fuente creada anteriormente para el objeto QTableWidgetItem
                item.setFont(font)
                # Define el color de fondo del objeto QTableWidgetItem basado en el valor de cuenta[5]
                if cuenta[5] == "BRAZIL":
                    color = QColor(0, 255, 0, 80)
                else:
                    color = QColor(0, 255, 255, 80)
                item.setBackground(color)
                # Inserta el objeto QTableWidgetItem en la tabla en la posición [row_position, i]
                self.table.setItem(row_position, i, item)
                # Obtiene el objeto QTableWidgetItem recién insertado para centrar el texto
                item = self.table.item(row_position, i)
                item.setTextAlignment(Qt.AlignCenter)

            # Obtiene la liga (una cadena) de la fila actual en la posición 4
            liga = cuenta[4]
            # Obtiene la ruta de la imagen correspondiente a la liga, si existe
            image_path = IMAGES.get(liga)
            # Si la ruta de la imagen existe
            if image_path:
                # Crea un nuevo objeto QLabel para mostrar la imagen
                image_label = QLabel()
                # Carga la imagen de la ruta de la imagen en un objeto QPixmap
                image_pixmap = QPixmap(image_path)
                # Verifica si la imagen se ha cargado correctamente
                if not image_pixmap.isNull():
                    # Escala la imagen a un tamaño de 45x45 píxeles y la establece en el objeto QLabel
                    image_pixmap = image_pixmap.scaled(45, 45, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(image_pixmap)
                    # Inserta el objeto QLabel en la tabla en la posición [row_position, 3]
                    self.table.setCellWidget(row_position, 3, image_label)
                else:
                    # Si la imagen no se ha cargado correctamente, muestra un mensaje de error
                    print(f"Error al cargar la imagen en {image_path}")

            # Inserta el valor de cuenta[0] en la tabla en la posición [row_position, 5]
            self.table.setItem(row_position, 5, QTableWidgetItem(str(cuenta[0])))

    def filtrar_cuentas(self):
        servidor = self.combo_filtrar_servidor.currentText()
        liga = self.combo_filtrar_liga.currentText()

        # Construir la consulta SQL en función de los valores seleccionados en los combos
        sql_query = 'SELECT * FROM cuentas'
        params = []

        if servidor != 'Todos' and liga != 'Todas':
            sql_query += ' WHERE servidor = ? AND liga = ?'
            params = [servidor, liga]
        elif servidor != 'Todos':
            sql_query += ' WHERE servidor = ?'
            params = [servidor]
        elif liga != 'Todas':
            sql_query += ' WHERE liga = ?'
            params = [liga]

        # Ejecutar la consulta SQL y cargar los resultados en la tabla
        self.table.setRowCount(0)
        self.cursor.execute(sql_query, params)
        cuentas = self.cursor.fetchall()

        for cuenta in cuentas:
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            for i in range(5):
                item = QTableWidgetItem(str(cuenta[i+1]))
                font = QFont()
                font.setBold(True)
                font.setPointSize(12)
                item.setFont(font)
                if cuenta[5] == "BRAZIL":
                    color = QColor(0, 255, 0, 40)
                else:
                    color = QColor(0, 255, 255, 40)
                item.setBackground(color)
                self.table.setItem(row_position, i, item)
                item = self.table.item(row_position, i)
                item.setTextAlignment(Qt.AlignCenter)

            self.table.setItem(row_position, 5, QTableWidgetItem(str(cuenta[0])))

    def abrir_dialogo_modificar_cuenta(self):
        if self.table.currentRow() >= 0:
            self.dialog = QDialog(self)
            self.dialog.setWindowTitle("Modificar cuenta")

            layout = QVBoxLayout()

            form_layout = QFormLayout()

            self.edit_modificar_cuenta = QLineEdit()
            self.edit_modificar_cuenta.setText(self.table.item(self.table.currentRow(), 0).text())
            form_layout.addRow("Cuenta:", self.edit_modificar_cuenta)

            self.edit_modificar_contraseña = QLineEdit()
            self.edit_modificar_contraseña.setText(self.table.item(self.table.currentRow(), 1).text())
            form_layout.addRow("Contraseña:", self.edit_modificar_contraseña)

            self.edit_modificar_nickname = QLineEdit()
            self.edit_modificar_nickname.setText(self.table.item(self.table.currentRow(), 2).text())
            form_layout.addRow("Nickname:", self.edit_modificar_nickname)

            self.combo_modificar_liga = QComboBox()
            self.combo_modificar_liga.addItems(["Hierro", "Bronce", "Plata", "Oro", "Platino", "Diamante", "Maestro", "Gran Maestro", "Retador"])
            self.combo_modificar_liga.setCurrentText(self.table.item(self.table.currentRow(), 3).text())
            form_layout.addRow("Liga:", self.combo_modificar_liga)

            self.combo_modificar_servidor = QComboBox()
            self.combo_modificar_servidor.addItems(["LAS", "BRAZIL"])
            self.combo_modificar_servidor.setCurrentText(self.table.item(self.table.currentRow(), 4).text())
            form_layout.addRow("Servidor:", self.combo_modificar_servidor)

            layout.addLayout(form_layout)

            btn_modificar_cuenta = QPushButton("Modificar")
            btn_modificar_cuenta.clicked.connect(self.modificar_cuenta)
            layout.addWidget(btn_modificar_cuenta)

            self.dialog.setLayout(layout)
            self.dialog.exec_()
        else:
            QMessageBox.warning(self, "Ninguna cuenta seleccionada", "Por favor, seleccione una cuenta para modificar.")

    def modificar_cuenta(self):
        id_cuenta = int(self.table.item(self.table.currentRow(), 5).text())
        cuenta = self.edit_modificar_cuenta.text()
        contraseña = self.edit_modificar_contraseña.text()
        nickname = self.edit_modificar_nickname.text()
        liga = self.combo_modificar_liga.currentText()
        servidor = self.combo_modificar_servidor.currentText()

        self.cursor.execute('''UPDATE cuentas SET cuenta = ?, contraseña = ?, nickname = ?, liga = ?, servidor = ? WHERE id = ?''', (cuenta, contraseña, nickname, liga, servidor, id_cuenta))
        self.conn.commit()
        self.dialog.close()
        self.cargar_cuentas()
        
    def eliminar_cuenta(self):
        row = self.table.currentRow()
        if row >= 0:
            id_cuenta_item = self.table.item(row, 5)
            if id_cuenta_item is not None:
                id_cuenta = int(id_cuenta_item.text())
                self.cursor.execute('''DELETE FROM cuentas WHERE id = ?''', (id_cuenta,))
                self.conn.commit()
                self.cargar_cuentas()
            else:
                QMessageBox.warning(self, "Error al eliminar cuenta", "No se pudo obtener el ID de la cuenta seleccionada.")
        else:
            QMessageBox.warning(self, "Ninguna cuenta seleccionada", "Por favor, seleccione una cuenta para eliminar.")

    def control_sonido(self, checked):
        if checked:
            self.btn_sonido.setText("Desactivar sonido")
            # Cargar el archivo de música
            music_file = QUrl.fromLocalFile('assets/musica.mp3')
            # Crear un reproductor multimedia y una lista de reproducción
            self.media_player = QMediaPlayer()
            self.media_playlist = QMediaPlaylist()
            # Agregar el archivo de música a la lista de reproducción
            self.media_playlist.addMedia(QMediaContent(music_file))
            self.media_playlist.setCurrentIndex(0)
            self.media_player.setPlaylist(self.media_playlist)
            # Reproducir la lista de reproducción
            self.media_player.play()
        else:
            self.btn_sonido.setText("Activar sonido")
            # Detener la música
            self.media_player.stop()

    def closeEvent(self, event):
        self.conn.close()

class CustomTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fondo_cuentas = QPixmap("assets/images/Fondo.jpg")
        self.setStyleSheet("QTableWidget { background-color: rgba(255, 255, 255, 120); }")

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.drawPixmap(0, 0, self.fondo_cuentas)
        super().paintEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())