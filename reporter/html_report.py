# reporter/html_report.py
# Carga la plantilla Jinja2, inyecta los datos y guarda el informe en output/

import os
import webbrowser
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

def generate_report(empresa: str, tecnologias: dict, cves: list, total_ofertas: int) -> str:
    # // Ruta de la plantilla
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("report.html")

    # // Datos a inyectar en la plantilla
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    context = {
        "empresa": empresa,
        "fecha": fecha,
        "total_ofertas": total_ofertas,
        "tecnologias": tecnologias,   # dict {nombre: menciones}
        "cves": cves,                 # lista de dicts con keys: id, severidad, score, descripcion, tecnologia
        "max_menciones": max(tecnologias.values()) if tecnologias else 1,
    }

    # // Renderizar HTML
    html_output = template.render(**context)

    # // Crear carpeta output/ si no existe
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    os.makedirs(output_dir, exist_ok=True)

    # // Nombre del archivo: empresa_YYYYMMDD.html
    nombre_archivo = f"{empresa.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.html"
    ruta_salida = os.path.join(output_dir, nombre_archivo)

    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write(html_output)

    # // Abrir en el navegador automáticamente
    webbrowser.open(f"file:///{os.path.abspath(ruta_salida)}")

    return ruta_salida