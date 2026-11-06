import { useState, useEffect } from 'react'
import { getDocuments } from './api'
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

  useEffect(() => {
    async function loadDocuments() {
        const data = await getDocuments()
        setDocuments(data)
    }

    loadDocuments()
  }, [])

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

                    {documents.length === 0 ? (
                        <p>No documents found.</p>
                    ) : (
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