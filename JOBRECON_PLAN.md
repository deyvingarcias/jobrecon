# JOBRECON — Plan Completo del Proyecto

## ¿Qué es JobRecon?

JobRecon es una herramienta de ciberseguridad desarrollada en Python orientada al **reconocimiento pasivo (OSINT)**. Su función principal es analizar las ofertas de trabajo públicas de una empresa objetivo para deducir qué tecnologías utiliza internamente, y cruzar esa información con la base de datos oficial de vulnerabilidades conocidas (NVD/CVEs) para generar un informe de posibles vectores de ataque.

Es una herramienta 100% de reconocimiento pasivo: no envía ningún paquete a los servidores del objetivo, solo analiza información pública. Esto la hace legal y éticamente usable en contextos de Red Team real y en entornos educativos.

---

## Contexto del autor

* **Nombre:** Deyvin García
* **Estudios:** CFGS Sistemas Informáticos y Ciberseguridad — Institut Baix Camp, Reus
* **Objetivo profesional:** Red Team / Hacking ético (eJPT → CEH)
* **Propósito del proyecto:** Proyecto propio para CV, prácticas (1000h, inicio julio) y GitHub

---

## ¿Por qué es original?

Existen herramientas de recon (FinalRecon, reconFTW, theHarvester, SpiderFoot) pero ninguna explota las **ofertas de trabajo** como fuente de inteligencia. Existe JobSpy que scrapea ofertas pero no hace ningún análisis de seguridad. La combinación concreta de:

**job scraping español (InfoJobs/Indeed ES) + keyword extraction + CVE mapping automático**

...no existe como herramienta standalone en GitHub. Es una idea original.

---

## Stack tecnológico

| Elemento             | Detalle                                            |
| -------------------- | -------------------------------------------------- |
| Lenguaje             | Python 3.11+                                       |
| Editor               | VS Code                                            |
| Sistema operativo    | Windows (desarrollo) / Compatible con Kali Linux   |
| Scraping             | requests + BeautifulSoup4                          |
| Extracción de texto  | re (regex estándar de Python)                      |
| CVEs                 | nvdlib (wrapper oficial de la NVD API v2 del NIST) |
| Informes             | Jinja2 (plantillas HTML)                           |
| CLI                  | argparse (estándar de Python)                      |
| Colores terminal     | colorama                                           |
| Variables de entorno | python-dotenv                                      |

---

## Instalación de dependencias

```bash
pip install -r requirements.txt
```

Contenido de `requirements.txt`:

```txt
requests==2.31.0
beautifulsoup4==4.12.3
nvdlib==0.8.3
jinja2==3.1.4
python-dotenv==1.0.1
colorama==0.4.6
```

---

## Estructura de carpetas completa

```text
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

```text
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

```env
NVD_API_KEY=tu_key_aqui
```

Sin key: funciona pero con 6 segundos entre peticiones.
Con key: funciona con 0.6 segundos entre peticiones (10x más rápido).

Este archivo NUNCA se sube a GitHub (está en .gitignore).

---

## Estado actual del proyecto (al inicio de desarrollo)

| Archivo                        | Estado                                             |
| ------------------------------ | -------------------------------------------------- |
| main.py                        | ✅ Hecho — CLI funcional con banner y argparse      |
| requirements.txt               | ✅ Hecho                                            |
| .gitignore                     | ✅ Hecho                                            |
| .env                           | ✅ Creado (sin key por ahora)                       |
| config/tech_keywords.json      | ✅ Hecho — diccionario completo de ~100 tecnologías |
| scrapers/base_scraper.py       | ⏳ Pendiente                                        |
| scrapers/infojobs.py           | ⏳ Pendiente                                        |
| scrapers/indeed.py             | ⏳ Pendiente                                        |
| analyzer/extractor.py          | ⏳ Pendiente                                        |
| analyzer/cve_lookup.py         | ⏳ Pendiente                                        |
| reporter/html_report.py        | ⏳ Pendiente                                        |
| reporter/templates/report.html | ⏳ Pendiente                                        |
| README.md                      | ⏳ Pendiente (se hace al final)                     |

---

