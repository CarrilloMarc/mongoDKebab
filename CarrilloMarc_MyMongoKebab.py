import pymongo
from pymongo import MongoClient
import tkinter as tk
from tkinter import messagebox, simpledialog

def create_database():
    client = MongoClient('mongodb://192.168.0.142:27017/')
    db = client.kebab_shop

    # Crear colección de Ingredientes
    if 'Ingredientes' not in db.list_collection_names():
        db.create_collection('Ingredientes')
    if 'Compra' not in db.list_collection_names():
        db.create_collection('Compra')
    if 'Kebab' not in db.list_collection_names():
        db.create_collection('Kebab')
    if 'Venta' not in db.list_collection_names():
        db.create_collection('Venta')

create_database()

def check_credentials(username, password):
    if username == "amigo" and password == "kebab":
        return "admin"
    elif username == "vendedor" and password == "dekebabs":
        return "vendedor"
    else:
        return None

def main_menu(root, user_type):
    root.title("Menú Principal")
    
    # Definir el fondo de la ventana principal
    root.configure(bg="#f0f0f0")

    # Crear un marco para contener los botones
    frame = tk.Frame(root, bg="#f0f0f0")
    frame.pack(padx=20, pady=20)

    # Función para crear botones con opciones
    def create_button(text, command, bg_color):
        button = tk.Button(frame, text=text, command=command, width=25, height=2, bg=bg_color)
        button.pack(side=tk.TOP if bg_color == "#6fa4e7" else tk.BOTTOM, padx=10, pady=5)
        
    # Crear botones según el tipo de usuario
    if user_type == "admin":
        create_button("Realizar compra", realizar_compra, "#ff6666")  # Rojo
        create_button("Editar Kebabs", editar_kebabs, "#ff6666")  # Rojo
        create_button("Realizar venta", realizar_venta, "#6fa4e7")  # Azul
        create_button("Consultar stock de ingredientes", consultar_stock, "#6fa4e7")  # Azul
    else:
        create_button("Realizar venta", realizar_venta, "#6fa4e7")  # Azul
        create_button("Consultar ingredientes", consultar_stock, "#6fa4e7")  # Azul

def login(root):
    login_window = tk.Toplevel()
    login_window.title("Inicio de Sesión")

    label_username = tk.Label(login_window, text="Usuario:")
    label_username.grid(row=0, column=0)
    entry_username = tk.Entry(login_window)
    entry_username.grid(row=0, column=1)

    label_password = tk.Label(login_window, text="Contraseña:")
    label_password.grid(row=1, column=0)
    entry_password = tk.Entry(login_window, show="*")
    entry_password.grid(row=1, column=1)

    def submit():
        username = entry_username.get()
        password = entry_password.get()
        user_type = check_credentials(username, password)
        if user_type:
            main_menu(root, user_type)
            login_window.destroy()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas. Por favor, inténtelo de nuevo.")
            entry_username.delete(0, tk.END)
            entry_password.delete(0, tk.END)

    button_submit = tk.Button(login_window, text="Iniciar Sesión", command=submit)
    button_submit.grid(row=2, columnspan=2)

def realizar_compra():
    client = MongoClient('mongodb://192.168.0.142:27017/')
    db = client.kebab_shop

    ingredientes = [
        {"nombre": "Ternera", "stock": 50},
        {"nombre": "Pollo", "stock": 50},
        {"nombre": "Lechuga", "stock": 0},
        {"nombre": "Cebolla", "stock": 0},
        {"nombre": "Queso", "stock": 0},
        {"nombre": "Tomate", "stock": 0},
        {"nombre": "Masa", "stock": 0},
        {"nombre": "Salsa Blanca", "stock": 0},
        {"nombre": "Salsa Picante", "stock": 0}
    ]

    # Crear ventana para seleccionar ingredientes y cantidades
    compra_window = tk.Toplevel()
    compra_window.title("Realizar Compra")

    # Función para agregar ingredientes al carrito
    def agregar_al_carrito(ingrediente, cantidad_str):
        if cantidad_str.strip() == '':
            return
        try:
            cantidad = int(cantidad_str)
        except ValueError:
            return
        if ingrediente in carrito:
            carrito[ingrediente] += cantidad
        else:
            carrito[ingrediente] = cantidad
        actualizar_carrito()

    # Función para actualizar el carrito de compras
    def actualizar_carrito():
        listbox_carrito.delete(0, tk.END)
        for ingrediente, cantidad in carrito.items():
            listbox_carrito.insert(tk.END, f"{ingrediente}: {cantidad}")

    # Función para confirmar la compra
    def confirmar_compra():
        total = sum(carrito.values())
        confirmar = messagebox.askyesno("Confirmar compra", f"Total de productos seleccionados: {total}\n¿Desea confirmar la compra?")
        if confirmar:
            for ingrediente, cantidad in carrito.items():
                db.Ingredientes.update_one(
                    {"nombre_ingrediente": ingrediente},
                    {"$inc": {"stock": cantidad}},
                    upsert=True
                )
            messagebox.showinfo("Compra realizada", "Compra realizada con éxito.")
            compra_window.destroy()
            consultar_stock()

    # Listbox para mostrar ingredientes disponibles y botones para agregar
    for ing in ingredientes:
        frame = tk.Frame(compra_window)
        frame.pack(padx=10, pady=5, fill="x")

        label_nombre = tk.Label(frame, text=ing["nombre"])
        label_nombre.pack(side="left", padx=5)

        stock = db.Ingredientes.find_one({"nombre_ingrediente": ing["nombre"]}, {"stock": 1})
        stock = stock["stock"] if stock is not None else 0
        label_stock = tk.Label(frame, text=f"Stock: {stock}")
        label_stock.pack(side="left", padx=5)

        entry_cantidad = tk.Entry(frame, width=5)
        entry_cantidad.pack(side="left", padx=5)
        button_set = tk.Button(frame, text="Añadir", command=lambda ingrediente=ing["nombre"], entry=entry_cantidad: agregar_al_carrito(ingrediente, entry.get().strip()))
        button_set.pack(side="left", padx=5)

    # Listbox para mostrar el carrito de compras
    listbox_carrito = tk.Listbox(compra_window)
    listbox_carrito.pack(padx=10, pady=5)

    # Botón para confirmar la compra
    button_confirmar = tk.Button(compra_window, text="Confirmar compra", command=confirmar_compra)
    button_confirmar.pack(padx=10, pady=5)

    carrito = {}

