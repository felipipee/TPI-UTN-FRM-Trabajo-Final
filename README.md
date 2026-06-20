# 🌍 GeoData — Gestión de Países

**Trabajo Práctico Integrador · Programación 1 · UTN**

Aplicación de escritorio en Python para gestionar información de países: agregar, editar, eliminar, buscar, filtrar, ordenar y visualizar estadísticas sobre un dataset en CSV.

---

Hecho entre los integrantes del proyecto en conjunto

---

## Requisitos

- Python 3.10 o superior
- `customtkinter` (única dependencia externa)

```bash
pip install customtkinter
```

> tkinter viene incluido con Python en Windows y macOS.  
> En Linux: `sudo apt install python3-tk`

---

## Cómo ejecutar

```bash
python main.py
```

El archivo `paises.csv` debe estar en la **misma carpeta** que `main.py` y `funciones.py`.

---

## Estructura del proyecto

```
tpi_paises/
├── main.py           # Interfaz gráfica (UI)
├── funciones.py      # Lógica de datos (funciones puras)
├── paises.csv        # Dataset base
└── README.md         # Este archivo
```

### Separación de responsabilidades

| Archivo | Contenido |
|---------|-----------|
| `main.py` | Ventanas, widgets, eventos, navegación |
| `funciones.py` | CSV, búsqueda, filtros, ordenamiento (burbuja), estadísticas, validaciones |

---

## Funcionalidades

| Función | Descripción |
|---------|-------------|
| **Agregar** | Formulario con validación de campos vacíos, tipos y duplicados |
| **Editar** | Doble clic o clic derecho → editar población y superficie (y nombre) |
| **Eliminar** | Clic derecho → eliminar con confirmación |
| **Buscar** | Barra de búsqueda en tiempo real, coincidencia parcial o exacta |
| **Filtrar por continente** | Chips de selección rápida en la barra de filtros |
| **Filtrar por rangos** | Ventana de filtros con rango de población y superficie |
| **Ordenar** | Por nombre, población o superficie (↑ / ↓), también haciendo clic en encabezados de columna |
| **Estadísticas** | Mayor/menor población y superficie, promedios, países por continente |
| **Importar CSV** | Carga cualquier CSV compatible con el formato requerido |
| **Exportar CSV** | Guarda el dataset actual (con cambios) a un archivo CSV |

---

## Formato del CSV

```
nombre,poblacion,superficie,continente
Argentina,45376763,2780400,América
Japón,125800000,377975,Asia
Brasil,213993437,8515767,América
Alemania,83149300,357022,Europa
```

**Columnas requeridas:** `nombre`, `poblacion`, `superficie`, `continente`  
Las filas con formato inválido se omiten con advertencia, sin interrumpir la carga.

---

## Ejemplos de uso

### Buscar un país
1. Escribir en la barra de búsqueda (ej: `"bra"` encuentra `"Brasil"`)
2. La tabla se actualiza en tiempo real

### Filtrar por continente y rango de población
1. Hacer clic en el chip `"América"`
2. Hacer clic en `"⚙ Rangos"` → ingresar `pob_min = 50000000`
3. La tabla muestra solo países americanos con más de 50 millones de habitantes

### Agregar un país
1. Botón `"+ Agregar país"` en la barra superior
2. Completar todos los campos → `"Guardar"`
3. El país se agrega al dataset y se guarda automáticamente en el CSV

### Ordenar la tabla
- Hacer clic en el encabezado `"Nombre ⇅"`, `"Población ⇅"` o `"Superficie km² ⇅"`
- Segundo clic en el mismo encabezado invierte el orden
- También disponible desde el menú lateral `"↕ Ordenar"`

---

## Criterios de validación

- Ningún campo puede estar vacío
- Población y superficie deben ser enteros mayores a 0
- No se permiten nombres de país duplicados (sin distinguir mayúsculas)
- El CSV debe contener exactamente las cuatro columnas requeridas

---

## Links

- 📁 Repositorio GitHub: `[URL del repositorio]`
- 🎥 Video demostración: `https://youtu.be/emF1itbxroM`
- 📄 Documentación PDF: `https://github.com/felipipee/TPI-UTN-FRM-Trabajo-Final/blob/main/GeoData%20-%20Documentaci%C3%B3n%20TPI%20Programaci%C3%B3n%201%20UTN.docx`