## Fases del proyecto

### FASE 1 — Base y configuración ✅ COMPLETADA

* Crear estructura de carpetas
* Configurar .gitignore, requirements.txt, .env
* Crear main.py con CLI funcional (argparse + banner colorama)
* Crear tech_keywords.json con diccionario de tecnologías

### FASE 2 — Scrapers (siguiente paso)

Objetivo: obtener texto real de ofertas de trabajo de InfoJobs e Indeed España.

**base_scraper.py:** Clase base con métodos comunes:

* Headers HTTP que imitan un navegador real (para no ser bloqueado)
* Función de delay entre peticiones (respetar rate limits)
* Función de limpieza de texto HTML

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

* Conectar todos los módulos en main.py
* Pruebas con datos mock (sin scraping real) para verificar extractor y CVE lookup
* Pruebas con empresa real pequeña (ej: Quercus Technologies Reus)
* Ajustar errores y casos edge (empresa sin ofertas, tecnología sin CVEs, etc.)

### FASE 6 — Pulido y GitHub

* Añadir manejo de errores en todos los módulos (try/except)
* Escribir README.md completo con: descripción, instalación, uso, ejemplos de output, capturas
* Subir a GitHub con commits limpios y descriptivos
* Añadir al CV como proyecto de ciberseguridad / Red Team

---

## Ejemplo de output esperado

Al ejecutar:

```bash
python main.py --empresa "ElringKlinger" --pais es
```

Se genera `output/elringklinger_20250419.html` con contenido similar a:

