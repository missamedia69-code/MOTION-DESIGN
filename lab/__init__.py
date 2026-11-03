"""Laboratoire MOTION-DESIGN : données en entrée → vidéo en sortie.

Analogie : l'IA est le *laborantin*, ``spec.json`` est le *protocole*,
les capacités du moteur sont les *instruments*, chaque rendu est une
*expérience* et le MP4 est l'*artefact*.

Portes d'entrée :
  ./md lab run  <spec.json>     CLI (une expérience)
  ./md lab serve --port 8080    API HTTP + paillasse web
  ./md lab mcp                  serveur MCP stdio (connexion directe d'un agent)
"""
