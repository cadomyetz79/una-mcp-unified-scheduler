"""Five signed synthetic identities; local ACL retrieval, not live RAGFlow."""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.mcp_server.entra_token_verifier import EntraTokenVerifier
from src.mcp_server.entra_rbac_acl import from_verified_access_token
from src.mcp_server import team_security as security
from src.agent.synthetic_knowledge import build_synthetic_knowledge
from src.agent.authorized_retrieval import SyntheticPrefilterBackend, AuthorizedKnowledgeRetriever

TENANT = "11111111-1111-4111-8111-111111111111"
AUDIENCE = "22222222-2222-4222-8222-222222222222"


async def run():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    verifier = EntraTokenVerifier(tenant_id=TENANT, audience=AUDIENCE)
    verifier._jwks_client.get_signing_key_from_jwt = lambda raw: SimpleNamespace(key=key.public_key())
    store = build_synthetic_knowledge(TENANT)
    backend = SyntheticPrefilterBackend(store)
    retriever = AuthorizedKnowledgeRetriever(store, backend,
        dataset_ids=tuple(store.dataset_domains), domains=set(store.dataset_domains.values()))
    rows = []
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(security, "AUTH_TENANT", TENANT)
        mp.setattr(security, "AUTH_AUDIENCE", AUDIENCE)
        mp.setattr(security, "ISSUER_URL", verifier.issuer)
        mp.setattr(security, "STUDENT_LOOKUP", {(TENANT, "synthetic-student"): "S10001"})
        for role, domain, groups in [
            ("RAG.Student", "student", []), ("RAG.Faculty", "faculty", []),
            ("RAG.HR", "hr", ["hr-confidential"]), ("RAG.Finance", "finance", []),
            ("RAG.Legal", "legal", ["legal-privileged"]),
        ]:
            now = int(time.time())
            raw = jwt.encode({
                "iss": verifier.issuer, "aud": AUDIENCE, "tid": TENANT,
                "oid": "synthetic-" + domain, "azp": "synthetic-client",
                "scp": "academic.read rag.query", "roles": [role], "groups": groups,
                "ver": "2.0", "iat": now, "nbf": now, "exp": now+600,
            }, key, algorithm="RS256", headers={"kid": "example-local-key"})
            token = await verifier.verify_token(raw)
            assert token is not None
            user = from_verified_access_token(token, expected_tenant=TENANT,
                expected_issuer=verifier.issuer, expected_audience=AUDIENCE)
            mp.setattr(security, "get_access_token", lambda: token)
            allowed, denied = [], []
            for name in security.ACADEMIC_TOOL_POLICIES:
                try:
                    security.authorize_tool_request(name)
                    allowed.append(name)
                except PermissionError:
                    denied.append(name)
            assert len(allowed) == (6 if domain == "student" else 0)
            hits = await retriever.search_for(user, "policy", 5)
            ids = sorted(h.source_id.split("/")[1] for h in hits)
            assert ids == sorted(["public", domain])
            rows.append({
                "synthetic_role": role, "signature_verified": True,
                "allowed_academic_tools": sorted(allowed), "denied_academic_tools": sorted(denied),
                "candidate_chunk_ids": sorted(backend.last_candidates),
                "retrieved_document_ids": ids, "passed": True,
            })
    return {"synthetic_only": True, "live_ragflow": False, "matrix": rows,
            "passed": True, "enrollment_operations": 0}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new evidence path.")
    result = asyncio.run(run())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+"\n")
    print("FIVE_SIGNED_SYNTHETIC_IDENTITIES_VERIFIED")
