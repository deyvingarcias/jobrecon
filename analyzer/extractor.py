# analyzer/extractor.py

import json
import re
from pathlib import Path

from colorama import Fore, Style


class TechExtractor:
    """
    Analiza el texto de las ofertas de trabajo y detecta
    qué tecnologías menciona, cruzándolas con tech_keywords.json.
    """

    KEYWORDS_PATH = Path("config/tech_keywords.json")

    def __init__(self):
        self.keywords = self._cargar_keywords()

    # ------------------------------------------------------------------
    # CARGA DEL DICCIONARIO
    # ------------------------------------------------------------------

    def _cargar_keywords(self) -> dict:
        """
        Carga el diccionario de tecnologías desde tech_keywords.json.
        Estructura esperada: { "categoria": ["tech1", "tech2", ...], ... }
        """
        try:
            with open(self.KEYWORDS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"{Fore.RED}[!] No se encontró {self.KEYWORDS_PATH}{Style.RESET_ALL}")
            return {}
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}[!] Error al leer tech_keywords.json: {e}{Style.RESET_ALL}")
            return {}

    # ------------------------------------------------------------------
    # MÉTODO PRINCIPAL
    # ------------------------------------------------------------------

    def extract(self, ofertas: list[str]) -> dict:
        """
        Alias compatible con main.py.
        Recibe lista de textos de ofertas y devuelve un diccionario
        con cada tecnología detectada y el número de menciones.
        """
        return self.analizar(ofertas)

    def analizar(self, ofertas: list[str]) -> dict:
        """
        Recibe lista de textos de ofertas y devuelve un diccionario
        con cada tecnología detectada y el número de menciones.

        Returns:
            {
                "SAP": 5,
                "Active Directory": 4,
                "Apache": 3,
                ...
            }
            Ordenado de mayor a menor número de menciones.
        """
        print(f"{Fore.CYAN}[Extractor]{Style.RESET_ALL} Analizando {len(ofertas)} ofertas...")

        if not self.keywords:
            print(f"{Fore.RED}[!] Diccionario de keywords vacío. Abortando análisis.{Style.RESET_ALL}")
            return {}

        conteo = {}

        for oferta in ofertas:
            texto = oferta.lower()
            detecciones = self._detectar_tecnologias(texto)
            for tech in detecciones:
                conteo[tech] = conteo.get(tech, 0) + 1

        resultado = dict(sorted(conteo.items(), key=lambda x: x[1], reverse=True))

        self._mostrar_resumen(resultado)
        return resultado

    # ------------------------------------------------------------------
    # DETECCIÓN DE TECNOLOGÍAS EN UNA OFERTA
    # ------------------------------------------------------------------

    def _detectar_tecnologias(self, texto: str) -> set:
        """
        Busca coincidencias de todas las tecnologías del diccionario
        en el texto de una oferta. Devuelve un set para evitar
        contar la misma tecnología dos veces en la misma oferta.
        """
        detecciones = set()

        for _, tecnologias in self.keywords.items():
            for tech in tecnologias:
                patron = r"\b" + re.escape(tech.lower()) + r"\b"
                if re.search(patron, texto):
                    detecciones.add(tech)

        return detecciones

    # ------------------------------------------------------------------
    # MOSTRAR RESUMEN EN TERMINAL
    # ------------------------------------------------------------------

    def _mostrar_resumen(self, resultado: dict):
        """
        Muestra en terminal las tecnologías detectadas con una
        barra de progreso visual proporcional al número de menciones.
        """
        if not resultado:
            print(f"{Fore.YELLOW}[Extractor] No se detectaron tecnologías conocidas.{Style.RESET_ALL}")
            return

        max_menciones = max(resultado.values())
        barra_max = 20

        print(f"\n{Fore.GREEN}{'─' * 50}")
        print(f"  TECNOLOGÍAS DETECTADAS")
        print(f"{'─' * 50}{Style.RESET_ALL}")

        for tech, menciones in resultado.items():
            longitud = int((menciones / max_menciones) * barra_max)
            barra = "█" * longitud
            print(f"  {tech:<25} {Fore.CYAN}{barra:<20}{Style.RESET_ALL} {menciones}")

        print(f"{Fore.GREEN}{'─' * 50}{Style.RESET_ALL}\n")