# Epic 6 — Polish & Features Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver branding assets, empty states, document viewer, queue search/pagination, ActionPanel server-action migration, and assets/payment-schedule panel.

**Architecture:** 6 independent tasks — each can be reviewed and committed in isolation. Backend tasks add endpoints (documents view-url, queue filters, assets/schedule). Frontend tasks consume them via server actions or server components. No new DB migration needed.

**Tech Stack:** FastAPI + SQLAlchemy async (backend), Next.js 16 App Router + TypeScript strict + Tailwind (web), Supabase Storage (document signed URLs), pytest-anyio (backend tests)

---

## Branch setup

- [ ] Create a new branch from `main` (or from `feat/phase1-web` if the PR is not merged yet):
  ```bash
  git checkout feat/phase1-web
  git checkout -b feat/epic6-polish
  ```

---

## File map

**New files:**
- `web/components/shared/EmptyState.tsx` — reusable empty-state component
- `web/lib/actions/document-actions.ts` — server action: get signed view URL
- `web/components/admin/DocumentViewer.tsx` — client modal wrapping iframe
- `web/lib/actions/admin-actions.ts` — server actions: requestDocument, preApprove, rejectDeal
- `web/components/admin/QueueFilters.tsx` — client search input + status dropdown (updates URL params)
- `web/components/admin/QueuePagination.tsx` — client prev/next buttons (updates URL params)
- `web/components/admin/AssetsPanel.tsx` — assets table + payment schedule table, visible when deal is active

**Modified files:**
- `web/app/layout.tsx` — add `icons` to metadata
- `web/components/dashboard/Sidebar.tsx` — replace text "LeaseAI" with `<img src="/logo.svg">`
- `web/app/(auth)/login/page.tsx` — replace hand-coded icon+text with `<img src="/logo.svg">`
- `web/components/admin/DealQueue.tsx` — use EmptyState instead of bare `<p>`
- `web/components/admin/DocumentList.tsx` — use EmptyState, add "Voir" button → DocumentViewer
- `web/components/admin/ActionPanel.tsx` — remove `token` prop, call server actions
- `web/app/(admin)/admin/queue/page.tsx` — accept `searchParams`, render QueueFilters + QueuePagination
- `web/app/(admin)/admin/deals/[id]/page.tsx` — remove `token` from ActionPanel props, fetch assets when active
- `backend/app/routers/documents.py` — add `GET /documents/{id}/view-url`
- `backend/app/services/document_service.py` — add `get_view_url(db, document_id, actor_role)`
- `backend/app/routers/admin.py` — add query params to `GET /admin/queue`
- `backend/app/services/admin_service.py` — add search/filter/pagination to `get_queue`
- `backend/app/routers/contracts.py` — add `GET /contracts/{id}/assets` and `GET /contracts/{id}/payment-schedule`
- `backend/app/schemas/contract.py` — add `AssetResponse`, `PaymentScheduleItemResponse`

**Test files (backend only):**
- `backend/tests/test_document_view_url.py`
- `backend/tests/test_queue_filters.py`
- `backend/tests/test_contract_assets.py`

---

## Task 1: Branding — favicon, sidebar logo, login logo, metadata

**Files:**
- `web/public/icon.svg` — already present (copied from Downloads)
- `web/public/logo.svg` — already present (copied from Downloads)
- Modify: `web/app/layout.tsx`
- Modify: `web/components/dashboard/Sidebar.tsx:53-56`
- Modify: `web/app/(auth)/login/page.tsx:39-46`

- [ ] **Step 1: Add favicon to root metadata**

In `web/app/layout.tsx`, replace the existing `metadata` export with:

```typescript
export const metadata: Metadata = {
  title: "LeaseAI — Back-office",
  description: "Plateforme opérationnelle de gestion de leasing IT",
  icons: {
    icon: "/icon.svg",
    apple: "/icon.svg",
  },
}
```

- [ ] **Step 2: Replace text logo in Sidebar**

In `web/components/dashboard/Sidebar.tsx`, replace the header `<div>` at line 54–57:

```tsx
// Replace this:
<div className="px-6 py-5 border-b border-white/10">
  <span className="text-white font-bold text-lg">LeaseAI</span>
  <span className="ml-2 text-white/40 text-xs">{ROLE_LABELS[role]}</span>
</div>

// With this:
<div className="px-6 py-5 border-b border-white/10 flex items-center justify-between">
  <img src="/logo.svg" alt="LeaseAI" className="h-7 w-auto brightness-0 invert" />
  <span className="text-white/40 text-xs">{ROLE_LABELS[role]}</span>
</div>
```

Note: `brightness-0 invert` makes a dark SVG/PNG white on the navy background. If the logo is already light-colored, remove those classes.

- [ ] **Step 3: Replace hand-coded icon in login page**

In `web/app/(auth)/login/page.tsx`, replace the logo block at lines 40–45:

```tsx
// Replace this:
<div className="mb-3 inline-flex items-center gap-2">
  <div className="h-8 w-8 rounded-lg bg-[#0D183D] flex items-center justify-center">
    <span className="text-white text-xs font-bold">L</span>
  </div>
  <span className="text-xl font-semibold text-[#0D183D]">LeaseAI</span>
</div>

// With this:
<div className="mb-3 flex justify-center">
  <img src="/logo.svg" alt="LeaseAI" className="h-10 w-auto" />
</div>
```

- [ ] **Step 4: Verify TypeScript is clean**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/web && npx tsc --noEmit
```

Expected: 0 errors.

- [ ] **Step 5: Commit**

```bash
git add web/app/layout.tsx web/components/dashboard/Sidebar.tsx web/app/\(auth\)/login/page.tsx web/public/icon.svg web/public/logo.svg
git commit -m "feat(branding): favicon, sidebar logo, login logo from brand assets"
```

---

## Task 2: EmptyState shared component

**Files:**
- Create: `web/components/shared/EmptyState.tsx`
- Modify: `web/components/admin/DealQueue.tsx:19-22`
- Modify: `web/components/admin/DocumentList.tsx:62-64`

- [ ] **Step 1: Create EmptyState component**

Create `web/components/shared/EmptyState.tsx`:

```tsx
interface EmptyStateProps {
  title: string
  subtitle?: string
}

