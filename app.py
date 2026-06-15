import streamlit as st
import xml.etree.ElementTree as ET
import re
import html as html_module
from datetime import datetime

# ==========================================
# 1. AGENTENTYPEN-WISSENSDATENBANK
# ==========================================
AGENT_TYPES = {
    "simple_reflex": {
        "name": "Simple Reflex Agent",
        "icon": "⚡",
        "color": "#4ECDC4",
        "gradient": "linear-gradient(135deg, #4ECDC4, #44A08D)",
        "kurz": "Reagiert auf aktuelle Eingaben mit festen Wenn-Dann-Regeln. Kein Gedächtnis, keine Planung.",
        "beschreibung": (
            "Simple Reflex Agents sind die einfachste Form intelligenter Agenten. "
            "Sie arbeiten mit einem festen Regelwerk aus Wenn-Dann-Bedingungen und reagieren "
            "ausschließlich auf den aktuellen Sensorinput. Sie speichern keine vergangenen Erfahrungen "
            "und nutzen kein internes Modell der Umgebung."
        ),
        "staerken": [
            "Einfache Implementierung und geringer Ressourcenbedarf",
            "Hohe Zuverlässigkeit bei klar definierten Regeln",
            "Schnelle Reaktionszeiten",
            "Gut geeignet für deterministische Umgebungen",
        ],
        "schwaechen": [
            "Kein Gedächtnis für vergangene Zustände",
            "Fehleranfällig bei unvollständigen Regeln",
            "Ungeeignet für dynamische Umgebungen",
            "Keine Lernfähigkeit",
        ],
        "use_cases": [
            "Passwort-Reset auf Basis von Schlüsselwörtern",
            "Thermostat-Steuerung (Temperaturregeln)",
            "Einfache Chatbot-Antworten auf FAQ",
            "Basis-Robotersteuerung (Staubsauger)",
        ],
    },
    "model_based_reflex": {
        "name": "Model-Based Reflex Agent",
        "icon": "🧩",
        "color": "#A78BFA",
        "gradient": "linear-gradient(135deg, #A78BFA, #7C3AED)",
        "kurz": "Nutzt ein internes Modell der Umgebung, um auch nicht direkt beobachtbare Zustände einzubeziehen.",
        "beschreibung": (
            "Model-Based Reflex Agents erweitern einfache Reflex-Agenten um ein internes Modell "
            "der Umgebung. Sie berücksichtigen neben dem aktuellen Sensorinput auch einen internen "
            "Zustand, der Aspekte der Umgebung repräsentiert, die nicht direkt beobachtbar sind. "
            "Ihr Entscheidungsprozess umfasst die Wahrnehmung durch Sensoren, die Aktualisierung "
            "des internen Modells und die regelbasierte oder ML-gestützte Entscheidungsfindung."
        ),
        "staerken": [
            "Bessere Entscheidungen durch Umgebungsverständnis",
            "Anpassungsfähiger als Simple Reflex Agents",
            "Kann auf teilweise beobachtbare Umgebungen reagieren",
            "Kontinuierliche Modellaktualisierung",
        ],
        "schwaechen": [
            "Höherer Rechenaufwand für Modellpflege",
            "Komplexität des Umgebungsmodells kann schwierig sein",
            "Keine Zielplanung oder Optimierung",
            "Modellgenauigkeit bestimmt Entscheidungsqualität",
        ],
        "use_cases": [
            "Fertigungssysteme mit Maschinenausfallvorhersage",
            "Lagerverwaltung mit Bestandsprognosen",
            "Verkehrsüberwachung mit Zustandserkennung",
            "Smart-Home-Systeme mit Kontextverständnis",
        ],
    },
    "goal_based": {
        "name": "Goal-Based Agent",
        "icon": "🎯",
        "color": "#F59E0B",
        "gradient": "linear-gradient(135deg, #F59E0B, #D97706)",
        "kurz": "Plant vorausschauend, um spezifische Ziele zu erreichen – nutzt Such- und Planungsalgorithmen.",
        "beschreibung": (
            "Goal-Based Agents sind KI-Systeme, die darauf ausgelegt sind, spezifische Ziele "
            "zu erreichen. Sie nutzen Such- und Planungsalgorithmen, um den effizientesten Weg "
            "zum gewünschten Ergebnis zu finden. Im Gegensatz zu Reflex-Agenten sind sie "
            "zukunftsorientiert und bewerten potenzielle Szenarien, um ihre Strategien anzupassen."
        ),
        "staerken": [
            "Vorausschauende Planung und Optimierung",
            "Anpassung an sich ändernde Bedingungen",
            "Hohe Autonomie mit minimaler menschlicher Intervention",
            "Effiziente Pfadfindung zum Ziel",
        ],
        "schwaechen": [
            "Höhere Komplexität in Design und Implementierung",
            "Kann bei unklaren Zielen suboptimal agieren",
            "Erfordert gute Zieldefinition",
            "Rechenintensiver als Reflex-Agenten",
        ],
        "use_cases": [
            "Autonome Fahrzeuge (Routenplanung)",
            "Spielstrategie-KI",
            "Automatisiertes Design und Prototyping",
            "Personalisiertes Marketing mit Zieloptimierung",
        ],
    },
    "utility_based": {
        "name": "Utility-Based Agent",
        "icon": "⚖️",
        "color": "#EF4444",
        "gradient": "linear-gradient(135deg, #EF4444, #DC2626)",
        "kurz": "Bewertet Szenarien mit einer Nutzenfunktion und optimiert zwischen konkurrierenden Zielen.",
        "beschreibung": (
            "Utility-Based Agents nutzen komplexe Bewertungsalgorithmen, um das bestmögliche Ergebnis "
            "zu erzielen. Eine Nutzenfunktion (Utility Function) weist verschiedenen Zuständen Werte "
            "basierend auf ihrer Wünschbarkeit zu. Der Agent wählt Aktionen, die zu Zuständen mit hohem "
            "Nutzen führen und balanciert dabei mehrere Ziele wie Kosten, Qualität oder Zeit."
        ),
        "staerken": [
            "Optimale Abwägung zwischen konkurrierenden Zielen",
            "Kontinuierliche Strategieanpassung an neue Daten",
            "Quantitative Bewertung verschiedener Szenarien",
            "Flexibel in dynamischen Umgebungen",
        ],
        "schwaechen": [
            "Benötigt ein akkurates Umgebungsmodell",
            "Sehr rechenintensiv (Szenariobewertung)",
            "Nutzenfunktion kann schwer zu definieren sein",
            "Hohe Betriebskosten",
        ],
        "use_cases": [
            "Finanzhandel (Renditeoptimierung)",
            "Logistik-Optimierung (Kosten vs. Lieferzeit)",
            "Kundenservice (Produkt-Empfehlungen)",
            "Energiemanagement (Last-Optimierung)",
        ],
    },
    "learning": {
        "name": "Learning Agent",
        "icon": "📚",
        "color": "#10B981",
        "gradient": "linear-gradient(135deg, #10B981, #059669)",
        "kurz": "Verbessert seine Leistung über die Zeit durch Lernen aus Erfahrungen und Feedback.",
        "beschreibung": (
            "Learning Agents sind darauf ausgelegt, ihre Leistung über die Zeit zu verbessern. "
            "Sie starten mit Basiswissen und verfeinern ihre Aktionen durch Machine-Learning-Techniken. "
            "Ihre Architektur umfasst vier Schlüsselkomponenten: ein Lernelement (aktualisiert Wissen), "
            "einen Kritiker (bewertet Leistung), ein Performanz-Element (trifft Entscheidungen) und "
            "einen Problemgenerator (stellt neue Herausforderungen)."
        ),
        "staerken": [
            "Kontinuierliche Verbesserung der Leistung",
            "Anpassung an neue Muster und Trends",
            "Kann aus Feedback-Schleifen lernen",
            "Vielseitig in verschiedenen Domänen einsetzbar",
        ],
        "schwaechen": [
            "Benötigt große Datenmengen zum Trainieren",
            "Hohe Entwicklungs- und Wartungskosten",
            "Anfällige Trainingsphase (Kaltstart-Problem)",
            "Schwer interpretierbare Entscheidungen",
        ],
        "use_cases": [
            "Personalisierte Empfehlungssysteme",
            "Medizinische Diagnostik und Behandlungsplanung",
            "Betrugserkennung im Finanzwesen",
            "Adaptive Qualitätskontrolle in der Fertigung",
        ],
    },
    "hierarchical": {
        "name": "Hierarchical Agent",
        "icon": "🏛️",
        "color": "#3B82F6",
        "gradient": "linear-gradient(135deg, #3B82F6, #2563EB)",
        "kurz": "Mehrstufiges Agentensystem mit klarer Hierarchie – übergeordnete Agenten delegieren an untergeordnete.",
        "beschreibung": (
            "Hierarchical Agents sind strukturierte Sammlungen von Agenten in einem mehrstufigen System. "
            "Übergeordnete Agenten setzen Ziele und Rahmenbedingungen, die an untergeordnete Agenten "
            "weitergegeben werden. Diese Struktur kann einfach (zwei Ebenen) oder komplex (mit "
            "Zwischenebenen zur Koordination) sein."
        ),
        "staerken": [
            "Reduzierung doppelter Arbeit durch Delegation",
            "Schnellere Entscheidungsfindung auf jeder Ebene",
            "Effiziente Nutzung von Ressourcen",
            "Skalierbar für komplexe Organisationen",
        ],
        "schwaechen": [
            "Feste Hierarchien können Anpassungsfähigkeit einschränken",
            "Komplexes Training über mehrere Ebenen",
            "Schwer für andere Anwendungsfälle umzuwidmen",
            "Hoher Koordinationsaufwand zwischen Ebenen",
        ],
        "use_cases": [
            "Transportmanagementsysteme (Verkehr & Routing)",
            "Unternehmensweite Prozessautomatisierung",
            "Militärische Einsatzplanung",
            "Supply-Chain-Management mit Regionskoordination",
        ],
    },
}


