import { useMutation } from '@tanstack/react-query'

import { confirmUpload, getUploadUrl, uploadFileDirect } from '@/src/services/documents'
import { useDealCreationStore } from '@/src/stores/dealCreation'

interface UploadPayload {
  dealId: string
  fileUri: string
  fileName: string
  mimeType: string
  sizeBytes: number
}

export function useUploadDocument() {
  const setDocumentId = useDealCreationStore((state) => state.setDocumentId)

  return useMutation({
    mutationFn: async ({ dealId, fileUri, fileName, mimeType, sizeBytes }: UploadPayload) => {
      const uploadData = await getUploadUrl(dealId)
      await uploadFileDirect(uploadData.upload_url, fileUri, mimeType)
      const document = await confirmUpload(dealId, uploadData.document_id, fileName, mimeType, sizeBytes)
      return document
    },
    onSuccess: (document) => setDocumentId(document.id),
    retry: 1,
  })
}