export function EmptyState({ title, subtitle }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-gray-50">
        <svg className="h-6 w-6 text-gray-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 9.776c.112-.017.227-.026.344-.026h15.812c.117 0 .232.009.344.026m-16.5 0a2.25 2.25 0 00-1.883 2.542l.857 6a2.25 2.25 0 002.227 1.932H19.05a2.25 2.25 0 002.227-1.932l.857-6a2.25 2.25 0 00-1.883-2.542m-16.5 0V6A2.25 2.25 0 016 3.75h3.879a1.5 1.5 0 011.06.44l2.122 2.12a1.5 1.5 0 001.06.44H18A2.25 2.25 0 0120.25 9v.776" />
        </svg>
      </div>
      <p className="text-sm font-medium text-gray-500">{title}</p>
      {subtitle && <p className="mt-1 text-xs text-gray-400">{subtitle}</p>}
    </div>
  )
}
```

- [ ] **Step 2: Use EmptyState in DealQueue**

In `web/components/admin/DealQueue.tsx`, add the import and replace the bare `<p>`:

```tsx
// Add import at top:
import { EmptyState } from '@/components/shared/EmptyState'

// Replace:
return (
  <p className="py-10 text-center text-sm text-gray-400">Aucun dossier en attente.</p>
)

// With:
return <EmptyState title="Aucun dossier en attente" subtitle="Les nouveaux dossiers soumis apparaîtront ici." />
```

- [ ] **Step 3: Use EmptyState in DocumentList**

In `web/components/admin/DocumentList.tsx`, add the import and replace:

```tsx
// Add import at top:
import { EmptyState } from '@/components/shared/EmptyState'

// Replace:
<p className="px-6 py-8 text-center text-sm text-gray-400">Aucun document.</p>

// With:
<EmptyState title="Aucun document" subtitle="Les documents uploadés par le partenaire apparaîtront ici." />
```

- [ ] **Step 4: TypeScript check**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/web && npx tsc --noEmit
```

Expected: 0 errors.

- [ ] **Step 5: Commit**

```bash
git add web/components/shared/EmptyState.tsx web/components/admin/DealQueue.tsx web/components/admin/DocumentList.tsx
git commit -m "feat(ux): EmptyState shared component — DealQueue + DocumentList"
```

---

## Task 3: Document viewer — backend signed URL + frontend modal

**Context:** Documents are stored in Supabase Storage under `deals/{deal_id}/{document_id}`. The backend already has upload URL generation. We need a read-signed-URL endpoint.

Security rule (from CLAUDE.md): explicit permission check before generating a signed URL for documents.

**Files:**
- Modify: `backend/app/services/document_service.py`
- Modify: `backend/app/routers/documents.py`
- Create: `backend/tests/test_document_view_url.py`
- Create: `web/lib/actions/document-actions.ts`
- Create: `web/components/admin/DocumentViewer.tsx`
- Modify: `web/components/admin/DocumentList.tsx`

### Backend

- [ ] **Step 1: Write failing test for view-url service**

Create `backend/tests/test_document_view_url.py`:

```python
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.errors import AppError
from app.services import document_service


@pytest.mark.asyncio
async def test_get_view_url_returns_url():
    doc_id = uuid.uuid4()
    deal_id = uuid.uuid4()

    mock_doc = MagicMock()
    mock_doc.id = doc_id
    mock_doc.deal_id = deal_id
    mock_doc.storage_key = f"deals/{deal_id}/{doc_id}"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_doc

    db = AsyncMock()
    db.execute = AsyncMock(return_value=mock_result)

    fake_signed_path = f"/storage/v1/object/sign/documents/deals/{deal_id}/{doc_id}?token=abc"

    with patch("app.services.document_service.httpx") as mock_httpx:
        mock_response = MagicMock()
        mock_response.json.return_value = {"signedURL": fake_signed_path}
        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_httpx.AsyncClient.return_value = mock_client

        result = await document_service.get_view_url(db, doc_id, "admin")

    assert result["url"].endswith("?token=abc")
    assert result["expires_in"] == 3600


@pytest.mark.asyncio
async def test_get_view_url_raises_when_no_storage_key():
    doc_id = uuid.uuid4()

    mock_doc = MagicMock()
    mock_doc.storage_key = None

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_doc

    db = AsyncMock()
    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(AppError) as exc_info:
        await document_service.get_view_url(db, doc_id, "admin")

    assert exc_info.value.code == "DOCUMENT_NOT_UPLOADED"


@pytest.mark.asyncio
async def test_get_view_url_raises_when_not_found():
    doc_id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    db = AsyncMock()
    db.execute = AsyncMock(return_value=mock_result)

    with pytest.raises(AppError) as exc_info:
        await document_service.get_view_url(db, doc_id, "admin")

    assert exc_info.value.code == "DOCUMENT_NOT_FOUND"
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/backend && python -m pytest tests/test_document_view_url.py -v
```

Expected: FAIL — `AttributeError: module 'app.services.document_service' has no attribute 'get_view_url'`

- [ ] **Step 3: Add `get_view_url` to document_service**

In `backend/app/services/document_service.py`, add `import httpx` at the top (after existing imports), then add this function at the end of the file:

```python
import httpx  # add at top of file with other imports

async def get_view_url(db: AsyncSession, document_id: uuid.UUID, actor_role: str) -> dict:
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    if document is None:
        raise AppError(404, "DOCUMENT_NOT_FOUND", f"Document {document_id} not found")
    if document.storage_key is None:
        raise AppError(409, "DOCUMENT_NOT_UPLOADED", "Document has no file uploaded yet")

    sign_url = (
        f"{settings.supabase_url}/storage/v1/object/sign"
        f"/{settings.object_storage_bucket}/{document.storage_key}"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            sign_url,
            headers={
                "Authorization": f"Bearer {settings.supabase_service_role_key}",
                "apikey": settings.supabase_service_role_key,
            },
            json={"expiresIn": 3600},
        )
        payload = resp.json()

    signed_path: str = payload.get("signedURL") or payload.get("signedUrl") or ""
    if signed_path.startswith("/"):
        view_url = f"{settings.supabase_url}/storage/v1{signed_path}"
    else:
        view_url = signed_path

    return {"url": view_url, "expires_in": 3600}
```

