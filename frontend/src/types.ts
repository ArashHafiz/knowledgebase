export interface DocumentSummary {
    id: number
    filename: string
    word_count: number
}

export interface DocumentDetail extends DocumentSummary {
    content: string
}

export interface SearchChunkResult {
    chunk_number: number
    start_line: number
    end_line: number
    doc_id: number
    filename: string
    text: string
    matches: number
}

export interface SearchDocumentResult {
    id: number
    filename: string
    results: SearchChunkResult[]
    score: number
}

export interface SearchResponse {
    total_score: number
    results: SearchDocumentResult[]
}