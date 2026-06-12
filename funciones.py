"""
funciones.py — Lógica de datos del TPI GeoData
Programación 1 — UTN

Contiene todas las funciones de negocio:
  - Lectura/escritura de CSV
  - Búsqueda y filtrado
  - Ordenamiento (burbuja, sin lambda)
  - Estadísticas
  - Formateo de números
"""

import csv
import os


# ─────────────────────────────────────────────
#  CONSTANTES DE DOMINIO
# ─────────────────────────────────────────────

CONTINENTES = ["América", "Europa", "Asia", "África", "Oceanía"]

CAMPOS_CSV = {"nombre", "poblacion", "superficie", "continente"}


# ─────────────────────────────────────────────
#  LECTURA Y ESCRITURA CSV
# ─────────────────────────────────────────────

def cargar_csv(ruta):
    """
    Lee un archivo CSV y devuelve una lista de diccionarios.

    Valida que el archivo tenga las columnas requeridas y que cada fila
    tenga valores correctos. Las filas con errores se omiten y se
    registran en la lista de advertencias.

    Parámetros:
        ruta (str): Ruta al archivo CSV.

    Retorna:
        tuple: (lista_paises, lista_errores)
            - lista_paises es None si el archivo no se pudo abrir o no
              tiene las columnas necesarias.
            - lista_errores es un str en ese caso, o una lista (vacía o
              con advertencias) si la carga fue exitosa.
    """
    paises = []
    errores = []
    try:
        with open(ruta, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Verificar columnas requeridas
            if not CAMPOS_CSV.issubset(set(reader.fieldnames or [])):
                return None, (
                    "El CSV no tiene las columnas requeridas: "
                    "nombre, poblacion, superficie, continente"
                )
            for i, fila in enumerate(reader, start=2):
                try:
                    nombre = fila["nombre"].strip()
                    continente = fila["continente"].strip()
                    poblacion = int(fila["poblacion"].strip())
                    superficie = int(fila["superficie"].strip())
                    if not nombre or not continente:
                        errores.append(f"Fila {i}: campos vacíos, se omite.")
                        continue
                    if poblacion <= 0 or superficie <= 0:
                        errores.append(f"Fila {i}: valores numéricos inválidos, se omite.")
                        continue
                    paises.append({
                        "nombre": nombre,
                        "poblacion": poblacion,
                        "superficie": superficie,
                        "continente": continente,
                    })
                except (ValueError, KeyError):
                    errores.append(f"Fila {i}: error de formato, se omite.")
    except FileNotFoundError:
        return None, f"No se encontró el archivo: {ruta}"
    except Exception as e:
        return None, f"Error al leer el CSV: {e}"
    return paises, errores


def guardar_csv(paises, ruta):
    """
    Guarda la lista de países en un archivo CSV.

    Parámetros:
        paises (list): Lista de diccionarios con los datos de los países.
        ruta (str): Ruta de destino para el archivo CSV.
    """
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["nombre", "poblacion", "superficie", "continente"]
        )
        writer.writeheader()
        writer.writerows(paises)


def obtener_ruta_csv_default():
    """
    Devuelve la ruta absoluta al archivo paises.csv ubicado junto al script.

    Usa os.path para que funcione correctamente en cualquier sistema
    operativo, independientemente del directorio de trabajo actual.

    Retorna:
        str: Ruta absoluta al archivo paises.csv.
    """
    directorio = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(directorio, "paises.csv")


# ─────────────────────────────────────────────
#  BÚSQUEDA Y FILTRADO
# ─────────────────────────────────────────────

def buscar_paises(paises, texto):
    """
    Busca países cuyo nombre contenga el texto dado (sin distinguir
    mayúsculas ni acentos en el término de búsqueda).

    Parámetros:
        paises (list): Lista de diccionarios de países.
        texto (str): Texto a buscar (parcial o exacto).

    Retorna:
        list: Lista filtrada de países que coinciden con la búsqueda.
    """
    texto = texto.lower().strip()
    resultado = []
    for p in paises:
        if texto in p["nombre"].lower():
            resultado.append(p)
    return resultado