# ==========================================
# 2. ERWEITERTER BPMN PARSER
# ==========================================
def _sanitize_dot_label(text):
    """Bereinigt Text für DOT-Graphen (Sonderzeichen escapen)."""
    if not text:
        return ""
    text = text.replace('"', '\\"')
    text = text.replace('\n', '\\n')
    text = text.replace('<', '\\<')
    text = text.replace('>', '\\>')
    # Kürze zu lange Labels
    if len(text) > 30:
        text = text[:27] + "..."
    return text


def parse_bpmn_xml(xml_content):
    """
    Erweiterter BPMN-Parser: Extrahiert Metriken UND Flussdaten für Visualisierung.
    Gibt (metrics, flow_data) zurück.
    """
    metrics = {
        "lanes": [],
        "service_tasks": [],
        "user_tasks": [],
        "sub_processes": [],
        "gateways": {"exclusive": 0, "parallel": 0, "inclusive": 0, "event_based": 0},
        "total_tasks": 0,
        "sequence_flows": 0,
        "has_loops": False,
        "end_events": 0,
        "start_events": 0,
        "script_tasks": [],
        "business_rule_tasks": [],
    }

    flow_data = {
        "nodes": {},   # id -> {"name": str, "type": str}
        "edges": [],   # [{"source": id, "target": id, "name": str}]
    }

    try:
        if isinstance(xml_content, bytes):
            xml_content = xml_content.decode("utf-8")

        root = ET.fromstring(xml_content)

        for elem in root.iter():
            local_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            elem_id = elem.get("id", "")
            elem_name = elem.get("name", "")

            # --- Start Events ---
            if local_name == "startEvent":
                metrics["start_events"] += 1
                if elem_id:
                    flow_data["nodes"][elem_id] = {
                        "name": elem_name or "Start",
                        "type": "start",
                    }

            # --- End Events ---
            elif local_name == "endEvent":
                metrics["end_events"] += 1
                if elem_id:
                    flow_data["nodes"][elem_id] = {
                        "name": elem_name or "Ende",
                        "type": "end",
                    }

            # --- Lanes ---
            elif local_name == "lane":
                lane_name = elem_name or f"Lane_{len(metrics['lanes'])+1}"
                metrics["lanes"].append(lane_name)

            # --- Service-ähnliche Tasks ---
            elif local_name in ["serviceTask", "sendTask", "receiveTask"]:
                task_name = elem_name or f"ServiceTask_{len(metrics['service_tasks'])+1}"
                metrics["service_tasks"].append(task_name)
                metrics["total_tasks"] += 1
                if elem_id:
                    flow_data["nodes"][elem_id] = {"name": task_name, "type": "service"}

            # --- User Tasks ---
            elif local_name == "userTask":
                task_name = elem_name or f"UserTask_{len(metrics['user_tasks'])+1}"
                metrics["user_tasks"].append(task_name)
                metrics["total_tasks"] += 1
                if elem_id:
                    flow_data["nodes"][elem_id] = {"name": task_name, "type": "user"}

            # --- Script Tasks ---
            elif local_name == "scriptTask":
                task_name = elem_name or f"ScriptTask_{len(metrics['script_tasks'])+1}"
                metrics["script_tasks"].append(task_name)
                metrics["total_tasks"] += 1
                if elem_id:
                    flow_data["nodes"][elem_id] = {"name": task_name, "type": "script"}

            # --- Business Rule Tasks ---
            elif local_name == "businessRuleTask":
                task_name = elem_name or f"RuleTask_{len(metrics['business_rule_tasks'])+1}"
                metrics["business_rule_tasks"].append(task_name)
                metrics["total_tasks"] += 1
                if elem_id:
                    flow_data["nodes"][elem_id] = {"name": task_name, "type": "rule"}

            # --- Generische Tasks ---
            elif local_name == "task":
                metrics["total_tasks"] += 1
                if elem_id:
                    flow_data["nodes"][elem_id] = {
                        "name": elem_name or f"Task_{metrics['total_tasks']}",
                        "type": "task",
                    }

            # --- Sub-Prozesse ---
            elif local_name == "subProcess":
                sub_name = elem_name or f"SubProcess_{len(metrics['sub_processes'])+1}"
                metrics["sub_processes"].append(sub_name)
                if elem_id:
                    flow_data["nodes"][elem_id] = {"name": sub_name, "type": "subprocess"}

            # --- Gateways ---
            elif local_name == "exclusiveGateway":
                metrics["gateways"]["exclusive"] += 1
                if elem_id:
                    flow_data["nodes"][elem_id] = {
                        "name": elem_name or "XOR",
                        "type": "gateway_exclusive",
                    }
            elif local_name == "parallelGateway":
                metrics["gateways"]["parallel"] += 1
                if elem_id:
                    flow_data["nodes"][elem_id] = {
                        "name": elem_name or "AND",
                        "type": "gateway_parallel",
                    }
            elif local_name == "inclusiveGateway":
                metrics["gateways"]["inclusive"] += 1
                if elem_id:
                    flow_data["nodes"][elem_id] = {
                        "name": elem_name or "OR",
                        "type": "gateway_inclusive",
                    }
            elif local_name in ["eventBasedGateway", "complexGateway"]:
                metrics["gateways"]["event_based"] += 1
                if elem_id:
                    flow_data["nodes"][elem_id] = {
                        "name": elem_name or "EVT",
                        "type": "gateway_event",
                    }

            # --- Sequence Flows ---
            elif local_name == "sequenceFlow":
                metrics["sequence_flows"] += 1
                source = elem.get("sourceRef", "")
                target = elem.get("targetRef", "")
                if source and target:
                    flow_data["edges"].append({
                        "source": source,
                        "target": target,
                        "name": elem_name or "",
                    })

            # --- Loop-Erkennung ---
            elif local_name in [
                "standardLoopCharacteristics",
                "multiInstanceLoopCharacteristics",
            ]:
                metrics["has_loops"] = True

        # Heuristische Loop-Erkennung im XML-Text
        loop_keywords = ["loop", "revert", "zurück", "wiederholung", "retry", "repeat"]
        xml_lower = xml_content.lower()
        if any(kw in xml_lower for kw in loop_keywords):
            metrics["has_loops"] = True

    except Exception as e:
        st.error(f"Fehler beim Parsen der XML-Struktur: {e}")

    return metrics, flow_data


