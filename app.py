import random
from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
from core.risk import Reading, calculate_risk, PROFILES
from core.simulator import generate_reading
from core.storage import save_result, get_history

ROOT=Path(__file__).parent
DATA=ROOT/"data"
st.set_page_config(page_title="PredictivaJal | Industria 4.0",page_icon="🏭",layout="wide")
st.markdown("""<style>
.block-container{padding-top:1.3rem;max-width:1400px}.hero{padding:1.4rem 1.6rem;border-radius:16px;background:linear-gradient(120deg,#102a43,#176b87);color:#fff;margin-bottom:1rem}.hero h1{color:white;margin:0}.hero p{color:#e6f1f5;margin:.3rem 0 0}.note{padding:12px;border-left:4px solid #d69e2e;background:#fff8e6;border-radius:6px}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="hero"><h1>🏭 PredictivaJal</h1><p>Plataforma demostrativa de analítica industrial y mantenimiento predictivo para MIPYMES de Jalisco</p></div>',unsafe_allow_html=True)
with st.sidebar:
    st.title("PredictivaJal")
    page=st.radio("Módulos",["Resumen ejecutivo","Contexto económico de Jalisco","Evaluar una máquina","Simulador de sensores","Importar lecturas CSV","Directorio DENUE (opcional)","Historial","Metodología y fuentes"])
    st.divider(); st.caption("Prototipo académico · Reto 03 Industria 4.0")

@st.cache_data
def load_csv(name): return pd.read_csv(DATA/name)

def show_result(r):
    a,b,c=st.columns(3); a.metric("Índice de Riesgo de Falla",f"{r['irf']:.1f}/100"); b.metric("Clasificación",r['level']); c.metric("Variable dominante",r['dominant_variable'].capitalize())
    st.info(r['recommendation'])
    d=pd.DataFrame({"Variable":list(r['components']),"Nivel normalizado (%)":list(r['components'].values())})
    st.plotly_chart(px.bar(d,x="Variable",y="Nivel normalizado (%)",range_y=[0,100],title="Indicadores de condición por variable"),use_container_width=True)
    st.caption(r['model_note'])

if page=="Resumen ejecutivo":
    ce_m=load_csv("ce2024_municipios_jalisco.csv"); ce_s=load_csv("ce2024_sectores_jalisco.csv"); en=load_csv("enaproce2018_indicadores.csv")
    salto=ce_m[ce_m.municipio=="El Salto"].iloc[0]; manuf=ce_s[ce_s.sector=="Manufacturas"].iloc[0]
    st.subheader("Panorama y propósito")
    st.write("PredictivaJal combina contexto económico oficial de Jalisco con un módulo demostrativo que analiza lecturas de operación de maquinaria. Está pensado como apoyo para priorizar revisiones técnicas en MIPYMES; no sustituye mantenimiento profesional.")
    x1,x2,x3,x4=st.columns(4); x1.metric("Unidades económicas Jalisco",f"{int(ce_s.iloc[0].unidades_economicas):,}"); x2.metric("Personal ocupado Jalisco",f"{int(ce_s.iloc[0].personal_ocupado):,}"); x3.metric("Unidades manufactureras",f"{int(manuf.unidades_economicas):,}"); x4.metric("Empleo manufacturero",f"{int(manuf.personal_ocupado):,}")
    st.markdown("### ¿Por qué El Salto?")
    st.write(f"En los Censos Económicos 2024, El Salto representó **{salto.participacion_unidades_economicas_pct:.1f}%** de las unidades económicas de Jalisco, **{salto.participacion_personal_ocupado_pct:.1f}%** del personal ocupado, **{salto.participacion_remuneraciones_pct:.1f}%** de las remuneraciones y **{salto.participacion_vacb_pct:.1f}%** del valor agregado censal bruto (datos de referencia 2023).")
    st.markdown("### ¿Qué problema aborda?")
    micro=en[en.indicador=="microempresas_sin_monitoreo_indicadores_pct"].iloc[0]
    st.metric("Microempresas que no monitoreaban indicadores clave",f"{micro.valor_pct:.1f}%",help="ENAPROCE 2018; dato nacional con referencia principal a 2017, no estimación exclusiva de Jalisco.")
    st.caption("El sistema muestra contexto estadístico oficial y, por separado, lecturas de sensores simuladas o cargadas por el usuario.")

elif page=="Contexto económico de Jalisco":
    st.subheader("Datos oficiales que fundamentan la propuesta")
    m=load_csv("ce2024_municipios_jalisco.csv"); s=load_csv("ce2024_sectores_jalisco.csv"); e=load_csv("enaproce2018_indicadores.csv")
    st.markdown("**Dataset 20 — Censos Económicos 2024 (INEGI).** Los datos económicos del segmento privado/paraestatal corresponden al año 2023; el levantamiento fue en 2024.")
    st.dataframe(m,use_container_width=True,hide_index=True)
    fig=px.bar(m[m.municipio!="Total Jalisco"].sort_values("participacion_vacb_pct",ascending=False),x="municipio",y="participacion_vacb_pct",title="Participación municipal en el VACB de Jalisco (2023)",labels={"participacion_vacb_pct":"Participación (%)","municipio":"Municipio"})
    st.plotly_chart(fig,use_container_width=True)
    st.markdown("**Estructura sectorial de Jalisco (valores absolutos).** Las cifras monetarias están en millones de pesos corrientes de 2023.")
    st.dataframe(s,use_container_width=True,hide_index=True)
    st.markdown("**Dataset 23 — ENAPROCE 2018 (INEGI).** Indicadores nacionales; la referencia principal es 2017. No deben interpretarse como porcentajes específicos de El Salto o Jalisco.")
    st.dataframe(e[["descripcion","valor_pct","cobertura","periodo_referencia"]].rename(columns={"descripcion":"Indicador","valor_pct":"Porcentaje","cobertura":"Cobertura","periodo_referencia":"Periodo"}),use_container_width=True,hide_index=True)
    st.info("Uso en PredictivaJal: Censos Económicos caracteriza la presencia y peso del sector manufacturero en Jalisco y El Salto; ENAPROCE aporta evidencia nacional sobre brechas de monitoreo y prevención en MIPYMES. Ninguno de estos datasets contiene lecturas de sensores de máquinas.")

elif page=="Evaluar una máquina":
    st.subheader("Evaluación de condición")
    with st.form("evaluate"):
        a,b=st.columns(2); mid=a.text_input("Identificador de máquina", "MAQ-001"); mt=b.selectbox("Perfil demostrativo",list(PROFILES),format_func=lambda x:PROFILES[x]["name"])
        lim=PROFILES[mt]["limits"]; st.caption("Los límites y ponderaciones son parámetros ilustrativos; deben calibrarse con manuales y especialistas.")
        c,d=st.columns(2); temp=c.number_input("Temperatura (°C)",0.0,300.0,70.0,0.5); vib=d.number_input("Vibración RMS (mm/s)",0.0,50.0,2.0,0.1); cur=c.number_input("Corriente (A)",0.0,500.0,13.0,0.5); hrs=d.number_input("Horas acumuladas",0.0,200000.0,150.0,1.0)
        go=st.form_submit_button("Calcular IRF",type="primary",use_container_width=True)
    if go:
        try:
            r=calculate_risk(Reading(mid,mt,temp,vib,cur,hrs)); save_result(r); st.success("Evaluación guardada."); show_result(r)
        except ValueError as ex: st.error(str(ex))

elif page=="Simulador de sensores":
    st.subheader("Simulación para demostrar el funcionamiento")
    a,b,c=st.columns(3); mt=a.selectbox("Perfil",list(PROFILES),format_func=lambda x:PROFILES[x]["name"]); scenario=b.selectbox("Escenario",["normal","warning","critical","mixed"],format_func=lambda x:{"normal":"Normal","warning":"Advertencia","critical":"Crítico","mixed":"Mixto"}[x]); n=c.slider("Cantidad de lecturas",5,100,25)
    if st.button("Generar lecturas simuladas",type="primary"):
        rows=[]
        for i in range(n):
            rd=generate_reading(mt,scenario,f"SIM-{i+1:03d}"); r=calculate_risk(rd); save_result(r); rows.append({**rd.__dict__,"IRF":r["irf"],"Estado":r["level"]})
        st.session_state["sim_df"]=pd.DataFrame(rows); st.success(f"Se generaron {n} registros sintéticos. No son mediciones reales.")
    if "sim_df" in st.session_state:
        df=st.session_state["sim_df"]; st.dataframe(df,use_container_width=True,hide_index=True); st.plotly_chart(px.histogram(df,x="IRF",color="Estado",nbins=12,title="Distribución de IRF simulado"),use_container_width=True); st.download_button("Descargar simulación CSV",df.to_csv(index=False).encode("utf-8-sig"),"predictivajal_simulacion.csv","text/csv")

elif page=="Importar lecturas CSV":
    st.subheader("Procesamiento de datos de sensores")
    st.write("Columnas requeridas: machine_id, machine_type, temperature, vibration, current, hours. Tipo: inyectora o cnc.")
    template="machine_id,machine_type,temperature,vibration,current,hours\nMAQ-001,inyectora,70,2.1,14,180\nCNC-001,cnc,68,3.0,16,250\n"
    st.download_button("Descargar plantilla",template,"plantilla_sensores.csv","text/csv")
    file=st.file_uploader("Sube CSV de lecturas",type=["csv"])
    if file:
        try:
            df=pd.read_csv(file); required={"machine_id","machine_type","temperature","vibration","current","hours"}; miss=required-set(df.columns)
            if miss: st.error("Faltan columnas: "+", ".join(sorted(miss)))
            else:
                st.dataframe(df.head(30),use_container_width=True,hide_index=True)
                if st.button("Procesar CSV",type="primary"):
                    out=[]; errors=[]
                    for i,row in df.iterrows():
                        try:
                            r=calculate_risk(Reading(str(row.machine_id),str(row.machine_type),float(row.temperature),float(row.vibration),float(row.current),float(row.hours))); save_result(r); out.append({"fila":i+2,"machine_id":r["machine_id"],"IRF":r["irf"],"Estado":r["level"]})
                        except Exception as ex: errors.append(f"Fila {i+2}: {ex}")
                    st.success(f"Procesadas: {len(out)}"); st.dataframe(pd.DataFrame(out),use_container_width=True,hide_index=True)
                    if errors: st.warning("\\n".join(errors[:15]))
        except Exception as ex: st.error(f"No se pudo leer el CSV: {ex}")

elif page=="Directorio DENUE (opcional)":
    st.subheader("Directorio de unidades económicas — DENUE")
    st.write("El catálogo del reto incluye DENUE (dataset 09). Esta pantalla permite incorporar un CSV descargado del INEGI para filtrar establecimientos manufactureros. El archivo no se incluye porque la descarga oficial masiva puede ser grande y el acceso API requiere token gratuito.")
    st.markdown("[Abrir DENUE de INEGI](https://www.inegi.org.mx/app/mapa/denue/Default.aspx) · [Documentación de API DENUE](https://www.inegi.org.mx/servicios/api_denue.html) · [Descarga masiva](https://www.inegi.org.mx/app/descarga/?ag=14)")
    den=st.file_uploader("Cargar CSV DENUE (si ya lo descargaste)",type=["csv"],key="denue")
    if den:
        try:
            d=pd.read_csv(den,encoding_errors="replace",low_memory=False); st.write(f"Registros cargados: {len(d):,}"); st.dataframe(d.head(30),use_container_width=True)
            cols=list(d.columns); search=st.text_input("Filtrar por municipio, actividad o nombre (si las columnas existen)","El Salto")
            mask=pd.Series(False,index=d.index)
            for col in cols:
                if any(k in col.lower() for k in ["municipio","ubicacion","actividad","nombre"]): mask=mask|d[col].astype(str).str.contains(search,case=False,na=False)
            st.dataframe(d[mask].head(500),use_container_width=True)
            st.download_button("Descargar registros filtrados",d[mask].to_csv(index=False).encode("utf-8-sig"),"denue_filtrado.csv","text/csv")
        except Exception as ex: st.error(f"No se pudo procesar el archivo: {ex}")

elif page=="Historial":
    st.subheader("Historial local de evaluaciones")
    hist=get_history(1000)
    if hist:
        df=pd.DataFrame([{"Fecha":x["created_at"],"Máquina":x["machine_id"],"Perfil":x["machine_type"],"IRF":x["irf"],"Estado":x["level"]} for x in hist]); st.dataframe(df,use_container_width=True,hide_index=True); st.download_button("Exportar historial",df.to_csv(index=False).encode("utf-8-sig"),"historial_predictivajal.csv","text/csv")
    else: st.info("Todavía no hay evaluaciones guardadas. Prueba Evaluar una máquina o Simulador de sensores.")

else:
    st.subheader("Metodología, disciplinas y fuentes")
    st.markdown("""
**Áreas de conocimiento integradas**
- **Programación:** aplicación web, procesamiento CSV, motor de reglas y almacenamiento SQLite.
- **Matemáticas / estadística:** normalización de variables, ponderación y análisis descriptivo de indicadores económicos.
- **Ingeniería industrial:** monitoreo de condición, priorización de inspecciones y mantenimiento preventivo/predictivo.

**Cálculo del IRF**

Cada variable se normaliza entre un valor nominal y uno crítico (ambos ilustrativos), se limita al intervalo 0–1 y se multiplica por su peso. `IRF = 100 × suma(peso × valor_normalizado)`. Normal <40; Advertencia 40–<70; Crítico ≥70.

**Límites:** no es una predicción estadística entrenada ni una probabilidad de falla; no estima vida útil restante. Los datos de sensores se simulan o se cargan como CSV. Los límites deben validarse para cada equipo con manuales de fabricante y personal técnico. El panel económico usa datos agregados oficiales; no contiene telemetría industrial.

**Dataset 20 — INEGI, Censos Económicos 2024, Jalisco.** Cobertura estatal y municipal; los indicadores económicos de unidades privadas/paraestatales se refieren a 2023. Se incorporan participación municipal, establecimientos, empleo, producción y valor agregado.

**Dataset 23 — INEGI, ENAPROCE 2018.** Cobertura nacional; la referencia principal de resultados es 2017. Se incorporan indicadores sobre monitoreo de desempeño y acciones ante problemas productivos. No se presentan como estimaciones específicas de Jalisco.

**Uso de IA:** se utilizó ChatGPT como apoyo para estructurar y generar código y documentación; el equipo debe revisar, probar y declarar este apoyo en su presentación.
""")
    st.markdown("**Fuentes oficiales**")
    st.markdown("- [INEGI — Censos Económicos 2024](https://www.inegi.org.mx/programas/ce/2024/default.html)")
    st.markdown("- [INEGI — Minimonografía Jalisco, Censos Económicos 2024 (PDF)](https://www.inegi.org.mx/contenidos/programas/ce/2024/doc/mjal_ce24.pdf)")
    st.markdown("- [INEGI — ENAPROCE 2018](https://www.inegi.org.mx/programas/enaproce/2018/default.html)")
    st.markdown("- [Secretaría de Economía — resultados ENAPROCE 2018](https://www.gob.mx/se/prensa/inegi-presenta-resultados-de-la-encuesta-nacional-sobre-productividad-y-competitividad-de-las-mipymes-enaproce-2018-215878)")
    st.markdown("- [INEGI — DENUE (adicional opcional)](https://www.inegi.org.mx/app/mapa/denue/Default.aspx)")

st.divider(); st.caption("PredictivaJal · Prototipo académico · Reto 03 Industria 4.0 · Jalisco, México")
