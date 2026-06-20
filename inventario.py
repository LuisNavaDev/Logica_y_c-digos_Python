import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import roll80, A4
from reportlab.pdfgen import canvas
import os

# --- CONFIGURACIÓN DE BASE DE DATOS ---
class Database:
    def __init__(self, db_name="moda_manager.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Tabla de Productos (Modelo base)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                categoria TEXT,
                precio_venta REAL,
                costo REAL
            )
        ''')
        # Tabla de Variantes (Talla, Color, Stock y Alerta Mínima)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS variantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                talla TEXT,
                color TEXT,
                stock INTEGER,
                stock_minimo INTEGER,
                FOREIGN KEY(producto_id) REFERENCES productos(id)
            )
        ''')
        # Tabla de Ventas
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT,
                total REAL
            )
        ''')
        # Tabla de Detalles de Venta
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detalle_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER,
                variante_id INTEGER,
                cantidad INTEGER,
                precio_unitario REAL,
                FOREIGN KEY(venta_id) REFERENCES ventas(id)
            )
        ''')
        self.conn.commit()

    def fetch_low_stock(self):
        query = '''
            SELECT p.nombre, v.talla, v.color, v.stock, v.stock_minimo 
            FROM variantes v 
            JOIN productos p ON v.producto_id = p.id 
            WHERE v.stock <= v.stock_minimo
        '''
        return self.cursor.execute(query).fetchall()

db = Database()

# --- LÓGICA DE PDF ---
def generar_ticket_pdf(venta_id, carrito, total):
    filename = f"ticket_{venta_id}.pdf"
    c = canvas.Canvas(filename, pagesize=(226, 400)) # Tamaño tipo ticket termico (80mm aprox)
    width, height = (226, 400)
    
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(width/2, height - 30, "MI MARCA DE ROPA")
    
    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, height - 45, f"Ticket #: {venta_id}")
    c.drawCentredString(width/2, height - 60, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    y = height - 90
    c.line(10, y+5, width-10, y+5)
    c.drawString(10, y, "Cant.")
    c.drawString(40, y, "Producto")
    c.drawString(180, y, "Total")
    y -= 15
    
    for item in carrito:
        nombre_completo = f"{item['nombre']} ({item['talla']}/{item['color']})"
        subtotal = item['precio'] * item['cantidad']
        
        c.drawString(10, y, str(item['cantidad']))
        c.setFont("Helvetica", 8)
        # Recorte simple de nombre si es muy largo
        c.drawString(40, y, nombre_completo[:25]) 
        c.setFont("Helvetica", 9)
        c.drawString(180, y, f"${subtotal:.2f}")
        y -= 15
        
    c.line(10, y+5, width-10, y+5)
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width-20, y, f"TOTAL: ${total:.2f}")
    
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, 30, "¡Gracias por su compra!")
    c.save()
    os.startfile(filename) # Abre el PDF automáticamente (Windows)