# ==========================================
# 3. BPMN-VISUALISIERUNG (Graphviz DOT)
# ==========================================
def generate_bpmn_dot(flow_data):
    """Erzeugt einen Graphviz-DOT-String aus den BPMN-Flussdaten."""
    if not flow_data["nodes"]:
        return None

    # Farben für verschiedene Elementtypen
    type_styles = {
        "start": 'shape=circle style=filled fillcolor="#10B981" fontcolor=white width=0.6 height=0.6',
        "end": 'shape=doublecircle style=filled fillcolor="#EF4444" fontcolor=white width=0.6 height=0.6',
        "service": 'shape=box style="filled,rounded" fillcolor="#3B82F6" fontcolor=white',
        "user": 'shape=box style="filled,rounded" fillcolor="#8B5CF6" fontcolor=white',
        "script": 'shape=box style="filled,rounded" fillcolor="#06B6D4" fontcolor=white',
        "rule": 'shape=box style="filled,rounded" fillcolor="#F59E0B" fontcolor=white',
        "task": 'shape=box style="filled,rounded" fillcolor="#64748B" fontcolor=white',
        "subprocess": 'shape=box style="filled,bold,rounded" fillcolor="#1E293B" fontcolor=white penwidth=2',
        "gateway_exclusive": 'shape=diamond style=filled fillcolor="#F59E0B" fontcolor=white width=0.7 height=0.7',
        "gateway_parallel": 'shape=diamond style=filled fillcolor="#10B981" fontcolor=white width=0.7 height=0.7',
        "gateway_inclusive": 'shape=diamond style=filled fillcolor="#A78BFA" fontcolor=white width=0.7 height=0.7',
        "gateway_event": 'shape=diamond style=filled fillcolor="#EF4444" fontcolor=white width=0.7 height=0.7',
    }

    lines = [
        "digraph BPMN {",
        '  rankdir=LR;',
        '  bgcolor="transparent";',
        '  pad=0.3;',
        '  nodesep=0.6;',
        '  ranksep=0.8;',
        '  node [fontname="Helvetica" fontsize=10 margin="0.2,0.1"];',
        '  edge [color="#64748B" arrowsize=0.7 fontname="Helvetica" fontsize=8];',
        "",
    ]

    # Nodes
    for node_id, info in flow_data["nodes"].items():
        label = _sanitize_dot_label(info["name"])
        style = type_styles.get(info["type"], 'shape=box style="filled,rounded" fillcolor="#475569" fontcolor=white')
        safe_id = node_id.replace('"', '\\"')
        lines.append(f'  "{safe_id}" [label="{label}" {style}];')

    lines.append("")

    # Edges
    for edge in flow_data["edges"]:
        src = edge["source"].replace('"', '\\"')
        tgt = edge["target"].replace('"', '\\"')
        # Nur Kanten für bekannte Nodes
        if edge["source"] in flow_data["nodes"] and edge["target"] in flow_data["nodes"]:
            edge_label = _sanitize_dot_label(edge["name"])
            label_attr = f' [label="{edge_label}"]' if edge_label else ""
            lines.append(f'  "{src}" -> "{tgt}"{label_attr};')

    lines.append("}")
    return "\n".join(lines)


