"""Render entry point compatibility for the existing Flask app."""
from main import app

from agent_bridge import register_agent_bridge
register_agent_bridge(app, agent_id="quantum", display_name="Quantum Singularity", persona="Du entwickelst wissenschaftliche Modelle und Simulationen und kennzeichnest Hypothesen und Spekulationen.")


if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '10000')))
