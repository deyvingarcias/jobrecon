# JOBRECON — Plan Completo del Proyecto

## ¿Qué es JobRecon?

JobRecon es una herramienta de ciberseguridad desarrollada en Python orientada al **reconocimiento pasivo (OSINT)**. Su función principal es analizar las ofertas de trabajo públicas de una empresa objetivo para deducir qué tecnologías utiliza internamente, y cruzar esa información con la base de datos oficial de vulnerabilidades conocidas (NVD/CVEs) para generar un informe de posibles vectores de ataque.

Es una herramienta 100% de reconocimiento pasivo: no envía ningún paquete a los servidores del objetivo, solo analiza información pública. Esto la hace legal y éticamente usable en contextos de Red Team real y en entornos educativos.

---

## Contexto del autor

- **Nombre:** Deyvin García
- **Estudios:** CFGS Sistemas Informáticos y Ciberseguridad — Institut Baix Camp, Reus
- **Objetivo profesional:** Red Team / Hacking ético (eJPT → CEH)
- **Propósito del proyecto:** Proyecto propio para CV, prácticas (1000h, inicio julio) y GitHub

---

## ¿Por qué es original?

Existen herramientas de recon (FinalRecon, reconFTW, theHarvester, SpiderFoot) pero ninguna explota las **ofertas de trabajo** como fuente de inteligencia. Existe JobSpy que scrapea ofertas pero no hace ningún análisis de seguridad. La combinación concreta de:

**job scraping español (InfoJobs/Indeed ES) + keyword extraction + CVE mapping automático**

...no existe como herramienta standalone en GitHub. Es una idea original.

---

## Stack tecnológico

| Elemento | Detalle |
|---|---|
| Lenguaje | Python 3.11+ |
| Editor | VS Code |
| Sistema operativo | Windows (desarrollo) / Compatible con Kali Linux |
| Scraping | requests + BeautifulSoup4 |
| Extracción de texto | re (regex estándar de Python) |
| CVEs | nvdlib (wrapper oficial de la NVD API v2 del NIST) |
| Informes | Jinja2 (plantillas HTML) |
| CLI | argparse (estándar de Python) |
| Colores terminal | colorama |
| Variables de entorno | python-dotenv |

---

## Instalación de dependencias

```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:
```
requests==2.31.0
beautifulsoup4==4.12.3
nvdlib==0.8.3
jinja2==3.1.4
python-dotenv==1.0.1
colorama==0.4.6
```

---

## Estructura de carpetas completa

```
jobrecon/
│
├── main.py                        ← Punto de entrada. CLI con argparse. Recoge argumentos y orquesta el flujo.
├── requirements.txt               ← Lista de librerías a instalar con pip
├── .env                           ← API Key de NVD (NO se sube a GitHub)
├── .gitignore                     ← Ignora .env, output/, __pycache__/
├── README.md                      ← Documentación del proyecto para GitHub
│
├── config/
│   └── tech_keywords.json         ← Diccionario de tecnologías a detectar agrupadas por categoría
│
├── scrapers/
│   ├── __init__.py                ← Hace que scrapers/ sea un módulo Python
│   ├── base_scraper.py            ← Clase base con métodos comunes (headers, delays, limpieza de texto)
│   ├── infojobs.py                ← Scraper específico de InfoJobs España
│   └── indeed.py                  ← Scraper específico de Indeed España
│
├── analyzer/
│   ├── __init__.py
│   ├── extractor.py               ← Compara texto de ofertas contra tech_keywords.json y extrae tecnologías detectadas
│   └── cve_lookup.py              ← Para cada tecnología detectada, consulta nvdlib y devuelve CVEs ordenadas por severidad
│
├── reporter/
│   ├── __init__.py
│   ├── html_report.py             ← Recibe todos los datos y genera el informe HTML usando Jinja2
│   └── templates/
│       └── report.html            ← Plantilla HTML del informe final
│
└── output/                        ← Aquí se guardan los informes generados (ej: nestle_20250419.html)
```

---

## Flujo de ejecución completo

```
El usuario escribe:
python main.py --empresa "Nestlé" --pais es --max-ofertas 10
        ↓
main.py recoge los argumentos con argparse
        ↓
scrapers/infojobs.py busca ofertas de "Nestlé" en InfoJobs España
scrapers/indeed.py   busca ofertas de "Nestlé" en Indeed España
        ↓
Se obtiene lista de textos crudos de ofertas de trabajo
        ↓
analyzer/extractor.py compara cada texto contra tech_keywords.json
→ Resultado: {"Apache": 3, "SAP": 5, "Active Directory": 4, "Fortinet": 2, ...}
        ↓
analyzer/cve_lookup.py consulta NVD por cada tecnología detectada
→ Resultado: lista de CVEs con ID, severidad (CRITICAL/HIGH/MEDIUM), score CVSS, descripción
        ↓
reporter/html_report.py une todo y rellena la plantilla report.html
        ↓