# ==========================================
# 4. AGENTENTYP-KLASSIFIKATION (VERBESSERT)
# ==========================================
def classify_agent_type(metrics):
    """
    Verbesserte Klassifikation: Absolute Scores (0-100) pro Agententyp.

    Jeder Typ hat gewichtete Kriterien, die sich zu max. 100 summieren.
    Der Score spiegelt direkt wider, wie gut der BPMN-Prozess zu diesem
    Agententyp passt – unabhängig von den anderen Typen.
    """
    scores = {}
    reasoning = {}

    num_lanes = len(metrics["lanes"])
    num_service = len(metrics["service_tasks"])
    num_user = len(metrics["user_tasks"])
    num_sub = len(metrics["sub_processes"])
    total_gateways = sum(metrics["gateways"].values())
    parallel_gw = metrics["gateways"]["parallel"]
    exclusive_gw = metrics["gateways"]["exclusive"]
    inclusive_gw = metrics["gateways"]["inclusive"]
    has_loops = metrics["has_loops"]
    total_tasks = metrics["total_tasks"]
    end_events = metrics["end_events"]

    # ──────────────────────────────────────────────
    # SIMPLE REFLEX (max 100)
    # Kriterien: Keine Gateways(30), ≤1 Lane(20), Wenige Tasks(25),
    #            Keine Loops(15), Keine Sub-Prozesse(10)
    # ──────────────────────────────────────────────
    sr = 0
    sr_r = []
    if total_gateways == 0:
        sr += 30
        sr_r.append("Keine Entscheidungspunkte (Gateways) → rein regelbasiertes Verhalten möglich.")
    if num_lanes <= 1:
        sr += 20
        sr_r.append("Einzelne Rolle → kein Multi-Agenten-Bedarf.")
    if total_tasks <= 3:
        sr += 25
        sr_r.append(f"Nur {total_tasks} Tasks → geringe Prozesskomplexität.")
    elif total_tasks <= 5:
        sr += 12
        sr_r.append(f"{total_tasks} Tasks → überschaubare Komplexität.")
    if not has_loops:
        sr += 15
        sr_r.append("Keine Schleifen → kein Zustandsgedächtnis nötig.")
    if num_sub == 0:
        sr += 10
        sr_r.append("Keine Sub-Prozesse → flache, lineare Struktur.")
    scores["simple_reflex"] = min(100, sr)
    reasoning["simple_reflex"] = sr_r

    # ──────────────────────────────────────────────
    # MODEL-BASED REFLEX (max 100)
    # Kriterien: XOR-Gateways(30), Service Tasks(20), ≤1 Lane(15),
    #            Keine Loops(15), Moderate Tasks(20)
    # ──────────────────────────────────────────────
    mbr = 0
    mbr_r = []
    if exclusive_gw > 0:
        mbr += 30
        mbr_r.append(f"{exclusive_gw} XOR-Gateways → Agent muss Umgebungszustand für Entscheidungen kennen.")
    if num_service > 0:
        mbr += 20
        mbr_r.append(f"{num_service} Schnittstellen → Agent muss Systemzustände modellieren.")
    if num_lanes <= 1:
        mbr += 15
        mbr_r.append("Einzelne Rolle mit Kontextbedarf → internes Modell sinnvoll.")
    elif num_lanes == 2:
        mbr += 5
    if not has_loops:
        mbr += 15
        mbr_r.append("Keine Schleifen → reaktives Modell mit Zustandsverfolgung ausreichend.")
    if 3 < total_tasks <= 8:
        mbr += 20
        mbr_r.append(f"{total_tasks} Tasks → moderate Komplexität, ideal für Modell-gestützte Entscheidungen.")
    elif total_tasks <= 3:
        mbr += 10
        mbr_r.append(f"Wenige Tasks → Modell bleibt überschaubar.")
    scores["model_based_reflex"] = min(100, mbr)
    reasoning["model_based_reflex"] = mbr_r

    # ──────────────────────────────────────────────
    # GOAL-BASED (max 100)
    # Kriterien: Parallele GW(25), Sub-Prozesse(25), Mehrere Enden(15),
    #            Viele Tasks(15), Service Tasks(10), Mehrere Lanes(10)
    # ──────────────────────────────────────────────
    gb = 0
    gb_r = []
    if parallel_gw > 0:
        gb += 25
        gb_r.append(f"{parallel_gw} parallele Gateways → Koordination paralleler Pfade erfordert Planung.")
    if num_sub > 0:
        gb += 25
        gb_r.append(f"{num_sub} Sub-Prozesse → Zieldekomposition in Teilziele nötig.")
    if end_events > 1:
        gb += 15
        gb_r.append(f"{end_events} End-Events → mehrere Ergebnispfade erfordern Zielnavigation.")
    if total_tasks > 5:
        gb += 15
        gb_r.append(f"{total_tasks} Tasks → strategische Planung für Prozesssteuerung nötig.")
    elif total_tasks > 3:
        gb += 8
    if num_service > 0:
        gb += 10
        gb_r.append(f"Schnittstellen als Werkzeuge → zielgerichteter Einsatz planbar.")
    if num_lanes > 1:
        gb += 10
        gb_r.append(f"{num_lanes} Rollen → Koordination erfordert Planung.")
    scores["goal_based"] = min(100, gb)
    reasoning["goal_based"] = gb_r

    # ──────────────────────────────────────────────
    # UTILITY-BASED (max 100)
    # Kriterien: Viele Services(30), Viele GW(25), Mix GW-Typen(15),
    #            Mehrere Enden(15), Hohe Taskkomplexität(15)
    # ──────────────────────────────────────────────
    ub = 0
    ub_r = []
    if num_service > 2:
        ub += 30
        ub_r.append(f"{num_service} Schnittstellen → Bewertung und Auswahl zwischen Optionen nötig.")
    elif num_service > 0:
        ub += 10
        ub_r.append(f"{num_service} Schnittstelle(n) → grundlegender Bewertungsbedarf.")
    if total_gateways > 3:
        ub += 25
        ub_r.append(f"{total_gateways} Gateways → viele Entscheidungspunkte erfordern Nutzenbewertung.")
    elif total_gateways > 1:
        ub += 10
    if exclusive_gw > 0 and parallel_gw > 0:
        ub += 15
        ub_r.append("Mix aus XOR- und Parallel-Gateways → Trade-off-Bewertung nötig.")
    elif inclusive_gw > 0:
        ub += 15
        ub_r.append("Inklusive Gateways → mehrere Optionen müssen bewertet werden.")
    if end_events > 1:
        ub += 15
        ub_r.append(f"{end_events} mögliche Ergebnisse → Nutzenbewertung der Ausgänge sinnvoll.")
    if total_tasks > 5:
        ub += 15
        ub_r.append(f"Hohe Prozesskomplexität ({total_tasks} Tasks) → systematische Optimierung nötig.")
    scores["utility_based"] = min(100, ub)
    reasoning["utility_based"] = ub_r

    # ──────────────────────────────────────────────
    # LEARNING (max 100)
    # Kriterien: Loops(40), User Tasks+Loops(25) ODER User Tasks(15),
    #            Service Tasks(15), Mehrere Tasks(10), Gateways(10)
    # ──────────────────────────────────────────────
    la = 0
    la_r = []
    if has_loops:
        la += 40
        la_r.append("Schleifen/Wiederholungen erkannt → iteratives Lernen aus jeder Iteration möglich.")
    if num_user > 0 and has_loops:
        la += 25
        la_r.append(f"{num_user} User Tasks + Loops → menschliches Feedback als Lernquelle.")
    elif num_user > 0:
        la += 15
        la_r.append(f"{num_user} User Tasks → menschliches Feedback als Lernsignal verfügbar.")
    if num_service > 0:
        la += 15
        la_r.append(f"Schnittstellen-Interaktionen → Lernen aus API-Ergebnissen möglich.")
    if total_tasks > 3:
        la += 10
        la_r.append(f"Mehrere Tasks bieten diverse Lernmöglichkeiten.")
    if total_gateways > 0:
        la += 10
        la_r.append("Entscheidungspunkte → Agent kann lernen, bessere Pfade zu wählen.")
    scores["learning"] = min(100, la)
    reasoning["learning"] = la_r

    # ──────────────────────────────────────────────
    # HIERARCHICAL (max 100)
    # Kriterien: >2 Lanes(35) / 2 Lanes(15), Sub+Lanes(25) / Sub(10),
    #            Viele Tasks(15), GW+Lanes(10), Services+Lanes(10)
    # ──────────────────────────────────────────────
    ha = 0
    ha_r = []
    if num_lanes > 2:
        ha += 35
        ha_r.append(f"{num_lanes} Lanes → natürliche Abbildung als mehrstufige Agentenhierarchie.")
    elif num_lanes == 2:
        ha += 15
        ha_r.append("2 Lanes → Supervisor-Worker-Muster möglich.")
    if num_sub > 0 and num_lanes > 1:
        ha += 25
        ha_r.append(f"{num_sub} Sub-Prozesse + {num_lanes} Rollen → klare hierarchische Delegation.")
    elif num_sub > 0:
        ha += 10
        ha_r.append(f"Sub-Prozesse → Aufgabendekomposition in Hierarchie möglich.")
    if total_tasks > 8:
        ha += 15
        ha_r.append(f"{total_tasks} Tasks → Komplexität erfordert hierarchische Aufteilung.")
    elif total_tasks > 5:
        ha += 8
    if total_gateways > 0 and num_lanes > 1:
        ha += 10
        ha_r.append("Entscheidungspunkte über mehrere Rollen → hierarchische Koordination nötig.")
    if num_service > 0 and num_lanes > 1:
        ha += 10
        ha_r.append("Schnittstellen über Rollen verteilt → zentrale Koordination sinnvoll.")
    scores["hierarchical"] = min(100, ha)
    reasoning["hierarchical"] = ha_r

    # --- Ergebnis ---
    sorted_types = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    primary = sorted_types[0][0]
    primary_score = sorted_types[0][1]

    # Sekundäre Empfehlung: zweithöchster Score falls ≥40%
    secondary = None
    if len(sorted_types) > 1 and sorted_types[1][1] >= 40:
        secondary = sorted_types[1][0]

    return {
        "primary": primary,
        "secondary": secondary,
        "confidence": primary_score,  # Absoluter Score = Konfidenz
        "scores": scores,
        "reasoning": reasoning,
        "sorted": sorted_types,
    }


