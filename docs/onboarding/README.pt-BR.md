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

> **Esta oficina trabalha no seu carro: o coding harness.** Ele é a camada de proteções para desenvolvimento com AI ao redor de um repositório de produto. Esse repositório — o subject — é o dono do carro; o código de negócio é o motor, e deixamos o motor fechado.
> O caminho curto: execute a instalação em uma linha → instale o Agent-Kit para Cursor, Claude Code ou Codex → opcionalmente conecte um subject real, depois faça sync, pin e verifique `harness-ready`. Peças novas ainda vão para o dinamômetro. Inspeção de pintura não é plano de testes.

| Termo | Significado (mapeamento da oficina) |
|------|---------|
| **coding harness** | Seu carro: a camada de proteções para desenvolvimento com AI ao redor de um repositório de produto (rules, skills, hooks, trusted suite e ledgers) |
| **subject** | O repositório de produto que é dono do carro (clone local; não é commitado aqui) |
| **harness surface** | A área de peças: `AGENTS.md`, skills, hooks e arquivos de proteção semelhantes; não é código de negócio |
| **Agent-Kit** | A estante de peças: materializa skills de metodologia e templates de hooks no Cursor, Claude Code, Codex etc. |
| **public trusted suite** | O dinamômetro: `bash tools/harness/test-harness.sh` (igual ao L2 CI) |

## 1. Entrada (inicialização)

A forma mais rápida de entrar na oficina é o instalador de uma linha. Ele clona o repositório, inicializa submodules, instala git hooks e o Agent-Kit e, depois, executa a public trusted suite:

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh)
```

Se o seu shell não oferecer process substitution, use a forma equivalente com pipe:

```bash
curl -fsSL https://raw.githubusercontent.com/JohnnySun/los-santos-customs/main/scripts/install.sh | bash
```

As variáveis de ambiente opcionais são `TARGET_DIR` e `CLIENT`. Defina `CLIENT` como `cursor` / `claude` / `codex` / `codex-native` / `skip`.

Como alternativa manual, ou para acompanhar cada aperto de chave:

```bash
git clone --recurse-submodules https://github.com/JohnnySun/los-santos-customs.git
cd los-santos-customs

# Se você esqueceu --recurse-submodules
git submodule update --init --recursive

# Instala a verificação de segurança L1 (bloqueia árvores privadas; executa a suite quando necessário)
bash tools/harness/install-git-hooks.sh
```

Agora você deve estar em `los-santos-customs/`, com os submodules inicializados e os git hooks instalados. O caminho de uma linha também instala o Agent-Kit para o cliente selecionado e executa a public suite. Se escolheu o caminho manual, continue na §2. Transmissões manuais têm uma etapa extra; aqui não é nostalgia.

## 2. Instalar as peças (Agent-Kit)

O Agent-Kit instala as skills e os hooks desta oficina no seu editor ou CLI. Uma instalação sem opções oferece estes padrões definidos pelo projeto:

- metodologia local;
- skills selecionadas de verificação, TDD e revisão do SP;
- uma biblioteca Matt acionada pelo usuário;
- um router consultivo de baixa frequência.

Ele não instala o bootstrap `using-superpowers` / `brainstorming` nem hooks de fornecedores. As árvores dos clientes (`.cursor` / `.claude` / `.codex` / `.agents`) são resultados da instalação e não entram em commits. Gere-as novamente com install; arquivos gerados não precisam de funilaria.

```bash
# Instala para um cliente específico
CLIENT=<client> bash tools/harness/agent-kit.sh install

# Valida se as peças estão encaixadas
bash tools/harness/agent-kit.sh validate

# Visualiza a instalação (dry-run)
CLIENT=<client> DRY_RUN=1 bash tools/harness/agent-kit.sh install
```

| Parâmetro | Valores |
|-----------|--------|
| `CLIENT` | `cursor`, `cursor-cli`, `claude`, `codex`, `codex-native` |
| `--process-scaffold` (opcional) | `lean`, `guided`, `structured`; ajusta somente a densidade consultiva |

```bash
# Instala os quatro clientes (bootstrap local comum)
for c in cursor claude codex codex-native; do
  CLIENT=$c bash tools/harness/agent-kit.sh install
done

