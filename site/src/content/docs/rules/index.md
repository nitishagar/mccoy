---
title: Rules
description: McCoy's eight deterministic MCP tool-surface rules.
---

McCoy runs eight deterministic rules over every tool definition. Each finding is graded by
severity and ships with a fix hint. The verdict (exit code) is driven by these rules alone — the
GPT-5.6 advisory pass only annotates.

| ID | Severity | What it catches |
|----|----------|-----------------|
| [MCC001](/rules/mcc001/) | High | Instruction-injection markers in the description |
| [MCC002](/rules/mcc002/) | Medium | Input schema that does not forbid unknown properties |
| [MCC003](/rules/mcc003/) | High | Secret-looking references in the schema or description |
| [MCC004](/rules/mcc004/) | Medium | Over-broad tool scope ("any file", "arbitrary command") |
| [MCC005](/rules/mcc005/) | Medium | A `0.0.0.0` bind advertised in the description |
| [MCC006](/rules/mcc006/) | High | Hidden Unicode controls in the description |
| [MCC007](/rules/mcc007/) | Medium | Description that permits runtime mutation |
| [MCC008](/rules/mcc008/) | Low | Unpinned dependency reference |
