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
  <strong>Português</strong> |
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

> **Em uma linha:** esta é uma oficina de desmanche para os *guardrails* do seu repo. O que sobe no elevador não é o código de negócio, mas o **coding harness** ao redor dele: a camada que impede uma AI (Cursor, Claude Code, Codex) de cortar caminho, fingir que “terminou” ou empurrar para o git o que não deveria ser commitado.
>
> **O que você ganha com isso:** use nossas skills de metodologia tunadas e hooks à prova de barbeiragem como estão, ou instale os mesmos guardrails nos seus próprios repos. Não mexemos no motor (seu código-fonte de negócio); só soldamos a gaiola externa até uma AI não conseguir amassá-la por descuido.
>
> **Três marchas para sair:** instalação em uma linha → (ignição) Agent-Kit na estante → (opcional) traga seu próprio subject. Antes de fechar a oficina, rode `bash tools/harness/test-harness.sh`: painel todo verde significa vistoria aprovada e carro liberado para a rua.

## Glossário (gíria de oficina)

Você verá estes termos por toda parte. Aprenda uma vez aqui; o restante do documento apenas os utiliza.

| Gíria | Em português claro |
|-------|---------------------|
| **coding harness** | O “carro” em que realmente mexemos — toda a camada de guardrails para desenvolvimento com AI ao redor de um repo de produto: rules, skills, hooks, trusted suite, ledgers |
| **subject** | Um repo de produto trazido para a oficina para absorb / compare; clonado apenas localmente e **nunca** commitado aqui |
| **harness surface** | Os painéis modificáveis desse carro (`AGENTS.md`, skills, hooks), não o motor (código-fonte de negócio) |
| **Agent-Kit** | O instalador da estante — coloca skills de metodologia / hook templates no Cursor, Claude Code, Codex etc. |
| **public trusted suite** | `bash tools/harness/test-harness.sh` — a passada no dinamômetro antes de esta oficina entregar qualquer coisa (mesmo equipamento do L2 CI) |

## Faixa mais rápida: entrada em uma linha

Um comando faz tudo: clona a oficina, baixa submodules, instala git hooks, põe o Agent-Kit na estante e leva direto para o dinamômetro (a public trusted suite).

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Moderno demais? O velho pipe dá partida no mesmo motor:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

Quer escolher onde será instalado e qual client será ligado? Defina estas duas variáveis de ambiente:

- `TARGET_DIR` — diretório de instalação
- `CLIENT` — client a conectar: `cursor` / `claude` / `codex` / `codex-native`; ou `skip` para deixar o Agent-Kit para depois

O comando de uma linha também instala o Agent-Kit e roda a suite — **a maioria das pessoas pode desligar o motor e bater o ponto aqui**. Quer montar uma marcha por vez ou o one-liner morreu no caminho? Pegue a faixa manual abaixo.

## Entrada manual (monte você mesmo)

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Forgot --recurse-submodules? Grab the missing parts:
git submodule update --init --recursive

# Weld on the git pre-commit hook (blocks private trees; runs the suite when needed)
bash tools/harness/install-git-hooks.sh
```

Neste ponto, só abrimos a porta da oficina — a caixa de peças (Agent-Kit) ainda está no chão. Continue.

## Instale o Agent-Kit (caixa de peças na parede)

O Agent-Kit instala as skills de metodologia e os hooks deste repo no seu editor / CLI. Uma instalação básica entrega um conjunto padrão tunado: metodologia local, uma seleção de skills SP para verification / TDD / review, uma biblioteca Matt chamada de propósito e um advisory router de baixa frequência.

Ele não enfia escondido o bootstrap `using-superpowers` / `brainstorming` e não mexe em vendor hooks — esses são somente opt-in. As árvores dos clients (`.cursor` / `.claude` / `.codex` / `.agents`) são **resultados de instalação e nunca entram em commits**. Sempre regenere com install, em vez de editar à mão e contrabandear para o git.

```bash
# Install for one client
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Check the install came out complete
bash tools/harness/agent-kit.sh validate

# Preview what it would install, without landing it (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parâmetro | Valores |
|-----------|---------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (opcional) | `lean`, `guided`, `structured`; somente densidade de advisory prompts — **nunca** altera enforcement |

O bootstrap local mais comum instala os quatro clients de uma vez:

```bash
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done
```

O profile do repo sempre passa pela CLI (editar o YAML à mão é pedir problema). Para levar a configuração a outro repo, primeiro exporte e depois confira:

```bash
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Export a portable profile into a subject; wire the fragments, then check again
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` só sobrevive como uma saída explícita de compatibilidade full-plugin para workflows antigos — não é mais o caminho recomendado. A materialização padrão da library não copia vendor plugins, hooks nem nenhuma skill fora da allowlist.

## Traga seu próprio carro (opcional: conecte um subject)

Só quer confirmar que a oficina acende tudo em verde? **Não conecte nada.** Um clone público não depende de nenhum repo de produto privado e, ainda assim, roda a trusted suite até ficar toda verde.

Execute estas linhas apenas quando realmente quiser fazer sync / import / compare de um subject real:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Point the remotes at repos you can access, then:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # local harness-ready (note: NOT the public suite)
```

Decore uma ordem: **crie `manifest.yaml` → sync → use `--pin` para registrar a versão → rode `check-local-absorb.sh` até ficar `harness-ready`**. Passe por esse gate primeiro; só depois import / compare / score podem rodar.

Estes itens permanecem locais e já estão no gitignore. Não tente forçá-los em um commit; o pre-commit hook os devolve na hora:

- `subjects/manifest.yaml`
- `pin.json` e `checkout/` de cada subject
- `snapshots/`, `comparisons/`

---

Abaixo fica o painel de ferramentas do dia a dia. Pegue uma quando precisar; não é necessário ler tudo de uma vez.

## Comandos comuns (painel de ferramentas)

| O que você quer | Linha para executar |
|-----------------|---------------------|
| Public trusted suite (dinamômetro / formato de CI) | `bash tools/harness/test-harness.sh` |
| Validar o Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Fazer sync da harness surface | `bash tools/sync/sync-subjects.sh` |
| Reescrever o pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Prontidão local de absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Importar snapshot | `python3 tools/import/import_subject.py --all` |
| Gerar relatório de compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Executar score | `python3 tools/score/score_subject.py <id>` |
| Gerar relatório semanal | `python3 tools/harness/weekly_report.py` |

## Planta da oficina (onde fica cada peça)

| Caminho | O que é | Entra no git? |
|---------|---------|---------------|
| `agent-kit/skills` | Metodologia aberta (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Hooks / settings templates por client | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Resultados da instalação | ✗ |
| `subjects/manifest.example.yaml` | Exemplo público de registry | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registry / clone local | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixtures públicas (CI) | ✓ |
| `snapshots/` / `comparisons/` | Produtos de absorb | ✗ |
| `docs/harness/` | Design + ledgers | parcial |
| `AGENTS.md` | SSOT de restrições (`CLAUDE.md` aponta para cá) | ✓ |

## Manual da oficina (vá mais fundo)

- [`docs/README.md`](../README.md) — regras de localização da documentação
- [`docs/harness/design.md`](../harness/design.md) — design do harness deste repo
- [`docs/specs/`](../specs/) — arquivo de designs
- [`AGENTS.md`](../../AGENTS.md) — definição de conclusão, blacklist e mapa de mecanismos

## Licença

[MIT](../../LICENSE) — saia dirigindo como quiser; o documento do carro está aqui.
