import { useState } from 'react'

function AnalyzerForm({ onAnalyze, loading }) {
  const [text, setText] = useState('')
  const [topN, setTopN] = useState(20)
  const [minLength, setMinLength] = useState(3)
  const [caseSensitive, setCaseSensitive] = useState(false)
  const [excludeStopwords, setExcludeStopwords] = useState(true)

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!text.trim()) return

    onAnalyze({
      text,
      top_n: topN,
      min_length: minLength,
      case_sensitive: caseSensitive,
      exclude_stopwords: excludeStopwords
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-group">
        <label htmlFor="text">Enter Text to Analyze</label>
        <textarea
          id="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste your document or text here..."
          required
        />
      </div>

      <div className="options-row">
        <label className="toggle-label">
          <input
            type="checkbox"
            checked={caseSensitive}
            onChange={(e) => setCaseSensitive(e.target.checked)}
          />
          Case Sensitive
        </label>

        <label className="toggle-label">
          <input
            type="checkbox"
            checked={excludeStopwords}
            onChange={(e) => setExcludeStopwords(e.target.checked)}
          />
          Exclude Stopwords
        </label>
      </div>

      <div className="options-row">
        <div className="number-input">
          <label htmlFor="topN">Top N Words</label>
          <input
            id="topN"
            type="number"
            min="1"
            max="100"
            value={topN}
            onChange={(e) => setTopN(parseInt(e.target.value) || 20)}
          />
        </div>

        <div className="number-input">
          <label htmlFor="minLength">Min Length</label>
          <input
            id="minLength"
            type="number"
            min="1"
            max="20"
            value={minLength}
            onChange={(e) => setMinLength(parseInt(e.target.value) || 3)}
          />
        </div>
      </div>

      <button 
        type="submit" 
        className="primary-btn" 
        disabled={loading || !text.trim()}
      >
        {loading ? (
          <>
            <span className="loading-spinner"></span>
            Analyzing...
          </>
        ) : (
          'Analyze Text'
        )}
      </button>
    </form>
  )
}

export default AnalyzerForm
