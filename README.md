# PredictivaJal — Prototipo Hackathon Jalisco 2026

Aplicación web demostrativa para contextualizar la industria de Jalisco y calcular un Índice de Riesgo de Falla (IRF) heurístico con lecturas de maquinaria.

## Ejecutar en Windows
1. Instala Python 3.10 o superior.
2. Descomprime la carpeta.
3. Haz doble clic en `INICIAR_WINDOWS.bat` o abre terminal en la carpeta y ejecuta:
   ```bash
   py -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Ejecutar en macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Ejecutar API
En otra terminal con el entorno activado: `uvicorn api:app --reload`. Documentación: `http://127.0.0.1:8000/docs`.

## Pruebas
Desde la carpeta del proyecto: `python -m unittest discover -s tests -v`.

## Datasets oficiales incorporados
- **Dataset 20 — INEGI, Censos Económicos 2024, Jalisco.** Los CSV incluidos contienen tablas agregadas de la Minimonografía Jalisco. La cobertura incluye el estado y municipios seleccionados. Los valores económicos del sector privado y empresas paraestatales se refieren principalmente a 2023. Se usa para contextualizar el peso económico del municipio de El Salto y el sector manufacturero.
- **Dataset 23 — INEGI, ENAPROCE 2018.** Se incluyen indicadores nacionales publicados por INEGI/Secretaría de Economía; la referencia principal es 2017. Se usa para describir brechas de monitoreo y mejora de procesos en MIPYMES. No debe confundirse con datos específicos de Jalisco.
- **DENUE (dataset 09)** está disponible como módulo opcional para cargar un CSV descargado de INEGI. La API oficial requiere token de acceso; no se incluye token en el proyecto.

## Cómo se usan los datos
1. El CSV `ce2024_municipios_jalisco.csv` muestra participaciones municipales en unidades económicas, empleo, remuneraciones y VACB. El dato de El Salto fundamenta la delimitación territorial.
2. `ce2024_sectores_jalisco.csv` muestra magnitudes económicas del sector manufacturero y otros sectores en Jalisco.
3. `enaproce2018_indicadores.csv` aporta contexto nacional sobre monitoreo de indicadores y acciones ante problemas productivos en MIPYMES.
4. El módulo de IRF usa datos de sensores introducidos manualmente, importados por CSV o simulados. Estos datos de sensores NO son parte de los datasets oficiales.

## Modelo y limitaciones
El IRF es una regla ponderada y transparente, con escala de 0 a 100. Normal <40; Advertencia 40–<70; Crítico >=70. Los umbrales y pesos son ilustrativos y no han sido validados en máquinas reales. El IRF no es una probabilidad estadística de falla ni estima vida útil restante. No debe usarse para decisiones de seguridad u operación sin validación técnica.

## Áreas de conocimiento
- Programación: aplicación, procesamiento CSV, API y base de datos SQLite.
- Matemáticas/estadística: normalización, ponderación y análisis descriptivo.
- Ingeniería industrial: monitoreo de condición y priorización de inspecciones.

## Uso de IA
Se utilizó ChatGPT como apoyo para generación y revisión de código y documentación. El equipo debe declarar este uso conforme al kit.

## Fuentes
- INEGI, Censos Económicos 2024: https://www.inegi.org.mx/programas/ce/2024/default.html
- INEGI, Minimonografía Jalisco CE2024: https://www.inegi.org.mx/contenidos/programas/ce/2024/doc/mjal_ce24.pdf
- INEGI, ENAPROCE 2018: https://www.inegi.org.mx/programas/enaproce/2018/default.html
- Secretaría de Economía, resultados ENAPROCE 2018: https://www.gob.mx/se/prensa/inegi-presenta-resultados-de-la-encuesta-nacional-sobre-productividad-y-competitividad-de-las-mipymes-enaproce-2018-215878
- INEGI, DENUE: https://www.inegi.org.mx/app/mapa/denue/Default.aspx
- API DENUE: https://www.inegi.org.mx/servicios/api_denue.html

## Nota de entrega
Este proyecto es un prototipo académico funcional. No se afirma que el modelo esté validado industrialmente ni que haya reducido paros de producción. Antes de presentar, ejecuta el proyecto y muestra el flujo con simulación, explicando claramente qué es dato oficial y qué es dato sintético.
