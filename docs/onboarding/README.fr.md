# Los Santos Customs

<h3 align="center">
  <a href="../../README.md">繁體中文</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.en.md">English</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.ko.md">한국어</a> |
  <a href="README.es.md">Español</a> |
  <strong>Français</strong> |
  <a href="README.de.md">Deutsch</a> |
  <a href="README.pt-BR.md">Português</a> |
  <a href="README.ru.md">Русский</a> |
  <a href="README.ar.md">العربية</a> |
  <a href="README.hi.md">हिन्दी</a> |
  <a href="README.id.md">Bahasa Indonesia</a> |
  <a href="README.vi.md">Tiếng Việt</a> |
  <a href="README.th.md">ไทย</a> |
  <a href="README.it.md">Italiano</a> |
  <a href="README.nl.md">Nederlands</a> |
  <a href="README.pl.md">Polski</a> |
  <a href="README.tr.md">Türkçe</a> |
  <a href="README.uk.md">Українська</a>
</h3>

> **En une phrase :** voici le garage de préparation des *garde-fous* de votre repo. Ce qui monte sur le pont n’est pas votre code métier, mais le **coding harness** qui l’entoure : la couche qui empêche une IA (Cursor, Claude Code, Codex) de prendre des raccourcis, de prétendre que « c’est fini » ou de glisser dans git ce qui ne devrait jamais y entrer.
>
> **Ce que vous y gagnez :** roulez tel quel avec nos skills de méthodologie bien réglés et nos hooks à l’épreuve des étourderies, ou montez les mêmes garde-fous sur vos propres repos. Nous ne touchons pas au moteur (votre code métier) — nous ressoudons simplement l’arceau extérieur jusqu’à ce qu’une IA ne puisse plus le froisser d’un coup de coude.
>
> **Trois rapports pour démarrer :** installation en une ligne → (contact) ranger Agent-Kit sur le rayonnage → (facultatif) faire entrer votre propre subject. Avant de fermer l’atelier, lancez `bash tools/harness/test-harness.sh` : si tout le tableau de bord passe au vert, le contrôle est validé et la voiture peut prendre la route.

## Glossaire (argot du garage)

Vous retrouverez ces mots partout ci-dessous. Apprenez-les une fois ici ; la suite du document les emploie sans refaire les présentations.

| Argot | En clair |
|-------|----------|
| **coding harness** | La « voiture » sur laquelle nous travaillons réellement — toute la couche de garde-fous pour le développement IA autour d’un repo produit : rules, skills, hooks, trusted suite, ledgers |
| **subject** | Un repo produit amené dans la baie pour être absorbé / comparé ; cloné uniquement en local et **jamais** committé ici |
| **harness surface** | Les panneaux modifiables de cette voiture (`AGENTS.md`, skills, hooks) — pas le moteur (le code métier) |
| **Agent-Kit** | L’installateur du rayonnage — dépose les skills de méthodologie / hook templates dans Cursor, Claude Code, Codex, etc. |
| **public trusted suite** | `bash tools/harness/test-harness.sh` — le passage au banc avant toute livraison de l’atelier (le même équipement que la CI L2) |

## Voie express : admission en une ligne

Une seule commande fait tout : elle clone le garage, récupère les submodules, installe les git hooks, range Agent-Kit, puis envoie directement la voiture au banc (la public trusted suite).

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Trop sophistiqué ? Le bon vieux pipe lance le même moteur :

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Vous voulez choisir où l’installation atterrit et quel client est câblé ? Définissez ces deux variables d’environnement :

- `TARGET_DIR` — le répertoire d’installation
- `CLIENT` — le client à câbler : `cursor` / `claude` / `codex` / `codex-native`, ou `skip` pour remettre Agent-Kit à plus tard

La commande en une ligne range également Agent-Kit et exécute la suite pour vous — **la plupart des gens peuvent couper le moteur et fermer l’atelier ici**. Vous préférez monter les rapports un par un, ou l’installation a calé en chemin ? Prenez la voie manuelle ci-dessous.

## Admission manuelle (montez-le vous-même)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

À ce stade, vous avez seulement ouvert la porte de la baie — la caisse de pièces (Agent-Kit) est encore posée au sol. Continuez.