# ==========================================
# 5. ARCHITEKTUR-DIAGRAMME
# ==========================================
def generate_architecture_dot(agent_type_key, metrics):
    """Erzeugt ein dynamisches Architektur-Diagramm basierend auf dem
    empfohlenen Agententyp und den konkreten BPMN-Daten."""

    lanes = metrics["lanes"] if metrics["lanes"] else ["Hauptprozess"]
    services = metrics["service_tasks"][:5]  # Max 5 für Übersicht
    user_tasks = metrics["user_tasks"][:3]

    common_attrs = """
  bgcolor="transparent";
  pad=0.4;
  node [fontname="Helvetica" fontsize=10 margin="0.2,0.1"];
  edge [color="#64748B" arrowsize=0.7 fontname="Helvetica" fontsize=8];
"""

    if agent_type_key == "simple_reflex":
        rules = []
        for i, s in enumerate(services[:3]):
            rules.append(f'    "rule_{i}" [label="{_sanitize_dot_label(s)}" shape=box style="filled,rounded" fillcolor="#334155" fontcolor=white];')
        rules_str = "\n".join(rules) if rules else '    "rule_0" [label="Wenn-Dann-Regel" shape=box style="filled,rounded" fillcolor="#334155" fontcolor=white];'
        rule_edges = "\n".join(
            [f'    "regelwerk" -> "rule_{i}";' for i in range(min(len(services), 3))]
        ) if services else '    "regelwerk" -> "rule_0";'

        return f"""digraph Architecture {{
  rankdir=LR;
{common_attrs}
  subgraph cluster_agent {{
    label="Simple Reflex Agent";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#1E293B";
    fontcolor="#F8FAFC";
    fontname="Helvetica";
    fontsize=12;
    color="#4ECDC4";
    penwidth=2;

    "input" [label="Sensorinput\\n(Percept)" shape=ellipse style=filled fillcolor="#4ECDC4" fontcolor=white];
    "regelwerk" [label="Regelwerk\\n(If-Then)" shape=hexagon style=filled fillcolor="#4ECDC4" fontcolor=white];
{rules_str}
    "output" [label="Aktion\\n(Actuator)" shape=ellipse style=filled fillcolor="#44A08D" fontcolor=white];

    "input" -> "regelwerk" [label="  aktueller\\n  Zustand"];
{rule_edges}
{chr(10).join([f'    "rule_{i}" -> "output";' for i in range(min(len(services), 3) or 1)])}
  }}
}}"""

    elif agent_type_key == "model_based_reflex":
        sensor_nodes = []
        for i, s in enumerate(services[:3]):
            sensor_nodes.append(f'    "sensor_{i}" [label="{_sanitize_dot_label(s)}" shape=box style="filled,rounded" fillcolor="#334155" fontcolor=white];')
        sensors_str = "\n".join(sensor_nodes) if sensor_nodes else '    "sensor_0" [label="Datenquelle" shape=box style="filled,rounded" fillcolor="#334155" fontcolor=white];'

        return f"""digraph Architecture {{
  rankdir=TB;
{common_attrs}
  subgraph cluster_agent {{
    label="Model-Based Reflex Agent";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#1E293B";
    fontcolor="#F8FAFC";
    fontname="Helvetica";
    fontsize=12;
    color="#A78BFA";
    penwidth=2;

    "umgebung" [label="Umgebung" shape=ellipse style=filled fillcolor="#7C3AED" fontcolor=white];
    "sensoren" [label="Sensoren" shape=box style="filled,rounded" fillcolor="#A78BFA" fontcolor=white];
    "modell" [label="Internes Modell\\n(Zustandsverfolgung)" shape=box3d style=filled fillcolor="#A78BFA" fontcolor=white];
    "regeln" [label="Regelwerk" shape=hexagon style=filled fillcolor="#7C3AED" fontcolor=white];
    "aktion" [label="Aktoren" shape=ellipse style=filled fillcolor="#A78BFA" fontcolor=white];

    "umgebung" -> "sensoren" [label="Percept"];
    "sensoren" -> "modell" [label="aktueller\\nZustand"];
    "modell" -> "regeln" [label="modellierter\\nZustand"];
    "regeln" -> "aktion" [label="Entscheidung"];
    "aktion" -> "umgebung" [label="Wirkung" style=dashed];
  }}

  subgraph cluster_sources {{
    label="Datenquellen";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#0F172A";
    fontcolor="#94A3B8";
    color="#334155";
{sensors_str}
  }}
{chr(10).join([f'  "sensor_{i}" -> "sensoren" [style=dashed color="#A78BFA88"];' for i in range(min(len(services), 3) or 1)])}
}}"""

    elif agent_type_key == "goal_based":
        goals = []
        subs = metrics["sub_processes"][:3] if metrics["sub_processes"] else ["Hauptziel"]
        for i, s in enumerate(subs):
            goals.append(f'    "goal_{i}" [label="{_sanitize_dot_label(s)}" shape=box style="filled,rounded" fillcolor="#334155" fontcolor=white];')

        return f"""digraph Architecture {{
  rankdir=LR;
{common_attrs}
  subgraph cluster_agent {{
    label="Goal-Based Agent";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#1E293B";
    fontcolor="#F8FAFC";
    fontname="Helvetica";
    fontsize=12;
    color="#F59E0B";
    penwidth=2;

    "percept" [label="Wahrnehmung" shape=ellipse style=filled fillcolor="#F59E0B" fontcolor=white];
    "modell" [label="Umgebungs-\\nmodell" shape=box3d style=filled fillcolor="#D97706" fontcolor=white];
    "ziel" [label="Ziel-\\ndefinition" shape=doubleoctagon style=filled fillcolor="#F59E0B" fontcolor=white];
    "planung" [label="Such- &\\nPlanungs-\\nalgorithmus" shape=hexagon style=filled fillcolor="#D97706" fontcolor=white];
    "aktion" [label="Aktion" shape=ellipse style=filled fillcolor="#F59E0B" fontcolor=white];

    "percept" -> "modell";
    "modell" -> "ziel";
    "ziel" -> "planung";
    "planung" -> "aktion";
  }}

  subgraph cluster_goals {{
    label="Teilziele (Sub-Prozesse)";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#0F172A";
    fontcolor="#94A3B8";
    color="#334155";
{chr(10).join(goals)}
  }}
{chr(10).join([f'  "ziel" -> "goal_{i}" [style=dashed color="#F59E0B88" label="  dekomp."];' for i in range(len(subs))])}
}}"""

    elif agent_type_key == "utility_based":
        scenarios = []
        for i in range(min(max(len(services), 2), 4)):
            name = services[i] if i < len(services) else f"Szenario {i+1}"
            scenarios.append(f'    "szen_{i}" [label="{_sanitize_dot_label(name)}" shape=box style="filled,rounded" fillcolor="#334155" fontcolor=white];')

        return f"""digraph Architecture {{
  rankdir=TB;
{common_attrs}
  subgraph cluster_agent {{
    label="Utility-Based Agent";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#1E293B";
    fontcolor="#F8FAFC";
    fontname="Helvetica";
    fontsize=12;
    color="#EF4444";
    penwidth=2;

    "zustand" [label="Zustand\\nerfassen" shape=ellipse style=filled fillcolor="#EF4444" fontcolor=white];
    "utility" [label="Nutzenfunktion\\nU(s)" shape=hexagon style=filled fillcolor="#DC2626" fontcolor=white width=1.5];
    "vergleich" [label="Vergleich &\\nRanking" shape=diamond style=filled fillcolor="#EF4444" fontcolor=white];
    "best" [label="Optimale\\nAktion" shape=ellipse style=filled fillcolor="#B91C1C" fontcolor=white];

    "zustand" -> "utility";
    "utility" -> "vergleich";
    "vergleich" -> "best" [label="  max U(s)"];
  }}

  subgraph cluster_scenarios {{
    label="Bewertete Szenarien";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#0F172A";
    fontcolor="#94A3B8";
    color="#334155";
{chr(10).join(scenarios)}
  }}
{chr(10).join([f'  "utility" -> "szen_{i}" [style=dashed color="#EF444488"];' for i in range(min(max(len(services), 2), 4))])}
{chr(10).join([f'  "szen_{i}" -> "vergleich" [style=dashed color="#EF444488"];' for i in range(min(max(len(services), 2), 4))])}
}}"""

    elif agent_type_key == "learning":
        feedback = []
        for i, u in enumerate(user_tasks[:2]):
            feedback.append(f'    "fb_{i}" [label="{_sanitize_dot_label(u)}" shape=box style="filled,rounded" fillcolor="#334155" fontcolor=white];')
        fb_str = "\n".join(feedback) if feedback else '    "fb_0" [label="Feedback-Quelle" shape=box style="filled,rounded" fillcolor="#334155" fontcolor=white];'

        return f"""digraph Architecture {{
  rankdir=TB;
{common_attrs}
  subgraph cluster_agent {{
    label="Learning Agent";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#1E293B";
    fontcolor="#F8FAFC";
    fontname="Helvetica";
    fontsize=12;
    color="#10B981";
    penwidth=2;

    "umgebung" [label="Umgebung" shape=ellipse style=filled fillcolor="#059669" fontcolor=white];
    "performance" [label="Performance-\\nElement" shape=box style="filled,rounded" fillcolor="#10B981" fontcolor=white];
    "kritiker" [label="Kritiker\\n(Bewertung)" shape=hexagon style=filled fillcolor="#059669" fontcolor=white];
    "lernen" [label="Lern-\\nelement" shape=box3d style=filled fillcolor="#10B981" fontcolor=white];
    "wissen" [label="Wissens-\\nbasis" shape=cylinder style=filled fillcolor="#065F46" fontcolor=white];
    "problem" [label="Problem-\\ngenerator" shape=diamond style=filled fillcolor="#059669" fontcolor=white];

    "umgebung" -> "performance" [label="Percept"];
    "performance" -> "umgebung" [label="Aktion"];
    "performance" -> "kritiker" [label="Ergebnis"];
    "kritiker" -> "lernen" [label="Feedback"];
    "lernen" -> "wissen" [label="Update"];
    "wissen" -> "performance" [label="Wissen"];
    "problem" -> "lernen" [label="neue\\nHerausforderungen" style=dashed];
  }}

  subgraph cluster_feedback {{
    label="Feedback-Quellen (User Tasks)";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#0F172A";
    fontcolor="#94A3B8";
    color="#334155";
{fb_str}
  }}
{chr(10).join([f'  "fb_{i}" -> "kritiker" [style=dashed color="#10B98188"];' for i in range(len(user_tasks[:2]) or 1)])}
}}"""

    elif agent_type_key == "hierarchical":
        # Dynamisch: Lanes werden zu Worker-Agenten
        agent_nodes = []
        agent_edges = []
        for i, lane in enumerate(lanes[:6]):
            safe = _sanitize_dot_label(lane)
            agent_nodes.append(
                f'    "worker_{i}" [label="{safe}\\nAgent" shape=box style="filled,rounded" fillcolor="#2563EB" fontcolor=white];'
            )
            agent_edges.append(f'  "supervisor" -> "worker_{i}" [label="  delegiert"];')

        task_nodes = []
        task_edges = []
        for i, s in enumerate(services[:4]):
            safe = _sanitize_dot_label(s)
            task_nodes.append(
                f'    "tool_{i}" [label="{safe}" shape=box style="filled,rounded" fillcolor="#334155" fontcolor=white];'
            )
            # Weise Tools dem nächstbesten Worker zu
            worker_idx = i % len(lanes[:6]) if lanes else 0
            task_edges.append(f'  "worker_{worker_idx}" -> "tool_{i}" [style=dashed color="#3B82F688"];')

        return f"""digraph Architecture {{
  rankdir=TB;
{common_attrs}
  subgraph cluster_supervisor {{
    label="Koordinations-Ebene";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#0F172A";
    fontcolor="#94A3B8";
    color="#1E40AF";
    penwidth=2;

    "supervisor" [label="Supervisor\\nAgent" shape=doubleoctagon style=filled fillcolor="#1E40AF" fontcolor=white width=1.3];
  }}

  subgraph cluster_workers {{
    label="Spezialisierte Agenten (aus Lanes)";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#1E293B";
    fontcolor="#F8FAFC";
    fontname="Helvetica";
    fontsize=12;
    color="#3B82F6";
    penwidth=2;

{chr(10).join(agent_nodes)}
  }}

{chr(10).join(agent_edges)}

{f'''  subgraph cluster_tools {{
    label="Werkzeuge (Service Tasks)";
    labeljust=l;
    style="filled,rounded";
    fillcolor="#0F172A";
    fontcolor="#94A3B8";
    color="#334155";

{chr(10).join(task_nodes)}
  }}

{chr(10).join(task_edges)}''' if task_nodes else ''}
}}"""

    return None