- [ ] **Step 4: Run test to verify it passes**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/backend && python -m pytest tests/test_document_view_url.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Add router endpoint**

In `backend/app/routers/documents.py`, add before the closing line (after `list_documents`):

```python
_DOC_READ_ROLES = {UserRole.admin, UserRole.ops, UserRole.risk}

@router.get("/documents/{document_id}/view-url")
async def get_document_view_url(
    document_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    actor_role = current_user.get("active_role", "")
    if isinstance(actor_role, UserRole):
        actor_role = actor_role.value
    if actor_role not in {r.value for r in _DOC_READ_ROLES}:
        raise HTTPException(status_code=403, detail="Forbidden: admin, ops or risk required")
    result = await document_service.get_view_url(db, document_id, actor_role)
    return {"data": result}
```

Note: `UserRole` and `HTTPException` are already imported in the file.

- [ ] **Step 6: Run full backend tests**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/backend && python -m pytest tests/ -v --tb=short 2>&1 | tail -15
```

Expected: all tests pass (68+ passing, 2 pre-existing failures in test_refi_router + test_roles).

### Frontend

- [ ] **Step 7: Create server action for view URL**

Create `web/lib/actions/document-actions.ts`:

```typescript
'use server'

import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'

export async function getDocumentViewUrl(
  documentId: string
): Promise<{ data?: { url: string; expires_in: number }; error?: string }> {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()
  if (!session) return { error: 'Non authentifié' }

  try {
    const result = await apiFetch<{ data: { url: string; expires_in: number } }>(
      `/documents/${documentId}/view-url`,
      session.access_token
    )
    return { data: result.data }
  } catch (e) {
    return { error: e instanceof Error ? e.message : 'Erreur serveur' }
  }
}
```

- [ ] **Step 8: Create DocumentViewer modal**

Create `web/components/admin/DocumentViewer.tsx`:

```tsx
'use client'

import { useState, useTransition } from 'react'
import { getDocumentViewUrl } from '@/lib/actions/document-actions'

interface Props {
  documentId: string
  fileName: string
}

export function DocumentViewerButton({ documentId, fileName }: Props) {
  const [url, setUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isPending, startTransition] = useTransition()

  function handleOpen() {
    startTransition(async () => {
      setError(null)
      const result = await getDocumentViewUrl(documentId)
      if (result.error) {
        setError(result.error)
        return
      }
      setUrl(result.data!.url)
    })
  }

  function handleClose() {
    setUrl(null)
  }

  return (
    <>
      <button
        onClick={handleOpen}
        disabled={isPending}
        className="shrink-0 text-xs text-blue-500 hover:text-blue-700 disabled:opacity-50 transition-colors"
      >
        {isPending ? '…' : 'Voir'}
      </button>

      {error && (
        <span className="text-xs text-red-500">{error}</span>
      )}

      {url && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div className="relative flex h-[90vh] w-[90vw] max-w-4xl flex-col rounded-xl bg-white shadow-2xl overflow-hidden">
            <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
              <span className="truncate text-sm font-medium text-gray-700">{fileName}</span>
              <div className="flex items-center gap-3">
                <a
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-xs text-blue-500 hover:text-blue-700"
                >
                  Ouvrir dans un onglet
                </a>
                <button
                  onClick={handleClose}
                  className="rounded p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
                  aria-label="Fermer"
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <iframe
              src={url}
              className="flex-1 w-full"
              title={fileName}
            />
          </div>
        </div>
      )}
    </>
  )
}
```

- [ ] **Step 9: Add "Voir" button to DocumentList**

In `web/components/admin/DocumentList.tsx`, add the import and the button to each document row:

```tsx
// Add import at top:
import { DocumentViewerButton } from '@/components/admin/DocumentViewer'

// In the <li> for each document, add the button before the validate/reject buttons:
<li key={doc.id} className="flex items-center justify-between gap-4 px-6 py-3">
  <div className="flex min-w-0 items-center gap-3">
    <StatusBadge status={DOC_STATUS_MAP[doc.status] ?? 'draft'} className="shrink-0" />
    <span className="truncate text-sm text-gray-700">{doc.file_name || doc.type}</span>
  </div>
  <div className="flex shrink-0 items-center gap-2">
    {doc.status !== 'pending_upload' && (
      <DocumentViewerButton documentId={doc.id} fileName={doc.file_name || doc.type} />
    )}
    {canWrite && doc.status !== 'validated' && doc.status !== 'rejected' && (
      <>
        <Button variant="success" size="xs" onClick={() => postDoc(doc.id, 'validate')} disabled={loadingId === doc.id}>
          Valider
        </Button>
        <Button variant="danger" size="xs" onClick={() => handleReject(doc.id)} disabled={loadingId === doc.id}>
          Refuser
        </Button>
      </>
    )}
  </div>
</li>
```

- [ ] **Step 10: TypeScript check**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/web && npx tsc --noEmit
```

Expected: 0 errors.

- [ ] **Step 11: Commit**

```bash
git add backend/app/services/document_service.py backend/app/routers/documents.py backend/tests/test_document_view_url.py web/lib/actions/document-actions.ts web/components/admin/DocumentViewer.tsx web/components/admin/DocumentList.tsx
git commit -m "feat: document viewer — signed URL endpoint + modal viewer in DocumentList"
```

---

## Task 4: Admin queue search, filter, pagination

