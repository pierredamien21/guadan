"""Client LLM contre un faux serveur local : aucun appel réseau réel."""
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from guadan import llm


class FauxServeur(BaseHTTPRequestHandler):
    reponses = []   # (code, en-têtes, corps) servis dans l'ordre
    recues = []     # (en-têtes, corps) des requêtes reçues

    def do_POST(self):
        corps = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FauxServeur.recues.append((dict(self.headers), corps))
        code, entetes, rep = FauxServeur.reponses.pop(0)
        self.send_response(code)
        for k, v in entetes.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(json.dumps(rep).encode())

    def log_message(self, *a):
        pass


@pytest.fixture
def serveur():
    FauxServeur.reponses, FauxServeur.recues = [], []
    s = HTTPServer(("127.0.0.1", 0), FauxServeur)
    threading.Thread(target=s.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{s.server_port}/v1"
    s.shutdown()


def ok(texte, jetons=10):
    return (200, {}, {"choices": [{"message": {"content": texte}}], "usage": {"total_tokens": jetons}})


def test_sans_cle_pas_de_client(monkeypatch):
    for v in ("GUADAN_API_KEY", "GROQ_API_KEY"):
        monkeypatch.delenv(v, raising=False)
    assert llm.Client.depuis_env() is None


def test_requete_au_format_openai_avec_user_agent(serveur):
    FauxServeur.reponses = [ok("bonjour", 42)]
    c = llm.Client(serveur, "cle-de-test", "modele-x", avertir=False)
    assert c.demander([{"role": "user", "content": "salut"}]) == "bonjour"
    entetes, corps = FauxServeur.recues[0]
    assert entetes["Authorization"] == "Bearer cle-de-test"
    assert entetes["User-Agent"].startswith("guadan/")
    assert corps["model"] == "modele-x" and corps["messages"][0]["content"] == "salut"
    assert c.jetons == 42


def test_attend_puis_reessaie_sur_429(serveur):
    FauxServeur.reponses = [(429, {"retry-after": "0"}, {}), ok("après attente")]
    c = llm.Client(serveur, "k", "m", avertir=False)
    assert c.demander([{"role": "user", "content": "x"}]) == "après attente"
    assert len(FauxServeur.recues) == 2


def test_erreur_http_explicite_sans_la_cle(serveur):
    FauxServeur.reponses = [(401, {}, {"error": "bad key"})]
    c = llm.Client(serveur, "cle-secrete-123", "m", avertir=False)
    with pytest.raises(llm.ErreurLLM) as e:
        c.demander([{"role": "user", "content": "x"}])
    assert "401" in str(e.value) and "cle-secrete-123" not in str(e.value)


def test_troncature_garde_le_debut_et_surtout_la_fin():
    log = "debut\n" + "x" * 50_000 + "\nCMake Error: la vraie cause\n"
    t = llm.tronquer(log, 1000)
    assert len(t) <= 1100 and t.startswith("debut") and t.rstrip().endswith("la vraie cause")
    assert llm.tronquer("court", 1000) == "court"
