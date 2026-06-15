import streamlit as st
import xml.etree.ElementTree as ET
import re

# ==========================================
# 1. BPMN PARSER ENGINE
# ==========================================
def parse_bpmn_xml(xml_content):
    """
    Parst den BPMN-XML-String und sucht flexibel nach relevanten Elementen,
    unabhängig davon, welche spezifischen Namensräume (bpmn:, bpmn2:, etc.) genutzt werden.
    """
    metrics = {
        "lanes": [],
        "service_tasks": [],
        "user_tasks": [],
        "sub_processes": [],
        "has_loops": False
    }
    
    try:
        # Dekodieren, falls es sich um Bytes handelt
        if isinstance(xml_content, bytes):
            xml_content = xml_content.decode("utf-8")
            
        # XML-Wurzel auflösen
        root = ET.fromstring(xml_content)
        
        # Nutzen von regulären Ausdrücken/lokalen Namen, um Namespace-Fehler zu vermeiden
        for elem in root.iter():
            # Lokalen Namen ohne Namespace extrahieren
            local_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            if local_name == "lane":
                lane_name = elem.get("name", f"Lane_{len(metrics['lanes'])+1}")
                metrics["lanes"].append(lane_name)
            elif local_name in ["serviceTask", "sendTask", "receiveTask"]:
                task_name = elem.get("name", f"ServiceTask_{len(metrics['service_tasks'])+1}")
                metrics["service_tasks"].append(task_name)
            elif local_name == "userTask":
                task_name = elem.get("name", f"UserTask_{len(metrics['user_tasks'])+1}")
                metrics["user_tasks"].append(task_name)
            elif local_name == "subProcess":
                sub_name = elem.get("name", f"SubProcess_{len(metrics['sub_processes'])+1}")
                metrics["sub_processes"].append(sub_name)
                
        # Einfacher Heuristik-Check für Loops: Gibt es Sequenzflüsse, die rückwärts zeigen?
        # In einem echten Camunda XML suchen wir nach kreuzenden sourceRef/targetRef IDs.
        # Für den Prototyp prüfen wir, ob das Wort "loop" oder "revert" im XML vorkommt.
        if "loop" in xml_content.lower() or "revert" in xml_content.lower() or "zurück" in xml_content.lower():
            metrics["has_loops"] = True
            
    except Exception as e:
        st.error(f"Fehler beim Parsen der XML-Struktur: {e}")
        
    return metrics

# ==========================================
# 2. CODE SKELETON GENERATOR (TEMPLATES)
# ==========================================
def generate_crewai_code(lanes, tools):
    agent_definitions = ""
    task_definitions = ""
    
    for i, lane in enumerate(lanes):
        var_name = re.sub(r'[^a-zA-Z0-9_]', '', lane.lower().replace(" ", "_"))
        agent_definitions += f"""
{var_name}_agent = Agent(
    role='{lane} Expert',
    goal='Verarbeite die spezifischen Aufgaben für den Bereich {lane}',
    backstory='Du bist ein hochspezialisierter KI-Agent, der aus der BPMN-Prozesslane {lane} abgeleitet wurde.',
    verbose=True,
    allow_delegation=False
)
"""
        task_definitions += f"""
task_{i} = Task(
    description='Führe die Prozessschritte für {lane} aus.',
    expected_output='Erfolgreicher Abschluss des Teilprozesses für {lane}.',
    agent={var_name}_agent
)
"""
    
    code = f"""# Generierter CrewAI Pipeline-Blueprint
from crewai import Agent, Task, Crew, Process

# --- AGENTEN DEFINITIONEN ---{agent_definitions}
# --- TASK DEFINITIONEN ---{task_definitions}
# --- CREW SETUP (SEQUENZIELL) ---
crew = Crew(
    agents=[{", ".join([re.sub(r'[^a-zA-Z0-9_]', '', l.lower().replace(" ", "_")) + "_agent" for l in lanes])}],
    tasks=[{", ".join([f"task_{i}" for i in range(len(lanes))])}],
    process=Process.sequential
)

# result = crew.kickoff()
"""
    return code