# Examina ou ajusta o profile do repositório (agents escrevem somente pela CLI)
bash tools/harness/agent-kit.sh profile show
bash tools/harness/agent-kit.sh profile set process_scaffold guided

# Exporta um profile portátil para um subject; conecta os fragments e depois verifica
bash tools/harness/agent-kit.sh profile export --root <subject-root> --client cursor
bash tools/harness/agent-kit.sh profile check --root <subject-root> --client cursor
```

`PLUGIN` permanece apenas como um caminho explícito de compatibilidade com o plugin completo para workflows antigos. Ele não é mais o caminho de instalação recomendado. A materialização padrão da biblioteca não copia plugins, hooks ou skills de fornecedores fora da allowlist; a estante de peças tem inventário por um motivo.

## 3. (Opcional) Traga seu próprio carro

Um clone público pode executar a public trusted suite sem repositórios de produto privados. Conecte um carro de cliente à sua oficina local somente quando precisar fazer sync, import ou compare de um subject real:

```bash
cp subjects/manifest.example.yaml subjects/manifest.yaml
# Edite os remotes para repositórios que você pode acessar e, depois:
bash tools/sync/sync-subjects.sh
bash tools/sync/sync-subjects.sh <id> --pin
bash tools/harness/check-local-absorb.sh --all   # harness-ready local (não é a public suite)
```

A ordem é importante:

1. Crie `subjects/manifest.yaml` a partir do exemplo. Aponte seus remotes para repositórios que você pode acessar.
2. Execute sync para buscar a harness surface de cada subject.
3. Use `<id> --pin` para registrar a revisão exata que pretende avaliar.
4. Execute a verificação local de absorb. Um subject aprovado está `harness-ready`; só então import, compare e score podem produzir resultados confiáveis.

`subjects/manifest.yaml`, `pin.json`, `checkout/`, `snapshots/` e `comparisons/` são carros e ordens de serviço dos clientes. Eles permanecem locais, são ignorados pelo git e nunca entram no showroom público. Isso não é sigilo; é controle básico de chaves.

---

O carro agora anda com a própria força. O restante é a referência da oficina.

## Comandos comuns

| Finalidade | Comando |
|---------|---------|
| Public trusted suite (fecha o ciclo / CI) | `bash tools/harness/test-harness.sh` |
| Validar o Agent-Kit | `bash tools/harness/agent-kit.sh validate` |
| Fazer sync da harness surface | `bash tools/sync/sync-subjects.sh` |
| Reescrever o pin | `bash tools/sync/sync-subjects.sh <id> --pin` |
| Prontidão local de absorb | `bash tools/harness/check-local-absorb.sh --all` |
| Importar snapshot | `python3 tools/import/import_subject.py --all` |
| Gerar relatório de compare | `python3 tools/compare/compare_subjects.py -o comparisons/report.md` |
| Executar score | `python3 tools/score/score_subject.py <id>` |
| Gerar relatório semanal | `python3 tools/harness/weekly_report.py` |

## Estrutura

| Caminho | Função | Entra no git? |
|------|------|---------|
| `agent-kit/skills` | Metodologia aberta (submodule → JohnnySun/skills) | ✓ |
| `agent-kit/hooks/clients/` | Templates de hooks/settings dos clientes | ✓ |
| `.cursor` / `.agents` / `.claude` / `.codex` | Resultados da instalação | ✗ |
| `subjects/manifest.example.yaml` | Exemplo público de registry | ✓ |
| `subjects/manifest.yaml` + `<id>/{pin,checkout}` | Registry / clone local | ✗ |
| `tools/` | sync / import / compare / score / suite / hooks | ✓ |
| `testdata/` | Fixtures públicas (CI) | ✓ |
| `snapshots/` / `comparisons/` | Produtos de absorb | ✗ |
| `docs/harness/` | Design + ledgers | parcial |
| `AGENTS.md` | SSOT de restrições (`CLAUDE.md` → ele) | ✓ |

## Documentação

- [`docs/README.md`](../README.md) — regras de localização da documentação
- [`docs/harness/design.md`](../harness/design.md) — design do harness deste repositório
- [`docs/specs/`](../specs/) — arquivo de designs
- [`AGENTS.md`](../../AGENTS.md) — definição de conclusão, blacklist e mapa de mecanismos

## Licença

[MIT](../../LICENSE)
