function Results({ data }) {
  if (!data || !data.statistics || !data.top_words) {
    return null;
  }

  const { statistics, top_words } = data;
  const maxCount = top_words.length > 0 ? top_words[0].count : 1;

  const statItems = [
    { label: 'Total Words', value: statistics.total_words },
    { label: 'Unique Words', value: statistics.unique_words },
    { label: 'Sentences', value: statistics.sentences },
    { label: 'Paragraphs', value: statistics.paragraphs },
    { label: 'Avg Length', value: statistics.avg_word_length },
    { label: 'Richness', value: statistics.lexical_richness }
  ];

  return (
    <div>
      <h2 className="results-header">Text Statistics</h2>
      
      <div className="stats-grid">
        {statItems.map((stat, i) => (
          <div className="stat-card" key={i}>
            <div className="stat-value">
              {typeof stat.value === 'number' && stat.value % 1 !== 0 
                ? stat.value.toFixed(2) 
                : stat.value.toLocaleString()}
            </div>
            <div className="stat-label">{stat.label}</div>
          </div>
        ))}
      </div>

      <h2 className="results-header">Top Words</h2>
      
      <div className="chart-container">
        {top_words.map((item, i) => {
          const widthPercent = (item.count / maxCount) * 100;
          return (
            <div className="bar-row" key={i}>
              <div className="bar-word" title={item.word}>
                {item.word}
              </div>
              <div className="bar-wrapper">
                <div 
                  className="bar-fill" 
                  style={{ width: `${widthPercent}%` }}
                ></div>
              </div>
              <div className="bar-count">
                {item.count.toLocaleString()}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  )
}

export default Results
