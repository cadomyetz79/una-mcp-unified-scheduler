# Step 142 — Interactive Leo, MCP and live RAGFlow

Date: 2026-11-07
Workstream: Unified system integration
Starting commit: 77087df
Status: Synthetic research demonstration

## CONFIRMED — Implementation

Created scripts/leo_live_ragflow_manual_demo.py as a
separate interactive launcher, preserving the existing
scheduling-only launcher.

The new launcher uses:
- Local HTTPS browser interface
- Locally signed synthetic JWT and student session
- Ollama qwen3:4b-instruct
- Protected MCP and synthetic Mock Banner
- Deterministic scheduling and verified plan cards
- Real local RAGFlow HTTP retrieval
- AuthorizedPolicyAnswerer
- Explicit live authorization canary at startup

The RAGFlow backend remains opt-in and localhost-only.
No enrollment operations were added.

## CONFIRMED — User-observed browser results

1. Leo proposed CIS376 SEC1001 and CIS410 SEC2002.
   The existing CIS376 registration was identified.
   No enrollment occurred.

2. A policy request returned an actual RAGFlow source ID
   and a synthetic public university-guidance excerpt.

3. A restricted Legal-policy request returned:
   "No authorized policy evidence was selected."
   No restricted content was displayed.

4. A request for student S10002's grades was refused.

5. After switching between scheduling and policy
   questions, Leo retained CIS376, CIS410 and the
   Friday restriction, added a soft 10:01 AM start
   preference, and identified the 09:30 start violation.

These observations come from the interactive transcript
provided by the project integrator. They are not a
new automated evaluation or a production security proof.

## CONFIRMED — Automated verification

Step 142D:
- Live RAGFlow authorization canary passed
- Five synthetic identity-role matrix passed
- Cross-tenant empty-result check passed
- MCP/gateway: 458 tests passed
- AI agent: 1073 passed, 1 skipped
- Python launcher compilation passed

Step 141 separately repaired deterministic parsing of
two natural-language scheduling follow-ups. Its
interactive three-message test was successful.

## WORKING ASSUMPTION

This bounded synthetic configuration provides a useful
repeatable demonstration of modular MCP and RAGFlow
integration, but not general retrieval or security
assurance.

## OPEN QUESTIONS

- The RAG teammates' actual RAGFlow instance, datasets,
  ingestion configuration and document permissions
  have not been established.
- The only datasets found in the local research account
  were synthetic authorization canaries.
- Real Entra, UNA Banner, approved institutional
  documents, OCR integration and deployment remain open.
- The interactive policy branch currently requires
  the explicit "Policy:" prefix.
- The current demo uses a temporary synthetic login;
  it is not approved for real students.
- A recorded manual browser session and full source
  provenance should be captured for final publication.

## RECOMMENDATION

Keep PR #3 draft. Preserve the existing successful
scheduling, privacy and retrieval boundaries.

Obtain the RAG workstream's actual approved corpus and
configuration before claiming complete team integration.

Document source attribution and validate authorization
again whenever a different dataset is connected.
