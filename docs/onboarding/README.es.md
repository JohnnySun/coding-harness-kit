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

> **Este taller trabaja en tu coche: el coding harness.** Es la capa de protección para el desarrollo con IA que rodea un repositorio de producto. Ese repositorio —el subject— es el dueño del coche. El código de negocio es el motor, y dejamos el capó cerrado.
> La ruta corta: ejecuta la recepción en una línea → instala Agent-Kit para Cursor, Claude Code o Codex → opcionalmente conecta un subject real y después ejecuta sync, pin y la comprobación `harness-ready`. Las piezas nuevas siguen pasando por el banco de potencia, la public trusted suite. Revisar la pintura no es un plan de pruebas.

| Término | Significado (equivalencia del taller) |
|------|---------|
| **coding harness** | Tu coche: la capa de protección para desarrollo con IA alrededor de un repositorio de producto (rules, skills, hooks, trusted suite, ledgers) |
| **subject** | El repositorio de producto propietario del coche (clone local; no se commitea aquí) |
| **harness surface** | La zona de piezas: `AGENTS.md`, skills, hooks y archivos de protección similares; no es código de negocio |
| **Agent-Kit** | El estante de piezas: materializa skills de metodología / hook templates en Cursor, Claude Code, Codex, etc. |
| **public trusted suite** | El banco de potencia: `bash tools/harness/test-harness.sh` (igual que L2 CI) |

## 1. Recepción (inicialización)

La entrada más rápida al taller es el instalador de una línea. Clona el repositorio, inicializa submodules, instala git hooks y Agent-Kit y, después, ejecuta la public trusted suite:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Si tu shell no admite process substitution, usa la forma equivalente con pipe:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Las variables de entorno opcionales son `TARGET_DIR` y `CLIENT`. Configura `CLIENT` como `cursor` / `claude` / `codex` / `codex-native` / `skip`.

Como alternativa manual, o para ver girar cada llave:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# If you forgot --recurse-submodules
git submodule update --init --recursive

# Install L1 safety check (blocks private trees; runs suite when needed)
bash tools/harness/install-git-hooks.sh
```

Ahora deberías estar dentro de `los-santos-customs/`, con submodules inicializados y git hooks instalados. La ruta de una línea también instala Agent-Kit para el client elegido y ejecuta la public suite. Si seguiste la ruta manual, continúa en §2. La transmisión manual tiene un paso adicional; no es por nostalgia.

## 2. Montar las piezas (Agent-Kit)

Agent-Kit instala los skills y hooks de este taller en tu editor o CLI. Una instalación sin opciones aporta estos valores predeterminados:

- metodología local;
- una selección de skills de SP verification, TDD y review;
- una Matt library invocada por el usuario;
- un advisory router de baja frecuencia.

No instala el bootstrap `using-superpowers` / `brainstorming` ni vendor hooks. Los client trees (`.cursor` / `.claude` / `.codex` / `.agents`) son salidas de instalación y no se commitean. Regénéralos con install; los archivos generados no necesitan chapa y pintura.

```bash
# Install for a specific client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Validate the parts are seated
bash tools/harness/agent-kit.sh validate

# Preview install (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parámetro | Valores |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (opcional) | `lean`, `guided`, `structured`; solo ajusta la densidad de avisos |

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

`PLUGIN` permanece solo como ruta explícita de compatibilidad full-plugin para workflows antiguos. Ya no es la ruta de instalación recomendada. La materialization predeterminada de la library no copia vendor plugins, hooks ni skills fuera de la allowlist. El estante de piezas lleva inventario por una razón.

## 3. (Opcional) Traer tu propio coche

Un public clone puede ejecutar la public trusted suite sin repositorios de producto privados. Conecta el coche de un cliente a tu zona local solo cuando necesites hacer sync, import o compare de un subject real:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edit remotes to repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (not the public suite)
```

El orden importa:

1. Crea `subjects/manifest.yaml` a partir del ejemplo. Haz que sus remotes apunten a repositorios a los que tengas acceso.
2. Ejecuta sync para obtener la harness surface de cada subject.
3. Usa `<id> --pin` para registrar la revision exacta que vas a evaluar.
4. Ejecuta el local absorb check. Un subject que lo supera está `harness-ready`; solo entonces import, compare y score pueden producir resultados fiables.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` y `comparisons/` son coches de clientes y órdenes de trabajo. Permanecen en local, están ignorados por git y nunca entran en el public showroom. No es secretismo; es control básico de llaves.

---

El coche ya se mueve por sus propios medios. El resto es referencia del área de servicio.

## Comandos comunes

| Propósito | Comando |
|---------|---------|
| Public trusted suite (cerrar el ciclo / CI) | `bash tools/harness/test-harness.sh` |
| Validar Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Hacer sync de la harness surface | `bash tools/sync/sync-subjects.sh` |
| Reescribir el pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Local absorb readiness | `bash tools/harness/check-local-absorb.sh --all` |
| Importar snapshot | `python3 tools/import/import_subject.py --all` |
| Compare report | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Score | `python3 tools/score/score_subject.py <id>` |
| Weekly report | `python3 tools/harness/weekly_report.py` |

## Estructura

| Ruta | Función | ¿En git? |
|------|------|---------|
| `agent-kit/skills` | Metodología abierta (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Client hooks/settings templates | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Salidas de instalación | ✗ |
| `subjects/manifest.example.yaml` | Ejemplo de registro público | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registro local / clone | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixtures públicas (CI) | ✓ |
| `snapshots/` / `comparisons/` | Productos de absorb | ✗ |
| `docs/harness/` | Design + ledgers | parcial |
| `AGENTS.md` | SSOT de restricciones (`CLAUDE.md` → it) | ✓ |

## Documentación

- [`docs/README.md`](../README.md) — reglas de ubicación de documentación
- [`docs/harness/design.md`](../harness/design.md) — harness design de este repositorio
- [`docs/specs/`](../specs/) — archivo de design
- [`AGENTS.md`](../../AGENTS.md) — definición de terminado, blacklist, mapa de mecanismos

## Licencia

[MIT](../../LICENSE)