def realizar_venta():
    client = MongoClient('mongodb://192.168.0.142:27017/')
    db = client.kebab_shop

    kebabs = db.Kebab.find()
    for kebab in kebabs:
        print(f"ID: {kebab['_id']}, Kebab: {kebab['nombre_kebab']}, Precio: {kebab['precio']}")

    try:
        id_kebab = simpledialog.askinteger("Realizar venta", "Ingrese el ID del kebab que desea vender:")
        cantidad = simpledialog.askinteger("Realizar venta", "Ingrese la cantidad de kebabs:")
        fecha_venta = simpledialog.askstring("Realizar venta", "Ingrese la fecha de venta (YYYY-MM-DD):")

        kebab = db.Kebab.find_one({"_id": id_kebab})
        if kebab and verificar_stock(db, id_kebab, cantidad):
            monto_total = kebab["precio"] * cantidad
            db.Venta.insert_one({
                "id_kebab": id_kebab,
                "fecha_venta": fecha_venta,
                "cantidad": cantidad,
                "monto_total": monto_total
            })
            messagebox.showinfo("Venta realizada", "Venta realizada con éxito.")
        else:
            messagebox.showerror("Error", "Stock insuficiente para realizar la venta.")
    except (ValueError, TypeError):
        messagebox.showerror("Error", "Debe ingresar un número válido.")
    except pymongo.errors.PyMongoError as e:
        messagebox.showerror("Error de base de datos", f"Error de la base de datos: {e}")

def verificar_stock(db, id_kebab, cantidad):
    kebab = db.Kebab.find_one({"_id": id_kebab})
    if not kebab:
        return False
    # Aquí deberías agregar la lógica para verificar los ingredientes necesarios y su stock
    # Por ahora, asumimos que hay suficiente stock
    return True

def editar_kebabs():
    client = MongoClient('mongodb://192.168.0.142:27017/')
    db = client.kebab_shop

    kebabs = db.Kebab.find()
    for kebab in kebabs:
        print(f"ID: {kebab['_id']}, Nombre: {kebab['nombre_kebab']}, Precio: {kebab['precio']}")

    try:
        id_kebab = simpledialog.askinteger("Editar Kebab", "Ingrese el ID del kebab que desea editar:")
        nuevo_nombre = simpledialog.askstring("Editar Kebab", "Ingrese el nuevo nombre del kebab:")
        nuevo_precio = simpledialog.askfloat("Editar Kebab", "Ingrese el nuevo precio del kebab:")

        editar_kebab_window = tk.Toplevel()
        editar_kebab_window.title("Seleccionar Ingredientes")

        selected_ingredients = []

        def toggle_ingredient(ingredient):
            if ingredient in selected_ingredients:
                selected_ingredients.remove(ingredient)
            else:
                selected_ingredients.append(ingredient)

        ingredientes = db.Ingredientes.find()
        for ingrediente in ingredientes:
            var = tk.BooleanVar()
            check = tk.Checkbutton(
                editar_kebab_window,
                text=ingrediente["nombre_ingrediente"],
                variable=var,
                command=lambda ingr=ingrediente["nombre_ingrediente"], var=var: toggle_ingredient(ingr)
            )
            check.pack()

        def save_changes():
            db.Kebab.update_one(
                {"_id": id_kebab},
                {"$set": {
                    "nombre_kebab": nuevo_nombre,
                    "precio": nuevo_precio,
                    "ingredientes": selected_ingredients
                }}
            )
            messagebox.showinfo("Éxito", "Kebab editado con éxito.")
            editar_kebab_window.destroy()

        button_save = tk.Button(editar_kebab_window, text="Guardar cambios", command=save_changes)
        button_save.pack(pady=10)

    except (ValueError, TypeError):
        messagebox.showerror("Error", "Debe ingresar un número válido.")
    except pymongo.errors.PyMongoError as e:
        messagebox.showerror("Error de base de datos", f"Error de la base de datos: {e}")

def consultar_stock():
    client = MongoClient('mongodb://192.168.0.142:27017/')
    db = client.kebab_shop

    ingredientes = db.Ingredientes.find()
    stock_info = ""
    for ingrediente in ingredientes:
        stock_info += f"{ingrediente['nombre_ingrediente']}: {ingrediente['stock']}\n"
    messagebox.showinfo("Stock de ingredientes", stock_info)

root = tk.Tk()
login(root)
root.mainloop()
