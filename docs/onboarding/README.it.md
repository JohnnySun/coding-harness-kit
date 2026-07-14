# Los Santos Customs

<h3 align="center">
  <a href="../../README.md">繁體中文</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.en.md">English</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.ko.md">한국어</a> |
  <a href="README.es.md">Español</a> |
  <a href="README.fr.md">Français</a> |
  <a href="README.de.md">Deutsch</a> |
  <a href="README.pt-BR.md">Português</a> |
  <a href="README.ru.md">Русский</a> |
  <a href="README.ar.md">العربية</a> |
  <a href="README.hi.md">हिन्दी</a> |
  <a href="README.id.md">Bahasa Indonesia</a> |
  <a href="README.vi.md">Tiếng Việt</a> |
  <a href="README.th.md">ไทย</a> |
  <strong>Italiano</strong> |
  <a href="README.nl.md">Nederlands</a> |
  <a href="README.pl.md">Polski</a> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a>
</h3>

> **In una riga:** questa è l’officina per i *guardrails* del tuo repo. Sul ponte non sale il codice di business, ma il **coding harness** che lo avvolge: lo strato che impedisce a un’IA (Cursor, Claude Code, Codex) di tagliare le curve, dichiarare “fatto” senza prove o infilare in git ciò che non va committato.
>
> **Cosa ci guadagni:** puoi guidare con le nostre methodology skills già messe a punto e gli hooks a prova di distrazione, oppure montare gli stessi guardrails sui tuoi repo. Il motore (il tuo codice di business) non si tocca: saldiamo soltanto il roll-bar esterno finché un’IA non può accartocciarlo con nonchalance.
>
> **Tre marce per partire:** installazione in una riga → (accensione) metti Agent-Kit sullo scaffale → (facoltativo) porta dentro il tuo subject. Prima di chiudere l’officina, esegui `bash tools/harness/test-harness.sh`: cruscotto tutto verde significa revisione superata e via libera su strada.

## Glossario (gergo da officina)

Queste parole tornano spesso. Imparale qui una volta sola; il resto del documento le usa senza ripresentarle.

| Gergo | In parole semplici |
|-------|--------------------|
| **coding harness** | L’“auto” su cui lavoriamo davvero: l’intero strato di guardrail AI-dev attorno a un repo di prodotto, cioè rules, skills, hooks, trusted suite, ledgers |
| **subject** | Un repo di prodotto portato sul ponte per absorb / compare; viene clonato solo in locale e **mai** committato qui |
| **harness surface** | I pannelli modificabili dell’auto (`AGENTS.md`, skills, hooks), non il motore (codice di business) |
| **Agent-Kit** | L’installer dello scaffale ricambi: distribuisce methodology skills / hook templates in Cursor, Claude Code, Codex, ecc. |
| **public trusted suite** | `bash tools/harness/test-harness.sh`: il giro al banco prova prima che qualcosa lasci l’officina (lo stesso impianto della CI L2) |

## Corsia più veloce: accettazione in una riga

Un solo command fa tutto: clona l’officina, recupera i submodules, installa i git hooks, sistema Agent-Kit sullo scaffale e porta subito il mezzo al banco prova (la public trusted suite).

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Troppo sofisticato? Il vecchio pipe mette in moto lo stesso motore:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Vuoi scegliere dove installare e quale client cablare? Imposta queste due env vars:

- `TARGET_DIR` — la directory in cui installare
- `CLIENT` — il client da cablare: `cursor` / `claude` / `codex` / `codex-native`, oppure `skip` per rimandare Agent-Kit

La one-liner sistema anche Agent-Kit ed esegue la suite: **la maggior parte delle persone può spegnere il motore e timbrare l’uscita qui**. Vuoi montare una marcia alla volta, oppure la one-liner si è fermata a metà? Prendi la corsia manuale.

## Accettazione manuale (montaggio fai da te)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

A questo punto hai soltanto aperto la saracinesca: la cassa dei ricambi (Agent-Kit) è ancora sul pavimento. Continua.