**Files:**
- Modify: `backend/app/services/admin_service.py`
- Modify: `backend/app/routers/admin.py`
- Create: `backend/tests/test_queue_filters.py`
- Create: `web/components/admin/QueueFilters.tsx`
- Create: `web/components/admin/QueuePagination.tsx`
- Modify: `web/app/(admin)/admin/queue/page.tsx`
- Modify: `web/components/admin/DealQueue.tsx`

### Backend

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_queue_filters.py`:

```python
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services import admin_service


def _make_deal(status: str, public_id: str = "LD-2024-ABC"):
    d = MagicMock()
    d.id = uuid.uuid4()
    d.status = status
    d.public_id = public_id
    d.amount_cents = 10000
    d.duration_months = 36
    d.risk_score = 70.0
    d.risk_band = "B"
    d.monthly_payment_cents = 300
    d.updated_at = MagicMock()
    return d


@pytest.mark.asyncio
async def test_get_queue_no_filters_returns_all():
    deals = [_make_deal("submitted"), _make_deal("internal_review")]
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = deals
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    count_scalars = MagicMock()
    count_scalars.one.return_value = 2
    count_result = MagicMock()
    count_result.scalars.return_value = count_scalars

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[mock_result, count_result])

    result_deals, total = await admin_service.get_queue(db)
    assert len(result_deals) == 2
    assert total == 2


@pytest.mark.asyncio
async def test_get_queue_filters_by_status():
    deals = [_make_deal("submitted")]
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = deals
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    count_scalars = MagicMock()
    count_scalars.one.return_value = 1
    count_result = MagicMock()
    count_result.scalars.return_value = count_scalars

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[mock_result, count_result])

    result_deals, total = await admin_service.get_queue(db, status="submitted")
    assert total == 1


@pytest.mark.asyncio
async def test_get_queue_paginates():
    deals = [_make_deal("submitted")]
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = deals
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    count_scalars = MagicMock()
    count_scalars.one.return_value = 25
    count_result = MagicMock()
    count_result.scalars.return_value = count_scalars

    db = AsyncMock()
    db.execute = AsyncMock(side_effect=[mock_result, count_result])

    result_deals, total = await admin_service.get_queue(db, page=2, page_size=20)
    assert total == 25
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/backend && python -m pytest tests/test_queue_filters.py -v
```

Expected: FAIL — `get_queue() takes 1 positional argument but got more`

- [ ] **Step 3: Update `get_queue` in admin_service**

In `backend/app/services/admin_service.py`, add `from sqlalchemy import case, func, select` at the top (func may not be imported yet — add it if missing). Then replace the existing `get_queue` function:

```python
PAGE_SIZE_MAX = 100

async def get_queue(
    db: AsyncSession,
    status: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Deal], int]:
    page_size = min(page_size, PAGE_SIZE_MAX)
    offset = (page - 1) * page_size

    allowed_statuses = list(_QUEUE_STATUSES) if status is None else [status]
    base_filter = Deal.status.in_(allowed_statuses)

    data_query = (
        select(Deal)
        .where(base_filter)
        .order_by(_STATUS_PRIORITY.asc(), Deal.updated_at.desc())
        .limit(page_size)
        .offset(offset)
    )
    count_query = select(func.count()).select_from(Deal).where(base_filter)

    if search:
        pattern = f"%{search}%"
        data_query = data_query.where(Deal.public_id.ilike(pattern))
        count_query = count_query.where(Deal.public_id.ilike(pattern))

    data_result = await db.execute(data_query)
    count_result = await db.execute(count_query)

    deals = list(data_result.scalars().all())
    total = count_result.scalars().one()
    return deals, total
```

Note: `func` must be imported — check the top of the file; `case` and `select` are already there.

- [ ] **Step 4: Update router endpoint**

In `backend/app/routers/admin.py`, replace the `get_queue` endpoint:

```python
from fastapi import Depends, Query  # add Query to existing import