def generate_langgraph_code(lanes, tools, has_user_task):
    nodes_code = ""
    edges_code = ""
    
    # Falls Single Agent
    if len(lanes) <= 1:
        lanes = ["MainAgent"]
        
    for lane in lanes:
        var_name = re.sub(r'[^a-zA-Z0-9_]', '', lane.lower().replace(" ", "_"))
        nodes_code += f"""
def {var_name}_node(state: AgentState):
    print("Executing steps for: {lane}")
    # Hier Logik einfügen
    return {{"messages": state["messages"] + ["{lane} verarbeitet."]}}
workflow.add_node("{var_name}", {var_name}_node)
"""
    
    # Erstelle lineare Kette für die Nodes
    for i in range(len(lanes)-1):
        from_node = re.sub(r'[^a-zA-Z0-9_]', '', lanes[i].lower().replace(" ", "_"))
        to_node = re.sub(r'[^a-zA-Z0-9_]', '', lanes[i+1].lower().replace(" ", "_"))
        edges_code += f'workflow.add_edge("{from_node}", "{to_node}")\n'
        
    start_node = re.sub(r'[^a-zA-Z0-9_]', '', lanes[0].lower().replace(" ", "_"))
    end_node = re.sub(r'[^a-zA-Z0-9_]', '', lanes[-1].lower().replace(" ", "_"))
    
    code = f"""# Generierter LangGraph Stateful Blueprint
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    messages: Sequence[BaseMessage]

workflow = StateGraph(AgentState)

# --- NODES DEFINITIONEN ---{nodes_code}
# --- EDGES DEFINITIONEN ---
workflow.set_entry_point("{start_node}")
{edges_code}workflow.add_edge("{end_node}", END)

# --- MEMORY & COMPILE ---
# Memory ermöglicht Zustandshaltung über Schleifen hinweg
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

app = workflow.compile(
    checkpointer=memory,
    # Human-in-the-loop Unterbrechung falls UserTasks im BPMN gefunden wurden
    {"interrupt_before=['" + end_node + "']" if has_user_task else ""}
)
"""
    return code

# ==========================================
# 3. STREAMLIT UI & HYBRID LOGIC
# ==========================================
st.set_page_config(page_title="Enterprise Agent Architect", layout="wide", page_icon="🤖")

st.title("🤖 Enterprise Agent Architect")
st.subheader("Übersetze BPMN-Geschäftsprozesse in KI-Agenten-Architekturen")

# Zwei Spalten für die beiden Eingabe-Methoden
tabs = st.tabs(["📁 Lösung 1: BPMN XML Upload (Automatisch)", "📋 Lösung 2: Interaktiver Fragebogen (Manuell)"])

# Shared State Initialisierung
if "metrics" not in st.session_state:
    st.session_state.metrics = None

# ------------------------------------------
# TAB 1: BPMN XML UPLOAD
# ------------------------------------------
with tabs[0]:
    st.write("Lade eine `.bpmn`- oder `.xml`-Datei aus Camunda, Signavio o.ä. hoch.")
    uploaded_file = st.file_uploader("BPMN Datei auswählen", type=["bpmn", "xml"], key="bpmn_uploader")
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        st.session_state.metrics = parse_bpmn_xml(file_bytes)
        st.success("BPMN-Struktur erfolgreich analysiert!")

# ------------------------------------------
# TAB 2: INTERAKTIVER FRAGEBOGEN
# ------------------------------------------
with tabs[1]:
    st.write("Falls kein BPMN-Diagramm vorliegt, kannst du die harten Faktoren hier manuell definieren.")
    col1, col2 = st.columns(2)
    with col1:
        manual_lanes = st.number_input("Wie viele unterschiedliche Rollen/Lanes hat der Prozess?", min_value=1, value=1)
        manual_services = st.number_input("Wie viele System-Schnittstellen (APIs/Service Tasks) gibt es?", min_value=0, value=0)
    with col2:
        manual_users = st.number_input("Wie viele manuelle Freigaben (User Tasks) gibt es?", min_value=0, value=0)
        manual_loops = st.checkbox("Gibt es Rückschleifen (Wiederholungen bei Fehlern)?")
        
    if st.button("Manuelle Daten übernehmen"):
        st.session_state.metrics = {
            "lanes": [f"Rolle_{i+1}" for i in range(manual_lanes)],
            "service_tasks": [f"API_{i+1}" for i in range(manual_services)],
            "user_tasks": [f"MenschlicheFreigabe_{i+1}" for i in range(manual_users)],
            "sub_processes": [],
            "has_loops": manual_loops
        }
        st.success("Manuelle Daten geladen! Scrolle nach unten für die weichen Faktoren.")

