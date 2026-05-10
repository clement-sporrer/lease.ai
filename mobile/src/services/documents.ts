import { apiGet, apiPost } from '@/src/lib/api'

export interface UploadUrlResponse {
  document_id: string
  upload_url: string
  expires_in: number
}

export interface DocumentRecord {
  id: string
  deal_id: string
  type: string
  status: string
  file_name: string
  mime_type: string | null
  size_bytes: number | null
  version: number
  created_at: string
}

export async function getUploadUrl(dealId: string): Promise<UploadUrlResponse> {
  return apiPost<UploadUrlResponse>(`/deals/${dealId}/documents/upload-url`, {})
}

export async function listDocuments(dealId: string): Promise<DocumentRecord[]> {
  return apiGet<DocumentRecord[]>(`/deals/${dealId}/documents`)
}

export async function uploadFileDirect(uploadUrl: string, fileUri: string, mimeType: string): Promise<void> {
  const response = await fetch(fileUri)
  const blob = await response.blob()
  const uploadResponse = await fetch(uploadUrl, {
    method: 'PUT',
    headers: { 'Content-Type': mimeType },
    body: blob,
  })

  if (!uploadResponse.ok) {
    throw new Error(`Upload failed: ${uploadResponse.status}`)
  }
}

export function buildStorageKey(dealId: string, documentId: string): string {
  return `deals/${dealId}/${documentId}`
}

export async function confirmUpload(
  dealId: string,
  documentId: string,
  fileName: string,
  mimeType: string,
  sizeBytes: number,
): Promise<DocumentRecord> {
  return apiPost<DocumentRecord>(`/deals/${dealId}/documents/confirm`, {
    document_id: documentId,
    storage_key: buildStorageKey(dealId, documentId),
    file_name: fileName,
    mime_type: mimeType,
    size_bytes: sizeBytes,
    document_type: 'quote',
  })
}
