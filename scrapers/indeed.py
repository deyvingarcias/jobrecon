# scrapers/indeed.py

from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
from colorama import Fore, Style


class IndeedScraper(BaseScraper):
    """
    Scraper para Indeed España.
    Busca ofertas de trabajo de una empresa y devuelve el texto de cada oferta.
    """

    BASE_URL = "https://es.indeed.com"
    SEARCH_URL = "https://es.indeed.com/jobs"

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
        print(f"{Fore.CYAN}[Indeed]{Style.RESET_ALL} Buscando ofertas de '{self.empresa}'...")

        urls = self._obtener_urls_ofertas()

        if not urls:
            print(f"{Fore.YELLOW}[Indeed] No se encontraron ofertas para '{self.empresa}'{Style.RESET_ALL}")
            return []

        print(f"{Fore.CYAN}[Indeed]{Style.RESET_ALL} {len(urls)} ofertas encontradas. Extrayendo texto...")

        textos = []
        for i, url in enumerate(urls, 1):
            print(f"  [{i}/{len(urls)}] {url}")
            texto = self._extraer_texto_oferta(url)
            if texto:
                textos.append(texto)
            self._delay()  # Pausa entre peticiones

        print(f"{Fore.GREEN}[Indeed]{Style.RESET_ALL} {len(textos)} ofertas procesadas correctamente.\n")
        return textos

    # ------------------------------------------------------------------
    # PASO 1: OBTENER URLs DE OFERTAS
    # ------------------------------------------------------------------

    def _obtener_urls_ofertas(self) -> list[str]:
        """
        Busca en Indeed España y extrae los enlaces a las ofertas individuales.
        """
        params = {
            "q": self.empresa,       # Término de búsqueda
            "l": "España",           # Ubicación
            "sort": "date",          # Ordenar por fecha
        }

        response = self._get(self.SEARCH_URL, params=params)
        if not response:
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # Cada oferta está en un <div> con class "job_seen_beacon"
        items = soup.select("div.job_seen_beacon")

        urls = []
        for item in items[:self.max_ofertas]:
            enlace = item.select_one("a[data-jk]")  # Indeed usa atributo data-jk
            if enlace and enlace.get("href"):
                href = enlace["href"]
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
        titulo = soup.select_one("h1.jobsearch-JobInfoHeader-title")
        if titulo:
            fragmentos.append(titulo.get_text(strip=True))

        # Nombre de la empresa
        empresa_tag = soup.select_one("div[data-company-name]")
        if empresa_tag:
            fragmentos.append(empresa_tag.get_text(strip=True))

        # Descripción completa de la oferta
        descripcion = soup.select_one("div#jobDescriptionText")
        if descripcion:
            fragmentos.append(self._limpiar_html(str(descripcion)))

        # Fallback: extraer todo el contenido del <main>
        if not fragmentos:
            main = soup.select_one("main") or soup.select_one("article")
            if main:
                fragmentos.append(self._limpiar_html(str(main)))

        return " ".join(fragmentos) if fragmentos else None