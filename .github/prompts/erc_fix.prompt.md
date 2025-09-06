```prompt
---
mode: ask
---
Diagnose and resolve an ERC (Electrical Rules Check) finding.

Provide:
- the ERC error text or paste of the failure
- short analysis of the root cause (missing net tie, power flag, passive connection, wrong symbol pin type, etc.)
- two remediation options: (A) minimal schematic change, (B) rule update or ERC suppression with justification

Required artifacts:
- a minimal patch (one or two hunks) that fixes the schematic or updates ERC rules (docs/config) with exact file paths
- rationale for the chosen fix, describing tradeoffs and risks

Success criteria:
- ERC passes locally after the change, or the updated ERC rule is narrowly scoped and documented
- `make erc` and `make netlist` re-run cleanly

Constraints & notes:
- prefer changes to the schematic over globally weakening ERC rules unless the rule is incorrect for the entire project
- if adding a suppression, target it to the specific net or symbol and document why it is safe

```
