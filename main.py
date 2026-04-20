import argparse
from colorama import init, Fore, Style

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

if __name__ == "__main__":
    main()