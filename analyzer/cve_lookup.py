# analyzer/cve_lookup.py

import nvdlib
import os
import time
from dotenv import load_dotenv
from colorama import Fore, Style

load_dotenv()


class CVELookup:
    """
    Para cada tecnología detectada, consulta la NVD (National Vulnerability Database)
    y devuelve las CVEs más relevantes ordenadas por severidad.
    """

    # Score CVSS mínimo para incluir una CVE en el informe
    SCORE_MINIMO = 7.0

    # Máximo de CVEs a recuperar por tecnología
    MAX_CVE_POR_TECH = 5

    def __init__(self):
        self.api_key = os.getenv("NVD_API_KEY") or None
        self._mostrar_estado_api()

    # ------------------------------------------------------------------
    # COMPATIBILIDAD CON MAIN (FIX DEL ERROR)
    # ------------------------------------------------------------------

    def lookup(self, tecnologias: dict) -> list[dict]:
        """
        Alias para mantener compatibilidad con código existente (main.py).
        """
        return self.buscar(tecnologias)

    # ------------------------------------------------------------------
    # ESTADO DE LA API
    # ------------------------------------------------------------------

    def _mostrar_estado_api(self):
        """Informa si se usará API key o modo sin autenticación."""
        if self.api_key:
            print(f"{Fore.GREEN}[CVE]{Style.RESET_ALL} API Key de NVD cargada. Modo rápido (0.6s entre peticiones).")
        else:
            print(f"{Fore.YELLOW}[CVE] Sin API Key. Modo lento (6s entre peticiones).{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[CVE] Obtén tu key gratis en: nvd.nist.gov/developers/request-an-api-key{Style.RESET_ALL}")

    # ------------------------------------------------------------------
    # MÉTODO PRINCIPAL
    # ------------------------------------------------------------------

    def buscar(self, tecnologias: dict) -> list[dict]:
        """
        Recibe el diccionario de tecnologías detectadas y devuelve
        una lista de CVEs ordenadas por score CVSS descendente.
        """
        if not tecnologias:
            print(f"{Fore.YELLOW}[CVE] No hay tecnologías para consultar.{Style.RESET_ALL}")
            return []

        print(f"{Fore.CYAN}[CVE]{Style.RESET_ALL} Consultando NVD para {len(tecnologias)} tecnologías...\n")

        todas_cves = []

        for tech in tecnologias.keys():
            cves = self._buscar_cves_de_tech(tech)
            todas_cves.extend(cves)
            time.sleep(0.5)

        # Ordenar por score descendente
        todas_cves.sort(key=lambda x: x["score"], reverse=True)

        self._mostrar_resumen(todas_cves)
        return todas_cves

    # ------------------------------------------------------------------
    # BÚSQUEDA DE CVEs POR TECNOLOGÍA
    # ------------------------------------------------------------------

    def _buscar_cves_de_tech(self, tech: str) -> list[dict]:
        print(f"  {Fore.CYAN}→{Style.RESET_ALL} Buscando CVEs para: {tech}")

        try:
            resultados = nvdlib.searchCVE(
                keywordSearch=tech,
                limit=self.MAX_CVE_POR_TECH,
                key=self.api_key,
                delay=None
            )
        except Exception as e:
            print(f"{Fore.RED}  [!] Error consultando NVD para '{tech}': {e}{Style.RESET_ALL}")
            return []

        cves_filtradas = []

        for cve in resultados:
            score, severidad = self._extraer_score(cve)

            if score < self.SCORE_MINIMO:
                continue

            cves_filtradas.append({
                "id": cve.id,
                "tecnologia": tech,
                "severidad": severidad,
                "score": score,
                "descripcion": self._extraer_descripcion(cve),
            })

        print(f"    {Fore.GREEN}✓{Style.RESET_ALL} {len(cves_filtradas)} CVEs relevantes encontradas")
        return cves_filtradas

    # ------------------------------------------------------------------
    # HELPERS
    # ------------------------------------------------------------------

    def _extraer_score(self, cve) -> tuple[float, str]:
        try:
            metricas = getattr(cve, "metrics", None)

            if metricas:
                v31 = getattr(metricas, "cvssMetricV31", None)
                v30 = getattr(metricas, "cvssMetricV30", None)

                if v31:
                    datos = v31[0].cvssData
                    return round(datos.baseScore, 1), datos.baseSeverity

                if v30:
                    datos = v30[0].cvssData
                    return round(datos.baseScore, 1), datos.baseSeverity

                v2 = getattr(metricas, "cvssMetricV2", None)
                if v2:
                    datos = v2[0].cvssData
                    return round(datos.baseScore, 1), "LEGACY"

        except Exception:
            pass

        return 0.0, "UNKNOWN"

    def _extraer_descripcion(self, cve) -> str:
        try:
            for desc in getattr(cve, "descriptions", []):
                if desc.lang == "en":
                    texto = desc.value
                    return texto[:200] + "..." if len(texto) > 200 else texto
        except Exception:
            pass

        return "No description available."

    # ------------------------------------------------------------------
    # OUTPUT
    # ------------------------------------------------------------------

    def _mostrar_resumen(self, cves: list[dict]):
        if not cves:
            print(f"{Fore.YELLOW}[CVE] No se encontraron CVEs relevantes (score >= {self.SCORE_MINIMO}).{Style.RESET_ALL}")
            return

        COLOR_SEVERIDAD = {
            "CRITICAL": Fore.RED,
            "HIGH":     Fore.LIGHTYELLOW_EX,
            "MEDIUM":   Fore.YELLOW,
            "LEGACY":   Fore.WHITE,
            "UNKNOWN":  Fore.WHITE,
        }

        print(f"\n{Fore.GREEN}{'─' * 70}")
        print(f"  CVEs ENCONTRADAS ({len(cves)} resultados)")
        print(f"{'─' * 70}{Style.RESET_ALL}")

        for cve in cves:
            color = COLOR_SEVERIDAD.get(cve["severidad"], Fore.WHITE)
            print(
                f"  {color}[{cve['severidad']:<8} {cve['score']}]{Style.RESET_ALL} "
                f"{cve['id']} — {cve['tecnologia']}\n"
                f"    {cve['descripcion'][:100]}..."
            )

        print(f"{Fore.GREEN}{'─' * 70}{Style.RESET_ALL}\n")