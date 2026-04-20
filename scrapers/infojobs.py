# scrapers/infojobs.py
from __future__ import annotations

from typing import List

import pandas as pd
from colorama import Fore
from jobspy import scrape_jobs


class InfoJobsScraper:
    def __init__(self, empresa: str, max_ofertas: int = 10):
        self.empresa = empresa
        self.max_ofertas = max_ofertas

    def _combine_text(self, title, description) -> str:
        title_text = "" if pd.isna(title) else str(title).strip()
        desc_text = "" if pd.isna(description) else str(description).strip()

        if title_text and desc_text:
            return f"{title_text} - {desc_text}"
        if title_text:
            return title_text
        if desc_text:
            return desc_text
        return ""

    def obtener_ofertas(self) -> List[str]:
        try:
            print(Fore.CYAN + f"[*] Buscando ofertas en InfoJobs vía JobSpy para: {self.empresa}")

            jobs = scrape_jobs(
                site_name="linkedin",
                search_term=self.empresa,
                location="Spain",
                results_wanted=self.max_ofertas,
                linkedin_fetch_description=True,
                verbose=0,
            )

            if jobs is None or len(jobs) == 0:
                print(Fore.YELLOW + "[!] InfoJobs/LinkedIn: no se encontraron ofertas.")
                return []

            ofertas = []

            for _, job in jobs.head(self.max_ofertas).iterrows():
                titulo = job.get("title", "")
                descripcion = job.get("description", "")
                texto = self._combine_text(titulo, descripcion)
                if texto:
                    ofertas.append(texto)

            print(Fore.GREEN + f"[+] InfoJobs/LinkedIn: {len(ofertas)} ofertas procesadas.")
            return ofertas

        except Exception as e:
            print(Fore.YELLOW + f"[!] Error en InfoJobsScraper con JobSpy: {e}")
            return []