def filtrar_paises(paises, continente=None, pob_min=None, pob_max=None,
                   sup_min=None, sup_max=None):
    """
    Aplica filtros combinados al dataset de países.

    Todos los parámetros son opcionales. Si se omite alguno, ese filtro
    no se aplica.

    Parámetros:
        paises (list): Lista de diccionarios de países.
        continente (str | None): Filtrar por continente exacto.
            "Todos" o None desactiva el filtro.
        pob_min (int | None): Población mínima (inclusive).
        pob_max (int | None): Población máxima (inclusive).
        sup_min (int | None): Superficie mínima en km² (inclusive).
        sup_max (int | None): Superficie máxima en km² (inclusive).

    Retorna:
        list: Lista de países que cumplen todos los filtros aplicados.
    """
    resultado = paises[:]
    if continente and continente != "Todos":
        filtrado = []
        for p in resultado:
            if p["continente"] == continente:
                filtrado.append(p)
        resultado = filtrado
    if pob_min is not None:
        filtrado = []
        for p in resultado:
            if p["poblacion"] >= pob_min:
                filtrado.append(p)
        resultado = filtrado
    if pob_max is not None:
        filtrado = []
        for p in resultado:
            if p["poblacion"] <= pob_max:
                filtrado.append(p)
        resultado = filtrado
    if sup_min is not None:
        filtrado = []
        for p in resultado:
            if p["superficie"] >= sup_min:
                filtrado.append(p)
        resultado = filtrado
    if sup_max is not None:
        filtrado = []
        for p in resultado:
            if p["superficie"] <= sup_max:
                filtrado.append(p)
        resultado = filtrado
    return resultado


# ─────────────────────────────────────────────
#  ORDENAMIENTO (BURBUJA, SIN LAMBDA)
# ─────────────────────────────────────────────

def _clave_orden(pais, campo):
    """
    Devuelve el valor de comparación de un país para un campo dado.

    Para "nombre" devuelve el nombre en minúsculas (orden alfabético
    sin distinguir mayúsculas). Para los demás campos numéricos devuelve
    el valor entero directamente.

    Parámetros:
        pais (dict): Diccionario con los datos del país.
        campo (str): Campo por el que se va a ordenar
            ("nombre", "poblacion" o "superficie").

    Retorna:
        str | int: Valor de comparación para ese campo.
    """
    if campo == "nombre":
        return pais["nombre"].lower()
    return pais[campo]


def ordenar_paises(paises, campo, ascendente=True):
    """
    Ordena la lista de países por el campo indicado usando el algoritmo
    de burbuja (bubble sort).

    No utiliza la función built-in sorted() ni lambdas. La lista original
    no se modifica; se trabaja sobre una copia.

    Parámetros:
        paises (list): Lista de diccionarios de países.
        campo (str): Campo por el que ordenar ("nombre", "poblacion",
            "superficie").
        ascendente (bool): True para orden ascendente, False para
            descendente. Por defecto True.

    Retorna:
        list: Nueva lista con los países ordenados.
    """
    resultado = paises[:]
    n = len(resultado)
    for i in range(n - 1):
        for j in range(n - i - 1):
            val_a = _clave_orden(resultado[j], campo)
            val_b = _clave_orden(resultado[j + 1], campo)
            if ascendente:
                intercambiar = val_a > val_b
            else:
                intercambiar = val_a < val_b
            if intercambiar:
                resultado[j], resultado[j + 1] = resultado[j + 1], resultado[j]
    return resultado


def ordenar_items_por_cantidad(items):
    """
    Ordena una lista de tuplas (clave, cantidad) de mayor a menor
    cantidad, usando burbuja. Se usa para el ranking de continentes.

    Parámetros:
        items (list): Lista de tuplas (str, int).

    Retorna:
        list: Lista ordenada de mayor a menor por el segundo elemento.
    """
    resultado = items[:]
    n = len(resultado)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if resultado[j][1] < resultado[j + 1][1]:
                resultado[j], resultado[j + 1] = resultado[j + 1], resultado[j]
    return resultado


# ─────────────────────────────────────────────
#  ESTADÍSTICAS
# ─────────────────────────────────────────────

def _pais_mayor(paises, campo):
    """
    Devuelve el país con el valor más alto en el campo dado.
    Recorre la lista manualmente, sin usar max() con lambda.

    Parámetros:
        paises (list): Lista de diccionarios de países (no vacía).
        campo (str): Campo numérico a comparar ("poblacion" o "superficie").

    Retorna:
        dict: El país con el valor máximo en ese campo.
    """
    mayor = paises[0]
    for p in paises[1:]:
        if p[campo] > mayor[campo]:
            mayor = p
    return mayor


