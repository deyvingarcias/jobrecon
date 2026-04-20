import argparse
import sys

from colorama import Fore, Style, init

from analyzer.cve_lookup import CVELookup
from analyzer.extractor import TechExtractor
from reporter.html_report import generate_report
from scrapers.indeed import IndeedScraper
from scrapers.infojobs import InfoJobsScraper

init(autoreset=True)


def banner():
    print(Fore.RED + r"""
     _       _     ____                      
    | | ___ | |__ |  _ \ ___  ___ ___  _ __  
 _  | |/ _ \| '_ \| |_) / _ \/ __/ _ \| '_ \ 
| |_| | (_) | |_) |  _ <  __/ (_| (_) | | | |
 \___/ \___/|_.__/|_| \_\___|\___\___/|_| |_|
    """)
    print(Fore.YELLOW + "  OSINT Job-Based Tech & CVE Recon Tool")
    print(Fore.WHITE + "  by Deyvin García\n")


def main():
    banner()

    parser = argparse.ArgumentParser(
        description="JobRecon - Detecta el stack tecnológico de una empresa mediante sus ofertas de trabajo y busca CVEs asociadas"
    )

    parser.add_argument(
        "--empresa",
        type=str,
        required=True,
        help="Nombre de la empresa objetivo (ej: Nestlé)"
    )

    parser.add_argument(
        "--pais",
        type=str,
        default="es",
        help="Código de país (default: es)"
    )

    parser.add_argument(
        "--max-ofertas",
        type=int,
        default=10,
        help="Número máximo de ofertas a analizar (default: 10)"
    )

    args = parser.parse_args()

    print(Fore.CYAN + f"[*] Empresa objetivo : {args.empresa}")
    print(Fore.CYAN + f"[*] País             : {args.pais}")
    print(Fore.CYAN + f"[*] Máx. ofertas     : {args.max_ofertas}")
    print(Fore.WHITE + "\n[...] Iniciando reconocimiento...\n")

    try:
        textos = []

        # InfoJobs
        try:
            infojobs_texts = InfoJobsScraper(args.empresa, args.max_ofertas).obtener_ofertas()
            infojobs_texts = infojobs_texts or []
            textos.extend(infojobs_texts)
            print(Fore.CYAN + f"[+] InfoJobs: {len(infojobs_texts)} ofertas obtenidas.")
        except Exception as e:
            print(Fore.YELLOW + f"[!] InfoJobs no disponible o falló el scraping: {e}")

        # Indeed
        try:
            indeed_texts = IndeedScraper(args.empresa, args.max_ofertas).obtener_ofertas()
            indeed_texts = indeed_texts or []
            textos.extend(indeed_texts)
            print(Fore.CYAN + f"[+] Indeed: {len(indeed_texts)} ofertas obtenidas.")
        except Exception as e:
            print(Fore.YELLOW + f"[!] Indeed no disponible o falló el scraping: {e}")

        if not textos:
            print(Fore.RED + "[x] No se han obtenido ofertas válidas desde ninguna fuente.")
            sys.exit(1)

        tecnologias = TechExtractor().extract(textos) or {}

        if not tecnologias:
            print(Fore.YELLOW + "[!] No se detectaron tecnologías en las ofertas analizadas.")
            sys.exit(1)

        print(Fore.GREEN + "\n[+] Tecnologías detectadas:")
        for tecnologia, menciones in sorted(tecnologias.items(), key=lambda item: item[1], reverse=True):
            print(Fore.GREEN + f"    - {tecnologia}: {menciones}")

        cves = CVELookup().lookup(tecnologias) or []

        critical_count = 0
        for cve in cves:
            severidad = str(cve.get("severidad", "")).upper()
            score = cve.get("score", 0)

            is_critical = "CRITICAL" in severidad
            try:
                is_critical = is_critical or float(score) >= 9.0
            except (TypeError, ValueError):
                pass

            if is_critical:
                critical_count += 1

        cve_color = Fore.RED if critical_count > 0 else Fore.YELLOW
        print(cve_color + f"\n[+] CVEs encontradas: {len(cves)} (críticas: {critical_count})")

        reporte = generate_report(args.empresa, tecnologias, cves, len(textos))
        print(Fore.GREEN + f"[+] Reporte generado: {reporte}")

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Reconocimiento cancelado por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"[x] Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()