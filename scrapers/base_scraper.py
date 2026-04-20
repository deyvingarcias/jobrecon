# scrapers/base_scraper.py

import requests
import time
import random
from bs4 import BeautifulSoup


class BaseScraper:
    """
    Clase base para todos los scrapers de JobRecon.
    Proporciona métodos comunes: headers, delays, peticiones HTTP y limpieza de texto.
    """

    # Lista de User-Agents reales para rotar y evitar bloqueos
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",

        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
        "Gecko/20100101 Firefox/125.0",

        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.4 Safari/605.1.15",
    ]

    def __init__(self, empresa: str, max_ofertas: int = 10):
        """
        Args:
            empresa: Nombre de la empresa a buscar.
            max_ofertas: Número máximo de ofertas a procesar.
        """
        self.empresa = empresa
        self.max_ofertas = max_ofertas
        self.session = requests.Session()
        self.session.headers.update(self._get_headers())

    # ------------------------------------------------------------------
    # HEADERS
    # ------------------------------------------------------------------

    def _get_headers(self) -> dict:
        """Devuelve headers HTTP que imitan un navegador real."""
        return {
            "User-Agent": random.choice(self.USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "DNT": "1",
        }

    # ------------------------------------------------------------------
    # DELAYS
    # ------------------------------------------------------------------

    def _delay(self, min_seg: float = 1.5, max_seg: float = 3.5):
        """
        Pausa aleatoria entre peticiones para respetar rate limits
        y reducir el riesgo de bloqueo.
        """
        tiempo = random.uniform(min_seg, max_seg)
        time.sleep(tiempo)

    # ------------------------------------------------------------------
    # PETICIÓN HTTP
    # ------------------------------------------------------------------

    def _get(self, url: str, params: dict = None) -> requests.Response | None:
        """
        Realiza una petición GET con manejo de errores.

        Returns:
            Response si tiene éxito, None si falla.
        """
        try:
            # Rotar User-Agent en cada petición
            self.session.headers.update({"User-Agent": random.choice(self.USER_AGENTS)})

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()  # Lanza excepción si 4xx o 5xx
            return response

        except requests.exceptions.HTTPError as e:
            print(f"[!] HTTP Error en {url}: {e}")
        except requests.exceptions.ConnectionError:
            print(f"[!] Error de conexión en {url}")
        except requests.exceptions.Timeout:
            print(f"[!] Timeout en {url}")
        except requests.exceptions.RequestException as e:
            print(f"[!] Error inesperado en {url}: {e}")

        return None

    # ------------------------------------------------------------------
    # LIMPIEZA DE TEXTO
    # ------------------------------------------------------------------

    def _limpiar_html(self, html: str) -> str:
        """
        Extrae el texto limpio de un fragmento HTML.
        Elimina etiquetas, espacios extra y líneas vacías.
        """
        soup = BeautifulSoup(html, "html.parser")
        texto = soup.get_text(separator=" ")
        # Eliminar espacios múltiples y saltos de línea innecesarios
        lineas = [linea.strip() for linea in texto.splitlines()]
        texto_limpio = " ".join(linea for linea in lineas if linea)
        return texto_limpio

    # ------------------------------------------------------------------
    # MÉTODO ABSTRACTO (a implementar en cada scraper hijo)
    # ------------------------------------------------------------------

    def obtener_ofertas(self) -> list[str]:
        """
        Cada scraper hijo debe implementar este método.
        Debe devolver una lista de strings, donde cada string
        es el texto completo de una oferta de trabajo.
        """
        raise NotImplementedError("Cada scraper debe implementar obtener_ofertas()")