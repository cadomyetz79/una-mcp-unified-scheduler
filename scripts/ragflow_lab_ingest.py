"""Create a NEW private synthetic corpus via authenticated RAGFlow HTTP APIs.

Never deletes or reparses an existing corpus. Requires an already provisioned
local test account/API credential and a configured local embedding model.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import httpx2
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.agent.secure_ingestion import DocumentRecord, ChunkRecord
from src.mcp_server.entra_rbac_acl import DocumentACL


def ingest(args):
    if args.credentials.is_symlink() or (os.name != "nt" and args.credentials.stat().st_mode & 0o077):
        raise PermissionError("Credential file must be private.")
    credential = json.loads(args.credentials.read_text())["api_key"]
    with httpx2.Client(base_url="http://127.0.0.1:19380/api/v1",
        headers={"Authorization": "Bearer " + credential}, timeout=60, trust_env=False,
        follow_redirects=False) as client:
        def request(method, path, **kwargs):
            response = client.request(method, path, **kwargs)
            data = response.json()
            if response.status_code != 200 or type(data.get("code")) is not int or data["code"] != 0:
                raise RuntimeError("Synthetic ingestion HTTP operation failed: " + path)
            return data["data"]
        dataset = request("POST", "/datasets", json={
            "name": "Synthetic authorization canary " + str(time.time_ns()),
            "embedding_model": args.embedding_model, "permission": "me",
            "chunk_method": "naive", "language": "English",
            "parser_config": {"chunk_token_num": 128, "auto_keywords": 0, "auto_questions": 0},
        })["id"]
        manifest = {"schema_version": "synthetic-ragflow-lab-v1", "base_url": "http://127.0.0.1:19380",
                    "tenant_id": args.tenant, "dataset_id": dataset, "documents": [], "indexing_complete": False}
        def save():
            args.output.write_text(json.dumps(manifest, indent=2) + "\n")
        save()
        for name in ["public", "student", "faculty", "hr", "finance", "legal"]:
            role = "RAG.HR" if name == "hr" else "RAG." + name.capitalize()
            group = {"hr": "hr-confidential", "legal": "legal-privileged"}.get(name)
            def acl(did):
                return DocumentACL(did, args.tenant, "public" if name == "public" else "restricted",
                    "university-policy", "synthetic-public" if name == "public" else "synthetic-restricted",
                    allowed_roles=frozenset() if name == "public" else frozenset({role}),
                    allowed_groups=frozenset({group}) if group else frozenset(), mode="all")
            # Validate trusted ACL BEFORE upload and parsing.
            DocumentRecord(acl(name), dataset, "synthetic://canary/" + name)
            content = ("Synthetic university guidance: consult your adviser before choosing classes."
                if name == "public" else "SYNTHETIC_" + name.upper() + "_ONLY. " +
                ("Quantum scholarship award eligibility quantum scholarship award eligibility. " * 5
                 if name == "legal" else "Synthetic " + name + " policy guidance for planning."))
            uploaded = request("POST", f"/datasets/{dataset}/documents",
                files={"file": (name + ".txt", content.encode(), "text/plain")})
            did = uploaded[0]["id"]
            record = DocumentRecord(acl(did), dataset, "synthetic://canary/" + name)
            metadata = ChunkRecord("pending", record, content, hashlib.sha256(content.encode()).hexdigest()).metadata
            metadata.pop("content_hash")
            request("PATCH", f"/datasets/{dataset}/documents/{did}", json={"meta_fields": metadata})
            manifest["documents"].append({"name": name, "id": did, "text": content, "metadata": metadata})
            save()
        request("POST", f"/datasets/{dataset}/documents/parse",
                json={"document_ids": [d["id"] for d in manifest["documents"]]})
        deadline = time.monotonic() + 180
        while time.monotonic() < deadline:
            docs = request("GET", f"/datasets/{dataset}/documents")["docs"]
            if any(d.get("run") == "FAIL" for d in docs):
                raise RuntimeError("Synthetic indexing failed; preserve corpus and inspect sanitized task status.")
            if len(docs) == 6 and all(d.get("run") == "DONE" and d.get("chunk_count") == 1 for d in docs):
                manifest["indexing_complete"] = True
                save()
                print("SIX_SYNTHETIC_DOCUMENTS_INDEXED")
                return
            time.sleep(2)
        raise TimeoutError("Indexing not confirmed; corpus and partial manifest preserved.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials", type=Path, required=True)
    parser.add_argument("--embedding-model", required=True)
    parser.add_argument("--tenant", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Use a new manifest filename; existing evidence is preserved.")
    ingest(args)
