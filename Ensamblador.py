import tkinter as tk
from tkinter import filedialog, scrolledtext


def traducir_a_ensamblador(texto_entrada):
    """
    Traduce operaciones aritméticas de un texto a código en ensamblador.
    Gestiona registros de forma dinámica para reutilizar los disponibles.
    """
    registros = ["AX", "BX", "CX", "DX"]  # Registros disponibles
    mapa_registros = {}  # Asignación de variables a registros
    registros_libres = set(registros)  # Controla registros disponibles

    def obtener_registro(var):
        """Asigna un registro a una variable o recupera uno ya asignado."""
        if var in mapa_registros:
            return mapa_registros[var]

        if not registros_libres:
            raise Exception("¡No hay suficientes registros disponibles!")

        nuevo_registro = registros_libres.pop()
        mapa_registros[var] = nuevo_registro
        return nuevo_registro

    def liberar_registro(var):
        """Libera el registro asignado a una variable para reutilizarlo."""
        if var in mapa_registros:
            registros_libres.add(mapa_registros.pop(var))

    codigo_ensamblador = []
    lineas = texto_entrada.splitlines()

    for linea in lineas:
        linea = linea.strip()
        if not linea or '=' not in linea:
            continue  # Saltar líneas vacías o inválidas

        izquierda, derecha = linea.split('=')
        izquierda = izquierda.strip()
        derecha = derecha.strip()

        # Detectar tipo de operación
        if '+' in derecha:
            operandos = derecha.split('+')
            operacion = 'ADD'
        elif '-' in derecha:
            operandos = derecha.split('-')
            operacion = 'SUB'
        elif '*' in derecha:
            operandos = derecha.split('*')
            operacion = 'MUL'
        elif '/' in derecha:
            operandos = derecha.split('/')
            operacion = 'DIV'
        else:
            raise ValueError(f"Operación no soportada en la línea: {linea}")

        if len(operandos) != 2:
            raise ValueError(f"Formato de operación inválido en la línea: {linea}")

        op1, op2 = map(str.strip, operandos)

        # Cargar operandos en registros
        reg1 = obtener_registro(op1)
        reg2 = obtener_registro(op2)

        if operacion in ['MUL', 'DIV']:
            codigo_ensamblador.append(f"MOV AX , [{op1}]")
            codigo_ensamblador.append(f"MOV BX , [{op2}]")
            codigo_ensamblador.append(f"{operacion} BX")
        else:
            codigo_ensamblador.append(f"MOV {reg1} , [{op1}]")
            codigo_ensamblador.append(f"MOV {reg2} , [{op2}]")
            codigo_ensamblador.append(f"{operacion} {reg1} , {reg2}")

        # Almacenar el resultado en la variable destino
        resultado_reg = obtener_registro(izquierda)
        codigo_ensamblador.append(f"MOV [{izquierda}] , AX")

        # Liberar registros de operandos y resultado
        liberar_registro(op1)
        liberar_registro(op2)
        liberar_registro(izquierda)

    return "\n".join(codigo_ensamblador)


def abrir_archivo():
    """Abre un cuadro de diálogo para seleccionar un archivo de entrada y muestra su contenido."""
    ruta_archivo = filedialog.askopenfilename(
        title="Seleccionar archivo de entrada",
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
    )
    if not ruta_archivo:
        return

    with open(ruta_archivo, 'r') as archivo:
        texto_entrada = archivo.read()

    caja_texto_entrada.delete(1.0, tk.END)
    caja_texto_entrada.insert(tk.END, texto_entrada)

    # Traducir a ensamblador
    try:
        codigo_ensamblador = traducir_a_ensamblador(texto_entrada)
        caja_texto_salida.delete(1.0, tk.END)
        caja_texto_salida.insert(tk.END, codigo_ensamblador)
    except Exception as e:
        caja_texto_salida.delete(1.0, tk.END)
        caja_texto_salida.insert(tk.END, f"Error: {e}")


def guardar_archivo():
    """Abre un cuadro de diálogo para guardar el código ensamblador generado."""
    ruta_archivo = filedialog.asksaveasfilename(
        title="Guardar archivo de salida",
        defaultextension=".txt",
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
    )
    if not ruta_archivo:
        return

    codigo_ensamblador = caja_texto_salida.get(1.0, tk.END).strip()
    with open(ruta_archivo, 'w') as archivo:
        archivo.write(codigo_ensamblador)


# Crear la interfaz gráfica
root = tk.Tk()
root.title("Generador de Código Ensamblador")

# Caja de texto para la entrada
etiqueta_entrada = tk.Label(root, text="Entrada (Operaciones Aritméticas):")
etiqueta_entrada.pack()
caja_texto_entrada = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, width=50)
caja_texto_entrada.pack()

# Caja de texto para la salida
etiqueta_salida = tk.Label(root, text="Salida (Código Ensamblador):")
etiqueta_salida.pack()
caja_texto_salida = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, width=50)
caja_texto_salida.pack()

# Botones
marco_botones = tk.Frame(root)
marco_botones.pack(pady=10)

boton_abrir = tk.Button(marco_botones, text="Abrir Archivo", command=abrir_archivo)
boton_abrir.pack(side=tk.LEFT, padx=10)

boton_guardar = tk.Button(marco_botones, text="Guardar Archivo", command=guardar_archivo)
boton_guardar.pack(side=tk.LEFT, padx=10)

# Ejecutar la aplicación
root.mainloop()
