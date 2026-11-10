import type { DocumentSummary, DocumentDetail, SearchResponse, AskResponse } from './types';

const API_URL = 'http://127.0.0.1:8000'

export async function getDocuments(): Promise<DocumentSummary[]> {
    const response = await safeFetch(`${API_URL}/documents`)

    if (!response.ok) {
        throw new Error(await getErrorMessage(response, `Failed to fetch documents (${response.status})`))
    }

    const documents: DocumentSummary[] = await response.json()
    return documents
}

export async function uploadDocument(file: File): Promise<DocumentSummary> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await safeFetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
    })

    if (response.status === 404) {
        throw new Error(await getErrorMessage(response, 'Document not found'))
    }

    if (!response.ok) {
        throw new Error(await getErrorMessage(response, `Failed to upload document: ${response.status}`))
    }

    const document : DocumentSummary = await response.json()
    return document
}

export async function getDocument(id: number): Promise<DocumentDetail> {
    const response = await safeFetch(`${API_URL}/documents/${id}`)

    if (!response.ok) {
        throw new Error(await getErrorMessage(response, `Failed to fetch document: ${response.status}`))
    }

    const document : DocumentDetail = await response.json()
    return document
}

export async function searchDocuments(query: string): Promise<SearchResponse> {
    const response = await safeFetch(`${API_URL}/search?query=${encodeURIComponent(query)}`)

    if (!response.ok) {
        throw new Error(await getErrorMessage(response, `Failed to perform search: ${response.status}`))
    }

    const searchResult : SearchResponse = await response.json()
    return searchResult
}

export async function askQuestion(question: string): Promise<AskResponse> {
    const response = await safeFetch(`${API_URL}/ask?question=${encodeURIComponent(question)}`, {
        method: 'POST'
    })

    if (response.status === 502) {
        throw new Error(await getErrorMessage(response, 'There was an issue with Gemini. Please try again at a later time.'))
    }

    if (!response.ok) {
        throw new Error(await getErrorMessage(response, `Failed to ask question: ${response.status}`))
    }

    const answer : AskResponse = await response.json()
    return answer
}

async function getErrorMessage(response: Response, fallback: string): Promise<string> {
    try {
        const data : { detail? : unknown } = await response.json()
        if (typeof data.detail === 'string') {
            return data.detail
        }
    } catch (err) {
        // Go to fallback
    }
    return fallback
}

async function safeFetch(url: string, options?: RequestInit): Promise<Response> {
    try {    
        return await fetch(url, options)
    } catch {
        throw new Error('Could not reach the server. Check that the backend is running.')
    }
}