# ==========================================
# 6. HTML REPORT GENERATOR
# ==========================================
def generate_html_report(metrics, result, flow_data):
    """Erzeugt einen eigenständigen HTML-Bericht zum Download."""
    primary_type = AGENT_TYPES[result["primary"]]
    now = datetime.now().strftime("%d.%m.%Y %H:%M")

    # Metriken-Tabelle
    metrics_rows = f"""
    <tr><td>Rollen / Lanes</td><td><strong>{len(metrics['lanes'])}</strong></td><td>{', '.join(metrics['lanes']) if metrics['lanes'] else '—'}</td></tr>
    <tr><td>Service Tasks</td><td><strong>{len(metrics['service_tasks'])}</strong></td><td>{', '.join(metrics['service_tasks'][:5]) if metrics['service_tasks'] else '—'}</td></tr>
    <tr><td>User Tasks</td><td><strong>{len(metrics['user_tasks'])}</strong></td><td>{', '.join(metrics['user_tasks'][:5]) if metrics['user_tasks'] else '—'}</td></tr>
    <tr><td>Sub-Prozesse</td><td><strong>{len(metrics['sub_processes'])}</strong></td><td>{', '.join(metrics['sub_processes'][:5]) if metrics['sub_processes'] else '—'}</td></tr>
    <tr><td>Gateways gesamt</td><td><strong>{sum(metrics['gateways'].values())}</strong></td><td>XOR: {metrics['gateways']['exclusive']}, AND: {metrics['gateways']['parallel']}, OR: {metrics['gateways']['inclusive']}</td></tr>
    <tr><td>Tasks gesamt</td><td><strong>{metrics['total_tasks']}</strong></td><td>—</td></tr>
    <tr><td>Schleifen</td><td><strong>{'Ja' if metrics['has_loops'] else 'Nein'}</strong></td><td>—</td></tr>
    <tr><td>End-Events</td><td><strong>{metrics['end_events']}</strong></td><td>—</td></tr>
    """

    # Begründungen
    reasons_html = ""
    for r in result["reasoning"].get(result["primary"], []):
        reasons_html += f"<li>{html_module.escape(r)}</li>\n"

    # Vergleichstabelle
    comparison_rows = ""
    for key, score in result["sorted"]:
        info = AGENT_TYPES[key]
        is_winner = key == result["primary"]
        highlight = 'style="background:#f0f9ff;font-weight:bold;"' if is_winner else ""
        badge = " ✅ Empfohlen" if is_winner else ""
        comparison_rows += f'<tr {highlight}><td>{info["icon"]} {info["name"]}{badge}</td><td>{score}%</td><td><div style="background:#e2e8f0;border-radius:8px;height:12px;width:100%;"><div style="background:{info["color"]};height:100%;border-radius:8px;width:{score}%;"></div></div></td></tr>\n'

    # Sekundär-Info
    secondary_html = ""
    if result["secondary"]:
        sec = AGENT_TYPES[result["secondary"]]
        sec_score = result["scores"][result["secondary"]]
        secondary_html = f"""
        <div style="margin-top:16px;padding:12px 16px;background:#f8fafc;border-left:4px solid {sec['color']};border-radius:4px;">
            <strong>Hybrid-Option:</strong> {sec['icon']} {sec['name']} (Score: {sec_score}%)<br>
            <small>Ein Hybrid aus {primary_type['name']} + {sec['name']} könnte die Stärken beider Ansätze kombinieren.</small>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="utf-8">
    <title>KI-Agenten Analyse-Bericht</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; color: #1e293b; line-height: 1.6; padding: 40px; max-width: 900px; margin: 0 auto; }}
        h1 {{ font-size: 1.8rem; color: #0f172a; margin-bottom: 4px; }}
        h2 {{ font-size: 1.3rem; color: #334155; margin: 28px 0 12px 0; padding-bottom: 6px; border-bottom: 2px solid #e2e8f0; }}
        .meta {{ color: #94a3b8; font-size: 0.85rem; margin-bottom: 24px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 12px 0; }}
        th, td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }}
        th {{ background: #f8fafc; font-weight: 600; color: #475569; }}
        .result-box {{ background: linear-gradient(135deg, #f0f9ff, #ede9fe); border-radius: 12px; padding: 24px; margin: 16px 0; text-align: center; border: 1px solid #c7d2fe; }}
        .result-box .icon {{ font-size: 2.5rem; }}
        .result-box .title {{ font-size: 1.5rem; font-weight: 700; color: #1e293b; margin: 8px 0 4px 0; }}
        .result-box .desc {{ color: #64748b; font-size: 0.95rem; }}
        .result-box .score {{ font-size: 1.1rem; font-weight: 600; color: #3b82f6; margin-top: 8px; }}
        ul {{ padding-left: 20px; }}
        li {{ margin: 6px 0; font-size: 0.9rem; }}
        .footer {{ margin-top: 40px; padding-top: 16px; border-top: 1px solid #e2e8f0; color: #94a3b8; font-size: 0.8rem; text-align: center; }}
        @media print {{
            body {{ padding: 20px; }}
            .result-box {{ break-inside: avoid; }}
        }}
    </style>
</head>
<body>
    <h1>🤖 Enterprise Agent Architect</h1>
    <p class="meta">Analyse-Bericht · Erstellt am {now}</p>

    <h2>📊 Prozess-Metriken</h2>
    <table>
        <thead><tr><th>Metrik</th><th>Wert</th><th>Details</th></tr></thead>
        <tbody>{metrics_rows}</tbody>
    </table>

    <h2>🏆 Empfohlener Agententyp</h2>
    <div class="result-box">
        <div class="icon">{primary_type['icon']}</div>
        <div class="title">{primary_type['name']}</div>
        <div class="desc">{primary_type['kurz']}</div>
        <div class="score">Eignung: {result['confidence']}%</div>
    </div>
    {secondary_html}

    <h2>📝 Begründung</h2>
    <ul>{reasons_html}</ul>

    <h2>📊 Vergleich aller Agententypen</h2>
    <table>
        <thead><tr><th>Agententyp</th><th>Score</th><th>Eignung</th></tr></thead>
        <tbody>{comparison_rows}</tbody>
    </table>

    <h2>📖 Über den empfohlenen Typ</h2>
    <p><strong>Beschreibung:</strong> {primary_type['beschreibung']}</p>
    <p style="margin-top:12px;"><strong>Stärken:</strong></p>
    <ul>{''.join(f'<li>{s}</li>' for s in primary_type['staerken'])}</ul>
    <p style="margin-top:12px;"><strong>Schwächen:</strong></p>
    <ul>{''.join(f'<li>{s}</li>' for s in primary_type['schwaechen'])}</ul>
    <p style="margin-top:12px;"><strong>Typische Anwendungsfälle:</strong></p>
    <ul>{''.join(f'<li>{s}</li>' for s in primary_type['use_cases'])}</ul>

    <div class="footer">
        <p>Generiert von Enterprise Agent Architect · Basierend auf "Building Generative AI Agents" (Taulli & Deshmukh, 2025)</p>
        <p>Hinweis: Diese Empfehlung basiert auf der automatisierten Analyse der BPMN-Prozessstruktur. Eine fachliche Validierung wird empfohlen.</p>
    </div>
</body>
</html>"""