Se guarda output/nestle_20250419.html
Se abre automáticamente en el navegador
```

---

## El archivo config/tech_keywords.json

Es el "diccionario" del programa. Contiene ~100 tecnologías agrupadas por categoría. Si una empresa usa algo que no está en este archivo, el programa no lo detectará. Se puede ampliar manualmente en cualquier momento.

Categorías actuales: web_servers, databases, languages, frameworks, os, network, virtualization, cloud, identity, erp, monitoring, other.

---

## El archivo .env

Contiene la API Key de NVD (gratuita, se pide en nvd.nist.gov/developers/request-an-api-key).

```
NVD_API_KEY=tu_key_aqui
```

Sin key: funciona pero con 6 segundos entre peticiones.
Con key: funciona con 0.6 segundos entre peticiones (10x más rápido).

Este archivo NUNCA se sube a GitHub (está en .gitignore).

---

## Estado actual del proyecto (al inicio de desarrollo)

| Archivo | Estado |
|---|---|
| main.py | ✅ Hecho — CLI funcional con banner y argparse |
| requirements.txt | ✅ Hecho |
| .gitignore | ✅ Hecho |
| .env | ✅ Creado (sin key por ahora) |
| config/tech_keywords.json | ✅ Hecho — diccionario completo de ~100 tecnologías |
| scrapers/base_scraper.py | ⏳ Pendiente |
| scrapers/infojobs.py | ⏳ Pendiente |
| scrapers/indeed.py | ⏳ Pendiente |
| analyzer/extractor.py | ⏳ Pendiente |
| analyzer/cve_lookup.py | ⏳ Pendiente |
| reporter/html_report.py | ⏳ Pendiente |
| reporter/templates/report.html | ⏳ Pendiente |
| README.md | ⏳ Pendiente (se hace al final) |

---

## Fases del proyecto

### FASE 1 — Base y configuración ✅ COMPLETADA
- Crear estructura de carpetas
- Configurar .gitignore, requirements.txt, .env
- Crear main.py con CLI funcional (argparse + banner colorama)
- Crear tech_keywords.json con diccionario de tecnologías

### FASE 2 — Scrapers (siguiente paso)
Objetivo: obtener texto real de ofertas de trabajo de InfoJobs e Indeed España.

**base_scraper.py:** Clase base con métodos comunes:
- Headers HTTP que imitan un navegador real (para no ser bloqueado)
- Función de delay entre peticiones (respetar rate limits)
- Función de limpieza de texto HTML

**infojobs.py:** Hereda de base_scraper. Busca ofertas de la empresa en InfoJobs, devuelve lista de textos.

**indeed.py:** Igual pero para Indeed España.

Resultado esperado: lista de strings con el texto de cada oferta encontrada.

### FASE 3 — Analyzer
Objetivo: extraer tecnologías y buscar CVEs.

**extractor.py:** Recibe lista de textos de ofertas. Para cada texto, busca coincidencias con tech_keywords.json usando regex. Devuelve diccionario con tecnología → número de menciones.

**cve_lookup.py:** Recibe lista de tecnologías detectadas. Para cada una, llama a nvdlib.searchCVE(keywordSearch="Apache"). Filtra las más críticas (CVSS > 7.0). Devuelve lista ordenada por severidad.

### FASE 4 — Reporter
Objetivo: generar el informe HTML final.

**report.html:** Plantilla Jinja2 con diseño oscuro estilo terminal. Muestra: empresa analizada, fecha, tecnologías detectadas con frecuencia, tabla de CVEs con colores por severidad (rojo=crítico, naranja=alto, amarillo=medio).

**html_report.py:** Rellena la plantilla con los datos reales y guarda el archivo en output/.

### FASE 5 — Integración y pruebas
- Conectar todos los módulos en main.py
- Pruebas con datos mock (sin scraping real) para verificar extractor y CVE lookup
- Pruebas con empresa real pequeña (ej: Quercus Technologies Reus)
- Ajustar errores y casos edge (empresa sin ofertas, tecnología sin CVEs, etc.)

### FASE 6 — Pulido y GitHub
- Añadir manejo de errores en todos los módulos (try/except)
- Escribir README.md completo con: descripción, instalación, uso, ejemplos de output, capturas
- Subir a GitHub con commits limpios y descriptivos
- Añadir al CV como proyecto de ciberseguridad / Red Team

---

## Ejemplo de output esperado

Al ejecutar:
```bash
python main.py --empresa "ElringKlinger" --pais es
```

Se genera `output/elringklinger_20250419.html` con contenido similar a:

```
JOBRECON REPORT — ElringKlinger S.A.U.
Fecha: 19/04/2025 | Ofertas analizadas: 8

TECNOLOGÍAS DETECTADAS:
  SAP S/4HANA        ████████  6 menciones
  Windows Server     ██████    4 menciones
  Active Directory   █████     3 menciones
  VMware             ███       2 menciones

CVEs ENCONTRADAS:
  [CRITICAL 9.8] CVE-2025-0070 — SAP NetWeaver — Remote Code Execution
  [HIGH 8.1]     CVE-2021-36934 — Windows Server — Privilege Escalation (HiveNightmare)
  [HIGH 7.8]     CVE-2021-26857 — Active Directory — Exchange RCE
```

---

## Relación con Red Team / Ciberseguridad

| Concepto | Cómo aplica en JobRecon |
|---|---|
| Reconocimiento pasivo | No toca los servidores del objetivo en ningún momento |
| OSINT | Usa fuentes públicas (portales de empleo) para obtener inteligencia |
| Threat Intelligence | Cruza el stack detectado con CVEs reales de la NVD |
| Attack Surface Mapping | Identifica qué tecnologías tiene la empresa y cuáles son vulnerables |
| Social Engineering prep | Detecta herramientas internas mencionadas en ofertas |

---

## Notas importantes para el desarrollo

- Python 3.11 mínimo (requerido por nvdlib)
- nvdlib tiene rate limiting integrado: 6 seg sin API key, 0.6 seg con key
- InfoJobs es más fácil de scrapear que LinkedIn (que bloquea agresivamente)
- El .env nunca va a GitHub — la key de NVD es gratis pero personal
- Los scrapers pueden romperse si el portal cambia su HTML — es mantenimiento normal, no un bug grave
- Todo el proyecto corre en local, sin servidor, sin dominio, coste 0€
