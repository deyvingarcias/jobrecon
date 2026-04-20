# scrapers/infojobs.py

from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from colorama import Fore, Style


class InfoJobsScraper(BaseScraper):
    """
    Scraper para InfoJobs España.
    Busca ofertas de trabajo de una empresa y devuelve el texto de cada oferta.
    """

    BASE_URL = "https://www.infojobs.net"
    SEARCH_URL = "https://www.infojobs.net/jobsearch/search-results/list.xhtml"

    def __init__(self, empresa: str, max_ofertas: int = 10):
        super().__init__(empresa, max_ofertas)

    # ------------------------------------------------------------------
    # MÉTODO PRINCIPAL
    # ------------------------------------------------------------------

    def obtener_ofertas(self) -> list[str]:
        """
        Punto de entrada principal.
        Devuelve lista de textos limpios de cada oferta encontrada.
        """
        print(f"{Fore.CYAN}[InfoJobs]{Style.RESET_ALL} Buscando ofertas de '{self.empresa}'...")

        urls = self._obtener_urls_ofertas()

        if not urls:
            print(f"{Fore.YELLOW}[InfoJobs] No se encontraron ofertas para '{self.empresa}'{Style.RESET_ALL}")
            return []

        print(f"{Fore.CYAN}[InfoJobs]{Style.RESET_ALL} {len(urls)} ofertas encontradas. Extrayendo texto...")

        textos = []
        for i, url in enumerate(urls, 1):
            print(f"  [{i}/{len(urls)}] {url}")
            texto = self._extraer_texto_oferta(url)
            if texto:
                textos.append(texto)
            self._delay()  # Pausa entre peticiones

        print(f"{Fore.GREEN}[InfoJobs]{Style.RESET_ALL} {len(textos)} ofertas procesadas correctamente.\n")
        return textos

    # ------------------------------------------------------------------
    # PASO 1: OBTENER URLs DE OFERTAS
    # ------------------------------------------------------------------

    def _obtener_urls_ofertas(self) -> list[str]:
        """
        Busca en InfoJobs y extrae los enlaces a las ofertas individuales.
        """
        params = {
            "keyword": self.empresa,
            "provinceIds": "0",       # Toda España
            "sortBy": "PUBLICATION_DATE",
        }

        response = self._get(self.SEARCH_URL, params=params)
        if not response:
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # Cada oferta en los resultados está en un <li> con class "js-offer-item"
        # Si InfoJobs cambia su HTML, ajustar este selector
        items = soup.select("li.js-offer-item")

        urls = []
        for item in items[:self.max_ofertas]:
            enlace = item.select_one("a.js-offer-title")
            if enlace and enlace.get("href"):
                href = enlace["href"]
                # Algunos hrefs son relativos, otros absolutos
                if href.startswith("http"):
                    urls.append(href)
                else:
                    urls.append(self.BASE_URL + href)

        return urls

    # ------------------------------------------------------------------
    # PASO 2: EXTRAER TEXTO DE CADA OFERTA
    # ------------------------------------------------------------------

    def _extraer_texto_oferta(self, url: str) -> str | None:
        """
        Visita la página de una oferta individual y extrae el texto relevante.
        """
        response = self._get(url)
        if not response:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        fragmentos = []

        # Título del puesto
        titulo = soup.select_one("h1.job-title")
        if titulo:
            fragmentos.append(titulo.get_text(strip=True))

        # Descripción principal de la oferta
        descripcion = soup.select_one("div.job-description")
        if descripcion:
            fragmentos.append(self._limpiar_html(str(descripcion)))

        # Requisitos (suelen estar en una sección separada)
        requisitos = soup.select_one("div.job-requirements")
        if requisitos:
            fragmentos.append(self._limpiar_html(str(requisitos)))

        # Si no encontró nada con los selectores específicos,
        # extraer todo el <main> como fallback
        if not fragmentos:
            main = soup.select_one("main") or soup.select_one("article")
            if main:
                fragmentos.append(self._limpiar_html(str(main)))

        return " ".join(fragmentos) if fragmentos else None