# ==========================================
# GEMEINSAME AUSWERTUNG (Wenn Daten vorhanden)
# ==========================================
if st.session_state.metrics is not None:
    m = st.session_state.metrics
    
    st.markdown("---")
    st.header("📊 Schritt 1: Extrahierte Prozess-Metriken (Harte Faktoren)")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Identifizierte Rollen (Lanes)", len(m["lanes"]))
    c2.metric("Schnittstellen (Service Tasks)", len(m["service_tasks"]))
    c3.metric("Menschliche Interaktionen", len(m["user_tasks"]))
    c4.metric("Schleifen/Wiederholungen", "Ja" if m["has_loops"] else "Nein")
    
    with st.expander("Details der erkannten Elemente anzeigen"):
        st.write("**Gefundene Lanes/Rollen:**", m["lanes"])
        st.write("**Gefundene IT-Schnittstellen:**", m["service_tasks"])
        st.write("**Gefundene User-Freigaben:**", m["user_tasks"])

    # ------------------------------------------
    # SCHRITT 2: DYNAMISCHE WEICHE FAKTOREN
    # ------------------------------------------
    st.header("🧠 Schritt 2: Strategische Anforderungen (Weiche Faktoren)")
    st.write("Basierend auf den obigen Metriken benötigt das System noch folgende kaufmännische Informationen:")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        compliance = st.radio(
            "Wie kritisch ist die strikte Einhaltung von Compliance und Kontrollierbarkeit?",
            ["Hoch (Fehlerquote muss nahe 0% sein, klare Hierarchie)", "Mittel (Standard-Pipeline reicht)", "Niedrig (Kreativität und autonomes Handeln erwünscht)"]
        )
        latency = st.radio(
            "Welche Antwortgeschwindigkeit (Latenz) wird erwartet?",
            ["Echtzeit (< 3 Sekunden für Live-Chat)", "Asynchron (Darf im Hintergrund einige Minuten laufen)"]
        )
    
    with col_right:
        budget = st.select_slider(
            "Wie hoch ist das Token-Budget für diesen Prozess?",
            options=["Minimal (Kleine Open-Source Modelle / Wenig Agenten-Chats)", "Medium", "Unbegrenzt (Maximale Agenten-Diskussion / GPT-4o)"]
        )
        
    # ------------------------------------------
    # SCHRITT 3: RECOMMENDATION ENGINE & CODE GENERATOR
    # ------------------------------------------
    if st.button("🎯 Optimale KI-Agenten-Architektur berechnen"):
        st.markdown("---")
        st.header("🏆 Architektur-Empfehlung & Code-Blueprint")
        
        # Logik-Entscheidungsbaum
        is_multi = len(m["lanes"]) > 1 or len(m["sub_processes"]) > 0
        
        rec_architecture = ""
        rec_framework = ""
        rec_reasoning = []
        generated_code = ""
        
        if is_multi:
            rec_architecture = "Multi-Agenten-System (MAS)"
            rec_reasoning.append(f"Da {len(m['lanes'])} unterschiedliche organisatorische Lanes gefunden wurden, müssen spezialisierte Agenten-Personas gebaut werden, um Kontext-Überlastung zu vermeiden.")
            
            if compliance == "Hoch (Fehlerquote muss nahe 0% sein, klare Hierarchie)":
                rec_framework = "LangGraph (Hierarchical Supervisor Pattern)"
                rec_reasoning.append("LangGraph wird gewählt, da es deterministische Zustandsdiagramme erlaubt. Ein Supervisor-Agent übernimmt die hierarchische Führung.")
                generated_code = generate_langgraph_code(m["lanes"], m["service_tasks"], len(m["user_tasks"]) > 0)
            else:
                rec_framework = "CrewAI (Sequential / Pipeline Process)"
                rec_reasoning.append("Da ein linearer Ablauf ohne extreme Governance-Vorgaben vorliegt, bietet CrewAI eine schnelle, sequenzielle Fließband-Pipeline.")
                generated_code = generate_crewai_code(m["lanes"], m["service_tasks"])
        else:
            rec_architecture = "Single-Agent-System (SAS)"
            rec_reasoning.append("Der Prozess findet in einer einzigen Rolle statt. Ein einzelner, mächtiger Agent ist wirtschaftlicher.")
            
            if m["has_loops"] or latency == "Asynchron (Darf im Hintergrund einige Minuten laufen)":
                rec_framework = "LangGraph (Stateful Agent / Model-Based Reflex)"
                rec_reasoning.append("Aufgrund der identifizierten Schleifen (Loops) im Prozess ist ein explizites State-Management via LangGraph nötig, damit der Agent weiß, in welcher Iteration er sich befindet.")
                generated_code = generate_langgraph_code(["HauptAgent"], m["service_tasks"], len(m["user_tasks"]) > 0)
            else:
                rec_framework = "LangChain / Tool-Calling Agent (Goal-Based)"
                rec_reasoning.append("Ein einfacher, zielbasierter ReAct- oder Tool-Calling-Agent reicht aus, um die Service-Schnittstellen direkt anzusteuern.")
                generated_code = generate_langgraph_code(["ToolAgent"], m["service_tasks"], len(m["user_tasks"]) > 0)
                
        # Ausgabe des Berichts
        res_col1, res_col2 = st.columns([1, 2])
        
        with res_col1:
            st.metric("Empfohlene Architektur", rec_architecture)
            st.metric("Empfohlenes Framework", rec_framework)
            
            st.write("**Begründung des Systems:**")
            for reason in rec_reasoning:
                st.write(f"- {reason}")
                
            if len(m["service_tasks"]) > 0:
                st.info(f"💡 System-Tipp: Registriere die erkannten Schnittstellen ({', '.join(m['service_tasks'])}) als Python-Tools via `@tool`-Dekorator.")
            if len(m["user_tasks"]) > 0:
                st.warning("⚠️ Human-in-the-Loop: Der generierte Code enthält eine automatische Unterbrechung für menschliche Freigaben.")

        with res_col2:
            st.write("### 💻 Fahrbereiter Python Code-Blueprint")
            st.code(generated_code, language="python")
            
            # Download Button für das fertige Code-Skelett
            st.download_button(
                label="📥 Python-Blueprint herunterladen",
                data=generated_code,
                file_name="agent_architecture_blueprint.py",
                mime="text/plain"
            )