# --- INTERFAZ GRÁFICA ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Inventario & POS - Ropa")
        self.geometry("1000x700")
        
        # Estilos
        style = ttk.Style()
        style.theme_use('clam')
        
        # Pestañas
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill='both', expand=True)
        
        self.tab_ventas = ttk.Frame(self.notebook)
        self.tab_inventario = ttk.Frame(self.notebook)
        self.tab_alertas = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_ventas, text="🛒 Punto de Venta")
        self.notebook.add(self.tab_inventario, text="👕 Inventario")
        self.notebook.add(self.tab_alertas, text="⚠️ Alertas Stock")
        
        # Variables Globales POS
        self.carrito = []
        
        self.setup_inventario_ui()
        self.setup_ventas_ui()
        self.setup_alertas_ui()
        
        # Chequear alertas al iniciar
        self.actualizar_alertas()

    # ---------------- SECCIÓN INVENTARIO ----------------
    def setup_inventario_ui(self):
        frame_form = ttk.LabelFrame(self.tab_inventario, text="Agregar/Editar Producto")
        frame_form.pack(side="left", fill="y", padx=10, pady=10)
        
        # Campos
        tk.Label(frame_form, text="Nombre Modelo:").pack()
        self.entry_nombre = tk.Entry(frame_form)
        self.entry_nombre.pack()
        
        tk.Label(frame_form, text="Categoría:").pack()
        self.entry_cat = tk.Entry(frame_form)
        self.entry_cat.pack()
        
        tk.Label(frame_form, text="Precio Venta:").pack()
        self.entry_precio = tk.Entry(frame_form)
        self.entry_precio.pack()
        
        tk.Label(frame_form, text="Costo (Egreso):").pack()
        self.entry_costo = tk.Entry(frame_form)
        self.entry_costo.pack()
        
        # Separador para variantes
        ttk.Separator(frame_form, orient='horizontal').pack(fill='x', pady=10)
        tk.Label(frame_form, text="-- VARIANTE --", fg="blue").pack()
        
        tk.Label(frame_form, text="Talla:").pack()
        self.combo_talla = ttk.Combobox(frame_form, values=["XS", "S", "M", "L", "XL", "XXL"])
        self.combo_talla.pack()
        
        tk.Label(frame_form, text="Color:").pack()
        self.entry_color = tk.Entry(frame_form)
        self.entry_color.pack()
        
        tk.Label(frame_form, text="Cantidad Inicial:").pack()
        self.entry_stock = tk.Entry(frame_form)
        self.entry_stock.pack()
        
        # NUEVO: Configuración de Alerta
        tk.Label(frame_form, text="Alerta Stock Mínimo:", fg="red").pack()
        self.entry_min_stock = tk.Entry(frame_form)
        self.entry_min_stock.insert(0, "5") # Valor por defecto
        self.entry_min_stock.pack()
        
        tk.Button(frame_form, text="Guardar Producto y Variante", command=self.guardar_producto, bg="#4CAF50", fg="white").pack(pady=15)
        
        # Tabla Inventario
        frame_table = ttk.Frame(self.tab_inventario)
        frame_table.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        self.tree_inv = ttk.Treeview(frame_table, columns=("ID", "Prod", "Talla", "Color", "Stock", "Min"), show="headings")
        self.tree_inv.heading("ID", text="ID")
        self.tree_inv.heading("Prod", text="Producto")
        self.tree_inv.heading("Talla", text="Talla")
        self.tree_inv.heading("Color", text="Color")
        self.tree_inv.heading("Stock", text="Stock Actual")
        self.tree_inv.heading("Min", text="Mínimo")
        self.tree_inv.pack(fill="both", expand=True)
        
        btn_refresh = tk.Button(frame_table, text="Actualizar Lista", command=self.cargar_inventario)
        btn_refresh.pack()
        
        self.cargar_inventario()

    def guardar_producto(self):
        try:
            nombre = self.entry_nombre.get()
            cat = self.entry_cat.get()
            precio = float(self.entry_precio.get())
            costo = float(self.entry_costo.get())
            talla = self.combo_talla.get()
            color = self.entry_color.get()
            stock = int(self.entry_stock.get())
            min_stock = int(self.entry_min_stock.get())

            # Verificar si el producto ya existe por nombre (simplificación)
            db.cursor.execute("SELECT id FROM productos WHERE nombre = ?", (nombre,))
            res = db.cursor.fetchone()
            
            if res:
                prod_id = res[0]
            else:
                db.cursor.execute("INSERT INTO productos (nombre, categoria, precio_venta, costo) VALUES (?, ?, ?, ?)",
                                  (nombre, cat, precio, costo))
                prod_id = db.cursor.lastrowid
            
            # Insertar variante
            db.cursor.execute("INSERT INTO variantes (producto_id, talla, color, stock, stock_minimo) VALUES (?, ?, ?, ?, ?)",
                              (prod_id, talla, color, stock, min_stock))
            db.conn.commit()
            
            messagebox.showinfo("Éxito", "Producto agregado correctamente")
            self.cargar_inventario()
            self.actualizar_alertas() # Revisar alertas tras guardar
            self.cargar_productos_pos()
            
        except ValueError:
            messagebox.showerror("Error", "Por favor revisa que los campos numéricos sean correctos.")

    def cargar_inventario(self):
        for item in self.tree_inv.get_children():
            self.tree_inv.delete(item)
            
        query = '''
            SELECT v.id, p.nombre, v.talla, v.color, v.stock, v.stock_minimo 
            FROM variantes v 
            JOIN productos p ON v.producto_id = p.id
        '''
        rows = db.cursor.execute(query).fetchall()
        for row in rows:
            self.tree_inv.insert("", "end", values=row)

    # ---------------- SECCIÓN POS (VENTAS) ----------------
    def setup_ventas_ui(self):
        # Panel Izquierdo: Selección de Productos
        left_panel = ttk.Frame(self.tab_ventas)
        left_panel.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        tk.Label(left_panel, text="Seleccionar Producto").pack()
        
        self.tree_pos = ttk.Treeview(left_panel, columns=("ID_Var", "Prod", "Talla", "Color", "Precio", "Stock"), show="headings")
        self.tree_pos.heading("ID_Var", text="ID")
        self.tree_pos.heading("Prod", text="Producto")
        self.tree_pos.heading("Talla", text="Talla")
        self.tree_pos.heading("Color", text="Color")
        self.tree_pos.heading("Precio", text="$$")
        self.tree_pos.heading("Stock", text="Disp.")
        self.tree_pos.column("ID_Var", width=30)
        self.tree_pos.pack(fill="both", expand=True)
        
        btn_add = tk.Button(left_panel, text="Añadir al Carrito >>", command=self.agregar_carrito, bg="#2196F3", fg="white")
        btn_add.pack(pady=10)
        
        # Panel Derecho: Carrito
        right_panel = ttk.Frame(self.tab_ventas)
        right_panel.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        tk.Label(right_panel, text="Carrito de Compras").pack()
        
        self.tree_cart = ttk.Treeview(right_panel, columns=("Prod", "Detalle", "Cant", "Subtotal"), show="headings")
        self.tree_cart.heading("Prod", text="Producto")
        self.tree_cart.heading("Detalle", text="Talla/Color")
        self.tree_cart.heading("Cant", text="Cant.")
        self.tree_cart.heading("Subtotal", text="$$")
        self.tree_cart.pack(fill="both", expand=True)
        
        self.lbl_total = tk.Label(right_panel, text="TOTAL: $0.00", font=("Arial", 16, "bold"))
        self.lbl_total.pack(pady=10)
        
        btn_pay = tk.Button(right_panel, text="Cobrar e Imprimir Ticket", command=self.procesar_venta, bg="#FF5722", fg="white", font=("Arial", 12))
        btn_pay.pack(pady=5, fill="x")
        
        self.cargar_productos_pos()

    def cargar_productos_pos(self):
        for item in self.tree_pos.get_children():
            self.tree_pos.delete(item)
            
        query = '''
            SELECT v.id, p.nombre, v.talla, v.color, p.precio_venta, v.stock 
            FROM variantes v 
            JOIN productos p ON v.producto_id = p.id
            WHERE v.stock > 0
        '''
        rows = db.cursor.execute(query).fetchall()
        for row in rows:
            self.tree_pos.insert("", "end", values=row)

    def agregar_carrito(self):
        selected = self.tree_pos.selection()
        if not selected:
            return
        
        item_values = self.tree_pos.item(selected[0])['values']
        var_id, nombre, talla, color, precio, stock_actual = item_values
        
        # Preguntar cantidad
        cantidad = simpledialog.askinteger("Cantidad", f"¿Cuántos {nombre} ({talla}/{color})?", minvalue=1, maxvalue=stock_actual)
        
        if cantidad:
            item = {
                "id_var": var_id,
                "nombre": nombre,
                "talla": talla,
                "color": color,
                "precio": float(precio),
                "cantidad": cantidad
            }
            self.carrito.append(item)
            self.actualizar_carrito_ui()

    def actualizar_carrito_ui(self):
        for item in self.tree_cart.get_children():
            self.tree_cart.delete(item)
            
        total = 0
        for item in self.carrito:
            subtotal = item['precio'] * item['cantidad']
            total += subtotal
            self.tree_cart.insert("", "end", values=(item['nombre'], f"{item['talla']}/{item['color']}", item['cantidad'], f"${subtotal}"))
            
        self.lbl_total.config(text=f"TOTAL: ${total:.2f}")

    def procesar_venta(self):
        if not self.carrito:
            return
            
        total = sum(i['precio'] * i['cantidad'] for i in self.carrito)
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            # 1. Registrar Venta Global
            db.cursor.execute("INSERT INTO ventas (fecha, total) VALUES (?, ?)", (fecha, total))
            venta_id = db.cursor.lastrowid
            
            # 2. Registrar Detalles y Descontar Stock
            for item in self.carrito:
                db.cursor.execute("INSERT INTO detalle_venta (venta_id, variante_id, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
                                  (venta_id, item['id_var'], item['cantidad'], item['precio']))
                
                # Descontar inventario
                db.cursor.execute("UPDATE variantes SET stock = stock - ? WHERE id = ?", (item['cantidad'], item['id_var']))
            
            db.conn.commit()
            
            # 3. Generar Ticket
            generar_ticket_pdf(venta_id, self.carrito, total)
            
            # Limpieza
            self.carrito = []
            self.actualizar_carrito_ui()
            self.cargar_productos_pos() # Actualizar POS
            self.cargar_inventario() # Actualizar Inventario
            self.actualizar_alertas() # REVISAR SI HAY STOCK BAJO AHORA
            
            messagebox.showinfo("Venta Exitosa", "Venta registrada y ticket generado.")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # ---------------- SECCIÓN ALERTAS (STOCK BAJO) ----------------
    def setup_alertas_ui(self):
        tk.Label(self.tab_alertas, text="⚠️ Productos con Stock Crítico", font=("Arial", 14, "bold"), fg="red").pack(pady=10)
        
        self.tree_alertas = ttk.Treeview(self.tab_alertas, columns=("Prod", "Detalle", "Stock Actual", "Mínimo Permitido"), show="headings")
        self.tree_alertas.heading("Prod", text="Producto")
        self.tree_alertas.heading("Detalle", text="Talla/Color")
        self.tree_alertas.heading("Stock Actual", text="Stock Actual")
        self.tree_alertas.heading("Mínimo Permitido", text="Umbral Mínimo")
        
        # Color rojo para filas
        self.tree_alertas.tag_configure('low_stock', background='#ffcccc')
        self.tree_alertas.pack(fill="both", expand=True, padx=20, pady=10)
        
        btn_refresh = tk.Button(self.tab_alertas, text="Refrescar Alertas", command=self.actualizar_alertas)
        btn_refresh.pack(pady=10)

    def actualizar_alertas(self):
        # Limpiar tabla
        for item in self.tree_alertas.get_children():
            self.tree_alertas.delete(item)
            
        items_bajos = db.fetch_low_stock()
        
        if items_bajos:
            # Cambiar color de pestaña si hay alertas (Visual cue)
            self.notebook.tab(2, text="⚠️ Alertas Stock (ACTIVO)")
            for item in items_bajos:
                nombre, talla, color, stock, minimo = item
                self.tree_alertas.insert("", "end", values=(nombre, f"{talla}/{color}", stock, minimo), tags=('low_stock',))
        else:
            self.notebook.tab(2, text="Alertas Stock")
            # Mensaje opcional de "Todo OK" en la tabla
            self.tree_alertas.insert("", "end", values=("Todo en orden", "-", "-", "-"))

if __name__ == "__main__":
    app = App()
    app.mainloop()