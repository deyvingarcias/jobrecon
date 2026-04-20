"""
analyzer/cve_lookup.py
Consulta NVD para cada tecnología detectada.
Filtrado por año (2015+), CVSS >= 7.0, deduplicación y scoring de riesgo propio.
"""

import os
import time
from datetime import datetime
import nvdlib
from dotenv import load_dotenv

load_dotenv()

# Año mínimo de publicación de CVE. CVEs más antiguas son legacy noise.
CVE_MIN_YEAR = 2015
# Score CVSS mínimo para incluir una CVE
CVE_MIN_SCORE = 7.0

# Mapa de normalización: keyword usado en búsqueda NVD por tecnología
# Evita buscar "AWS" directamente (falsos positivos brutales).
TECH_QUERY_MAP = {
    "AWS":              "Amazon Web Services",
    "Azure":            "Microsoft Azure",
    "GCP":              "Google Cloud Platform",
    "Active Directory": "Microsoft Active Directory",
    "Python":           "Python interpreter CPython",
    "Java":             "Oracle Java JDK",
    "Node":             "Node.js",
    "Node.js":          "Node.js",
    "Docker":           "Docker container",
    "Kubernetes":       "Kubernetes",
    "VMware":           "VMware ESXi",
    "Hyper-V":          "Microsoft Hyper-V",
    "Windows Server":   "Microsoft Windows Server",
    "Linux":            "Linux Kernel",
    "Ubuntu":           "Ubuntu",
    "Debian":           "Debian",
    "Apache":           "Apache HTTP Server",
    "Nginx":            "Nginx",
    "IIS":              "Microsoft IIS",
    "MySQL":            "MySQL",
    "PostgreSQL":       "PostgreSQL",
    "MongoDB":          "MongoDB",
    "Redis":            "Redis",
    "SAP":              "SAP NetWeaver",
    "S/4HANA":          "SAP S/4HANA",
    "Fortinet":         "Fortinet FortiOS",
    "Cisco":            "Cisco IOS",
    "Palo Alto":        "Palo Alto PAN-OS",
    "Exchange":         "Microsoft Exchange Server",
    "SharePoint":       "Microsoft SharePoint",
    "Office 365":       "Microsoft Office 365",
    "Outlook":          "Microsoft Outlook",
    "Teams":            "Microsoft Teams",
    "Jenkins":          "Jenkins",
    "GitLab":           "GitLab",
    "GitHub":           "GitHub Enterprise",
    "Ansible":          "Ansible",
    "Terraform":        "HashiCorp Terraform",
    "Elasticsearch":    "Elasticsearch",
    "Splunk":           "Splunk",
    "Nagios":           "Nagios",
    "Zabbix":           "Zabbix",
    "WordPress":        "WordPress",
    "Drupal":           "Drupal",
    "Joomla":           "Joomla",
    "PHP":              "PHP",
    "Ruby":             "Ruby on Rails",
    "Spring":           "Spring Framework",
    "Tomcat":           "Apache Tomcat",
    "JBoss":            "JBoss EAP",
    "WebLogic":         "Oracle WebLogic",
    "WebSphere":        "IBM WebSphere",
}


def _year_weight(published_date) -> float:
    """
    Devuelve un peso basado en la antigüedad del CVE.
    CVE de este año = 1.0, hace 5 años = 0.5, hace 10 años = 0.0
    """
    try:
        if isinstance(published_date, str):
            year = int(published_date[:4])
        elif hasattr(published_date, "year"):
            year = published_date.year
        else:
            year = 2015
        current_year = datetime.now().year
        age = current_year - year
        # Escala lineal: 0 años = 1.0, 10+ años = 0.0
        return max(0.0, 1.0 - (age / 10.0))
    except Exception:
        return 0.5


def _risk_score(cvss: float, published_date) -> float:
    """
    Score de riesgo propio: combina CVSS y recencia.
    risk_score = cvss * 0.7 + year_weight * 10 * 0.3
    Resultado en escala 0-10.
    """
    yw = _year_weight(published_date)
    return round(cvss * 0.7 + yw * 10 * 0.3, 2)


