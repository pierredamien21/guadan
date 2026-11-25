#!/usr/bin/env bash
# Régénère les images du site (site/img) à partir de vrais rapports guadan rangés dans .apercu/<cas>/.
# Recadrage sans dépendance : une page cadre le rapport sur un élément, Edge sans interface la
# photographie à la taille voulue. À lancer depuis Git Bash sous Windows, rapports déjà produits.
set -euo pipefail
RACINE="$(cd "$(dirname "$0")/.." && pwd)"
APERCU="$RACINE/.apercu"
EDGE="/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
PORT=8766

cat > "$APERCU/capture.html" <<'EOF'
<!doctype html><meta charset="utf-8">
<style>html,body{margin:0;overflow:hidden;background:#472913}iframe{border:0;display:block}</style>
<iframe id="f"></iframe>
<script>
const q = new URLSearchParams(location.search), f = document.getElementById("f");
f.style.width = (q.get("l") || 1200) + "px"; f.style.height = "6000px";
f.onload = () => {
  f.contentDocument.querySelectorAll("details").forEach((d) => { d.open = true; });
  const el = q.get("sel") && f.contentDocument.querySelector(q.get("sel"));
  const y = el ? el.getBoundingClientRect().top + Number(q.get("dy") || 0) : 0;
  f.style.marginTop = -y + "px";
  f.style.marginLeft = -(q.get("dx") || 0) + "px";
};
f.src = q.get("r") + "/rapport.html";
</script>
EOF

python -m http.server "$PORT" --bind 127.0.0.1 --directory "$APERCU" > /dev/null 2>&1 &
SERVEUR=$!
trap 'kill $SERVEUR' EXIT
sleep 2

capture() { # nom largeur hauteur rapport sélecteur [dy] [largeur du rapport] [dx]
  "$EDGE" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --virtual-time-budget=4000 --window-size="$2,$3" \
    --screenshot="$(cygpath -w "$RACINE/site/img/$1.png")" \
    "http://127.0.0.1:$PORT/capture.html?r=$4&sel=$5&dy=${6:-0}&l=${7:-1200}&dx=${8:-0}" 2> /dev/null
  echo "$1.png"
}

mkdir -p "$RACINE/site/img"
capture muparser-ubsan      900 180  muparser       ".constat"  -2 1000 36
capture rapport-alertes     900 600  alertes        "table"     -70 1000 36
capture rapport-debordement 900 600  debordement-tas ".constat" -2 1000 36
capture rapport-reparation  900 900  vieux-code     "h2"        -16 1000 36
capture rapport-fuzzing     900 1125 parseur-fragile ".constat" -2 1000 36
capture rapport-muparser    900 600  muparser       ".chiffres" -16 1000 36
