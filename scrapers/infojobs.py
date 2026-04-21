"""
scrapers/infojobs.py
Scraper de InfoJobs usando Playwright (headless).
Fallback a JobSpy si Playwright falla.
"""

import random
import re
import time
from urllib.parse import quote_plus

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


class InfoJobsScraper:
    """
    Scraper de InfoJobs España.
    Busca ofertas de trabajo por nombre de empresa y devuelve
    una lista de strings con título + descripción.
    """

    BASE_URL = "https://www.infojobs.net/jobsearch/search-results/list.xhtml"

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )

    def __init__(self, empresa: str, max_ofertas: int = 15):
        self.empresa = empresa
        self.max_ofertas = max_ofertas

    def _limpiar_texto(self, texto: str) -> str:
        """Elimina espacios extra y saltos de línea innecesarios."""
        texto = re.sub(r"\s+", " ", texto or "")
        return texto.strip()

    def _normalizar_desc(self, desc_raw) -> str:
        """Convierte None/'None'/vacío en string vacío."""
        if desc_raw is None:
            return ""
        desc = str(desc_raw).strip()
        if not desc or desc.lower() == "none":
            return ""
        return desc

    def _extraer_texto_item(self, item) -> tuple[str, str]:
        """
        Extrae título, snippet y link de una oferta del DOM.
        Devuelve: (texto_final, href)
        """
        titulo = ""
        desc = ""
        href = ""

        try:
            title_candidates = [
                "h2",
                "h3",
                "h4",
                "[class*='title']",
                "a[title]",
            ]
            for sel in title_candidates:
                loc = item.locator(sel).first
                if loc.count() > 0:
                    try:
                        titulo = self._limpiar_texto(loc.inner_text(timeout=1200))
                    except Exception:
                        try:
                            titulo = self._limpiar_texto(loc.get_attribute("title") or "")
                        except Exception:
                            titulo = ""
                    if titulo:
                        break
        except Exception:
            pass

        try:
            desc_candidates = [
                "p",
                "[class*='desc']",
                "[class*='snippet']",
                "[class*='summary']",
                "[class*='detail']",
            ]
            for sel in desc_candidates:
                loc = item.locator(sel).first
                if loc.count() > 0:
                    try:
                        desc = self._limpiar_texto(loc.inner_text(timeout=1200))
                    except Exception:
                        desc = ""
                    if desc:
                        break
        except Exception:
            pass

        try:
            link_candidates = [
                "a[href*='/oferta-empleo/']",
                "a[href*='/job/']",
                "a[href]",
            ]
            for sel in link_candidates:
                loc = item.locator(sel).first
                if loc.count() > 0:
                    try:
                        href = loc.get_attribute("href") or ""
                    except Exception:
                        href = ""
                    if href:
                        break
        except Exception:
            pass

        texto = self._limpiar_texto(f"{titulo} {desc}".strip())
        return texto, href

    def _leer_detalle_oferta(self, context, href: str) -> str:
        """
        Abre la oferta individual para intentar obtener una descripción completa.
        Devuelve texto limpio o string vacío.
        """
        if not href:
            return ""

        if href.startswith("/"):
            url = f"https://www.infojobs.net{href}"
        elif href.startswith("http"):
            url = href
        else:
            url = f"https://www.infojobs.net/{href.lstrip('/')}"

        page = context.new_page()
        try:
            page.set_default_timeout(8000)
            page.goto(url, wait_until="domcontentloaded", timeout=8000)
            if "/distil/distil/captcha.xhtml" in page.url:
                return ""

            # Intentamos capturar contenido relevante de la ficha.
            selectores = [
                "main",
                "article",
                "[class*='job-description']",
                "[class*='description']",
                "[class*='offer']",
                "body",
            ]

            contenido = ""
            for sel in selectores:
                loc = page.locator(sel).first
                try:
                    if loc.count() > 0:
                        contenido = self._limpiar_texto(loc.inner_text(timeout=2500))
                        if contenido:
                            break
                except Exception:
                    continue

            return contenido
        except Exception:
            return ""
        finally:
            try:
                page.close()
            except Exception:
                pass

    def _obtener_con_playwright(self) -> list[str]:
        """
        Scraping principal con Playwright.
        Hace un intento normal y, si detecta CAPTCHA, reintenta una vez tras 3s.
        """
        textos = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=self.USER_AGENT,
                viewport={"width": 1366, "height": 768},
                locale="es-ES",
            )

            def cargar_y_extraer() -> list[str]:
                page = context.new_page()
                try:
                    page.set_default_timeout(8000)

                    url = f"{self.BASE_URL}?keyword={quote_plus(self.empresa)}"
                    print(f"[*] Abriendo InfoJobs: {self.empresa}")

                    page.goto(url, wait_until="domcontentloaded", timeout=8000)

                    # Detección de CAPTCHA por URL o por contenido inline
                    try:
                        html = page.content().lower()
                        if (
                            "/distil/distil/captcha.xhtml" in page.url
                            or "humano o un robot" in html
                            or "eres humano" in html
                        ):
                            raise RuntimeError("CAPTCHA detectado en InfoJobs")
                    except Exception as e:
                        if "CAPTCHA detectado" in str(e):
                            raise
                        # Si page.content() falla por cualquier motivo, seguimos con la extracción normal
                        pass

                    # Espera a que aparezca algo parecido a una oferta
                    selectors = [
                        "li[data-jobid]",
                        "article.ij-OfferCard",
                        "li.ij-OfferListItem",
                        "article",
                        "li",
                    ]

                    found = False
                    for sel in selectors:
                        try:
                            page.locator(sel).first.wait_for(state="visible", timeout=8000)
                            found = True
                            break
                        except Exception:
                            continue

                    if not found:
                        raise TimeoutError("No se encontraron resultados visibles en el tiempo esperado")

                    containers = []
                    for sel in [
                        "li[data-jobid]",
                        "article.ij-OfferCard",
                        "li.ij-OfferListItem",
                    ]:
                        try:
                            handles = page.locator(sel).all()
                            if handles:
                                containers.extend(handles)
                        except Exception:
                            pass

                    if not containers:
                        containers = page.locator("article, li").all()

                    for item in containers:
                        if len(textos) >= self.max_ofertas:
                            break

                        texto_base, href = self._extraer_texto_item(item)
                        if not texto_base:
                            continue

                        # Si el snippet es corto, intentamos ampliar con la ficha.
                        if len(texto_base) < 100 and href:
                            detalle = self._leer_detalle_oferta(context, href)
                            if detalle:
                                combinado = self._limpiar_texto(f"{texto_base} {detalle}")
                                texto_final = combinado
                            else:
                                texto_final = texto_base
                        else:
                            texto_final = texto_base

                        if texto_final and len(texto_final) >= 50:
                            textos.append(texto_final)

                    return textos

                finally:
                    try:
                        page.close()
                    except Exception:
                        pass

            try:
                try:
                    textos = cargar_y_extraer()
                except RuntimeError as e:
                    if "CAPTCHA detectado" in str(e):
                        print("[!] CAPTCHA detectado en InfoJobs, reintentando en 3 segundos...")
                        time.sleep(3)
                        textos = cargar_y_extraer()
                    else:
                        raise

            finally:
                try:
                    context.close()
                except Exception:
                    pass
                try:
                    browser.close()
                except Exception:
                    pass

        return textos[: self.max_ofertas]

    def _fallback_jobspy(self) -> list[str]:
        """
        Fallback: usa JobSpy con LinkedIn si InfoJobs falla.
        Devuelve lista de strings.
        """
        try:
            from jobspy import scrape_jobs

            print("[!] Playwright falló. Usando fallback JobSpy (LinkedIn)...")

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
            descartadas_sin_desc = 0
            descartadas_cortas = 0
            debug = False  # Ponlo en True si quieres ver métricas

            for _, row in jobs.iterrows():
                titulo = str(row.get("title", "")).strip()
                desc_raw = row.get("description", None)

                desc = self._normalizar_desc(desc_raw)

                if desc:
                    texto = self._limpiar_texto(f"{titulo} {desc}")
                else:
                    texto = self._limpiar_texto(titulo)
                    descartadas_sin_desc += 1

                if not texto or len(texto) < 50:
                    descartadas_cortas += 1
                    continue

                textos.append(texto)

            if debug:
                print(f"[DEBUG] JobSpy: {descartadas_sin_desc} ofertas sin descripción válida.")
                print(f"[DEBUG] JobSpy: {descartadas_cortas} ofertas descartadas por ser cortas (<50 chars).")
                print(f"[DEBUG] JobSpy: {len(textos)} ofertas finales válidas.")

            return textos[: self.max_ofertas]

        except Exception as e:
            print(f"[!] Fallback JobSpy falló: {e}")
            return []

    def obtener_ofertas(self) -> list[str]:
        """
        Método principal.
        Intenta scraping con Playwright.
        Si no obtiene resultados, cae al fallback JobSpy.
        Devuelve lista de strings (máx self.max_ofertas).
        """
        print(f"[*] Buscando ofertas en InfoJobs para: {self.empresa}")

        try:
            textos = self._obtener_con_playwright() or []
            if textos:
                print(f"[+] InfoJobs Playwright: {len(textos)} ofertas obtenidas.")
                return textos[: self.max_ofertas]
            print("[!] Playwright no devolvió resultados útiles.")
        except Exception as e:
            print(f"[!] Playwright falló: {e}")

        textos = self._fallback_jobspy()
        print(f"[+] InfoJobs/LinkedIn (fallback): {len(textos)} ofertas obtenidas.")
        return textos[: self.max_ofertas]

    # Alias para compatibilidad con main.py
    def scrape(self) -> list[str]:
        return self.obtener_ofertas()