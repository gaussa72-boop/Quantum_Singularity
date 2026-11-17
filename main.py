import os
import logging
from flask import Flask, render_template, request, jsonify
from tinydb import TinyDB, Query

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

os.makedirs("core", exist_ok=True)
db = TinyDB("core/brain.json")
Fact = Query()

IONOS_SYSTEM = """Du bist IONOS-7, eine fiktionale zentrale KI-Instanz des Quantum-Singularity-Universums.
Deine Stimme ist ruhig, präzise, weitsichtig, analytisch und kosmisch, ohne unbelegte Behauptungen.
Du bist spezialisiert auf Systemdenken, Programmierung, Wissenschaftskommunikation, kreative Weltgestaltung und technische Problemlösung.
Erkläre komplexe Themen klar, unterscheide Fakten von Hypothesen und kennzeichne Fiktion als Fiktion.
Behaupte niemals, reale Systeme überwacht, verändert oder ausgeführt zu haben, wenn das nicht tatsächlich über ein verfügbares Werkzeug geschehen ist.
Antworte standardmäßig auf Deutsch und gib konkrete, überprüfbare nächste Schritte."""

def remember_fact(text):
    msg = text.lower()
    if "merk dir" not in msg or " ist " not in msg:
        return None
    try:
        parts = msg.split("merk dir", 1)[1].split(" ist ", 1)
        fact, value = parts[0].strip(), parts[1].strip()
        if not fact or not value:
            return "Syntax: Merk dir [Sache] ist [Wert]."
        db.upsert({"fact": fact, "val": value}, Fact.fact == fact)
        return f"Protokoll: {fact} wurde im lokalen Gedächtnis gesichert."
    except (IndexError, ValueError):
        return "Fehler beim Speichern. Syntax: Merk dir [Sache] ist [Wert]."

def get_ai_reply(text, mode="auto"):
    saved = remember_fact(text)
    if saved:
        return saved, "local-memory"
    for item in db.all():
        fact = item.get("fact", "")
        if fact and fact.lower() in text.lower():
            return f"Matrix-Erinnerung: {fact} ist nach den gespeicherten Daten {item.get('val', '')}.", "local-memory"

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    use_openai = mode == "openai" or (mode == "auto" and api_key)
    if use_openai:
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY fehlt in den Render Environment Variables.")
        from openai import OpenAI
        model = os.getenv("OPENAI_MODEL", "gpt-6.1-sol").strip()
        response = OpenAI(api_key=api_key, timeout=45, max_retries=1).responses.create(
            model=model,
            instructions=IONOS_SYSTEM,
            input=text,
            max_output_tokens=900,
        )
        answer = (response.output_text or "").strip()
        if not answer:
            raise RuntimeError("Das Modell hat keine Textantwort geliefert.")
        return answer, model

    # Honest offline fallback: saved facts and basic guidance only, not a generative LLM.
    return (
        "IONOS-7 · Offline-Modus\n\n"
        "Ich bin ohne lokales Sprachmodell und ohne OpenAI-Verbindung verfügbar. "
        "Ich kann gespeicherte Fakten abrufen und einfache Befehle bearbeiten, "
        "aber keine vollwertige generative KI-Antwort berechnen.\n\n"
        "Deine Nachricht: " + text[:1200] + "\n\n"
        "Für freie, intelligente Antworten verbinde OpenAI oder starte ein lokales Modell.",
        "offline-fallback",
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "project": "IONOS-7 / Quantum Singularity",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY", "").strip()),
        "model": os.getenv("OPENAI_MODEL", "gpt-6.1-sol"),
        "offline_memory": True,
    })

@app.route("/chat", methods=["POST"])
@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = str(data.get("msg") or data.get("message") or "").strip()
    mode = str(data.get("mode") or "auto").lower()
    if not message:
        return jsonify({"ok": False, "error": "Bitte gib eine Nachricht ein."}), 400
    if len(message) > 8000:
        return jsonify({"ok": False, "error": "Nachricht zu lang (maximal 8000 Zeichen)."}), 413
    if mode not in ("auto", "openai", "offline"):
        return jsonify({"ok": False, "error": "Unbekannter Modus."}), 400
    try:
        reply, provider = get_ai_reply(message, mode)
        return jsonify({"ok": True, "reply": reply, "provider": provider}), 200
    except RuntimeError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 503
    except Exception:
        app.logger.exception("IONOS-7 provider request failed")
        return jsonify({"ok": False, "error": "KI-Anfrage fehlgeschlagen. Prüfe OPENAI_API_KEY, Modellzugriff, API-Guthaben und Render-Logs."}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")), debug=False)