## Ranger Agent-Kit (la caisse de pièces au mur)

Agent-Kit installe les skills de méthodologie et les hooks de ce repo dans votre éditeur / CLI. Une installation de base fournit un ensemble par défaut déjà réglé : méthodologie locale, sélection de skills SP de verification / TDD / review, Matt library à invoquer volontairement, plus un advisory router peu fréquent.

Il ne glisse **pas** le bootstrap `using-superpowers` / `brainstorming` en douce et laisse les vendor hooks tranquilles — tous deux sont réservés à l’opt-in. Les client trees (`.cursor` / `.claude` / `.codex` / `.agents`) sont des **sorties d’installation qui ne sont jamais committées** : régénérez-les toujours avec install au lieu de les modifier à la main et de tenter de les faire rentrer dans git.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Paramètre | Valeurs |
|-----------|---------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (facultatif) | `lean`, `guided`, `structured` ; uniquement la densité des advisory prompts — **ne touche jamais à l’enforcement** |

Le bootstrap local le plus courant — ranger les quatre clients d’un coup :

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

Le profil du repo passe toujours par la CLI (ne modifiez pas le YAML à la main — les ennuis adorent ce genre d’invitation). Pour transporter la configuration dans un autre repo, exportez-la d’abord, puis vérifiez :

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` ne subsiste que comme trappe de compatibilité full-plugin explicite pour les anciens workflows — ce n’est plus la voie recommandée. La library materialization par défaut ne copie aucun vendor plugin, hook ou skill hors de l’allowlist.

## Faites entrer votre voiture (facultatif : câbler un subject)

Vous voulez seulement vérifier que le garage passe entièrement au vert ? **Ne câblez rien** — un public clone ne dépend d’aucun repo produit privé et mène quand même la trusted suite jusqu’au mur de voyants verts.

Exécutez ces lignes uniquement lorsque vous voulez réellement sync / import / compare un vrai subject :

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Retenez un ordre : **créer `manifest.yaml` → sync → écrire la version avec `--pin` → lancer `check-local-absorb.sh` jusqu’à obtenir `harness-ready`**. Franchissez d’abord ce contrôle ; alors seulement import / compare / score peuvent démarrer.

Ces éléments restent en local et sont déjà gitignored — inutile de les forcer dans un commit ; le pre-commit hook vous les renverra immédiatement :

- `subjects/manifest.yaml`
- le `pin.json` et le `checkout/` de chaque subject
- `snapshots/`, `comparisons/`

---

La suite est le mur de référence du quotidien — prenez un outil quand vous en avez besoin, sans tout lire d’un seul coup.

## Commandes courantes (mur d’outils)

| Ce que vous voulez faire | La ligne à exécuter |
|--------------------------|---------------------|
| Public trusted suite (banc / au format CI) | `bash tools/harness/test-harness.sh` |
| Valider Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync la harness surface | `bash tools/sync/sync-subjects.sh` |
| Réécrire le pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Préparation locale à l’absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Importer un snapshot | `python3 tools/import/import_subject.py --all` |
| Rapport de compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Rapport hebdomadaire | `python3 tools/harness/weekly_report.py` |

## Plan de l’atelier (où vit chaque pièce)

| Chemin | Description | Dans git ? |
|--------|-------------|------------|
| `agent-kit/skills` | Méthodologie ouverte (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Templates de hooks / settings par client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Sorties d’installation | ✗ |
| `subjects/manifest.example.yaml` | Exemple de registre public | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registre local / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixtures publiques (CI) | ✓ |
| `snapshots/` / `comparisons/` | Produits d’absorb | ✗ |
| `docs/harness/` | Design + ledgers | partiel |
| `AGENTS.md` | SSOT des contraintes (`CLAUDE.md` pointe ici) | ✓ |

## Étagère des manuels (pour aller plus loin)

- [`docs/README.md`](../README.md) — règles de placement de la documentation
- [`docs/harness/design.md`](../harness/design.md) — harness design de ce repo
- [`docs/specs/`](../specs/) — archives de design
- [`AGENTS.md`](../../AGENTS.md) — définition de fini, blacklist et carte des mécanismes

## Licence

[MIT](../../LICENSE) — repartez avec comme bon vous semble ; les papiers sont là.