def _pais_menor(paises, campo):
    """
    Devuelve el país con el valor más bajo en el campo dado.
    Recorre la lista manualmente, sin usar min() con lambda.

    Parámetros:
        paises (list): Lista de diccionarios de países (no vacía).
        campo (str): Campo numérico a comparar ("poblacion" o "superficie").

    Retorna:
        dict: El país con el valor mínimo en ese campo.
    """
    menor = paises[0]
    for p in paises[1:]:
        if p[campo] < menor[campo]:
            menor = p
    return menor


def calcular_estadisticas(paises):
    """
    Calcula un conjunto de estadísticas descriptivas sobre el dataset.

    Parámetros:
        paises (list): Lista de diccionarios de países.

    Retorna:
        dict: Diccionario con las siguientes claves:
            - "total" (int): Cantidad total de países.
            - "mayor_pob" (dict): País con mayor población.
            - "menor_pob" (dict): País con menor población.
            - "mayor_sup" (dict): País con mayor superficie.
            - "menor_sup" (dict): País con menor superficie.
            - "prom_pob" (int): Promedio de población (entero).
            - "prom_sup" (int): Promedio de superficie (entero).
            - "por_continente" (dict): {continente: cantidad_países}.
        Devuelve {} si la lista está vacía.
    """
    if not paises:
        return {}

    total_pob = 0
    total_sup = 0
    conteo = {}

    for p in paises:
        total_pob += p["poblacion"]
        total_sup += p["superficie"]
        c = p["continente"]
        if c in conteo:
            conteo[c] = conteo[c] + 1
        else:
            conteo[c] = 1

    return {
        "total": len(paises),
        "mayor_pob": _pais_mayor(paises, "poblacion"),
        "menor_pob": _pais_menor(paises, "poblacion"),
        "mayor_sup": _pais_mayor(paises, "superficie"),
        "menor_sup": _pais_menor(paises, "superficie"),
        "prom_pob": total_pob // len(paises),
        "prom_sup": total_sup // len(paises),
        "por_continente": conteo,
    }


# ─────────────────────────────────────────────
#  VALIDACIONES DE PAÍS
# ─────────────────────────────────────────────

def validar_pais(nombre, pob_str, sup_str, continente):
    """
    Valida los datos ingresados para un país antes de guardarlo.

    Parámetros:
        nombre (str): Nombre del país (puede tener espacios sin recortar).
        pob_str (str): Población como string (se intenta convertir a int).
        sup_str (str): Superficie como string (se intenta convertir a int).
        continente (str): Nombre del continente.

    Retorna:
        tuple: (es_valido, mensaje_error, poblacion_int, superficie_int)
            - es_valido (bool): True si todos los datos son válidos.
            - mensaje_error (str): Descripción del error, o "" si es válido.
            - poblacion_int (int | None): Valor convertido, o None si inválido.
            - superficie_int (int | None): Valor convertido, o None si inválido.
    """
    nombre = nombre.strip()
    pob_str = pob_str.strip()
    sup_str = sup_str.strip()
    continente = continente.strip()

    if not nombre or not pob_str or not sup_str or not continente:
        return False, "Todos los campos son obligatorios.", None, None

    try:
        poblacion = int(pob_str)
        superficie = int(sup_str)
    except ValueError:
        return False, "Población y superficie deben ser números enteros.", None, None

    if poblacion <= 0 or superficie <= 0:
        return False, "Población y superficie deben ser mayores a 0.", None, None

    return True, "", poblacion, superficie


def nombre_duplicado(paises, nombre, excluir_idx=None):
    """
    Verifica si ya existe un país con el nombre dado en la lista.

    Parámetros:
        paises (list): Lista de diccionarios de países.
        nombre (str): Nombre a verificar.
        excluir_idx (int | None): Índice a ignorar en la comparación
            (útil al editar un país existente). Por defecto None.

    Retorna:
        bool: True si el nombre ya está en uso por otro país.
    """
    nombre_lower = nombre.lower()
    for i, p in enumerate(paises):
        if i == excluir_idx:
            continue
        if p["nombre"].lower() == nombre_lower:
            return True
    return False


# ─────────────────────────────────────────────
#  FORMATEO
# ─────────────────────────────────────────────

def formatear_numero(n):
    """
    Formatea un número entero con separador de miles usando puntos.

    Ejemplo: formatear_numero(1234567) → "1.234.567"

    Parámetros:
        n (int): Número a formatear.

    Retorna:
        str: Número formateado con puntos como separador de miles.
    """
    return f"{n:,}".replace(",", ".")
