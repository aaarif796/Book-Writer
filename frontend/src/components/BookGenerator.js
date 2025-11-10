import React, { useState } from "react";

const API_URL = process.env.REACT_APP_API_URL;

export default function BookGenerator() {
  const [title, setTitle] = useState("");
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleGenerate = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        `${API_URL}/books/generate?title=${encodeURIComponent(title)}&topic=${encodeURIComponent(topic)}`,
        { method: "POST" }
      );
      const data = await response.json();
      setResult(data);
    } catch (err) {
      console.error(err);
      alert("Error generating book!");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="book-generator">
      <h2>📚 Book Writer AI</h2>
      <input
        type="text"
        placeholder="Enter Book Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <input
        type="text"
        placeholder="Enter Topic"
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
      />
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? "Generating..." : "Generate Book"}
      </button>

      {result && (
        <div className="download-links">
          <h3>✅ Book Generated Successfully!</h3>
          <p><strong>Title:</strong> {result.title}</p>
          <a href={`${API_URL}/${result.docx_file}`} download>📄 Download DOCX</a>
          <a href={`${API_URL}/${result.pdf_file}`} download>📘 Download PDF</a>
        </div>
      )}
    </div>
  );
}
