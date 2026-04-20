# JobRecon

**Autor:** Deyvin García
**Repo:** [https://github.com/deyvingarcias/jobrecon](https://github.com/deyvingarcias/jobrecon)

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Passive Recon Only](https://img.shields.io/badge/Passive%20Recon-Only-red)

JobRecon es una herramienta OSINT en Python que analiza ofertas de trabajo públicas de una empresa objetivo para inferir su stack tecnológico interno y cruzar esos hallazgos con la base de datos NVD/CVEs del NIST. El resultado es un informe HTML con posibles vectores de ataque asociados a tecnologías detectadas.

> Reconocimiento 100% pasivo: no envía ningún paquete al objetivo.

## Qué es

JobRecon automatiza la recopilación y correlación de información pública sobre una empresa a partir de ofertas de empleo. A partir de las tecnologías mencionadas en esas ofertas, busca CVEs relacionadas y genera un reporte visual en HTML con:

* Tecnologías detectadas con barras de progreso por menciones
* CVEs asociadas a esas tecnologías
* Severidad, score, risk score, año y descripción
* Una vista rápida pensada para análisis técnico y triage

## Por qué es útil

En contextos de Red Team, OSINT y análisis de superficie de ataque, las ofertas de empleo suelen revelar herramientas, frameworks, entornos cloud, soluciones de seguridad y dependencias internas. JobRecon ayuda a convertir ese ruido público en señales accionables.

Casos de uso habituales:

* Identificar posibles tecnologías expuestas públicamente por una organización
* Priorizar hipótesis de ataque basadas en CVEs conocidas
* Preparar un análisis previo a una auditoría autorizada
* Obtener una visión rápida del ecosistema tecnológico sin interacción activa con el objetivo

## Instalación

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Linux / Kali

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración del `.env`

JobRecon usa variables de entorno para la configuración sensible. En especial, se recomienda añadir una clave de API de NVD para mejorar la experiencia y evitar límites más agresivos.

Crea un archivo `.env` en la raíz del proyecto con un contenido similar a este:

```env
NVD_API_KEY=tu_clave_aqui
```

Puedes solicitar una clave aquí: [https://nvd.nist.gov/developers/request-an-api-key](https://nvd.nist.gov/developers/request-an-api-key)

## Uso

Ejemplo básico:

```bash
python main.py --empresa "Telefonica" --pais es --max-ofertas 15
```

Ejemplos adicionales:

```bash
python main.py --empresa "Indra" --pais es --max-ofertas 25
python main.py --empresa "Sopra Steria" --pais es --max-ofertas 10
python main.py --empresa "Accenture" --pais es --max-ofertas 20
```

### Resultado

JobRecon genera un archivo HTML dentro de `output/` con el informe final, incluyendo:

* Panel resumen
* Tecnologías detectadas
* Tabla de CVEs con severidad, score, risk score, año y descripción

## Ejemplo de output

```text
+--------------------------------------------------------------------------------------+
| JobRecon Report — Telefonica                                                         |
+--------------------------------------------------------------------------------------+
| Fecha: 2026-04-21 | Ofertas: 15 | Tecnologías: 12 | CVEs: 8                         |
+--------------------------------------------------------------------------------------+
| TECNOLOGÍAS DETECTADAS                                                               |
| Python                ████████████████████ 18                                         |
| AWS                   ████████████████     14                                         |
| Docker                ████████████         11                                         |
| Kubernetes            ██████████            9                                         |
+--------------------------------------------------------------------------------------+
| CVEs ENCONTRADAS                                                                     |
| Severidad | Score | Risk | CVE ID         | Tecnología | Año | Descripción           |
|-----------+-------+------+----------------+------------+-----+-----------------------|
| CRITICAL  | 9.8   | 9.6  | CVE-2024-XXXX  | Kubernetes | 2024| RCE en componente ... |
| HIGH      | 8.7   | 8.4  | CVE-2023-XXXX  | Docker     | 2023| Escalada de privile...|
| MEDIUM    | 7.1   | 6.9  | CVE-2022-XXXX  | Python     | 2022| Validación incomple...|
+--------------------------------------------------------------------------------------+
```

## Cómo funciona

El flujo de JobRecon es el siguiente:

1. **Scraping**: recopila ofertas públicas de empleo de la empresa objetivo.
2. **Extracción**: identifica tecnologías, frameworks, productos y servicios mencionados.
3. **CVE lookup**: cruza cada tecnología con la base de datos NVD/CVEs del NIST.
4. **HTML report**: genera un informe visual en HTML con los hallazgos.

En resumen: **ofertas públicas → tecnologías inferidas → CVEs relacionadas → informe final**.

## Stack

* Python 3.11+
* requests
* BeautifulSoup4
* python-jobspy
* nvdlib
* Jinja2
* colorama
* python-dotenv

## Roadmap

### v1.1

* Normalización avanzada de tecnologías
* Filtrado semántico de menciones irrelevantes
* Mejora del scoring y deduplicación de CVEs

### v2.0

* Dashboard web
* Integración con Shodan
* Mejor navegación del reporte y filtros interactivos

## Disclaimer ético / legal

JobRecon está diseñado para **reconocimiento pasivo** y debe utilizarse únicamente en entornos autorizados. No está pensado para realizar intrusión, explotación ni actividad no autorizada sobre sistemas de terceros.

El usuario es responsable de cumplir la legislación aplicable, las políticas internas de su organización y el alcance de cualquier auditoría o ejercicio autorizado.

---

**JOBRECON — OSINT Tool | Passive Reconnaissance**
