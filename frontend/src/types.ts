export interface DocumentSummary {
    id: number
    filename: string
    word_count: number
}

export interface DocumentDetail extends DocumentSummary {
    content: string
}