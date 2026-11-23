"""Client LLM facultatif, au format OpenAI (D-05, D-08). Sans clé, guadan fonctionne sans LLM.

Variables : GUADAN_API_KEY (ou GROQ_API_KEY), GUADAN_API_URL, GUADAN_MODEL.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from guadan import __version__

URL_DEFAUT = "https://api.groq.com/openai/v1"
MODELE_DEFAUT = "openai/gpt-oss-120b"


class ErreurLLM(Exception):
    pass


def tronquer(texte: str, max_caracteres: int = 12_000) -> str:
    """Garde le début et surtout la fin, où se trouvent en général les erreurs."""
    if len(texte) <= max_caracteres:
        return texte
    debut = max_caracteres // 6
    return texte[:debut] + "\n[… tronqué par guadan …]\n" + texte[-(max_caracteres - debut):]


class Client:
    def __init__(self, url: str, cle: str, modele: str, avertir: bool = True):
        self.url, self._cle, self.modele = url.rstrip("/"), cle, modele
        self.jetons, self._averti = 0, not avertir

    @classmethod
    def depuis_env(cls):
        cle = os.environ.get("GUADAN_API_KEY") or os.environ.get("GROQ_API_KEY")
        if not cle:
            return None
        return cls(os.environ.get("GUADAN_API_URL", URL_DEFAUT), cle,
                   os.environ.get("GUADAN_MODEL", MODELE_DEFAUT))

    def demander(self, messages: list, max_jetons: int = 3000) -> str:
        if not self._averti:  # D-08 : dire que du code part chez un tiers, avant le premier envoi
            hote = urllib.parse.urlparse(self.url).hostname
            print(f"guadan: envoi d'extraits du dépôt à {hote} (modèle {self.modele})",
                  file=sys.stderr, flush=True)
            self._averti = True
        corps = json.dumps({"model": self.modele, "messages": messages,
                            "max_completion_tokens": max_jetons}).encode()
        for _ in range(6):
            req = urllib.request.Request(f"{self.url}/chat/completions", corps, {
                "Authorization": f"Bearer {self._cle}", "Content-Type": "application/json",
                # sans User-Agent explicite, Cloudflare bloque « Python-urllib » (403, code 1010)
                "User-Agent": f"guadan/{__version__}"})
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    d = json.load(r)
                self.jetons += d.get("usage", {}).get("total_tokens", 0)
                return d["choices"][0]["message"]["content"] or ""
            except urllib.error.HTTPError as e:
                if e.code != 429:
                    raise ErreurLLM(f"HTTP {e.code} de {self.url}: {e.read()[:200]!r}") from None
                time.sleep(float(e.headers.get("retry-after") or 30) + 0.5)
            except (urllib.error.URLError, TimeoutError) as e:
                raise ErreurLLM(f"{self.url} injoignable : {e}") from None
        raise ErreurLLM("limite de débit toujours atteinte après 6 essais")
