import type { DocumentSummary } from './types';

const API_URL = 'http://127.0.0.1:8000'

export async function getDocuments(): Promise<DocumentSummary[]> {
    const response = await fetch(`${API_URL}/documents`)

    const documents: DocumentSummary[] = await response.json()

    return documents
}