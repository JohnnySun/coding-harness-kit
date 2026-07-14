# Research memo: price-aware model routing inputs

**Research snapshot:** 2026-07-10
**Decision scope:** this memo supplies evidence and a preliminary admission/tie-break policy. It does not change any client setting, model roster, or capability-tier policy.

## Executive conclusion

There is no defensible global cheapest-to-best ordering for this set. Route only within a capability-qualified pool, then use task-specific evidence and the observed token mix to compare cost.

The strongest directly comparable coding evidence retrieved is the independent DeepSWE v1.1 shared-harness run: GPT-5.6 Sol/Terra/Luna at `max` and GLM-5.2 at `max` were all run through `mini-swe-agent`; their Pass@1 results were 73%±3%, 70%±3%, 67%±4%, and 44%±2%, respectively. The page has no Grok 4.5, GPT-5.3 Codex, or Composer 2.5 row. [DeepSWE v1.1 leaderboard](https://deepswe.datacurve.ai/)

For agentic general knowledge work, the independent GDPval-AA v2 leaderboard uses a shared Stirrup agent loop with shell and web access. Its exact entries show Sol `max` at 1748 Elo (CI −20/+20), Terra `max` at 1593 (−20/+20), Luna `max` at 1592 (−19/+19), Grok 4.5 `high` at 1542 (−25/+25), and GLM-5.2 `max` at 1514 (−17/+17). [GDPval-AA v2](https://artificialanalysis.ai/evaluations/gdpval-aa) [method and scope](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index)

**Preliminary recommendation:** treat Sol as having a demonstrated advantage over Grok 4.5 for the GDPval-AA-style configuration, not as universally or conclusively stronger for all routing workloads. The available coding-index comparison is 80 for Sol `max` in Codex versus 76 for Grok 4.5 in Grok Build, but it changes both model and native agent harness; it is not a model-only head-to-head. [Artificial Analysis GPT-5.6 analysis](https://artificialanalysis.ai/articles/gpt-5-6-has-landed) [Artificial Analysis Grok analysis](https://artificialanalysis.ai/articles/grok-4-5-brings-spacexai-to-the-the-intelligence-frontier)

## Source and comparability rules

This memo uses model-owner documentation for identifiers and token rates. It uses DataCurve and Artificial Analysis for performance evidence; it does not use owner-published performance claims to establish an advantage for Composer. Artificial Analysis states that its Terminal-Bench v2.1 runs are independent; its GPT-5.6 article also discloses pre-release evaluation support, which should remain visible when consuming that evidence. [Terminal-Bench methodology](https://artificialanalysis.ai/evaluations/terminalbench-v2-1) [GPT-5.6 disclosure](https://artificialanalysis.ai/articles/gpt-5-6-has-landed)

A score is comparable for routing only when its evidence card names all of: model ID and reasoning/effort setting, benchmark version, measurement date, agent harness and tool access, budgets/timeouts, repetitions, and pricing path. A change to any of those fields creates a new configuration rather than a silent substitute.

## 1. Candidate configurations with independent evidence

| Configuration | Agentic coding evidence | Tool-use evidence | General-reasoning / knowledge-work evidence | Routing interpretation | Evidence source(s) |
| --- | --- | --- | --- | --- | --- |
| GPT-5.6 Sol `max` | DeepSWE v1.1: 73%±3%, 113 tasks, shared `mini-swe-agent`, updated 2026-07-09. | AA Terminal-Bench v2.1 independently runs the common Terminus 2 harness in an e2b sandbox, three repeats per task; the retrieved leaderboard explicitly reports Sol `max` at 88.0% and Sol `xhigh` at 89.5%. | GDPval-AA v2: Sol `max` 1748 Elo (−20/+20) in the common Stirrup loop. | Directly comparable with Terra/Luna/GLM on DeepSWE; directly comparable with Grok/Terra/Luna/GLM on GDPval-AA. | [DeepSWE](https://deepswe.datacurve.ai/); [Terminal-Bench](https://artificialanalysis.ai/evaluations/terminalbench-v2-1); [GDPval-AA](https://artificialanalysis.ai/evaluations/gdpval-aa) |
| GPT-5.6 Terra `max` | DeepSWE v1.1: 70%±3% in the same shared harness. | The retrieved AA Terminal-Bench page explicitly reports Terra `max` at 88.0% under its common harness. | GDPval-AA v2: 1593 Elo (−20/+20). | Same direct-comparison sets as Sol, but only at the listed effort/configuration. | [DeepSWE](https://deepswe.datacurve.ai/); [Terminal-Bench](https://artificialanalysis.ai/evaluations/terminalbench-v2-1); [GDPval-AA](https://artificialanalysis.ai/evaluations/gdpval-aa) |
| GPT-5.6 Luna `max` | DeepSWE v1.1: 67%±4% in the same shared harness. | No exact Luna row was exposed in the retrieved Terminal-Bench page text; do not infer one from family results. | GDPval-AA v2: 1592 Elo (−19/+19). | Direct coding and general-work comparison exists; tool-use evidence needs an exact retrieved row before it can enter a tool-use tie-break. | [DeepSWE](https://deepswe.datacurve.ai/); [Terminal-Bench](https://artificialanalysis.ai/evaluations/terminalbench-v2-1); [GDPval-AA](https://artificialanalysis.ai/evaluations/gdpval-aa) |
| Grok 4.5 `high` | No shared-harness DeepSWE row was retrieved. AA’s coding index records Grok 4.5 in **Grok Build**, not the same configuration as Sol in Codex. | AA’s coding index says Grok performs strongly on Terminal-Bench v2, but the index’s native-harness setup cannot isolate the model from the agent product. | GDPval-AA v2: 1542 Elo (−25/+25) in the common Stirrup loop. | Directly comparable to Sol for GDPval-AA-like work, not yet for shared-harness coding quality. | [AA GPT-5.6](https://artificialanalysis.ai/articles/gpt-5-6-has-landed); [AA Grok](https://artificialanalysis.ai/articles/grok-4-5-brings-spacexai-to-the-the-intelligence-frontier); [GDPval-AA](https://artificialanalysis.ai/evaluations/gdpval-aa) |
| GPT-5.3 Codex `xhigh` | No current shared-harness coding result was retrieved for this exact configuration. | Its 77.3% Terminal-Bench **v2.0** number is a different benchmark version and vendor-reported; it must not be compared to v2.1 scores. | AA’s current model leaderboard lists GPT-5.3 Codex `xhigh` on its composite Intelligence Index, but no current GDPval-AA v2 row was retrieved. | Insufficient non-composite, exact-config evidence for a new cross-task price tie-break. | [v2.0 archive](https://ai-stats.vercel.app/benchmarks/terminal-bench-2.0); [AA models](https://artificialanalysis.ai/leaderboards/models/); [GDPval-AA](https://artificialanalysis.ai/evaluations/gdpval-aa) |
| GLM-5.2 `max` | DeepSWE v1.1: 44%±2% in the same shared `mini-swe-agent` run as the GPT-5.6 family. | No exact GLM row was exposed in the retrieved Terminal-Bench page text; do not substitute launch or provider scores. | GDPval-AA v2: 1514 Elo (−17/+17) in the common Stirrup loop. | Directly comparable with Sol/Terra/Luna in both named shared-harness evaluations. | [DeepSWE](https://deepswe.datacurve.ai/); [Terminal-Bench](https://artificialanalysis.ai/evaluations/terminalbench-v2-1); [GDPval-AA](https://artificialanalysis.ai/evaluations/gdpval-aa) |
| Composer 2.5 standard / Fast | AA published an independent result for **Cursor CLI + Composer 2.5**: Index 62; SWE-Bench-Pro-Hard-AA 47%; Terminal-Bench v2 66%; SWE-Atlas-QnA 72%. It reports the same scores for Fast. | Those are useful product-configuration observations, but client, harness, and model are bundled. | No independent common-harness general-reasoning result was retrieved. | Evidence exists, but is insufficient to claim model-only equivalence or portability to another client. | [AA Composer evaluation](https://artificialanalysis.ai/articles/cursor-composer-2-5-coding-agent-index); [GDPval-AA](https://artificialanalysis.ai/evaluations/gdpval-aa) |

### What the comparison does and does not establish

DeepSWE is the cleanest coding comparison here because it states that all listed models run on `mini-swe-agent`; its 113 tasks span 91 repositories and five languages. It supports the listed Sol/Terra/Luna/GLM ordering for that benchmark and effort level only. It does not establish a Sol-versus-Grok coding ordering because Grok is not in that table. [DeepSWE methodology and results](https://deepswe.datacurve.ai/)

Terminal-Bench v2.1 is relevant to terminal tool use because it covers 89 curated tasks across software engineering, administration, data processing, model training, and security. Artificial Analysis states that it runs Terminus 2 in an e2b sandbox with three repeats per task. The retrieved page exposes exact top rows for Sol and Terra, but not exact rows for every candidate; missing rows remain missing evidence. [AA Terminal-Bench v2.1](https://artificialanalysis.ai/evaluations/terminalbench-v2-1)

GDPval-AA v2 is a shared agent loop for real-world knowledge work across 44 occupations and nine industries, with shell and browsing capabilities. It is valuable complementary evidence for general agentic work, but it is neither an agentic-coding benchmark nor a universal proxy for a repository task. [GDPval-AA scope](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index)

## 2. Sol versus Grok 4.5

The evidence supports a **configuration- and evaluation-specific** advantage, not a routing-wide assertion that Sol is clearly stronger than Grok 4.5.

For the shared GDPval-AA v2 configuration, Sol `max` scores 1748 Elo (−20/+20) versus Grok 4.5 `high` at 1542 (−25/+25). The reported intervals do not overlap, so the evidence is materially stronger than a one-point composite-index difference for this knowledge-work setting. [GDPval-AA v2](https://artificialanalysis.ai/evaluations/gdpval-aa)

For agentic coding, Artificial Analysis reports 80 for Sol `max` in Codex and 76 for Grok 4.5 in Grok Build, with Sol leading the three index components and tying Grok on SWE-Atlas-QnA. Those are agent-plus-model configurations in different native products, not an otherwise-identical harness. The result therefore supports “higher score in those measured configurations,” not “the Sol model is conclusively stronger for coding.” [AA GPT-5.6 analysis](https://artificialanalysis.ai/articles/gpt-5-6-has-landed) [AA Grok analysis](https://artificialanalysis.ai/articles/grok-4-5-brings-spacexai-to-the-the-intelligence-frontier)

Grok’s lower API token rates remain relevant to a cost tie-break, but they cannot erase the GDPval-AA quality difference for a task class validated by that evaluation. Grok’s direct rate is $2/M input and $6/M output; Sol’s direct standard rate is $5/M input and $30/M output. [Grok 4.5 model page](https://docs.x.ai/developers/models/grok-4.5) [GPT-5.6 pricing](https://developers.openai.com/api/docs/pricing)

## 3. First-party token-rate snapshot

All values are USD per million tokens and are the source owner’s published token rates as retrieved on 2026-07-10. They are not a client subscription’s included-usage, request-credit, or billing-pool behavior.

| Candidate configuration | Input | Cached input/read | Cache write or storage, when published | Output | First-party source |
| --- | ---: | ---: | ---: | ---: | --- |
| GPT-5.6 Sol | $5.00 | $0.50 | $6.25 write | $30.00 | [API pricing](https://developers.openai.com/api/docs/pricing) |
| GPT-5.6 Terra | $2.50 | $0.25 | $3.125 write | $15.00 | [API pricing](https://developers.openai.com/api/docs/pricing) |
| GPT-5.6 Luna | $1.00 | $0.10 | $1.25 write | $6.00 | [API pricing](https://developers.openai.com/api/docs/pricing) |
| Grok 4.5 | $2.00 | $0.50 | Not separately published; do not model this as $0 | $6.00 | [model page](https://docs.x.ai/developers/models/grok-4.5) |
| GPT-5.3 Codex | $1.75 | $0.175 | Not separately published; do not model this as $0 | $14.00 | [model page](https://developers.openai.com/api/docs/models/gpt-5.3-codex) |
| GLM-5.2 | $1.40 | $0.26 | Cached-input storage: “Limited-time Free”; this is not a published cache-write token rate | $4.40 | [pricing](https://docs.z.ai/guides/overview/pricing) |
| Composer 2.5 standard | $0.50 | $0.20 | No separate write rate shown | $2.50 | [owner pricing table](https://cursor.com/docs/models-and-pricing) |
| Composer 2.5 Fast | $3.00 | Not published for Fast in the retrieved owner documentation | Not separately published | $15.00 | [owner model page](https://cursor.com/docs/models/cursor-composer-2-5) |

### Normalized-cost method and caveats

For a specific observed workload, calculate:

```text
normalized_cost =
  fresh_input_tokens × input_rate
+ cached_input_tokens × cached_input_rate
+ cache_write_tokens × published_cache_write_rate
+ output_tokens × output_rate
+ separately metered tool/storage charges
```

Use actual request telemetry for the selected API path; do not estimate total cost from input/output headline rates alone. A model can be cheaper per token but more expensive per completed task if it uses more reasoning, output, retries, tool calls, or fresh context.

- GPT-5.6 has an explicit 1.25× cache-write charge and a 90% cached-input discount. Its `pro` reasoning mode can consume more model work and therefore more billable tokens at the selected model’s standard rates. [GPT-5.6 release pricing and cache terms](https://openai.com/index/previewing-gpt-5-6-sol/) [reasoning-mode billing](https://developers.openai.com/api/docs/guides/reasoning)
- Grok caching is automatic for an identical message prefix, and its documentation recommends a conversation-affinity key to maximize cache hits. Its published rate card names input, cached input, and output only. [Grok cache documentation](https://docs.x.ai/developers/advanced-api-usage/prompt-caching) [Grok rate card](https://docs.x.ai/developers/models/grok-4.5)
- GLM cache detection is automatic and similarity-dependent; the provider says cache behavior, including retention, is in open beta. Treat the published cached-input/storage terms as provisional and meter observed hits. [GLM cache documentation](https://docs.z.ai/guides/capabilities/cache) [GLM FAQ](https://docs.z.ai/help/faq)
- Composer standard and Fast are separate price/latency configurations. The owner documentation exposes direct token pricing but no externally accessible API; do not equate its published price with a third-party API’s operational cost or assume that Fast has an identical cache regime. [Composer pricing](https://cursor.com/docs/models-and-pricing) [AA availability note](https://artificialanalysis.ai/articles/cursor-composer-2-5-coding-agent-index)
- Direct-provider prices can differ from proxy, cloud-marketplace, priority, batch, region, long-context, or plan-mediated prices. The routing calculation must pin one purchase path before comparing candidates. The OpenAI price page, for example, separately lists Standard, Batch, Flex, and Priority rows. [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)

## 4. Preliminary evidence thresholds for a candidate pool

These are proposed routing controls, not a claim that a single benchmark fixes a universal ranking.

1. **Qualify capability before price.** The capability-tier system supplies the permitted candidate pool. This price policy may select only among configurations already qualified for the task’s required tool access, context, safety, latency, and quality tier.
2. **Create a configuration evidence card.** Record the exact model ID, effort/mode, client/harness, tool set, benchmark version, measurement date, cost path, and raw component scores. Do not carry a score across a mode, client, or harness change.
3. **Admit a candidate for an automatic price tie-break only with complementary evidence.** Require (a) one task-relevant, non-composite shared-harness result and (b) a second non-composite evaluation in a different relevant task family, or a maintained task-local holdout. A composite index can prioritize research, but cannot satisfy either requirement by itself. A client-owner configuration result may be supporting evidence, but cannot be the only performance evidence.
4. **Define “tie” as non-inferiority, not overlapping confidence intervals.** On the routing workload’s primary metric, the cheaper candidate must have a lower confidence bound no worse than a predeclared tolerated regression `δ`. A starting `δ` of 3 percentage points may be appropriate only after calibration against that workload’s acceptable failure cost; it is not a cross-benchmark conversion rule.
5. **Make quality dominate when the material-advantage test passes.** If the stronger candidate’s lower confidence-bound advantage exceeds that workload’s `δ`, or if the cheaper candidate fails a task-specific reliability/safety gate, select quality regardless of headline token price. GDPval-AA’s Sol-versus-Grok gap can justify this outcome for a GDPval-like workload, but does not automatically transfer to coding.
6. **Use price only after equivalence is demonstrated.** Calculate normalized per-task cost from the same telemetry window and include cache hits, writes, output/reasoning tokens, retries, and metered tools. Re-evaluate after a material price, model, benchmark, or harness change.

## 5. Defensible treatment of Composer 2.5

The premise that Composer 2.5 has no independent performance evidence is too strong: Artificial Analysis published an external evaluation of the Cursor CLI + Composer 2.5 configuration, including raw component scores rather than only an index. [AA Composer 2.5 evaluation](https://artificialanalysis.ai/articles/cursor-composer-2-5-coding-agent-index)

That evidence is still insufficient for a model-portable quality claim because the measured unit bundles Composer with its owner’s CLI/harness, and no shared-harness general-reasoning or cross-client result was retrieved. Owner-published claims about Composer’s strength are deliberately excluded from the performance conclusion. [Owner model documentation](https://cursor.com/docs/models/cursor-composer-2-5)

**Preliminary recommendation:** retain Composer standard and Fast as distinct, **provisional product-configuration candidates** only where that client and its tools are already allowed. Do not let either displace a capability-qualified candidate merely because its token rates are lower. Promote it to an automatic price tie-break only after the threshold above is met with independent shared-harness or task-local evidence; until then, use a controlled, explicitly measured evaluation cohort and keep the fallback eligible.

## Material evidence gaps

- No retrieved shared-harness coding result directly compares GPT-5.6 Sol with Grok 4.5.
- The retrieved Terminal-Bench v2.1 content did not expose exact rows for every candidate, so it cannot fill missing tool-use scores by inference.
- GPT-5.3 Codex lacks retrieved current, exact-configuration, non-composite evidence across the required coding, tool-use, and general-work dimensions.
- Composer 2.5 has independent client-specific evidence, but no retrieved model-only/shared-harness or general-reasoning evidence; Fast’s cached-input/write rates are also not published in the retrieved owner documentation.
- Cache hit rate, tool fees, retries, reasoning-token use, and purchase path can reverse a headline-rate ranking. No normalized-cost order should be committed until production-like telemetry exists.
