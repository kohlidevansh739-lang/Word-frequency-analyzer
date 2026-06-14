import { useState } from 'react'
import AnalyzerForm from './components/AnalyzerForm'
import Results from './components/Results'

function App() {
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async (formData) => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      })
      
      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || 'Analysis failed. Please try again.')
      }
      
      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <header>
        <h1>Word Frequency Analyzer</h1>
        <p className="subtitle">Discover the lexical DNA of your text.</p>
      </header>

      <main className="grid">
        <section>
          <div className="glass-panel">
            <AnalyzerForm onAnalyze={handleAnalyze} loading={loading} />
            {error && <div className="error-message">{error}</div>}
          </div>
        </section>

        <section>
          <div className="glass-panel" style={{ height: '100%' }}>
            {results ? (
              <Results data={results} />
            ) : (
              <div className="empty-state">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <p>Submit text to see the analysis results here.</p>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
