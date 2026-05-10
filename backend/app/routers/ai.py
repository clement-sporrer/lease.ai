"""AI assistant — keyword-matched canned responses. No LLM in demo mode."""
from typing import Any

from fastapi import APIRouter, Depends

from app._demo_auth import get_current_user_demo
from app.envelope import ok
from app.errors import APIError
from app.state import db, fake_latency, new_id, now_iso, state_lock

router = APIRouter()


def _format_eur(cents: int | None) -> str:
    if cents is None:
        return "indéterminé"
    return f"{cents / 100:,.2f} EUR".replace(",", " ").replace(".", ",")


def _deal_context(deal_id: str | None) -> dict | None:
    if not deal_id:
        return None
    deal = db()["deals"].get(deal_id)
    if not deal:
        return None
    company = db()["companies"].get(deal.get("company_id") or "", {})
    return {"deal": deal, "company": company}


def _answer_for(question: str, ctx: dict | None) -> str:
    q = (question or "").lower()
    deal = ctx["deal"] if ctx else None
    company = ctx["company"] if ctx else {}
    name = company.get("legal_name", "le client")

    if any(k in q for k in ("où", "ou", "statut", "where", "status", "etat", "état")):
        if deal:
            return (
                f"Le dossier {deal['public_id']} pour {name} est au statut '{deal['status']}'. "
                f"Mensualité indicative: {_format_eur(deal.get('monthly_payment_cents'))}."
            )
        return "Aucun dossier ciblé pour cette question."

    if any(k in q for k in ("pièce", "piece", "document", "manqu", "missing")):
        if deal and deal.get("missing_documents"):
            return f"Pièces manquantes pour {deal['public_id']}: {', '.join(deal['missing_documents'])}."
        return "Aucune pièce bloquante actuellement."

    if any(k in q for k in ("score", "risque", "risk")):
        if deal and deal.get("risk_band"):
            return (
                f"Score risk: {deal.get('risk_score')}/100, band {deal.get('risk_band')}. "
                f"Recommandation système: revue standard."
            )
        return "Aucun scoring exécuté pour le moment. Lancez l'évaluation depuis la fiche dossier."

    if any(k in q for k in ("offre ferme", "firm offer", "générer l'offre")):
        if deal and deal.get("status") == "financier_approved":
            return "Oui, l'accord financeur est reçu. Vous pouvez générer l'offre ferme."
        return "L'offre ferme requiert un accord financeur préalable."

    if any(k in q for k in ("paiement", "echeance", "échéance", "next payment")):
        upcoming = [s for s in db()["payment_schedules"].values() if s["status"] == "upcoming"]
        upcoming.sort(key=lambda s: s["due_date"])
        if upcoming:
            s = upcoming[0]
            return f"Prochaine échéance: {s['due_date']}, {_format_eur(s['amount_cents'])}."
        return "Aucune échéance future en base."

    if any(k in q for k in ("résumer", "resume", "summary", "résumé")):
        if deal:
            return (
                f"Dossier {deal['public_id']} — {name}, {_format_eur(deal['amount_cents'])}, "
                f"{deal['duration_months']} mois, statut '{deal['status']}', "
                f"band {deal.get('risk_band') or 'N/A'}."
            )
        return "Pas de dossier sélectionné pour le résumé."

    return (
        "Question non comprise par l'assistant en mode démo. "
        "Reformulez en mentionnant statut, pièces, score, paiement ou résumé."
    )


@router.post("/ai/assistant/query")
def assistant_query(payload: dict[str, Any], user: dict = Depends(get_current_user_demo)) -> dict:
    fake_latency()
    question = payload.get("question", "")
    deal_id = payload.get("deal_id")
    ctx = _deal_context(deal_id)
    answer = _answer_for(question, ctx)

    log_id = new_id("ailog")
    with state_lock():
        db().setdefault("ai_logs", {})[log_id] = {
            "id": log_id,
            "user_id": user["user_id"],
            "deal_id": deal_id,
            "question": question,
            "answer": answer,
            "created_at": now_iso(),
        }

    return ok({"answer": answer, "deal_id": deal_id, "log_id": log_id, "decision_taken": False})


@router.post("/ai/deals/{deal_id}/summary")
def deal_summary(deal_id: str, user: dict = Depends(get_current_user_demo)) -> dict:
    ctx = _deal_context(deal_id)
    if not ctx:
        raise APIError("ENTITY_NOT_FOUND", "Deal not found", status=404)
    deal = ctx["deal"]
    company = ctx["company"]
    docs = [d for d in db()["documents"].values() if d.get("deal_id") == deal_id]
    return ok(
        {
            "deal_id": deal_id,
            "summary": _answer_for("résumé", ctx),
            "next_action": _next_action(deal),
            "documents_present": [d["type"] for d in docs],
            "missing_documents": deal.get("missing_documents", []),
            "company": {
                "legal_name": company.get("legal_name"),
                "siren": company.get("siren"),
                "active_status": company.get("active_status"),
            },
        }
    )


@router.post("/ai/documents/{document_id}/extract")
def doc_extract(
    document_id: str, payload: dict[str, Any] | None = None, user: dict = Depends(get_current_user_demo)
) -> dict:
    fake_latency()
    doc = db()["documents"].get(document_id)
    if not doc:
        raise APIError("ENTITY_NOT_FOUND", "Document not found", status=404)
    return ok(
        {
            "document_id": document_id,
            "type": doc["type"],
            "fields": {
                "supplier": "Tech Distrib SAS",
                "amount_excl_tax_cents": 8550000,
                "currency": "EUR",
                "category": "Laptops & Accessories",
                "line_count": 4,
            },
            "confidence": 0.93,
        }
    )


def _next_action(deal: dict) -> str:
    mapping = {
        "draft": "Compléter SIREN puis enrichir l'entreprise",
        "company_enriched": "Ajouter le devis IT",
        "quote_added": "Calculer la mensualité indicative",
        "indicative_offer_ready": "Soumettre le dossier",
        "submitted": "ADV: passer en revue interne",
        "internal_review": "Demander pièce ou pré-accorder",
        "missing_documents": "Récupérer pièces manquantes",
        "pre_approved": "Générer le package financeur",
        "refi_package_ready": "Envoyer au financeur",
        "refi_review": "Attendre la décision financeur",
        "financier_approved": "Générer l'offre ferme",
        "firm_offer_generated": "Générer le contrat",
        "contract_generated": "Envoyer en signature",
        "signing": "Attendre signature",
        "signed": "Compléter la checklist d'activation",
        "activation_pending": "Activer le contrat",
        "active": "Suivre échéancier et paiements",
    }
    return mapping.get(deal["status"], "Aucune action recommandée")
