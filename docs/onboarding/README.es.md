# Los Santos Customs

<h3 align="center">
  <a href="../../README.md">繁體中文</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.en.md">English</a> |
  <a href="README.ja.md">日本語</a> |
  <a href="README.ko.md">한국어</a> |
  <strong>Español</strong> |
  <a href="README.fr.md">Français</a> |
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

> **En una línea:** este es el taller de desguace y tuneo para los *guardarraíles* de tu repo. Lo que sube al elevador no es tu código de negocio, sino el **coding harness** que lo envuelve: la capa que impide que una IA (Cursor, Claude Code, Codex) tome atajos, finja que «ya está» o cuele en git cosas que nunca debieron entrar.
>
> **Qué ganas tú:** puedes conducir tal cual con nuestros skills de metodología afinados y hooks a prueba de despistes, o montar los mismos guardarraíles en tus propios repos. No tocamos el motor (tu código de negocio): solo soldamos la jaula exterior hasta que una IA ya no pueda arrugarla como si nada.
>
> **Tres marchas para echar a rodar:** instalación en una línea → (contacto) colocar Agent-Kit en el estante → (opcional) meter tu propio subject. Antes de cerrar el taller, pisa `bash tools/harness/test-harness.sh`: si todo el salpicadero se enciende en verde, ha pasado la inspección y puede circular.

## Glosario (jerga del taller)

Estas palabras aparecen por todas partes más abajo. Apréndelas una vez aquí; el resto del documento se limita a usarlas.

| Jerga | En cristiano |
|-------|--------------|
| **coding harness** | El «coche» en el que trabajamos de verdad: toda la capa de guardarraíles para desarrollo con IA que rodea un repo de producto (rules, skills, hooks, trusted suite, ledgers) |
| **subject** | Un repo de producto que entra en el box para hacer absorb / compare; se clona solo en local y **nunca** se commitea aquí |
| **harness surface** | Los paneles modificables de ese coche (`AGENTS.md`, skills, hooks), no el motor (el código de negocio) |
| **Agent-Kit** | El instalador del estante: coloca skills de metodología / hook templates en Cursor, Claude Code, Codex, etc. |
| **public trusted suite** | `bash tools/harness/test-harness.sh`: la pasada por el banco de potencia antes de que este taller entregue nada (el mismo equipo que L2 CI) |

## Carril rápido: entrada en una línea

Un solo comando hace todo el trabajo: clona el taller, trae los submodules, instala los git hooks, coloca Agent-Kit en su sitio y lleva el coche directo al banco de potencia (la public trusted suite).

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

¿Demasiado moderno? La clásica tubería arranca el mismo motor:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

¿Quieres elegir dónde aterriza y qué client queda cableado? Configura estas dos variables de entorno:

- `TARGET_DIR` — el directorio de instalación
- `CLIENT` — el client que se cableará: `cursor` / `claude` / `codex` / `codex-native`, o `skip` para dejar Agent-Kit para más tarde

El comando de una línea también coloca Agent-Kit y ejecuta la suite por ti: **la mayoría puede apagar el motor y cerrar el taller justo aquí**. ¿Prefieres montar cada marcha por separado o el instalador se ha calado a mitad de camino? Toma el carril manual.

## Entrada manual (móntalo tú mismo)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

Por ahora solo has abierto la puerta del box: la caja de piezas (Agent-Kit) sigue en el suelo. Continúa.

## Colocar Agent-Kit (la caja de piezas, al estante)

Agent-Kit instala los skills de metodología y hooks de este repo en tu editor / CLI. Una instalación básica te entrega un conjunto predeterminado ya afinado: metodología local, una selección de skills SP de verification / TDD / review, una Matt library que invocas a propósito y un advisory router de baja frecuencia.

**No** cuela el bootstrap `using-superpowers` / `brainstorming` y deja tranquilos los vendor hooks; ambos son solo opt-in. Los client trees (`.cursor` / `.claude` / `.codex` / `.agents`) son **salidas de instalación y nunca se commitean**: regénéralos siempre mediante install, en vez de editarlos a mano e intentar colarlos de vuelta en git.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parámetro | Valores |
|-----------|---------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (opcional) | `lean`, `guided`, `structured`; solo cambia la densidad de los advisory prompts — **nunca** toca la enforcement |

El bootstrap local más habitual: colocar los cuatro clients de una vez.

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

El perfil del repo siempre se gestiona mediante la CLI (no edites el YAML a mano: eso es buscarse problemas). Para llevar la configuración a otro repo, exporta primero y comprueba después:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` solo sobrevive como salida de compatibilidad full-plugin explícita para workflows antiguos; ya no es la ruta recomendada. La materialization predeterminada de la library no copia vendor plugins, hooks ni ningún skill fuera de la allowlist.

## Mete tu propio coche (opcional: cablear un subject)

¿Solo quieres comprobar que el taller se pone todo verde? **No cables nada**: un public clone no depende de ningún repo de producto privado y aun así ejecuta la trusted suite hasta dejar una pared de luces verdes.

Solo cuando quieras hacer sync / import / compare de un subject real debes ejecutar estas líneas:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Memoriza un orden: **crear `manifest.yaml` → sync → usar `--pin` para guardar la versión → ejecutar `check-local-absorb.sh` hasta obtener `harness-ready`**. Supera primero esa barrera; solo entonces pueden arrancar import / compare / score.

Todo esto se queda en local y ya está incluido en gitignore. No intentes meterlo a la fuerza en un commit: el pre-commit hook lo devolverá al instante.

- `subjects/manifest.yaml`
- el `pin.json` y `checkout/` de cada subject
- `snapshots/`, `comparisons/`

---

A partir de aquí está la pared de referencia para el día a día: coge una herramienta cuando la necesites; no hace falta leerlo todo de una sentada.

## Comandos habituales (pared de herramientas)

| Lo que quieres hacer | La línea que debes ejecutar |
|----------------------|-----------------------------|
| Public trusted suite (banco de potencia / con forma de CI) | `bash tools/harness/test-harness.sh` |
| Validar Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Hacer sync de la harness surface | `bash tools/sync/sync-subjects.sh` |
| Reescribir el pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Preparación local para absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Importar snapshot | `python3 tools/import/import_subject.py --all` |
| Informe de compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Informe semanal | `python3 tools/harness/weekly_report.py` |

## Plano del taller (dónde vive cada pieza)

| Ruta | Qué es | ¿En git? |
|------|--------|----------|
| `agent-kit/skills` | Metodología abierta (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Templates de hooks / settings por client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Salidas de instalación | ✗ |
| `subjects/manifest.example.yaml` | Ejemplo de registro público | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registro local / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixtures públicas (CI) | ✓ |
| `snapshots/` / `comparisons/` | Productos de absorb | ✗ |
| `docs/harness/` | Design + ledgers | parcial |
| `AGENTS.md` | SSOT de restricciones (`CLAUDE.md` apunta aquí) | ✓ |

## Estante de manuales (para profundizar)

- [`docs/README.md`](../README.md) — reglas de ubicación de la documentación
- [`docs/harness/design.md`](../harness/design.md) — harness design de este repo
- [`docs/specs/`](../specs/) — archivo de design
- [`AGENTS.md`](../../AGENTS.md) — definición de terminado, blacklist y mapa de mecanismos

## Licencia

[MIT](../../LICENSE) — sácalo del taller como quieras; aquí tienes los papeles.
