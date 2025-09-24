import { useState, useEffect } from 'react';

export default function Home() {
  const [articles, setArticles] = useState([]);
  const [query, setQuery] = useState('');

  useEffect(() => {
    async function fetchArticles() {
      const response = await fetch(`/api/articles?q=${query}`);
      const data = await response.json();
      setArticles(data.items);
    }
    fetchArticles();
  }, [query]);

  return (
    <div>
      <h1>新闻展示</h1>
      <input
        type="text"
        placeholder="输入关键词筛选"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <ul>
        {articles.map((article) => (
          <li key={article.id}>{article.title}</li>
        ))}
      </ul>
    </div>
  );
}