## Metti Agent-Kit sullo scaffale (la cassa va a parete)

Agent-Kit distribuisce le methodology skills e gli hooks di questo repo nel tuo editor / CLI. Un’installazione senza opzioni fornisce un set predefinito già messo a punto: metodologia locale, una selezione curata di SP verification / TDD / review skills, una Matt library da richiamare quando serve e un advisory router a bassa frequenza.

Non installa di nascosto il bootstrap `using-superpowers` / `brainstorming` e lascia stare i vendor hooks: sono solo opt-in. I client trees (`.cursor` / `.claude` / `.codex` / `.agents`) sono **output di installazione e non vanno mai committati**: rigenerali sempre con install, invece di modificarli a mano e contrabbandarli in git.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parametro | Valori |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (facoltativo) | `lean`, `guided`, `structured`; regola solo la densità degli advisory prompt e **non** modifica mai l’enforcement |

Il bootstrap locale più comune: sistema tutti e quattro i client in una volta:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Il profile del repo passa sempre dalla CLI (modificare lo YAML a mano significa cercarsi guai). Per portare la configurazione in un altro repo, prima esporta e poi controlla:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` rimane soltanto come uscita di compatibilità full-plugin esplicita per i vecchi workflow: non è più il percorso consigliato. La materialization predefinita della library non copia vendor plugins, hooks o skills fuori dalla allowlist.

## Porta dentro la tua auto (facoltativo: collega un subject)

Vuoi solo verificare che l’officina sia tutta verde? **Non collegare nulla**: un clone pubblico non dipende da alcun repo di prodotto privato e può comunque eseguire la trusted suite fino all’ultimo semaforo verde.

Esegui queste righe solo quando vuoi davvero fare sync / import / compare di un subject reale:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Ricorda un solo ordine: **crea `manifest.yaml` → sync → `--pin` per riscrivere la versione → `check-local-absorb.sh` finché non è `harness-ready`**. Supera prima questo gate; solo allora possono partire import / compare / score.

Questi elementi restano in locale e sono già ignorati da git: non provare a forzarli in un commit, perché il pre-commit hook li respingerà all’istante:

- `subjects/manifest.yaml`
- `pin.json` e `checkout/` di ogni subject
- `snapshots/`, `comparisons/`

---

Qui sotto trovi la parete degli attrezzi quotidiani: prendi ciò che serve, senza leggere tutto in una volta.

## Comandi comuni (parete degli attrezzi)

| Cosa vuoi fare | Riga da eseguire |
|----------------|------------------|
| Public trusted suite (banco prova / come la CI) | `bash tools/harness/test-harness.sh` |
| Validare Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sincronizzare la harness surface | `bash tools/sync/sync-subjects.sh` |
| Riscrivere il pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| Importare uno snapshot | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Weekly report | `python3 tools/harness/weekly_report.py` |

## Pianta dell’officina (dove vive ogni pezzo)

| Percorso | Cos’è | In git? |
|----------|-------|---------|
| `agent-kit/skills` | Metodologia aperta (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Hooks / settings templates per client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Output di installazione | ✗ |
| `subjects/manifest.example.yaml` | Esempio pubblico di registry | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registry / clone locale | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixture pubbliche (CI) | ✓ |
| `snapshots/` / `comparisons/` | Prodotti di absorb | ✗ |
| `docs/harness/` | Design + ledgers | parziale |
| `AGENTS.md` | SSOT dei vincoli (`CLAUDE.md` rimanda qui) | ✓ |

## Scaffale dei manuali (per approfondire)

- [`docs/README.md`](../README.md) — regole di collocazione della documentazione
- [`docs/harness/design.md`](../harness/design.md) — design del harness di questo repo
- [`docs/specs/`](../specs/) — archivio dei design
- [`AGENTS.md`](../../AGENTS.md) — definizione di completamento, blacklist, mappa dei meccanismi

## Licenza

[MIT](../../LICENSE) — portala fuori dal salone come preferisci; il libretto è qui.
