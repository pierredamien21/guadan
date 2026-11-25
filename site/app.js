// La page fonctionne sans ce script : il rend vivantes la saisie, les étapes, le quota et la commande.

// --- 1. L'expression : même règle de C++ que celle que muparser enfreignait à la ligne 158 ---
// Évaluateur arithmétique minimal (nombres, + - * /, parenthèses), sans eval.
function evaluer(texte) {
  const jetons = texte.match(/\d+\.?\d*(?:e[+-]?\d+)?|\.\d+(?:e[+-]?\d+)?|[()+\-*/]/gi);
  if (!jetons || jetons.join("") !== texte.replace(/\s+/g, "")) return null;
  let i = 0;
  const prim = () => {
    const t = jetons[i++];
    if (t === "(") { const v = somme(); if (jetons[i++] !== ")") throw 0; return v; }
    if (t === "-") return -prim();
    if (t === "+") return prim();
    const v = Number(t); if (Number.isNaN(v)) throw 0; return v;
  };
  const produit = () => { let v = prim(); while (jetons[i] === "*" || jetons[i] === "/") v = jetons[i++] === "*" ? v * prim() : v / prim(); return v; };
  const somme = () => { let v = produit(); while (jetons[i] === "+" || jetons[i] === "-") v = jetons[i++] === "+" ? v + produit() : v - produit(); return v; };
  try { const v = somme(); return i === jetons.length ? v : null; } catch { return null; }
}

const tientDansInt = (x) => !Number.isNaN(x) && x > -2147483649 && x < 2147483648;
// format %g d'UBSan pour les grands nombres : 8.8e+09, -5e+09
const ecrire = (x) => (Number.isNaN(x) ? "nan" : Math.abs(x) >= 1e6
  ? x.toExponential().replace(/e([+-])(\d)$/, "e$10$2") : String(x));

function juger(expr) {
  const m = expr.replace(/\s+/g, "").match(/^(.+?)(&&|\|\|)(.+)$/);
  if (!m) return { ub: false, verdict: "Ce pré-calcul n'a pas lieu.", sortie: "", note: "Pas de && ni de || entre deux nombres : la ligne 158 n'est pas atteinte." };
  const [x, y] = [evaluer(m[1]), evaluer(m[3])];
  if (x === null || y === null) return { ub: false, verdict: "Expression non reconnue.", sortie: "", note: "Essayez deux nombres reliés par && ou ||, par exemple 88e8&&2." };
  const fautif = [x, y].find((v) => !tientDansInt(v));
  if (fautif === undefined) return { ub: false, verdict: "Aucun comportement indéfini.", sortie: `${ecrire(x)} ${m[2]} ${ecrire(y)} → ${m[2] === "&&" ? Number(!!x && !!y) : Number(!!x || !!y)}`, note: "Les deux nombres tiennent dans un int : la conversion de la ligne 158 est sûre." };
  return { ub: true, verdict: "Comportement indéfini : UBSan arrête muparser.",
    sortie: `muParserBytecode.cpp:158:25: runtime error: ${ecrire(fautif)} is outside the range of representable values of type 'int'`,
    note: "Le message est celui qu'affiche UBSan pour cette conversion ; muparser 9e28c71, corrigé depuis en amont (430ce5c)." };
}

const expr = document.getElementById("expr");
function majExpr() {
  const r = juger(expr.value);
  document.getElementById("verdict").textContent = r.verdict;
  document.getElementById("sortie").textContent = r.sortie || "—";
  document.getElementById("note").textContent = r.note;
  document.querySelector(".reponse").classList.toggle("ub", r.ub);
}
expr.addEventListener("input", majExpr);
document.querySelectorAll(".exemples button").forEach((b) =>
  b.addEventListener("click", () => { expr.value = b.dataset.expr; majExpr(); expr.focus(); }));

// --- 2. Les étapes ---
const CLAUSES = [
  ["D'abord, une copie du dépôt.", "Le dépôt est copié dans un dossier de travail : l'original n'est jamais modifié."],
  ["Ensuite, configurer avec réseau.", "Phase A : CMake télécharge ce qu'il faut ; le compilateur ajoute ASan, UBSan et neutralise -Werror."],
  ["Puis tout exécuter sans réseau.", "Phase B : compilation, tests, analyse statique et fuzzing, sans réseau ni secret."],
  ["Enfin, ne garder que les preuves.", "Le rapport sépare ce qui a été vu à l'exécution, avec sa commande, des alertes non confirmées."],
];
const etape = document.getElementById("etape");
etape.addEventListener("input", () => {
  const n = Number(etape.value);
  document.getElementById("t-etape").textContent = CLAUSES[n][0];
  document.getElementById("detail-etape").textContent = CLAUSES[n][1];
  document.querySelectorAll(".fragment").forEach((f) => { f.hidden = Number(f.dataset.etape) !== n; });
  document.querySelectorAll(".noms-etapes li").forEach((li, i) => li.classList.toggle("actif", i === n));
});

// --- 3. Le quota gratuit ---
const jetons = document.getElementById("jetons");
const nombre = new Intl.NumberFormat("fr-FR");
function majQuota() {
  const j = Number(jetons.value);
  document.getElementById("jetons-val").textContent = `${nombre.format(j)} jetons`;
  document.getElementById("analyses").textContent = nombre.format(Math.floor(200000 / j));
}
jetons.addEventListener("input", majQuota);
majQuota();

// --- 4. La commande à lancer ---
document.getElementById("forme-commande").addEventListener("submit", (e) => {
  e.preventDefault();
  const chemin = document.getElementById("chemin").value.trim() || "./mon-projet";
  const sur = /^[\w./~-]+$/.test(chemin) ? chemin : `'${chemin.replace(/'/g, "'\\''")}'`;
  const bloc = document.getElementById("commandes");
  bloc.querySelector("code").textContent =
    "git clone https://github.com/pierredamien21/guadan && cd guadan\n" +
    "docker build -t guadan-outils docker/\n" +
    `python3 -m guadan analyse ${sur} --sortie /tmp/rapport-guadan`;
  bloc.hidden = false;
});

// --- 5. Les noms qui s'allument tour à tour, et les entrées des sections ---
const reduit = matchMedia("(prefers-reduced-motion: reduce)").matches;
const noms = [...document.querySelectorAll("#liste-alertes .a")];
let k = 0;
if (!reduit && noms.length) setInterval(() => { noms[k].classList.remove("vif"); k = (k + 1) % noms.length; noms[k].classList.add("vif"); }, 2000);

document.documentElement.classList.add("anim");
const obs = new IntersectionObserver((entrees) => entrees.forEach((en) => {
  if (en.isIntersecting) { en.target.classList.add("vu"); obs.unobserve(en.target); }
}), { threshold: 0.15 });
document.querySelectorAll("section, .rangee").forEach((s) => obs.observe(s));
