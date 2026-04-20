"""
scrapers/infojobs.py
Scraper directo de InfoJobs usando requests + BeautifulSoup.
Fallback a JobSpy si falla.
"""

import time
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus


class InfoJobsScraper:
    """
    Scraper de InfoJobs España.
    Busca ofertas de trabajo por nombre de empresa y devuelve
    una lista de strings con título + descripción.
    """

    BASE_URL = "https://www.infojobs.net/jobsearch/search-results/list.xhtml"

    HEADERS_POOL = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.infojobs.net/",
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                          "Version/17.0 Safari/605.1.15",
            "Accept-Language": "es-ES,es;q=0.8,en;q=0.5",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.infojobs.net/",
        },
    ]

    def __init__(self, empresa: str, max_ofertas: int = 15):
        self.empresa = empresa
        self.max_ofertas = max_ofertas
        self.session = requests.Session()

    def _get_headers(self) -> dict:
        return random.choice(self.HEADERS_POOL)

    def _delay(self, min_s: float = 1.0, max_s: float = 2.5):
        time.sleep(random.uniform(min_s, max_s))

    def _limpiar_texto(self, texto: str) -> str:
        """Elimina espacios extra y saltos de línea innecesarios."""
        import re
        texto = re.sub(r'\s+', ' ', texto)
        return texto.strip()

    def _get_pagina(self, pagina: int = 1) -> BeautifulSoup | None:
        """
        Descarga una página de resultados de InfoJobs para la empresa dada.
        Devuelve el objeto BeautifulSoup o None si falla.
        """
        params = {
            "keyword": self.empresa,
            "page": pagina,
            "sortBy": "RELEVANCE",
        }
        try:
            resp = self.session.get(
                self.BASE_URL,
                params=params,
                headers=self._get_headers(),
                timeout=10,
            )
            if resp.status_code == 200:
                return BeautifulSoup(resp.text, "html.parser")
            else:
                return None
        except Exception:
            return None

    def _extraer_ofertas_pagina(self, soup: BeautifulSoup) -> list[str]:
        """
        Extrae texto de ofertas de una página de resultados de InfoJobs.
        Devuelve lista de strings (título + descripción snippet).
        """
        textos = []

        # InfoJobs usa diferentes selectores según la versión del HTML.
        # Intentamos varios para ser resilientes a cambios de layout.
        candidatos = []

        # Selector principal: tarjetas de oferta modernas
        candidatos += soup.select("li[data-jobid]")
        candidatos += soup.select("article.ij-OfferCard")
        candidatos += soup.select("div.ij-OfferCard-description")
        candidatos += soup.select("li.ij-OfferListItem")

        # Fallback genérico: buscar cualquier elemento con título de oferta
        if not candidatos:
            candidatos = soup.find_all(
                ["article", "li", "div"],
                class_=lambda c: c and ("offer" in c.lower() or "job" in c.lower()),
            )

        for item in candidatos:
            partes = []

            # Título
            titulo = item.find(["h2", "h3", "h4", "a"], class_=lambda c: c and "title" in c.lower() if c else False)
            if not titulo:
                titulo = item.find(["h2", "h3", "h4"])
            if titulo:
                partes.append(titulo.get_text(separator=" "))

            # Descripción / snippet
            desc = item.find(
                ["p", "div", "span"],
                class_=lambda c: c and any(x in c.lower() for x in ["desc", "snippet", "summary", "detail"]) if c else False,
            )
            if desc:
                partes.append(desc.get_text(separator=" "))

            # Texto completo como fallback
            if not partes:
                partes.append(item.get_text(separator=" "))

            texto = self._limpiar_texto(" ".join(partes))
            if texto and len(texto) > 20:
                textos.append(texto)

        return textos

    def _fallback_jobspy(self) -> list[str]:
        """
        Fallback: usa JobSpy con LinkedIn si InfoJobs directo falla.
        Devuelve lista de strings.
        """
        try:
            from jobspy import scrape_jobs
            jobs = scrape_jobs(
                site_name=["linkedin"],
                search_term=self.empresa,
                location="Spain",
                results_wanted=self.max_ofertas,
                country_indeed="Spain",
            )
            if jobs is None or jobs.empty:
                return []
            textos = []
            for _, row in jobs.iterrows():
                titulo = str(row.get("title", ""))
                desc = str(row.get("description", ""))
                texto = self._limpiar_texto(f"{titulo} {desc}")
                if texto:
                    textos.append(texto)
            return textos
        except Exception:
            return []

    def obtener_ofertas(self) -> list[str]:
        """
        Método principal. Intenta scraping directo de InfoJobs.
        Si no obtiene resultados, cae al fallback JobSpy.
        Devuelve lista de strings (máx self.max_ofertas).
        """
        print(f"[*] Buscando ofertas en InfoJobs para: {self.empresa}")
        textos = []
        pagina = 1

        while len(textos) < self.max_ofertas:
            soup = self._get_pagina(pagina)
            if not soup:
                break

            nuevos = self._extraer_ofertas_pagina(soup)
            if not nuevos:
                break

            textos.extend(nuevos)
            pagina += 1
            self._delay()

        # Recortar al máximo solicitado
        textos = textos[: self.max_ofertas]

        if textos:
            print(f"[+] InfoJobs directo: {len(textos)} ofertas obtenidas.")
            return textos

        # Fallback
        print("[!] InfoJobs directo falló. Usando fallback JobSpy (LinkedIn)...")
        textos = self._fallback_jobspy()
        print(f"[+] InfoJobs/LinkedIn (fallback): {len(textos)} ofertas obtenidas.")
        return textos

    # Alias para compatibilidad con main.py
    def scrape(self) -> list[str]:
        return self.obtener_ofertas()