"""Verify an explicitly configured synthetic RAGFlow corpus; save no credentials."""
import argparse
import asyncio
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agent.ragflow_lab import verified_lab_retriever

async def main(args):
    evidence = {"passed": False, "live_ragflow": True, "synthetic_only": True}
    try:
        _, evidence = await verified_lab_retriever(args.manifest, args.credentials, expected_tenant=args.tenant)
        print("LIVE_RAGFLOW_CANARY_AND_FIVE_IDENTITY_MATRIX_PASSED")
    finally:
        args.output.write_text(json.dumps(evidence, indent=2) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--credentials", type=Path, required=True)
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Existing research evidence must be preserved.")
    asyncio.run(main(args))
