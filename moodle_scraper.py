"""
Moodle Scraper - Automatización de Descargas para Aules (GVA)
------------------------------------------------------------
Este script permite descargar automáticamente todos los recursos (archivos y carpetas)
de las asignaturas en las que un usuario está matriculado en la plataforma Aules (Moodle).

Requisitos:
- Python 3.x
- Librería 'requests' (pip install requests)
- Cookie 'MoodleSession' activa (obtenida del navegador)

Uso:
1. Configura MOODLE_SESSION_COOKIE con tu cookie de sesión.
2. Configura DOWNLOAD_DIR con la ruta donde deseas guardar los archivos.
3. Ejecuta el script: python moodle_scraper.py
"""

import os
import re
import json
import requests
from typing import Optional, List, Dict, Tuple

# --- CONFIGURACIÓN ---
# Obtén esta cookie de las herramientas de desarrollador de tu navegador (F12 -> Aplicación -> Cookies)
MOODLE_SESSION_COOKIE = "1aep2vlrrsj7cshb5uo6ufs091" 

# Ruta local donde se organizarán las carpetas por asignatura
DOWNLOAD_DIR = "/media/gabi/TOSHIBA EXT/ESTUDIAR/CLASE/IABD/3_RECURSOS_Librerias_Datasets/Apuntes_Descargados"  

# URL base de la instancia de Moodle
BASE_URL = "https://aules.edu.gva.es"
# ---------------------

def get_filename_from_cd(cd: Optional[str]) -> Optional[str]:
    """
    Extrae el nombre del archivo de la cabecera 'Content-Disposition'.
    
    Args:
        cd: Valor de la cabecera Content-Disposition.
        
    Returns:
        El nombre del archivo si se encuentra, de lo contrario None.
    """
    if not cd:
        return None
    fname = re.findall('filename="?([^"]+)"?', cd)
    return fname[0] if fname else None

