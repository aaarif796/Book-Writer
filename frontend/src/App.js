import React, { useState } from 'react';
import axios from 'axios';
export default function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const handleSubmit = async (agent, input) => {
    setLoading(true);
    try {
      const endpoint = { writer: '/agents/write', reviewer: '/agents/review', designer: '/agents/design' }[agent];
      const payload = agent === 'writer' ? { prompt: input } : agent === 'reviewer' ? { text: input } : { context: input };
      const res = await axios.post(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}${endpoint}`, payload);
      setResult(JSON.stringify(res.data, null, 2));
    } catch (err) {
      setResult('Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="app-container">
      <h1>Book Writer AI (Robust)</h1>
      <p>Run agents: Writer, Reviewer, Designer</p>
      <AgentForm onSubmit={handleSubmit} loading={loading} />
      {result && <div className="output-box"><pre>{result}</pre></div>}
    </div>
  );
}

function AgentForm({ onSubmit, loading }) {
  const [agent, setAgent] = useState('writer');
  const [input, setInput] = useState('');
  const handle = (e) => { e.preventDefault(); if (!input.trim()) return alert('enter text'); onSubmit(agent, input); };
  return (
    <form onSubmit={handle} className="agent-form">
      <label>Agent: <select value={agent} onChange={(e)=>setAgent(e.target.value)}><option value="writer">Writer</option><option value="reviewer">Reviewer</option><option value="designer">Designer</option></select></label>
      <textarea value={input} onChange={(e)=>setInput(e.target.value)} placeholder="Enter prompt or text" />
      <button type="submit" disabled={loading}>{loading ? 'Running...' : 'Run Agent'}</button>
    </form>
  );
}