"""Explicit opt-in teaching fixtures. Never auto-load into a deployment."""
from src.agent.secure_ingestion import SyntheticDocumentStore, DocumentRecord
from src.mcp_server.entra_rbac_acl import DocumentACL

def build_synthetic_knowledge(tenant):
    domains = {
        "public": "university-policy", "student": "student-policy",
        "faculty": "faculty-policy", "hr": "hr", "finance": "finance", "legal": "legal",
    }
    store = SyntheticDocumentStore({f"synthetic-{k}": v for k,v in domains.items()})
    for name, domain in domains.items():
        role = "RAG.HR" if name == "hr" else "RAG." + name.capitalize()
        groups = {"hr": "hr-confidential", "legal": "legal-privileged"}
        acl = DocumentACL(
            name, tenant, "public" if name == "public" else "restricted",
            domain, "synthetic-public" if name == "public" else "synthetic-restricted",
            allowed_roles=frozenset() if name == "public" else frozenset({role}),
            allowed_groups=frozenset({groups[name]}) if name in groups else frozenset(),
            mode="all",
        )
        text = ("Synthetic university policy: consult your adviser for planning guidance."
                if name == "public" else f"SYNTHETIC_{name.upper()}_ONLY policy evidence.")
        store.ingest(DocumentRecord(acl, f"synthetic-{name}", f"synthetic://classroom/{name}"), text.encode())
    return store