@router.get("/queue")
async def get_queue(
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _require_read(current_user)
    deals, total = await admin_service.get_queue(db, status=status, search=search, page=page, page_size=page_size)
    return {
        "data": [DealResponse.model_validate(d).model_dump(mode="json") for d in deals],
        "meta": {"total": total, "page": page, "page_size": page_size},
    }
```

- [ ] **Step 5: Run tests**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/backend && python -m pytest tests/test_queue_filters.py tests/ -v --tb=short 2>&1 | tail -15
```

Expected: test_queue_filters tests PASS, full suite still 68+ passing.

### Frontend

The queue page will use URL search params so the server component re-renders with the right filters. The `QueueFilters` component updates the URL; the page reads it.

- [ ] **Step 6: Create QueueFilters client component**

Create `web/components/admin/QueueFilters.tsx`:

```tsx
'use client'

import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { useCallback } from 'react'

const STATUS_OPTIONS = [
  { value: '', label: 'Tous les statuts' },
  { value: 'submitted', label: 'Soumis' },
  { value: 'internal_review', label: 'En revue' },
  { value: 'missing_documents', label: 'Documents manquants' },
]

export function QueueFilters() {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  const createQueryString = useCallback(
    (updates: Record<string, string>) => {
      const params = new URLSearchParams(searchParams.toString())
      for (const [key, value] of Object.entries(updates)) {
        if (value) {
          params.set(key, value)
        } else {
          params.delete(key)
        }
      }
      params.delete('page')
      return params.toString()
    },
    [searchParams]
  )

  const currentSearch = searchParams.get('search') ?? ''
  const currentStatus = searchParams.get('status') ?? ''

  return (
    <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-50">
      <input
        type="search"
        placeholder="Rechercher (réf…)"
        defaultValue={currentSearch}
        onChange={(e) => {
          router.push(pathname + '?' + createQueryString({ search: e.target.value }))
        }}
        className="h-8 w-48 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 placeholder-gray-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
      <select
        value={currentStatus}
        onChange={(e) => {
          router.push(pathname + '?' + createQueryString({ status: e.target.value }))
        }}
        className="h-8 rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      >
        {STATUS_OPTIONS.map((opt) => (
          <option key={opt.value} value={opt.value}>{opt.label}</option>
        ))}
      </select>
    </div>
  )
}
```

- [ ] **Step 7: Create QueuePagination client component**

Create `web/components/admin/QueuePagination.tsx`:

```tsx
'use client'

import { usePathname, useRouter, useSearchParams } from 'next/navigation'
import { useCallback } from 'react'

interface Props {
  total: number
  page: number
  pageSize: number
}

export function QueuePagination({ total, page, pageSize }: Props) {
  const router = useRouter()
  const pathname = usePathname()
  const searchParams = useSearchParams()

  const totalPages = Math.ceil(total / pageSize)

  const goToPage = useCallback(
    (newPage: number) => {
      const params = new URLSearchParams(searchParams.toString())
      params.set('page', String(newPage))
      router.push(pathname + '?' + params.toString())
    },
    [router, pathname, searchParams]
  )

  if (totalPages <= 1) return null

  return (
    <div className="flex items-center justify-between px-6 py-3 border-t border-gray-50 text-sm text-gray-500">
      <span>
        {(page - 1) * pageSize + 1}–{Math.min(page * pageSize, total)} sur {total}
      </span>
      <div className="flex items-center gap-2">
        <button
          onClick={() => goToPage(page - 1)}
          disabled={page <= 1}
          className="rounded px-2 py-1 text-xs hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          ← Préc.
        </button>
        <span className="text-xs tabular-nums">{page} / {totalPages}</span>
        <button
          onClick={() => goToPage(page + 1)}
          disabled={page >= totalPages}
          className="rounded px-2 py-1 text-xs hover:bg-gray-100 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          Suiv. →
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 8: Update queue page to accept searchParams**

Replace `web/app/(admin)/admin/queue/page.tsx` entirely:

```tsx
import { Suspense } from 'react'
import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { DashboardShell } from '@/components/dashboard/DashboardShell'
import { DealQueue } from '@/components/admin/DealQueue'
import { QueueFilters } from '@/components/admin/QueueFilters'
import { QueuePagination } from '@/components/admin/QueuePagination'
import type { Deal } from '@/lib/types/admin'

interface QueueResponse {
  data: Deal[]
  meta: { total: number; page: number; page_size: number }
}

interface Props {
  searchParams: Promise<{ status?: string; search?: string; page?: string }>
}

export default async function AdminQueuePage({ searchParams }: Props) {
  const { status, search, page: pageStr } = await searchParams
  const page = Math.max(1, parseInt(pageStr ?? '1', 10))
  const pageSize = 20

  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()

  if (!session) {
    return <p className="p-8 text-sm text-gray-500">Non authentifié.</p>
  }

  const params = new URLSearchParams()
  if (status) params.set('status', status)
  if (search) params.set('search', search)
  params.set('page', String(page))
  params.set('page_size', String(pageSize))

  let queueData: QueueResponse = { data: [], meta: { total: 0, page: 1, page_size: pageSize } }
  let apiError = false
  try {
    queueData = await apiFetch<QueueResponse>(
      `/admin/queue?${params.toString()}`,
      session.access_token
    )
  } catch {
    apiError = true
  }

  return (
    <DashboardShell
      role="admin"
      title="File d'attente"
      subtitle={`${queueData.meta.total} dossier(s)`}
    >
      {apiError && (
        <p className="mb-4 text-sm text-red-500">Impossible de charger la file d'attente.</p>
      )}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
        <Suspense>
          <QueueFilters />
        </Suspense>
        <DealQueue deals={queueData.data} />
        <Suspense>
          <QueuePagination
            total={queueData.meta.total}
            page={page}
            pageSize={pageSize}
          />
        </Suspense>
      </div>
    </DashboardShell>
  )
}
```

Note: `QueueFilters` and `QueuePagination` use `useSearchParams()` which requires `<Suspense>` wrapping in Next.js App Router.

- [ ] **Step 9: TypeScript check**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/web && npx tsc --noEmit
```

Expected: 0 errors.

- [ ] **Step 10: Commit**

```bash
git add backend/app/services/admin_service.py backend/app/routers/admin.py backend/tests/test_queue_filters.py web/components/admin/QueueFilters.tsx web/components/admin/QueuePagination.tsx web/app/\(admin\)/admin/queue/page.tsx
git commit -m "feat: admin queue search, status filter, pagination"
```

---

## Task 5: ActionPanel → server actions

**Context:** ActionPanel currently takes a `token` prop and calls the API client-side using `NEXT_PUBLIC_API_URL`. The pattern used by OfferPanel, ContractPanel, and RefiPackagePanel is server actions — no token prop, no client-side fetch. This task migrates ActionPanel to that pattern.

**Files:**
- Create: `web/lib/actions/admin-actions.ts`
- Modify: `web/components/admin/ActionPanel.tsx`
- Modify: `web/app/(admin)/admin/deals/[id]/page.tsx`

- [ ] **Step 1: Create admin server actions**

Create `web/lib/actions/admin-actions.ts`:

```typescript
'use server'

import { createSupabaseServerClient } from '@/lib/supabase-server'
import { apiFetch } from '@/lib/api-client'
import { revalidatePath } from 'next/cache'

type ActionResult = { data?: true; error?: string }

export async function requestDocument(
  dealId: string,
  documentType: string,
  reason: string
): Promise<ActionResult> {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()
  if (!session) return { error: 'Non authentifié' }
  try {
    await apiFetch(`/admin/deals/${dealId}/request-document`, session.access_token, {
      method: 'POST',
      body: JSON.stringify({ document_type: documentType, reason }),
    })
    revalidatePath(`/admin/deals/${dealId}`)
    return { data: true }
  } catch (e) {
    return { error: e instanceof Error ? e.message : 'Erreur serveur' }
  }
}

export async function preApproveDeal(
  dealId: string,
  justification: string | null
): Promise<ActionResult> {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()
  if (!session) return { error: 'Non authentifié' }
  try {
    await apiFetch(`/admin/deals/${dealId}/pre-approve`, session.access_token, {
      method: 'POST',
      body: JSON.stringify({ justification }),
    })
    revalidatePath(`/admin/deals/${dealId}`)
    return { data: true }
  } catch (e) {
    return { error: e instanceof Error ? e.message : 'Erreur serveur' }
  }
}

export async function rejectDeal(dealId: string, reason: string): Promise<ActionResult> {
  const supabase = await createSupabaseServerClient()
  const {
    data: { session },
  } = await supabase.auth.getSession()
  if (!session) return { error: 'Non authentifié' }
  try {
    await apiFetch(`/admin/deals/${dealId}/reject`, session.access_token, {
      method: 'POST',
      body: JSON.stringify({ reason }),
    })
    revalidatePath(`/admin/deals/${dealId}`)
    return { data: true }
  } catch (e) {
    return { error: e instanceof Error ? e.message : 'Erreur serveur' }
  }
}
```

- [ ] **Step 2: Rewrite ActionPanel to use server actions**

Replace `web/components/admin/ActionPanel.tsx` entirely:

```tsx
'use client'

import { useState, useTransition } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { requestDocument, preApproveDeal, rejectDeal } from '@/lib/actions/admin-actions'

interface Props {
  dealId: string
  canWrite: boolean
}

type Modal = 'request_doc' | 'pre_approve' | 'reject' | null

export function ActionPanel({ dealId, canWrite }: Props) {
  const [modal, setModal] = useState<Modal>(null)
  const [isPending, startTransition] = useTransition()
  const [docType, setDocType] = useState('')
  const [reason, setReason] = useState('')
  const [justification, setJustification] = useState('')

  function reset() {
    setModal(null)
    setDocType('')
    setReason('')
    setJustification('')
  }

  function handleRequestDoc() {
    startTransition(async () => {
      const result = await requestDocument(dealId, docType, reason)
      if (result.error) {
        toast.error(result.error)
      } else {
        toast.success('Demande de pièce envoyée')
        reset()
      }
    })
  }

  function handlePreApprove() {
    startTransition(async () => {
      const result = await preApproveDeal(dealId, justification || null)
      if (result.error) {
        toast.error(result.error)
      } else {
        toast.success('Dossier pré-accordé')
        reset()
      }
    })
  }

  function handleReject() {
    startTransition(async () => {
      const result = await rejectDeal(dealId, reason)
      if (result.error) {
        toast.error(result.error)
      } else {
        toast.success('Dossier refusé')
        reset()
      }
    })
  }

  if (!canWrite) return null

  return (
    <div className="sticky bottom-0 flex items-center gap-3 border-t border-gray-200 bg-white px-8 py-4">
      <Button variant="warning" onClick={() => setModal('request_doc')}>
        Demander une pièce
      </Button>
      <Button variant="success" onClick={() => setModal('pre_approve')}>
        Pré-accorder
      </Button>
      <Button variant="danger" onClick={() => setModal('reject')}>
        Refuser
      </Button>

      {modal === 'request_doc' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h4 className="mb-4 font-semibold text-navy-900">Demander une pièce</h4>
            <label className="mb-1 block text-sm text-gray-600">Type de document</label>
            <input
              className="mb-3 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              placeholder="rib, kbis, id_card..."
            />
            <label className="mb-1 block text-sm text-gray-600">Raison</label>
            <textarea
              className="mb-4 w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={reset}>Annuler</Button>
              <Button variant="warning" disabled={isPending || !docType || !reason} onClick={handleRequestDoc}>
                Envoyer
              </Button>
            </div>
          </div>
        </div>
      )}

      {modal === 'pre_approve' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h4 className="mb-4 font-semibold text-navy-900">Pré-accorder le dossier</h4>
            <label className="mb-1 block text-sm text-gray-600">
              Justification{' '}
              <span className="font-normal text-gray-400">(requise si checklist incomplète)</span>
            </label>
            <textarea
              className="mb-4 w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              value={justification}
              onChange={(e) => setJustification(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={reset}>Annuler</Button>
              <Button variant="success" disabled={isPending} onClick={handlePreApprove}>
                Confirmer
              </Button>
            </div>
          </div>
        </div>
      )}

      {modal === 'reject' && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
            <h4 className="mb-4 font-semibold text-navy-900">Refuser le dossier</h4>
            <label className="mb-1 block text-sm text-gray-600">
              Raison <span className="text-red-500">*</span>
            </label>
            <textarea
              className="mb-4 w-full resize-none rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
            <div className="flex justify-end gap-2">
              <Button variant="ghost" size="sm" onClick={reset}>Annuler</Button>
              <Button variant="danger" disabled={isPending || !reason} onClick={handleReject}>
                Confirmer le refus
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

- [ ] **Step 3: Remove `token` prop from ActionPanel usage in deal detail page**

In `web/app/(admin)/admin/deals/[id]/page.tsx`, find the `<ActionPanel>` render and remove the `token` prop:

```tsx
// Replace:
<ActionPanel dealId={id} token={token} canWrite={userCanWrite} />

// With:
<ActionPanel dealId={id} canWrite={userCanWrite} />
```

Also verify there are no remaining TypeScript references to `ActionPanel` receiving `token`.

- [ ] **Step 4: TypeScript check**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/web && npx tsc --noEmit
```

Expected: 0 errors. If there are errors about `token` prop on ActionPanel, the Props interface in ActionPanel.tsx still has it — remove it.

- [ ] **Step 5: Commit**

```bash
git add web/lib/actions/admin-actions.ts web/components/admin/ActionPanel.tsx web/app/\(admin\)/admin/deals/\[id\]/page.tsx
git commit -m "refactor: ActionPanel — remove token prop, migrate to server actions"
```

---

## Task 6: Assets + payment schedule panel

**Context:** After a deal is activated (`deal.status === 'active'`), `Asset` and `PaymentSchedule` rows exist in the DB linked to the contract. This task adds backend endpoints to read them and a frontend panel to display them on the deal detail page.

**Files:**
- Modify: `backend/app/schemas/contract.py`
- Modify: `backend/app/routers/contracts.py`
- Create: `backend/tests/test_contract_assets.py`
- Create: `web/components/admin/AssetsPanel.tsx`
- Modify: `web/lib/types/contract.ts`
- Modify: `web/app/(admin)/admin/deals/[id]/page.tsx`

### Backend

- [ ] **Step 1: Write failing tests**

Create `backend/tests/test_contract_assets.py`:

```python
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

BASE = "http://test"
ADMIN_TOKEN = "admin-token"


def _mock_user(role: str = "admin"):
    return {
        "user_id": str(uuid.uuid4()),
        "active_role": role,
        "email": "test@example.com",
    }


@pytest.fixture
def client():
    return TestClient(app)


def test_get_assets_returns_200(client):
    contract_id = uuid.uuid4()
    asset_id = uuid.uuid4()

    with (
        patch("app.core.auth.get_jwks", return_value={}),
        patch("app.core.auth.verify_token", return_value=_mock_user("admin")),
        patch("app.routers.contracts.contract_service.get_contract") as mock_get,
        patch("app.routers.contracts.contract_service.get_assets") as mock_assets,
    ):
        mock_contract = MagicMock()
        mock_contract.id = contract_id
        mock_get.return_value = mock_contract

        mock_asset = MagicMock()
        mock_asset.id = asset_id
        mock_asset.name = "MacBook Pro"
        mock_asset.category = "laptop"
        mock_asset.quantity = 1
        mock_asset.unit_value_cents = 200000
        mock_assets.return_value = [mock_asset]

        resp = client.get(
            f"/contracts/{contract_id}/assets",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
        )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["name"] == "MacBook Pro"


def test_get_payment_schedule_returns_200(client):
    contract_id = uuid.uuid4()
    schedule_id = uuid.uuid4()

    with (
        patch("app.core.auth.get_jwks", return_value={}),
        patch("app.core.auth.verify_token", return_value=_mock_user("admin")),
        patch("app.routers.contracts.contract_service.get_contract") as mock_get,
        patch("app.routers.contracts.contract_service.get_payment_schedule") as mock_sched,
    ):
        mock_contract = MagicMock()
        mock_contract.id = contract_id
        mock_get.return_value = mock_contract

        mock_entry = MagicMock()
        mock_entry.id = schedule_id
        mock_entry.due_date = "2026-06-01T00:00:00+00:00"
        mock_entry.amount_cents = 30000
        mock_entry.status = "pending"
        mock_sched.return_value = [mock_entry]

        resp = client.get(
            f"/contracts/{contract_id}/payment-schedule",
            headers={"Authorization": f"Bearer {ADMIN_TOKEN}"},
        )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 1
    assert data[0]["amount_cents"] == 30000
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/backend && python -m pytest tests/test_contract_assets.py -v
```

Expected: FAIL — `404 Not Found` (endpoints don't exist yet).

- [ ] **Step 3: Add schemas**

In `backend/app/schemas/contract.py`, add at the end:

```python
class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    category: str | None
    quantity: int
    unit_value_cents: int


class PaymentScheduleItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    due_date: datetime
    amount_cents: int
    status: str
```

- [ ] **Step 4: Add service methods**

In `backend/app/services/contract_service.py`, add after `get_contract`:

```python
async def get_assets(db: AsyncSession, contract_id: uuid.UUID) -> list[Asset]:
    result = await db.execute(select(Asset).where(Asset.contract_id == contract_id))
    return list(result.scalars().all())


async def get_payment_schedule(db: AsyncSession, contract_id: uuid.UUID) -> list[PaymentSchedule]:
    result = await db.execute(
        select(PaymentSchedule)
        .where(PaymentSchedule.contract_id == contract_id)
        .order_by(PaymentSchedule.due_date.asc())
    )
    return list(result.scalars().all())
```

- [ ] **Step 5: Add router endpoints**

In `backend/app/routers/contracts.py`, add these two endpoints after `get_activation_checklist`:

```python
@router.get("/contracts/{contract_id}/assets")
async def get_contract_assets(
    contract_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _check_read_role(current_user)
    await contract_service.get_contract(db, contract_id)
    assets = await contract_service.get_assets(db, contract_id)
    return {
        "data": [
            AssetResponse.model_validate(a).model_dump(mode="json") for a in assets
        ]
    }


@router.get("/contracts/{contract_id}/payment-schedule")
async def get_payment_schedule(
    contract_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    _check_read_role(current_user)
    await contract_service.get_contract(db, contract_id)
    schedule = await contract_service.get_payment_schedule(db, contract_id)
    return {
        "data": [
            PaymentScheduleItemResponse.model_validate(s).model_dump(mode="json")
            for s in schedule
        ]
    }
```

Also add the new schema imports at the top of `contracts.py` — add `AssetResponse, PaymentScheduleItemResponse` to the existing schema import line.

- [ ] **Step 6: Run tests**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/backend && python -m pytest tests/test_contract_assets.py tests/ -v --tb=short 2>&1 | tail -15
```

Expected: test_contract_assets tests PASS.

### Frontend

- [ ] **Step 7: Add types**

In `web/lib/types/contract.ts`, add:

```typescript
export interface Asset {
  id: string
  name: string
  category: string | null
  quantity: number
  unit_value_cents: number
}

export interface PaymentScheduleItem {
  id: string
  due_date: string
  amount_cents: number
  status: 'pending' | 'paid' | string
}
```

- [ ] **Step 8: Create AssetsPanel**

Create `web/components/admin/AssetsPanel.tsx`:

```tsx
import { CardContent, CardHeader } from '@/components/ui/card'
import type { Asset, PaymentScheduleItem } from '@/lib/types/contract'

function formatMoney(cents: number): string {
  return new Intl.NumberFormat('fr-FR', { style: 'currency', currency: 'EUR' }).format(cents / 100)
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

interface Props {
  assets: Asset[]
  schedule: PaymentScheduleItem[]
}

export function AssetsPanel({ assets, schedule }: Props) {
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
        <CardHeader>
          <h3 className="text-sm font-semibold text-navy-900">Équipements activés</h3>
        </CardHeader>
        <CardContent className="p-0">
          {assets.length === 0 ? (
            <p className="px-6 py-8 text-center text-sm text-gray-400">Aucun équipement.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider text-left bg-gray-50/60">
                  <th className="px-6 py-3">Désignation</th>
                  <th className="py-3">Catégorie</th>
                  <th className="py-3">Qté</th>
                  <th className="py-3 pr-6 text-right">Valeur unitaire</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {assets.map((asset) => (
                  <tr key={asset.id}>
                    <td className="px-6 py-3 text-gray-700">{asset.name}</td>
                    <td className="py-3 text-gray-500">{asset.category ?? '—'}</td>
                    <td className="py-3 font-mono text-xs tabular-nums text-gray-700">{asset.quantity}</td>
                    <td className="py-3 pr-6 text-right font-mono text-xs tabular-nums text-gray-700">
                      {formatMoney(asset.unit_value_cents)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </div>

      <div className="rounded-xl border border-gray-100 bg-white shadow-sm overflow-hidden">
        <CardHeader>
          <h3 className="text-sm font-semibold text-navy-900">Échéancier</h3>
        </CardHeader>
        <CardContent className="p-0">
          {schedule.length === 0 ? (
            <p className="px-6 py-8 text-center text-sm text-gray-400">Aucune échéance.</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="text-[11px] font-semibold text-gray-400 uppercase tracking-wider text-left bg-gray-50/60">
                  <th className="px-6 py-3">Date</th>
                  <th className="py-3">Montant</th>
                  <th className="py-3 pr-6">Statut</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {schedule.map((entry) => (
                  <tr key={entry.id}>
                    <td className="px-6 py-2 font-mono text-xs tabular-nums text-gray-700">
                      {formatDate(entry.due_date)}
                    </td>
                    <td className="py-2 font-mono text-xs tabular-nums text-gray-700">
                      {formatMoney(entry.amount_cents)}
                    </td>
                    <td className="py-2 pr-6">
                      <span className={`inline-flex rounded-full px-2 py-0.5 text-[11px] font-medium ${
                        entry.status === 'paid'
                          ? 'bg-green-50 text-green-700'
                          : 'bg-gray-100 text-gray-500'
                      }`}>
                        {entry.status === 'paid' ? 'Payée' : 'En attente'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </div>
    </div>
  )
}
```

- [ ] **Step 9: Wire AssetsPanel into deal detail page**

In `web/app/(admin)/admin/deals/[id]/page.tsx`:

1. Add imports at top:
```tsx
import { AssetsPanel } from '@/components/admin/AssetsPanel'
import type { Asset, PaymentScheduleItem } from '@/lib/types/contract'
```

2. Add state variables after existing ones:
```tsx
let assets: Asset[] = []
let paymentSchedule: PaymentScheduleItem[] = []
```

3. After the existing `activationChecklist` fetch block, add a fetch for assets when the deal is active and contract exists:
```tsx
if (deal?.status === 'active' && contract) {
  const [assetsResult, scheduleResult] = await Promise.allSettled([
    apiFetch<{ data: Asset[] }>(`/contracts/${contract.id}/assets`, token),
    apiFetch<{ data: PaymentScheduleItem[] }>(`/contracts/${contract.id}/payment-schedule`, token),
  ])
  if (assetsResult.status === 'fulfilled') assets = assetsResult.value.data
  if (scheduleResult.status === 'fulfilled') paymentSchedule = scheduleResult.value.data
}
```

4. After `<ActivationChecklist />`, add:
```tsx
{deal?.status === 'active' && (
  <AssetsPanel assets={assets} schedule={paymentSchedule} />
)}
```

- [ ] **Step 10: TypeScript check**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/web && npx tsc --noEmit
```

Expected: 0 errors.

- [ ] **Step 11: Final backend tests**

```bash
cd /Users/clementsporrer/.superset/projects/lease.ai/backend && python -m pytest tests/ -v --tb=short 2>&1 | tail -10
```

Expected: 70+ tests PASS.

- [ ] **Step 12: Commit**

```bash
git add backend/app/schemas/contract.py backend/app/services/contract_service.py backend/app/routers/contracts.py backend/tests/test_contract_assets.py web/lib/types/contract.ts web/components/admin/AssetsPanel.tsx web/app/\(admin\)/admin/deals/\[id\]/page.tsx
git commit -m "feat: assets + payment schedule panel — backend endpoints + AssetsPanel"
```

---

## Self-review

**Spec coverage check:**
- ✅ Favicon + branding (Task 1)
- ✅ EmptyState component replacing bare `<p>` (Task 2)
- ✅ Document viewer — backend signed URL + modal (Task 3)
- ✅ Queue search/filter/pagination — backend params + frontend QueueFilters + QueuePagination (Task 4)
- ✅ ActionPanel → server actions, `token` prop removed (Task 5)
- ✅ Assets + payment schedule panel visible on active deal (Task 6)

**Placeholder scan:** None found. All code blocks are complete.

**Type consistency check:**
- `Asset.id`, `Asset.name`, `Asset.unit_value_cents` defined in `contract.ts` Task 7 and used identically in `AssetsPanel.tsx` Task 8 ✅
- `PaymentScheduleItem.due_date`, `.amount_cents`, `.status` consistent across types and panel ✅
- `get_assets(db, contract_id)` and `get_payment_schedule(db, contract_id)` defined in service Task 4, called in router Task 5 ✅
- `AssetResponse`, `PaymentScheduleItemResponse` added to schemas Task 3, imported in router Task 5 ✅
- `QueueFilters` + `QueuePagination` exported from their files and imported in queue page ✅
- `DocumentViewerButton` exported and imported in DocumentList ✅
- `EmptyState` exported and imported in DealQueue + DocumentList ✅
