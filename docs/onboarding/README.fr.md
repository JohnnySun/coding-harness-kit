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

> **Cet atelier travaille sur votre voiture : le coding harness.** C’est la couche de garde-fous pour le développement assisté par l’IA qui entoure un dépôt produit. Ce dépôt produit — le subject — possède la voiture. Le code métier est le moteur, et nous gardons le capot fermé.
> Le trajet court : lancez la commande d’admission en une ligne → installez Agent-Kit pour Cursor, Claude Code ou Codex → si nécessaire, connectez un vrai subject, puis lancez sync, pin et la vérification `harness-ready`. Les pièces neuves passent toujours au banc, la public trusted suite. Inspecter la peinture ne remplace pas un plan de test.

| Terme | Signification (correspondance atelier) |
|------|---------|
| **coding harness** | Votre voiture : la couche de garde-fous pour le développement IA autour d’un dépôt produit (rules, skills, hooks, trusted suite, ledgers) |
| **subject** | Le dépôt produit propriétaire de la voiture (clone local ; non committé ici) |
| **harness surface** | La baie des pièces : `AGENTS.md`, skills, hooks et fichiers de garde-fous similaires ; pas le code métier |
| **Agent-Kit** | Le rayonnage de pièces : déploie les skills de méthodologie / hook templates dans Cursor, Claude Code, Codex, etc. |
| **public trusted suite** | Le banc d’essai : `bash tools/harness/test-harness.sh` (identique à la CI L2) |

## 1. Admission (initialisation)

L’accès le plus rapide à l’atelier est l’installateur en une ligne. Il clone le dépôt, initialise les submodules, installe les git hooks et Agent-Kit, puis exécute la public trusted suite :

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Si votre shell ne prend pas en charge la process substitution, utilisez la forme équivalente avec un pipe :

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Les variables d’environnement facultatives sont `TARGET_DIR` et `CLIENT`. Définissez `CLIENT` sur `cursor` / `claude` / `codex` / `codex-native` / `skip`.

Pour une solution de repli manuelle, ou pour observer chaque tour de clé :

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

Vous devriez maintenant être dans `los-santos-customs/`, avec les submodules initialisés et les git hooks installés. Le parcours en une ligne installe également Agent-Kit pour le client choisi et exécute la public suite. Si vous avez suivi le parcours manuel, passez au §2. Une boîte manuelle ajoute une étape ; ce n’est pas par nostalgie.

## 2. Monter les pièces (Agent-Kit)

Agent-Kit installe les skills et hooks de cet atelier dans votre éditeur ou votre CLI. Une installation sans option fournit ces réglages assumés :

- la méthodologie locale ;
- une sélection de skills SP verification, TDD et review ;
- une Matt library invoquée par l’utilisateur ;
- un advisory router peu fréquent.

Il n’installe ni le bootstrap `using-superpowers` / `brainstorming` ni les vendor hooks. Les client trees (`.cursor` / `.claude` / `.codex` / `.agents`) sont des sorties d’installation et ne sont pas committés. Régénérez-les avec install ; les fichiers générés n’ont pas besoin de carrosserie.

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Paramètre | Valeurs |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (facultatif) | `lean`, `guided`, `structured` ; ajuste uniquement la densité des conseils |

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

`PLUGIN` ne subsiste que comme chemin de compatibilité full-plugin explicite pour les anciens workflows. Ce n’est plus la méthode d’installation recommandée. La materialization par défaut de la library ne copie aucun vendor plugin, hook ou skill hors de l’allowlist. Le rayonnage tient un inventaire pour une bonne raison.

## 3. (Facultatif) Amener votre propre voiture

Un public clone peut exécuter la public trusted suite sans dépôt produit privé. Ne connectez une voiture client à votre baie locale que si vous devez sync, import ou compare un vrai subject :

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

L’ordre compte :

1. Créez `subjects/manifest.yaml` à partir de l’exemple. Faites pointer ses remotes vers des dépôts auxquels vous avez accès.
2. Exécutez sync pour récupérer la harness surface de chaque subject.
3. Utilisez `<id> --pin` pour enregistrer la revision exacte à évaluer.
4. Exécutez le local absorb check. Un subject qui réussit est `harness-ready` ; alors seulement import, compare et score peuvent produire des résultats fiables.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` et `comparisons/` sont les voitures des clients et les ordres de travail. Ils restent en local, sont ignorés par git et n’entrent jamais dans le public showroom. Ce n’est pas du secret : c’est la gestion élémentaire des clés.

---

La voiture roule maintenant par ses propres moyens. La suite est la référence de la baie de service.

## Commandes courantes

| Objectif | Commande |
|---------|---------|
| Public trusted suite (boucler la boucle / CI) | `bash tools/harness/test-harness.sh` |
| Valider Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Sync la harness surface | `bash tools/sync/sync-subjects.sh` |
| Réécrire le pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| Importer un snapshot | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Weekly report | `python3 tools/harness/weekly_report.py` |

## Arborescence

| Chemin | Rôle | Dans git ? |
|------|------|---------|
| `agent-kit/skills` | Méthodologie ouverte (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Client hooks/settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Sorties d’installation | ✗ |
| `subjects/manifest.example.yaml` | Exemple de registre public | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registre local / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixtures publiques (CI) | ✓ |
| `snapshots/` / `comparisons/` | Produits d’absorb | ✗ |
| `docs/harness/` | Design + ledgers | partiel |
| `AGENTS.md` | SSOT des contraintes (`CLAUDE.md` → it) | ✓ |

## Documentation

- [`docs/README.md`](../README.md) — règles de placement de la documentation
- [`docs/harness/design.md`](../harness/design.md) — harness design de ce dépôt
- [`docs/specs/`](../specs/) — archives de design
- [`AGENTS.md`](../../AGENTS.md) — définition de fini, blacklist, carte des mécanismes

## Licence

[MIT](../../LICENSE)
