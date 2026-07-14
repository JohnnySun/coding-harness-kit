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

> **Questa officina lavora sulla tua auto: il coding harness.** È lo strato di protezione per lo sviluppo con l’IA che circonda un repository di prodotto. Quel repository — il subject — possiede l’auto. Il codice di business è il motore, e il cofano resta chiuso.
> Il percorso breve: esegui l’accettazione con una riga → installa Agent-Kit per Cursor, Claude Code o Codex → se serve, collega un subject reale, quindi esegui sync, pin e il controllo `harness-ready`. I pezzi nuovi passano comunque sul banco prova, la public trusted suite. Controllare la vernice non è un piano di test.

| Termine | Significato (corrispondenza con l’officina) |
|------|---------|
| **coding harness** | La tua auto: lo strato di protezione per lo sviluppo IA attorno a un repository di prodotto (rules, skills, hooks, trusted suite, ledgers) |
| **subject** | Il repository di prodotto proprietario dell’auto (clone locale; non viene committato qui) |
| **harness surface** | Il reparto ricambi: `AGENTS.md`, skills, hooks e file di protezione simili; non è codice di business |
| **Agent-Kit** | Lo scaffale dei ricambi: materializza skills metodologiche / hook templates in Cursor, Claude Code, Codex, ecc. |
| **public trusted suite** | Il banco prova: `bash tools/harness/test-harness.sh` (uguale alla CI L2) |

## 1. Accettazione (inizializzazione)

Il modo più rapido per entrare in officina è l’installer in una riga. Clona il repository, inizializza i submodules, installa git hooks e Agent-Kit, quindi esegue la public trusted suite:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Se la shell non supporta la process substitution, usa la forma equivalente con pipe:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Le variabili d’ambiente opzionali sono `TARGET_DIR` e `CLIENT`. Imposta `CLIENT` su `cursor` / `claude` / `codex` / `codex-native` / `skip`.

Come alternativa manuale, o per osservare ogni giro di chiave:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

Ora dovresti trovarti in `los-santos-customs/`, con i submodules inizializzati e i git hooks installati. Il percorso in una riga installa anche Agent-Kit per il client scelto ed esegue la public suite. Se hai seguito il percorso manuale, continua al §2. Il cambio manuale richiede un passaggio in più; non è nostalgia.

## 2. Montare i ricambi (Agent-Kit)

Agent-Kit installa gli skills e gli hooks di questa officina nel tuo editor o nella CLI. Un’installazione senza opzioni fornisce questi valori predefiniti:

- metodologia locale;
- una selezione di skills per SP verification, TDD e review;
- una Matt library invocata dall’utente;
- un advisory router a bassa frequenza.

Non installa il bootstrap `using-superpowers` / `brainstorming` né i vendor hooks. I client trees (`.cursor` / `.claude` / `.codex` / `.agents`) sono output di installazione e non vengono committati. Rigenerali con install; i file generati non hanno bisogno del carrozziere.

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parametro | Valori |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (opzionale) | `lean`, `guided`, `structured`; regola solo la densità dei suggerimenti |

```bash
# Install all four clients (common local bootstrap)
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# Inspect or adjust the repo profile (agents write via CLI only)
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire fragments, then check
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` resta solo come percorso esplicito di compatibilità full-plugin per i workflow meno recenti. Non è più il percorso di installazione consigliato. La materialization predefinita della library non copia vendor plugins, hooks o skills fuori dalla allowlist. Lo scaffale dei ricambi ha un inventario per un motivo.

## 3. (Opzionale) Portare la propria auto

Un public clone può eseguire la public trusted suite senza repository di prodotto privati. Collega l’auto di un cliente alla tua officina locale solo quando devi eseguire sync, import o compare su un subject reale:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

L’ordine è importante:

1. Crea `subjects/manifest.yaml` dall’esempio. Fai puntare i remotes a repository a cui puoi accedere.
2. Esegui sync per recuperare la harness surface di ogni subject.
3. Usa `<id> --pin` per registrare la revision esatta da valutare.
4. Esegui il local absorb check. Un subject che lo supera è `harness-ready`; solo allora import, compare e score possono produrre risultati attendibili.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` e `comparisons/` sono auto dei clienti e ordini di lavoro. Restano in locale, sono ignorati da git e non entrano mai nel public showroom. Non è segretezza: è gestione basilare delle chiavi.

---

L’auto ora si muove con le proprie forze. Il resto è il riferimento per il reparto assistenza.

## Comandi comuni

| Scopo | Comando |
|---------|---------|
| Public trusted suite (chiudere il ciclo / CI) | `bash tools/harness/test-harness.sh` |
| Validare Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Eseguire sync della harness surface | `bash tools/sync/sync-subjects.sh` |
| Riscrivere il pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| Importare uno snapshot | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Weekly report | `python3 tools/harness/weekly_report.py` |

## Struttura

| Percorso | Ruolo | In git? |
|------|------|---------|
| `agent-kit/skills` | Metodologia aperta (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Client hooks/settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Output di installazione | ✗ |
| `subjects/manifest.example.yaml` | Esempio di registro pubblico | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registro locale / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixture pubbliche (CI) | ✓ |
| `snapshots/` / `comparisons/` | Prodotti di absorb | ✗ |
| `docs/harness/` | Design + ledgers | parziale |
| `AGENTS.md` | SSOT dei vincoli (`CLAUDE.md` → it) | ✓ |

## Documentazione

- [`docs/README.md`](../README.md) — regole per la posizione della documentazione
- [`docs/harness/design.md`](../harness/design.md) — harness design di questo repository
- [`docs/specs/`](../specs/) — archivio dei design
- [`AGENTS.md`](../../AGENTS.md) — definizione di completamento, blacklist, mappa dei meccanismi

## Licenza

[MIT](../../LICENSE)
