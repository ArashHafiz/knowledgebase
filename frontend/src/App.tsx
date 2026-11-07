import { useState, useEffect } from 'react'
import { getDocuments, uploadDocument } from './api'
import type { DocumentSummary } from './types'
import './App.css'

type Section = 'documents' | 'search' | 'ask'

const navigationItems: { id: Section; label: string }[] = [
  { id: 'documents', label: 'Documents' },
  { id: 'search', label: 'Search' },
  { id: 'ask', label: 'Ask AI' },
]

function App() {
  const [activeSection, setActiveSection] = useState<Section>('documents')
  const [documents, setDocuments] = useState<DocumentSummary[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null)
  const [inputKey, setInputKey] = useState(0)

  useEffect(() => {
    async function loadDocuments() {
        try {
          setIsLoading(true)
          setError(null)

          const data = await getDocuments()
          setDocuments(data)
        } catch(err) {
          setError(
            err instanceof Error
            ? err.message
            : 'An unexpected error occurred.'
          )
        } finally {
          setIsLoading(false)
        }
    }

    loadDocuments()
  }, [])

  async function handleUpload() {
    if (!selectedFile) {
      return
    }

    setIsUploading(true)
    setUploadError(null)
    setUploadSuccess(null)

    try {
      const uploadedDocument = await uploadDocument(selectedFile)

      setSelectedFile(null)
      setInputKey((k) => k + 1)
      setUploadSuccess(
        `${uploadedDocument.filename} uploaded successfully.`
      )

      try {
        const updatedDocuments = await getDocuments()
        setDocuments(updatedDocuments)
        setError(null)
      } catch (err) {
        setError(
          err instanceof Error
          ? err.message
          : 'Failed to refresh document.'
        )
      }
    } catch (err) {
      setUploadError(
        err instanceof Error
        ? err.message
        : 'An unexpected error occurred.'
      )
    } finally {
      setIsUploading(false)
    }
  }

  const activeItem = navigationItems.find(
    (item) => item.id === activeSection,
  )

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">K</div>
          <span>Knowledge Base</span>
        </div>
        <span className="topbar-label">PERSONAL WORKSPACE</span>
      </header>

      <div className="workspace">
        <aside className="sidebar">
          <div className="sidebar-heading">WORKSPACE</div>

          <nav className="navigation" aria-label="Main navigation">
            {navigationItems.map((item) => (
              <button
                key={item.id}
                type="button"
                className={`nav-item ${
                  activeSection === item.id ? 'active' : ''
                }`}
                aria-current={
                  activeSection === item.id ? 'page' : undefined
                }
                onClick={() => setActiveSection(item.id)}
              >
                {item.label}
              </button>
            ))}
          </nav>

          <div className="sidebar-footer">
            <span className="status-indicator" />
            API connection will be configured later
          </div>
        </aside>

        <main className="main-content">
          <div className="page-heading">
            <div>
              <span className="eyebrow">KNOWLEDGE BASE</span>
              <h1>{activeItem?.label}</h1>
              <p className="page-description">
                {activeSection === 'documents' &&
                  'Manage and access your stored documents.'}
                {activeSection === 'search' &&
                  'Find relevant information across your documents.'}
                {activeSection === 'ask' &&
                  'Ask questions and get answers grounded in your documents.'}
              </p>
            </div>
          </div>

          <section className="content-panel">
            {activeSection === 'documents' && (
              <>
                  <h2>Your documents</h2>

                  <div className="upload-section">
                      <h3>Upload a document</h3>

                      <input
                          key={inputKey}
                          type="file"
                          accept=".txt,text/plain"
                          onChange={(event) => {
                              setSelectedFile(event.target.files?.[0] ?? null)
                              setUploadError(null)
                              setUploadSuccess(null)
                          }}
                      />

                      <button
                          type="button"
                          onClick={handleUpload}
                          disabled={!selectedFile || isUploading}
                      >
                          {isUploading ? 'Uploading...' : 'Upload'}
                      </button>

                      {uploadError && (
                          <p role="alert">{uploadError}</p>
                      )}

                      {uploadSuccess && (
                          <p>{uploadSuccess}</p>
                      )}
                  </div>

                  {isLoading && <p>Loading documents...</p>}

                  {!isLoading && error && (
                      <p role="alert">{error}</p>
                  )}

                  {!isLoading && !error && documents.length === 0 && (
                      <p>No documents found.</p>
                  )}

                  {!isLoading && !error && documents.length > 0 && (
                      <ul>
                          {documents.map((document) => (
                              <li key={document.id}>
                                  {document.filename} — {document.word_count} words
                              </li>
                          ))}
                      </ul>
                  )}
              </>
          )}

            {activeSection === 'search' && (
                <>
                    <h2>Search your knowledge base</h2>
                    <p>Search functionality will be implemented next.</p>
                </>
            )}

            {activeSection === 'ask' && (
                <>
                    <h2>Ask your knowledge base</h2>
                    <p>AI question answering will be implemented later.</p>
                </>
            )}
        </section>
        </main>
      </div>
    </div>
  )
}

export default App