def _get_cvss_and_severity(cve) -> tuple[float, str]:
    """
    Extrae score CVSS y severidad de un objeto nvdlib CVE.
    Intenta CVSSv3 primero, luego CVSSv2.
    """
    try:
        # CVSSv3
        if hasattr(cve, "v31score") and cve.v31score:
            return float(cve.v31score), str(getattr(cve, "v31severity", "UNKNOWN"))
        if hasattr(cve, "v30score") and cve.v30score:
            return float(cve.v30score), str(getattr(cve, "v30severity", "UNKNOWN"))
        # CVSSv2 fallback
        if hasattr(cve, "v2score") and cve.v2score:
            return float(cve.v2score), str(getattr(cve, "v2severity", "LEGACY"))
    except Exception:
        pass
    return 0.0, "UNKNOWN"


class CVELookup:
    """
    Consulta la NVD para cada tecnología detectada.
    Aplica normalización de keywords, filtrado por año y scoring propio.
    """

    def __init__(self):
        self.api_key = os.getenv("NVD_API_KEY")
        if self.api_key:
            print("[CVE] API Key de NVD cargada. Modo rápido (0.6s entre peticiones).")
            self.delay = 0.6
        else:
            print("[CVE] Sin API Key. Modo lento (6s entre peticiones).")
            self.delay = 6.0

    def _normalizar_query(self, tech: str) -> str:
        """
        Convierte el nombre de la tecnología en una query NVD más precisa.
        """
        return TECH_QUERY_MAP.get(tech, tech)

    def _buscar_cves_para_tech(self, tech: str) -> list[dict]:
        """
        Busca CVEs en NVD para una tecnología.
        Devuelve lista de dicts con campos normalizados.
        """
        query = self._normalizar_query(tech)
        resultados = []
        seen_ids = set()

        try:
            cves = nvdlib.searchCVE(
                keywordSearch=query,
                key=self.api_key,
                delay=self.delay,
                limit=20,  # Traemos 20 y filtramos
            )

            for cve in cves:
                cve_id = getattr(cve, "id", None) or getattr(cve, "cveId", "UNKNOWN")

                # Deduplicar
                if cve_id in seen_ids:
                    continue
                seen_ids.add(cve_id)

                # Score y severidad
                score, severity = _get_cvss_and_severity(cve)

                # Filtrar por score mínimo
                if score < CVE_MIN_SCORE:
                    continue

                # Año de publicación
                published_raw = getattr(cve, "published", None)
                try:
                    if isinstance(published_raw, str):
                        year = int(published_raw[:4])
                    elif hasattr(published_raw, "year"):
                        year = published_raw.year
                    else:
                        year = 0
                except Exception:
                    year = 0

                # Filtrar por año mínimo
                if year and year < CVE_MIN_YEAR:
                    continue

                # Descripción
                descripcion = "Sin descripción disponible."
                try:
                    if hasattr(cve, "descriptions") and cve.descriptions:
                        for d in cve.descriptions:
                            if getattr(d, "lang", "") == "en":
                                descripcion = d.value
                                break
                except Exception:
                    pass

                rs = _risk_score(score, published_raw)

                resultados.append({
                    "id": cve_id,
                    "tech": tech,
                    "score": score,
                    "severity": severity,
                    "year": year,
                    "risk_score": rs,
                    "description": descripcion[:300],
                })

        except Exception as e:
            print(f"    [!] Error consultando NVD para '{tech}': {e}")

        # Ordenar por risk_score descendente, tomar top 5 por tecnología
        resultados.sort(key=lambda x: x["risk_score"], reverse=True)
        return resultados[:5]

    def buscar(self, tecnologias: dict) -> list[dict]:
        """
        Recibe dict {tech: menciones} y devuelve lista de CVEs ordenadas por risk_score.
        """
        if not tecnologias:
            return []

        print(f"[CVE] Consultando NVD para {len(tecnologias)} tecnologías...")
        todas_cves = []

        for tech in tecnologias:
            print(f"  → Buscando CVEs para: {tech}")
            cves = self._buscar_cves_para_tech(tech)
            todas_cves.extend(cves)
            print(f"    ✓ {len(cves)} CVEs relevantes encontradas")

        # Deduplicar a nivel global por CVE ID
        seen = set()
        unicas = []
        for cve in todas_cves:
            if cve["id"] not in seen:
                seen.add(cve["id"])
                unicas.append(cve)

        # Ordenar por risk_score descendente
        unicas.sort(key=lambda x: x["risk_score"], reverse=True)

        return unicas

    # Alias para compatibilidad con main.py
    def lookup(self, tecnologias: dict) -> list[dict]:
        return self.buscar(tecnologias)