```text
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

| Concepto                | Cómo aplica en JobRecon                                              |
| ----------------------- | -------------------------------------------------------------------- |
| Reconocimiento pasivo   | No toca los servidores del objetivo en ningún momento                |
| OSINT                   | Usa fuentes públicas (portales de empleo) para obtener inteligencia  |
| Threat Intelligence     | Cruza el stack detectado con CVEs reales de la NVD                   |
| Attack Surface Mapping  | Identifica qué tecnologías tiene la empresa y cuáles son vulnerables |
| Social Engineering prep | Detecta herramientas internas mencionadas en ofertas                 |

---

## Notas importantes para el desarrollo

* Python 3.11 mínimo (requerido por nvdlib)
* nvdlib tiene rate limiting integrado: 6 seg sin API key, 0.6 seg con key
* InfoJobs es más fácil de scrapear que LinkedIn (que bloquea agresivamente)
* El .env nunca va a GitHub — la key de NVD es gratis pero personal
* Los scrapers pueden romperse si el portal cambia su HTML — es mantenimiento normal, no un bug grave
* Todo el proyecto corre en local, sin servidor, sin dominio, coste 0€

---

## ----------- DIA 2 ----------------

# 🔄 ACTUALIZACIÓN DEL PROYECTO — JOBRECON

Estado actualizado del proyecto (tras nuevos avances)

⚠️ Nota: Este bloque actualiza el estado original. El resto del documento sigue siendo válido.

| Archivo                        | Estado                                                   |
| ------------------------------ | -------------------------------------------------------- |
| main.py                        | ✅ Hecho — CLI funcional con banner y argparse            |
| requirements.txt               | ✅ Hecho                                                  |
| .gitignore                     | ✅ Hecho                                                  |
| .env                           | ✅ Creado (con API key de NVD)                            |
| config/tech_keywords.json      | ✅ Hecho — diccionario completo de ~100 tecnologías       |
| scrapers/base_scraper.py       | ✅ Ya no se usa para el scraping principal                |
| scrapers/infojobs.py           | ✅ Reescrito con JobSpy                                   |
| scrapers/indeed.py             | ✅ Reescrito con JobSpy                                   |
| analyzer/extractor.py          | ✅ Hecho — detección de tecnologías con regex y conteo    |
| analyzer/cve_lookup.py         | ✅ Hecho — integración con NVD + método lookup compatible |
| reporter/html_report.py        | ✅ Hecho — genera el informe HTML                         |
| reporter/templates/report.html | ✅ Hecho — plantilla HTML completa estilo terminal        |
| README.md                      | ⏳ Pendiente (se hace al final)                           |

### Nuevos hitos completados

* Repositorio GitHub creado y publicado
* `.env` protegido y excluido del control de versiones
* `.gitignore` corregido para evitar subir `.venv/`
* Entorno virtual creado con Python 3.12 para compatibilidad con `python-jobspy`
* Dependencias instaladas correctamente
* `python-jobspy` integrado en el proyecto

### Scrapers actualizados

**InfoJobsScraper**

* Mantiene la interfaz `InfoJobsScraper(empresa, max_ofertas)`
* Ahora usa `jobspy.scrape_jobs()`
* Como JobSpy no soporta InfoJobs de forma nativa, se usa una fuente equivalente cercana para obtener resultados útiles
* Devuelve lista de strings combinando título + descripción

**IndeedScraper**

* Mantiene la interfaz `IndeedScraper(empresa, max_ofertas)`
* Usa `jobspy.scrape_jobs(site_name="indeed", ...)`
* Devuelve lista de strings combinando título + descripción

### Analyzer actualizado

**TechExtractor**

* Se añadió compatibilidad con `extract(textos)` para encajar con `main.py`
* Sigue soportando el método original `analizar(textos)`
* Devuelve diccionario ordenado por menciones
* Cuenta detecciones únicas por oferta para evitar duplicados internos

**CVELookup**

* Se añadió compatibilidad con `lookup(tecnologias)` para encajar con `main.py`
* Sigue soportando el método original `buscar(tecnologias)`
* Consulta la NVD con `nvdlib.searchCVE()`
* Extrae score CVSS, severidad y descripción
* Filtra CVEs con score ≥ 7.0

### Estado real actual del flujo

* Scraping funcional
* Análisis funcional
* Integración con CVEs funcional
* Generación de HTML funcional
* Git limpio y configurado para no subir dependencias
* Proyecto listo para pruebas y refinamiento

### Observación importante sobre la calidad de los datos

El pipeline funciona, pero la calidad semántica de las CVEs todavía puede generar ruido en tecnologías genéricas como:

* AWS
* Azure
* GCP
* Active Directory
* Python

Eso no rompe el sistema, pero sí sugiere una mejora futura: normalizar tecnologías y filtrar CVEs antiguas o irrelevantes.

### Siguiente paso lógico

* Mejorar la precisión del mapeo tecnología → CVE
* Reducir falsos positivos
* Añadir filtrado por año/recencia
* Añadir scoring de relevancia
* Preparar README final y presentación de GitHub

---

## Estado actual del proyecto (real, tras los avances)

| Archivo                        | Estado                                     |
| ------------------------------ | ------------------------------------------ |
| main.py                        | ✅ Integrado y funcionando                  |
| requirements.txt               | ✅ Actualizado con `python-jobspy`          |
| .gitignore                     | ✅ Limpiado y correcto                      |
| .env                           | ✅ Configurado con la NVD API key           |
| scrapers/infojobs.py           | ✅ Reescrito con JobSpy                     |
| scrapers/indeed.py             | ✅ Reescrito con JobSpy                     |
| analyzer/extractor.py          | ✅ Corregido con `extract()` y `analizar()` |
| analyzer/cve_lookup.py         | ✅ Corregido con `lookup()` y `buscar()`    |
| reporter/html_report.py        | ✅ Funcionando                              |
| reporter/templates/report.html | ✅ Funcionando                              |
| output/                        | ✅ Genera informes HTML                     |
| README.md                      | ⏳ Pendiente                                |

---

## Pendientes reales

* Refinar el mapeo de tecnologías para reducir falsos positivos
* Filtrar CVEs antiguas o poco relevantes
* Mejorar el scoring de riesgo
* Escribir el README final de GitHub
* Añadir capturas y ejemplos reales
* Revisar el contenido final del reporte HTML
* Hacer commits limpios y preparar publicación final

---

## Notas de trabajo recientes

* Se evitó subir `.venv/` al repositorio
* Se corrigió el `.gitignore`
* Se usó Python 3.12 para poder instalar `python-jobspy`
* Se verificó que la extracción de ofertas y la generación del HTML funcionan
* Se detectó que el output de CVEs es técnicamente correcto, pero todavía necesita afinado semántico para ser más útil

---

## Objetivo inmediato

El siguiente objetivo no es rehacer el proyecto, sino **pulirlo**:

1. mejorar precisión de CVEs
2. dejar el README listo
3. preparar el repo para GitHub
4. documentar el estado real del proyecto para futuras IAs o iteraciones

---

## Resumen rápido del estado actual

JobRecon ya está en una fase funcional avanzada:

* Scraping de ofertas: ✅
* Extracción de tecnologías: ✅
* Consulta de CVEs: ✅
* Generación del reporte HTML: ✅
* Manejo de dependencias y Git: ✅
* Documentación final: ⏳ pendiente

---

## Próximo trabajo sugerido

* Añadir normalización de tecnologías
* Filtrar CVEs demasiado antiguas
* Mejorar el valor de salida del informe
* Cerrar README y preparación final de GitHub

---

## Meta de portabilidad a Linux

Además del desarrollo en Windows, uno de los objetivos del proyecto es **llevar JobRecon a Linux** para que funcione correctamente en entornos como Kali Linux y otras distribuciones orientadas a ciberseguridad.

### Objetivos de la migración a Linux

* Verificar compatibilidad de rutas, dependencias y permisos
* Asegurar que el entorno virtual y `requirements.txt` funcionan igual en Linux
* Comprobar que los scrapers y el reporte HTML no dependen de comportamientos exclusivos de Windows
* Ajustar la documentación para instalación y ejecución en Linux
* Preparar una versión portable para uso en laboratorios, máquinas de pruebas y entornos de Red Team

### Pendientes para la versión Linux

* Probar instalación completa en Kali Linux / Debian / Ubuntu
* Validar `python-jobspy` en entorno Linux
* Revisar diferencias de `pathlib`, permisos de archivos y navegador por defecto
* Documentar pasos de instalación en Linux dentro del README
* Verificar que la generación de reportes en `output/` funciona sin cambios

### Estado de esta meta

* Windows: ✅ funcional
* Linux: ⏳ pendiente de portabilidad y pruebas

---

## Último resumen útil para futuras IAs

JobRecon ya no está en fase inicial. Ahora es un proyecto funcional con:

* scraping real de ofertas
* extracción de tecnologías
* búsqueda de CVEs
* generación de HTML
* dependencia a NVD API key opcional
* entorno virtual correctamente aislado
* `.gitignore` limpio
* objetivo adicional de portarlo a Linux

La siguiente iteración no debe reescribir la base, sino centrarse en:

* precisión de datos
* portabilidad Linux
* documentación final
* presentación en GitHub

--------------------
🎯 CHECKLIST COMPLETO: JobRecon v1.0 RELEASE

📊 PROGRESO ACTUAL
36% completado ✅ → Fase de pulido y refinamiento
FASE 1: Base & Config      ████████████████████████████  100% ✅
FASE 2: Scrapers (base)    ████████████████████░░░░░░░░   60% ⏳
FASE 3: Analyzer           ████████████████████░░░░░░░░   70% ⏳
FASE 4: Reporter           ████████████████████░░░░░░░░   80% ✅
FASE 5: Integración        ████████████░░░░░░░░░░░░░░░░   40% ⏳
FASE 6: Polish & GitHub    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% ⏳
───────────────────────────────────────────────────
TOTAL: 36%

✅ CHECKLIST DE TAREAS (para v1.0)
SEMANA 1: CORE FIXES (Prioridad ALTA)
🔧 T1: Mejorar scraper InfoJobs (2-3h)

 Reescribir scrapers/infojobs.py con BeautifulSoup directo

 Conectar a https://www.infojobs.net/search?q=...
 Parsear ofertas reales (título + descripción)
 Manejar paginación (máx 15 ofertas)
 Testear con "ElringKlinger" → debe dar 3-5 ofertas reales


 Mantener fallback a JobSpy si falla
ESTIMADO: 1.5h

🧹 T2: Normalización de tecnologías (1-2h)

 Crear analyzer/tech_normalizer.py

 AWS → "Amazon Web Services Cloud"
 Azure → "Microsoft Azure Cloud"
 GCP → "Google Cloud Platform"
 Python → "Python Programming Language" (NO generic)
 Mapeo 1:1 de aliases (ej: "S/4HANA" → "SAP")


 Integrar en extractor.py
ESTIMADO: 1h

🔍 T3: Filtrado inteligente de CVEs (1.5-2h)

 Mejorar analyzer/cve_lookup.py:

 Filtrar por año: if cve.year < 2015: skip
 Filtrar por CVSS: if cvss < 7.0: skip
 Desduplicar CVEs (mismo vendor, mismo ID)
 Ordenar por severidad + recencia


 Test con SAP → solo CVEs relevantes 2015+
ESTIMADO: 1.5h

🎯 T4: Scoring básico (1h)

 Añadir a cve_lookup.py:

python  risk_score = (cvss * 0.7) + (recency_weight * 0.3)

 Ordenar por risk_score desc
 Mostrar en HTML report
ESTIMADO: 1h

🧪 T5: Test end-to-end (30min)

 Ejecutar con "Nestlé" → debe dar 5-10 ofertas reales
 Verificar tecnologías detectadas
 Verificar CVEs son post-2015
 Verificar HTML se ve limpio
ESTIMADO: 30min


SEMANA 2: POLISH & GITHUB (Prioridad MEDIA)
📝 T6: README profesional (1-1.5h)

 Descripción clara de qué es JobRecon
 Instalación paso a paso (Windows + Linux)
 Ejemplos de uso
 Explicación del output
 Disclaimer ético/legal
 Roadmap futuro
ESTIMADO: 1h

🐛 T7: Error handling robusto (1h)

 Try/except en todos los scrapers
 Manejo de "0 ofertas encontradas"
 Manejo de "API NVD timeout"
 Mensajes de error claros
ESTIMADO: 1h

🎨 T8: Mejorar HTML report (30min-1h)

 Añadir colores por severidad (rojo=CRITICAL, naranja=HIGH)
 Mejorar tabla de CVEs (más legible)
 Añadir fecha/hora generación
 Dark theme limpio
ESTIMADO: 45min

🔐 T9: Security & Git cleanup (30min)

 Verificar .env no está en git
 Verificar .gitignore correcto
 Limpiar comentarios viejos
 Commits limpios y descriptivos
ESTIMADO: 30min

🚀 T10: GitHub release v1.0 (15min)

 Crear repo público
 Push con commits limpios
 Crear release v1.0
 Añadir descripción en GitHub
ESTIMADO: 15min


⏱️ TIEMPO TOTAL ESTIMADO
FaseTareasTiempoCORE FIXEST1-T56-7hPOLISH & GITHUBT6-T104-5hBUFFERImprevistos1-2hTOTAL—11-14h
Equivalente: 2-3 semanas a ritmo relajado (1-2h/día), o 2-3 días intensos (6-8h/día)

📍 PLAN PARA AHORA (próxima 1h)
Vamos directo a:

T1: Mejorar scraper InfoJobs ← ESTO ES LO BLOQUEADOR
Testear que funciona

Si en 1h sacamos InfoJobs funcionando bien, ya tenemos 80% de la victoria porque el resto encaja fácil.

🎯 OBJETIVO EN 1 HORA
Input:
bashpython main.py --empresa "Nestlé" --pais es --max-ofertas 10
Output esperado:
[+] InfoJobs: 5-8 ofertas reales
[+] Indeed: 2-3 ofertas
[+] Tecnologías detectadas: 8-12 (SAP, Azure, Windows Server, etc.)
[+] CVEs relevantes: 15-20 (solo post-2015, CVSS 7+)
[+] HTML generado y limpio

¿Vamos? 🚀
Empezamos con el scraper de InfoJobs. Dame 5 min para escribirte el código nuevo de scrapers/infojobs.py
¿Listo?


----

Nota Linux/Kali: InfoJobs aplica CAPTCHA en entornos no-browser. En Linux el scraper usa automáticamente el fallback LinkedIn. Para mejores resultados en Linux se recomienda aumentar --max-ofertas para compensar.