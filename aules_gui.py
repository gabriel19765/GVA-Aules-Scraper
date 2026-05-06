import os
import re
import json
import requests
import threading
import urllib.parse
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional, List, Dict, Tuple

# --- CONFIGURACIÓN DE AULES ---
AULES_FLAVORS = {
    "FP Presencial": "https://aules.edu.gva.es/fp",
    "ESO": "https://aules.edu.gva.es/eso",
    "Batxillerat": "https://aules.edu.gva.es/batxillerat",
    "Infantil": "https://aules.edu.gva.es/infantil",
    "Primària": "https://aules.edu.gva.es/primaria",
    "Semipresencial": "https://aules.edu.gva.es/semipresencial",
    "FPA (Adultos)": "https://aules.edu.gva.es/fpa",
    "CEED (Distancia)": "https://aules.edu.gva.es/ed",
    "Especials": "https://aules.edu.gva.es/especials",
    "ISEACV": "https://aules.edu.gva.es/iseacv",
    "Formació Professorat": "https://aules.edu.gva.es/formaciodelprofessorat",
    "Autoformació": "https://aules.edu.gva.es/autoformacio",
    "Docent": "https://aules.edu.gva.es/docent"
}

def sanitize_name(name: str) -> str:
    """Limpia nombres de archivos y carpetas preservando acentos y ñ."""
    # Eliminar caracteres prohibidos en sistemas de archivos (Windows/Linux)
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Reemplazar espacios múltiples por uno solo y quitar espacios al inicio/final
    return " ".join(name.split()).strip()

class AulesDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Aules Moodle Downloader Pro")
        self.root.geometry("700x600")
        self.root.configure(bg="#1e1e1e")
        
        # Estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.setup_styles()
        
        # Variables
        self.cookie_var = tk.StringVar()
        self.dir_var = tk.StringVar(value=os.getcwd())
        self.flavor_var = tk.StringVar(value="FP Presencial")
        self.is_running = False
        
        self.create_widgets()

    def setup_styles(self):
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#4a9eff")
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"))
        self.style.configure("Action.TButton", background="#4a9eff", foreground="white")
        self.style.map("Action.TButton", background=[('active', '#357abd')])

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        header = ttk.Label(main_frame, text="🚀 Aules Moodle Downloader", style="Header.TLabel")
        header.pack(pady=(0, 20))

        # Configuración
        config_lf = tk.LabelFrame(main_frame, text=" Configuración de Acceso ", bg="#1e1e1e", fg="#4a9eff", font=("Segoe UI", 10, "bold"), padx=15, pady=15)
        config_lf.pack(fill=tk.X, pady=10)

        # Modalidad (Flavor)
        ttk.Label(config_lf, text="Modalidad de Aules:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.flavor_menu = ttk.Combobox(config_lf, textvariable=self.flavor_var, values=list(AULES_FLAVORS.keys()), state="readonly", width=40)
        self.flavor_menu.grid(row=0, column=1, columnspan=2, pady=5, sticky=tk.W)

        # Cookie
        ttk.Label(config_lf, text="Cookie MoodleSession:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(config_lf, textvariable=self.cookie_var, width=43, show="*").grid(row=1, column=1, pady=5, sticky=tk.W)

        # Directorio
        ttk.Label(config_lf, text="Carpeta de Descarga:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(config_lf, textvariable=self.dir_var, width=32).grid(row=2, column=1, pady=5, sticky=tk.W)
        ttk.Button(config_lf, text="Buscar...", command=self.browse_dir).grid(row=2, column=2, padx=5)

        # Consola de salida
        self.log_area = tk.Text(main_frame, height=12, bg="#000000", fg="#00ff00", font=("Consolas", 9), padx=10, pady=10)
        self.log_area.pack(fill=tk.BOTH, expand=True, pady=15)
        self.log_area.insert(tk.END, "Esperando configuración...\n")
        self.log_area.config(state=tk.DISABLED)

        # Botón de inicio
        self.btn_run = ttk.Button(main_frame, text="INICIAR DESCARGA", style="Action.TButton", command=self.start_thread)
        self.btn_run.pack(pady=10, ipady=5, fill=tk.X)

    def browse_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_var.set(directory)

    def log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, f"{message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def start_thread(self):
        if not self.cookie_var.get() or not self.dir_var.get():
            messagebox.showwarning("Faltan datos", "Por favor, introduce la cookie y selecciona una carpeta.")
            return
            
        if self.is_running:
            return
            
        self.is_running = True
        self.btn_run.config(state=tk.DISABLED)
        threading.Thread(target=self.run_scraper, daemon=True).start()

    def run_scraper(self):
        cookie = self.cookie_var.get()
        download_dir = self.dir_var.get()
        base_url = AULES_FLAVORS[self.flavor_var.get()]
        domain = base_url.replace("https://", "").split("/")[0]

        self.log(f"--- INICIANDO SCRAPER EN {self.flavor_var.get()} ---")
        
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)",
            "Accept": "application/json, text/javascript, */*; q=0.01"
        })
        session.cookies.set("MoodleSession", cookie, domain=domain)

        try:
            # 1. Obtener Sesskey
            self.log("🔑 Verificando sesión...")
            resp = session.get(f"{base_url}/my/")
            sesskey_match = re.search(r"\"sesskey\":\"([^\"]+)\"", resp.text)
            
            if not sesskey_match:
                self.log("❌ ERROR: Sesión inválida. Revisa la cookie.")
                self.finish()
                return
                
            sesskey = sesskey_match.group(1)
            ajax_url = f"{base_url}/lib/ajax/service.php?sesskey={sesskey}"

            # 2. Obtener Asignaturas
            self.log("📚 Buscando tus asignaturas...")
            payload_courses = [{
                "index": 0,
                "methodname": "core_course_get_enrolled_courses_by_timeline_classification",
                "args": {"offset": 0, "limit": 0, "classification": "all", "sort": "fullname"}
            }]
            
            api_resp = session.post(f"{ajax_url}&info=core_course_get_enrolled_courses", json=payload_courses)
            courses = []
            if api_resp.status_code == 200:
                data = api_resp.json()
                courses_data = data[0].get("data", {}).get("courses", [])
                for c in courses_data:
                    courses.append({"id": c.get("id"), "name": c.get("fullname")})

            if not courses:
                self.log("⚠️ No se encontraron asignaturas.")
                self.finish()
                return

            self.log(f"✅ ¡{len(courses)} asignaturas detectadas!")

            # 3. Procesar Cursos
            for course in courses:
                self.log(f"\n📂 Procesando: {course['name']}")
                safe_name = sanitize_name(course['name'])
                course_dir = os.path.join(download_dir, safe_name)
                os.makedirs(course_dir, exist_ok=True)

                payload_content = [{
                    "index": 0,
                    "methodname": "core_courseformat_get_state",
                    "args": {"courseid": course['id']}
                }]
                
                content_resp = session.post(f"{ajax_url}&info=core_courseformat_get_state", json=payload_content)
                if content_resp.status_code != 200: continue
                
                content_data = content_resp.json()
                state_json = json.loads(content_data[0].get("data", "{}"))
                
                # Mapeo de secciones
                sections_map = {}
                for sec in state_json.get("section", []):
                    sec_name = sec.get("name") or sec.get("title") or f"Tema_{sec.get('section', 0)}"
                    sections_map[sec.get("id")] = sanitize_name(sec_name)

                # Recursos
                for cm in state_json.get("cm", []):
                    mod_type = cm.get("module", cm.get("modname", ""))
                    if mod_type in ["resource", "folder", "Fitxer", "Carpeta"]:
                        url = cm.get("url")
                        name = cm.get("name", "Archivo")
                        section_name = sections_map.get(cm.get("sectionid"), "General")
                        
                        if url:
                            if "folder" in mod_type:
                                url = url.replace("view.php", "download_folder.php")
                                if not name.endswith(".zip"): name += ".zip"
                            
                            self.download_file(session, url, name, os.path.join(course_dir, section_name))

            self.log("\n✨ ¡PROCESO COMPLETADO AL 100%!")
            messagebox.showinfo("Éxito", "Descarga completada con éxito.")
            
        except Exception as e:
            self.log(f"❌ ERROR CRÍTICO: {e}")
        finally:
            self.finish()

    def download_file(self, session, url, name, folder):
        try:
            os.makedirs(folder, exist_ok=True)
            # Limpiar rastro de Moodle del nombre visual
            clean_name = re.sub(r'(Archivo|Documento PDF|Fitxer|Document|Fitxer PDF).*', '', name).strip()
            
            resp = session.get(url, stream=True)
            cd = resp.headers.get('content-disposition')
            filename = self.get_filename(cd)
            
            # Si no hay nombre en cabecera, fabricar uno
            if not filename:
                ext = ".zip" if "download_folder" in url else ".pdf"
                filename = f"{sanitize_name(clean_name)}{ext}"
            
            filepath = os.path.join(folder, filename)
            
            # Evitar descargar si ya existe
            if os.path.exists(filepath):
                remote_size = int(resp.headers.get('content-length', 0))
                if os.path.getsize(filepath) == remote_size and remote_size > 0:
                    return

            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(8192): f.write(chunk)
            self.log(f"   ✅ {filename}")
        except Exception as e:
            self.log(f"   ❌ Fallo en: {name} ({e})")

    def get_filename(self, cd):
        if not cd: return None
        
        # Intentar RFC 6266 (filename*) primero
        fn_star = re.findall(r"filename\*=([^;']+)'[^']*'([^;]+)", cd)
        if fn_star:
            encoding, name = fn_star[0]
            return urllib.parse.unquote(name, encoding=encoding)
            
        # Intentar filename normal
        fname = re.findall(r'filename="?([^"]+)"?', cd)
        if fname:
            return urllib.parse.unquote(fname[0])
            
        return None

    def finish(self):
        self.is_running = False
        self.btn_run.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = AulesDownloaderGUI(root)
    root.mainloop()