# ==========================================
# 7. CUSTOM CSS
# ==========================================
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

.stApp {
    font-family: 'Inter', sans-serif;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #F8FAFC !important;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li {
    color: #CBD5E1 !important;
    font-size: 0.88rem;
}

.metric-card {
    background: linear-gradient(135deg, #1E293B, #334155);
    border-radius: 16px;
    padding: 20px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.06);
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    transition: transform 0.2s ease;
}
.metric-card:hover { transform: translateY(-2px); }
.metric-card .metric-value {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #60A5FA, #A78BFA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-card .metric-label {
    font-size: 0.82rem;
    color: #94A3B8;
    margin-top: 4px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.result-primary {
    border-radius: 20px;
    padding: 32px;
    color: #ffffff;
    text-align: center;
    box-shadow: 0 12px 48px rgba(0,0,0,0.3);
    position: relative;
    overflow: hidden;
}
.result-primary::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 60%);
    animation: shimmer 8s infinite linear;
}
@keyframes shimmer {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
.result-primary .result-icon { font-size: 4rem; margin-bottom: 12px; position: relative; z-index: 1; }
.result-primary .result-title { font-size: 1.8rem; font-weight: 800; margin-bottom: 8px; position: relative; z-index: 1; color: #ffffff !important; }
.result-primary .result-subtitle { font-size: 1rem; opacity: 0.9; position: relative; z-index: 1; color: #ffffff !important; }

.score-bar-container {
    background: rgba(255,255,255,0.08);
    border-radius: 12px;
    overflow: hidden;
    height: 14px;
    margin: 6px 0;
    backdrop-filter: blur(4px);
}
.score-bar-fill {
    height: 100%;
    border-radius: 12px;
    transition: width 1s ease;
    background: linear-gradient(90deg, var(--bar-color), var(--bar-color-end));
}

.comparison-row {
    display: flex;
    align-items: center;
    padding: 14px 18px;
    margin: 6px 0;
    border-radius: 12px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
    transition: background 0.2s ease;
}
.comparison-row:hover { background: rgba(255,255,255,0.06); }
.comparison-row .comp-icon { font-size: 1.6rem; margin-right: 14px; min-width: 36px; }
.comparison-row .comp-name { flex: 1; font-weight: 600; font-size: 0.95rem; }
.comparison-row .comp-score { font-weight: 700; font-size: 1.1rem; margin-left: 12px; min-width: 48px; text-align: right; }

.main-header { text-align: center; padding: 20px 0 30px 0; }
.main-header h1 {
    font-size: 2.6rem; font-weight: 800;
    background: linear-gradient(135deg, #60A5FA, #A78BFA, #F472B6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin-bottom: 8px;
}
.main-header p { color: #94A3B8; font-size: 1.1rem; font-weight: 400; }

.reasoning-card {
    background: linear-gradient(135deg, #1E293B, #334155);
    border-radius: 14px;
    padding: 20px 24px;
    margin: 8px 0;
    border-left: 4px solid;
    border-image: linear-gradient(180deg, var(--accent-color), transparent) 1;
}
.reasoning-card li { margin: 6px 0; font-size: 0.9rem; line-height: 1.6; }

.badge {
    display: inline-block; padding: 4px 12px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;
}
.badge-primary { background: rgba(96,165,250,0.15); color: #60A5FA; border: 1px solid rgba(96,165,250,0.3); }
.badge-secondary { background: rgba(167,139,250,0.15); color: #A78BFA; border: 1px solid rgba(167,139,250,0.3); }

.section-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    margin: 30px 0;
}

/* Validation box */
.validation-warning {
    background: linear-gradient(135deg, #451a03, #78350f);
    border: 1px solid #92400e;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
    color: #fef3c7;
    font-size: 0.9rem;
}
.validation-ok {
    background: linear-gradient(135deg, #022c22, #064e3b);
    border: 1px solid #065f46;
    border-radius: 12px;
    padding: 16px 20px;
    margin: 12px 0;
    color: #d1fae5;
    font-size: 0.9rem;
}
</style>
"""


# ==========================================
# 8. STREAMLIT APP
# ==========================================
st.set_page_config(
    page_title="Enterprise Agent Architect",
    layout="wide",
    page_icon="🤖",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# --- SIDEBAR: THEORIE-ÜBERSICHT ---
with st.sidebar:
    st.markdown("## 📖 Agententypen-Lexikon")
    st.markdown(
        '<p style="color:#94A3B8;font-size:0.85rem;margin-bottom:16px;">'
        "Basierend auf <em>Building Generative AI Agents</em> (Taulli & Deshmukh, 2025)</p>",
        unsafe_allow_html=True,
    )

    for key, agent in AGENT_TYPES.items():
        with st.expander(f"{agent['icon']} {agent['name']}"):
            st.markdown(f"**{agent['kurz']}**")
            st.markdown(agent["beschreibung"])
            st.markdown("**✅ Stärken:**")
            for s in agent["staerken"]:
                st.markdown(f"- {s}")
            st.markdown("**❌ Schwächen:**")
            for s in agent["schwaechen"]:
                st.markdown(f"- {s}")
            st.markdown("**💡 Anwendungsfälle:**")
            for s in agent["use_cases"]:
                st.markdown(f"- {s}")


# --- HAUPTBEREICH ---
st.markdown(
    """
    <div class="main-header">
        <h1>🤖 Enterprise Agent Architect</h1>
        <p>Lade deinen BPMN-Geschäftsprozess hoch und erhalte eine fundierte Agententyp-Empfehlung</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Session State
if "metrics" not in st.session_state:
    st.session_state.metrics = None
if "flow_data" not in st.session_state:
    st.session_state.flow_data = None
if "last_file_name" not in st.session_state:
    st.session_state.last_file_name = None

# --- BPMN UPLOAD ---
st.markdown("### 📁 BPMN-Datei hochladen")
st.markdown(
    '<p style="color:#94A3B8;font-size:0.9rem;">'
    "Unterstützt Exporte aus Camunda, Signavio, Bizagi und anderen BPMN 2.0 Tools.</p>",
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "BPMN Datei auswählen",
    type=["bpmn", "xml"],
    key="bpmn_uploader",
    label_visibility="collapsed",
)

# Nur neu parsen, wenn eine neue Datei hochgeladen wurde
if uploaded_file is not None:
    if uploaded_file.name != st.session_state.last_file_name:
        file_bytes = uploaded_file.read()
        parsed_metrics, parsed_flow = parse_bpmn_xml(file_bytes)

        # Validierung: Ist es wirklich eine BPMN-Datei?
        has_content = (
            parsed_metrics["total_tasks"] > 0
            or len(parsed_metrics["lanes"]) > 0
            or sum(parsed_metrics["gateways"].values()) > 0
        )

        if has_content:
            st.session_state.metrics = parsed_metrics
            st.session_state.flow_data = parsed_flow
            st.session_state.last_file_name = uploaded_file.name
            # Altes Ergebnis löschen
            if "result" in st.session_state:
                del st.session_state.result
            st.markdown(
                '<div class="validation-ok">✅ BPMN-Struktur erfolgreich analysiert! '
                f'Datei: <strong>{uploaded_file.name}</strong></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="validation-warning">⚠️ Die Datei wurde geparst, aber es konnten '
                "keine BPMN-Elemente (Tasks, Lanes, Gateways) erkannt werden. "
                "Bitte stelle sicher, dass es sich um eine valide BPMN 2.0 XML-Datei handelt.</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="validation-ok">✅ Datei geladen: '
            f'<strong>{uploaded_file.name}</strong></div>',
            unsafe_allow_html=True,
        )


# ==========================================
# AUSWERTUNG
# ==========================================
if st.session_state.metrics is not None:
    m = st.session_state.metrics
    fd = st.session_state.flow_data

    # --- BPMN-VISUALISIERUNG ---
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 🔀 Prozess-Visualisierung")

    bpmn_dot = generate_bpmn_dot(fd) if fd else None
    if bpmn_dot:
        st.graphviz_chart(bpmn_dot, use_container_width=True)
    else:
        st.info("Keine Flussdaten zum Visualisieren gefunden. Die Analyse nutzt die extrahierten Metriken.")

    # --- METRIKEN-DASHBOARD ---
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📊 Prozess-Metriken")

    mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
    metric_data = [
        (mc1, str(len(m["lanes"])), "Rollen"),
        (mc2, str(len(m["service_tasks"])), "Schnittstellen"),
        (mc3, str(len(m["user_tasks"])), "User Tasks"),
        (mc4, str(sum(m["gateways"].values())), "Gateways"),
        (mc5, str(m["total_tasks"]), "Tasks gesamt"),
        (mc6, "Ja" if m["has_loops"] else "Nein", "Loops"),
    ]

    for col, value, label in metric_data:
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with st.expander("🔍 Details der erkannten Elemente"):
        det1, det2 = st.columns(2)
        with det1:
            st.write("**Gefundene Lanes/Rollen:**", m["lanes"] if m["lanes"] else "—")
            st.write("**Service Tasks:**", m["service_tasks"] if m["service_tasks"] else "—")
            st.write("**User Tasks:**", m["user_tasks"] if m["user_tasks"] else "—")
        with det2:
            st.write("**Sub-Prozesse:**", m["sub_processes"] if m["sub_processes"] else "—")
            st.write("**Gateways:**", m["gateways"])
            st.write("**End-Events:**", m["end_events"])
            st.write("**Sequence Flows:**", m["sequence_flows"])

    # --- KLASSIFIKATION ---
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    if st.button("🎯 Optimalen Agententyp berechnen", type="primary", use_container_width=True):
        result = classify_agent_type(m)
        st.session_state.result = result

    if "result" in st.session_state:
        result = st.session_state.result
        primary_type = AGENT_TYPES[result["primary"]]

        st.markdown("### 🏆 Empfehlung")

        res_col1, res_col2 = st.columns([1, 2])

        with res_col1:
            # Primäre Empfehlung
            st.markdown(
                f"""
                <div class="result-primary" style="background:{primary_type['gradient']};">
                    <div class="result-icon">{primary_type['icon']}</div>
                    <div class="result-title">{primary_type['name']}</div>
                    <div class="result-subtitle">{primary_type['kurz']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            confidence = result["confidence"]
            st.markdown(f"**Eignung: {confidence}%**")
            st.progress(confidence / 100)

            # Sekundäre Empfehlung
            if result["secondary"]:
                sec_type = AGENT_TYPES[result["secondary"]]
                sec_score = result["scores"][result["secondary"]]
                st.markdown(
                    f"""
                    <div style="margin-top:16px;">
                        <span class="badge badge-secondary">Hybrid-Option</span>
                        <p style="margin-top:8px;font-size:0.95rem;">
                            {sec_type['icon']} <strong>{sec_type['name']}</strong> (Score: {sec_score}%)
                        </p>
                        <p style="font-size:0.85rem;color:#94A3B8;">
                            Ein Hybrid aus {primary_type['name']} + {sec_type['name']} könnte
                            die Stärken beider Ansätze kombinieren.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with res_col2:
            # Begründungen
            primary_reasons = result["reasoning"][result["primary"]]
            if primary_reasons:
                accent_color = primary_type["color"]
                st.markdown(f"**Warum {primary_type['icon']} {primary_type['name']}?**")
                reasons_html = "".join(f"<li>{r}</li>" for r in primary_reasons)
                st.markdown(
                    f"""
                    <div class="reasoning-card" style="--accent-color:{accent_color};">
                        <ul style="margin:0;padding-left:18px;">
                            {reasons_html}
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Vergleichsmatrix
            st.markdown("**Vergleich aller Agententypen:**")
            for agent_key, score in result["sorted"]:
                agent_info = AGENT_TYPES[agent_key]
                is_primary = agent_key == result["primary"]
                bar_opacity = "1" if is_primary else "0.7"
                badge_html = (
                    ' <span class="badge badge-primary">Empfohlen</span>'
                    if is_primary else ""
                )
                st.markdown(
                    f"""
                    <div class="comparison-row" style="{'border: 1px solid ' + agent_info['color'] + '30;' if is_primary else ''}">
                        <span class="comp-icon">{agent_info['icon']}</span>
                        <span class="comp-name">{agent_info['name']}{badge_html}</span>
                        <span class="comp-score" style="color:{agent_info['color']};">{score}%</span>
                    </div>
                    <div class="score-bar-container">
                        <div class="score-bar-fill" style="width:{score}%;--bar-color:{agent_info['color']};--bar-color-end:{agent_info['color']}88;opacity:{bar_opacity};"></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        # --- ARCHITEKTUR-DIAGRAMM ---
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown(f"### 🏗️ Empfohlene Agenten-Architektur: {primary_type['icon']} {primary_type['name']}")
        st.markdown(
            '<p style="color:#94A3B8;font-size:0.9rem;margin-bottom:12px;">'
            "Dieses Diagramm zeigt, wie der empfohlene Agententyp auf Basis deines konkreten "
            "BPMN-Prozesses strukturiert werden könnte.</p>",
            unsafe_allow_html=True,
        )

        arch_dot = generate_architecture_dot(result["primary"], m)
        if arch_dot:
            st.graphviz_chart(arch_dot, use_container_width=True)

        # --- THEORIE ---
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        with st.expander(f"📖 Theorie: {primary_type['icon']} {primary_type['name']} im Detail"):
            th_col1, th_col2 = st.columns(2)
            with th_col1:
                st.markdown(f"**Beschreibung:**\n\n{primary_type['beschreibung']}")
                st.markdown("**✅ Stärken:**")
                for s in primary_type["staerken"]:
                    st.markdown(f"- {s}")
            with th_col2:
                st.markdown("**❌ Schwächen:**")
                for s in primary_type["schwaechen"]:
                    st.markdown(f"- {s}")
                st.markdown("**💡 Typische Anwendungsfälle:**")
                for s in primary_type["use_cases"]:
                    st.markdown(f"- {s}")

        if result["secondary"]:
            sec_type = AGENT_TYPES[result["secondary"]]
            with st.expander(f"📖 Theorie: {sec_type['icon']} {sec_type['name']} (Hybrid-Option)"):
                th2_col1, th2_col2 = st.columns(2)
                with th2_col1:
                    st.markdown(f"**Beschreibung:**\n\n{sec_type['beschreibung']}")
                    st.markdown("**✅ Stärken:**")
                    for s in sec_type["staerken"]:
                        st.markdown(f"- {s}")
                with th2_col2:
                    st.markdown("**❌ Schwächen:**")
                    for s in sec_type["schwaechen"]:
                        st.markdown(f"- {s}")
                    st.markdown("**💡 Typische Anwendungsfälle:**")
                    for s in sec_type["use_cases"]:
                        st.markdown(f"- {s}")

        # --- REPORT DOWNLOAD ---
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### 📥 Bericht exportieren")

        report_html = generate_html_report(m, result, fd)
        dl_col1, dl_col2 = st.columns([1, 3])
        with dl_col1:
            st.download_button(
                label="📄 HTML-Bericht herunterladen",
                data=report_html,
                file_name=f"agent_analyse_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
                mime="text/html",
                use_container_width=True,
            )
        with dl_col2:
            st.markdown(
                '<p style="color:#94A3B8;font-size:0.85rem;padding-top:8px;">'
                "💡 Tipp: Öffne die HTML-Datei im Browser und nutze <strong>Strg+P / ⌘+P</strong> "
                "um sie als PDF zu speichern.</p>",
                unsafe_allow_html=True,
            )