def main():
    """
    Flujo principal del scraper:
    1. Autentica usando la cookie de sesión.
    2. Obtiene la 'sesskey' necesaria para llamadas AJAX.
    3. Lista todas las asignaturas matriculadas.
    4. Itera por cada asignatura, busca recursos descargables y los guarda localmente.
    """
    print("🚀 Iniciando Moodle API Scraper Automático...")
    
    if not MOODLE_SESSION_COOKIE or not DOWNLOAD_DIR:
        print("❌ ERROR: Debes configurar MOODLE_SESSION_COOKIE y DOWNLOAD_DIR en el script.")
        return

    # Configuración de la sesión de requests
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/json"
    })
    session.cookies.set("MoodleSession", MOODLE_SESSION_COOKIE, domain="aules.edu.gva.es")

    # 1. Obtener Sesskey (Token de seguridad de Moodle)
    print("🔑 Conectando y obteniendo tokens de seguridad...")
    try:
        resp = session.get(f"{BASE_URL}/fp/my/")
        sesskey_match = re.search(r"\"sesskey\":\"([^\"]+)\"", resp.text)
        
        if not sesskey_match:
            print("❌ ERROR: Sesión caducada o MoodleSession inválida. Por favor, actualiza la cookie.")
            return
            
        sesskey = sesskey_match.group(1)
        print("✅ Autenticación exitosa.")
    except Exception as e:
        print(f"❌ ERROR de conexión: {e}")
        return

    # 2. Obtener Lista de Asignaturas vía API
    print("📚 Buscando asignaturas...")
    ajax_url = f"{BASE_URL}/fp/lib/ajax/service.php?sesskey={sesskey}"
    payload_courses = [{
        "index": 0,
        "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
        "args": {"offset": 0, "limit": 0, "classification": "all", "sort": "fullname"}
    }]
    
    courses: List[Dict] = []
    try:
        api_resp = session.post(f"{ajax_url}&info=core_course_get_enrolled_courses", json=payload_courses)
        if api_resp.status_code == 200:
            data = api_resp.json()
            if isinstance(data, list) and not data[0].get("error"):
                courses_data = data[0].get("data", {}).get("courses", [])
                for c in courses_data:
                    courses.append({
                        "id": c.get("id"),
                        "name": c.get("fullname")
                    })
    except Exception as e:
        print(f"❌ Error al obtener asignaturas: {e}")

    if not courses:
        print("⚠️ No tienes asignaturas matriculadas o la API está bloqueada.")
        return
        
    print(f"🎓 ¡Detectadas {len(courses)} asignaturas oficiales!")

    # 3. Procesar cada Asignatura
    for course in courses:
        print(f"\n📂 Explorando asignatura: {course['name']}")
        
        # Limpiar el nombre de la carpeta para evitar caracteres ilegales
        safe_name = re.sub(r'[^a-zA-Z0-9_\- ]', '', course['name']).strip().replace(" ", "_")
        course_dir = os.path.join(DOWNLOAD_DIR, safe_name)
        os.makedirs(course_dir, exist_ok=True)
        
        # Consultar la estructura interna de la asignatura (recursos y módulos)
        payload_content = [{
            "index": 0,
            "methodname": "core_courseformat_get_state",
            "args": {"courseid": course['id']}
        }]
        
        try:
            content_resp = session.post(f"{ajax_url}&info=core_courseformat_get_state", json=payload_content)
            if content_resp.status_code != 200:
                continue
                
            content_data = content_resp.json()
            if not isinstance(content_data, list) or content_data[0].get("error"):
                print("   ⚠️ Acceso denegado o curso vacío.")
                continue
                
            # 1. Obtener el mapeo de secciones (Temas)
            state_str = content_data[0].get("data", "{}")
            state_json = json.loads(state_str)
            
            # Mapear IDs de sección a sus nombres reales
            sections_map: Dict[int, str] = {}
            for sec in state_json.get("section", []):
                sec_id = sec.get("id")
                sec_name = sec.get("name") or sec.get("title")
                
                # Si no tiene nombre, tratar de inferirlo o usar un genérico
                if not sec_name:
                    sec_num = sec.get("section", 0)
                    sec_name = f"Tema_{sec_num}" if sec_num > 0 else "General"
                
                # Limpiar nombre de sección para sistema de archivos
                clean_sec_name = re.sub(r'[^a-zA-Z0-9_\- ]', '', sec_name).strip().replace(" ", "_")
                sections_map[sec_id] = clean_sec_name

            # 2. Organizar recursos por sección
            # Guardamos como: (nombre_archivo, url_descarga, carpeta_destino)
            resources: List[Tuple[str, str, str]] = []
            
            for cm in state_json.get("cm", []):
                mod_type = cm.get("module", cm.get("modname", ""))
                
                # Filtramos recursos descargables (archivos y carpetas)
                if mod_type in ["resource", "folder", "Fitxer", "Carpeta"]:
                    url = cm.get("url")
                    name = cm.get("name", "Documento_Sin_Nombre")
                    section_id = cm.get("sectionid")
                    
                    if url:
                        # Determinar carpeta de destino basada en la sección
                        dest_folder = sections_map.get(section_id, "General")
                        
                        # Si es una carpeta de Moodle, descargar como ZIP
                        if "folder" in mod_type or "mod/folder/view.php" in url:
                            url = url.replace("view.php", "download_folder.php")
                            if not name.endswith(".zip"):
                                name = f"{name}.zip"
                        
                        resources.append((name, url, dest_folder))
                        
            print(f"   🔍 Encontrados {len(resources)} documentos organizados en {len(sections_map)} secciones.")
            
            # 3. Descargar cada documento en su carpeta correspondiente
            for res_name, res_url, res_folder in resources:
                # Limpiar el nombre visual del recurso
                res_name_clean = re.sub(r'(Archivo|Documento PDF|Fitxer|Document).*', '', res_name).strip()
                
                # Crear la subcarpeta del tema
                target_dir = os.path.join(course_dir, res_folder)
                os.makedirs(target_dir, exist_ok=True)
                
                print(f"   ⬇️  [{res_folder}] Descargando: {res_name_clean}...")
                
                try:
                    dl_resp = session.get(res_url, stream=True, allow_redirects=True)
                    cd = dl_resp.headers.get('content-disposition')
                    filename = get_filename_from_cd(cd)
                    
                    if not filename:
                        ext = ".zip" if "download_folder" in res_url else ".pdf"
                        filename = f"{res_name_clean.replace(' ', '_')}{ext}"
                        
                    filepath = os.path.join(target_dir, filename)
                    
                    if os.path.exists(filepath):
                        local_size = os.path.getsize(filepath)
                        remote_size = int(dl_resp.headers.get('content-length', 0))
                        if local_size == remote_size and local_size > 0:
                            print(f"      ⏭️  Ya existe, saltando.")
                            continue

                    with open(filepath, 'wb') as f:
                        for chunk in dl_resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"      ✅ Guardado en {res_folder}")
                    
                except Exception as e:
                    print(f"      ❌ Error al descargar {res_name_clean}: {e}")

                    
        except Exception as e:
            print(f"   ❌ Error parseando la estructura del curso: {e}")

    print("\n✨ ¡PROCESO COMPLETADO! Todos los archivos han sido organizados.")

if __name__ == "__main__":
    main()

