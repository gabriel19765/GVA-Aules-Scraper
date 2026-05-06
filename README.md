# 🚀 Aules Moodle Downloader

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/tu-usuario/Aules-Moodle-Downloader/graphs/commit-activity)

**Aules Moodle Downloader** es una herramienta potente y automatizada escrita en Python para descargar masivamente todos los materiales de tus cursos de la plataforma **Aules (GVA)**. Olvídate de descargar archivos uno por uno; este script organiza todo por asignaturas y carpetas automáticamente.

---

## ✨ Características Principales

*   **🔍 Detección Automática:** Obtiene la lista completa de tus asignaturas matriculadas.
*   **📂 Organización Inteligente:** Crea carpetas locales basadas en el nombre real de tus cursos.
*   **📂 Estructura por Temas:** Organiza automáticamente los archivos dentro de subcarpetas correspondientes a cada tema o sección del curso.
*   **📦 Soporte para Carpetas:** Descarga carpetas completas de Moodle como archivos ZIP de forma automática.
*   **⚡ Descarga Eficiente:** Salta archivos que ya han sido descargados basándose en el tamaño del archivo.
*   **🛡️ Robusto:** Maneja errores de conexión y nombres de archivos con caracteres especiales.

---

## 🛠️ Requisitos Previos

Antes de empezar, asegúrate de tener instalado:

1.  **Python 3.8+**
2.  La librería `requests`:
    ```bash
    pip install requests
    ```

---

## 🚀 Guía de Inicio Rápido

### 1. Obtener la Cookie de Sesión
Este script utiliza tu sesión activa para autenticarse. 
1. Abre [Aules GVA](https://aules.edu.gva.es) e inicia sesión.
2. Pulsa `F12` para abrir las herramientas de desarrollador.
3. Ve a la pestaña **Aplicación** (o Almacenamiento) -> **Cookies** -> `https://aules.edu.gva.es`.
4. Copia el valor de la cookie llamada `MoodleSession`.

### 2. Configurar el Script
Abre `moodle_scraper.py` y rellena las variables en la sección de configuración:

```python
# --- CONFIGURACIÓN ---
MOODLE_SESSION_COOKIE = "TU_VALOR_AQUÍ" 
DOWNLOAD_DIR = "/ruta/a/tu/carpeta/de/estudio"
# ---------------------
```

### 3. Ejecutar
Lanza el script desde tu terminal:

```bash
python moodle_scraper.py
```

---

## 📂 Estructura de Salida

El script generará una estructura como esta en tu directorio de descarga:

```text
DOWNLOAD_DIR/
├── Matematicas_II/
│   ├── Tema_1_Algebra.pdf
│   ├── Ejercicios_Resueltos.docx
│   └── Material_Adicional.zip
├── Sistemas_Operativos/
│   ├── Practica_1.pdf
│   └── Guia_Instalacion.pdf
└── ...
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si tienes alguna idea para mejorar el scraper o encuentras algún error, no dudes en abrir un *Issue* o enviar un *Pull Request*.

---

## ⚠️ Descargo de Responsabilidad

Este proyecto ha sido creado con fines exclusivamente educativos. El uso de este script para interactuar con plataformas institucionales debe cumplir con los términos de servicio de la Generalitat Valenciana (GVA) y la política de uso de Aules. El autor no se hace responsable del mal uso de esta herramienta.

---

<p align="center">
  Hecho con ❤️ para estudiantes que quieren ahorrar tiempo.
</p>
