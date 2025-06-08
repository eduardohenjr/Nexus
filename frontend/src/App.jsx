import { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Olá! Pergunte algo sobre sua máquina.' }
  ]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;
    setMessages((msgs) => [...msgs, { sender: 'user', text: question }]);
    setLoading(true);
    const currentQuestion = question;
    setQuestion('');
    try {
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: currentQuestion })
      });
      const data = await response.json();
      setMessages((msgs) => [...msgs, { sender: 'bot', text: data.answer }]);
    } catch (err) {
      setMessages((msgs) => [...msgs, { sender: 'bot', text: 'Erro ao conectar ao backend.' }]);
    }
    setLoading(false);
  };

  return (
    <div className="main-bg">
      <header className="header">
        <div className="logo">Nexus IA Local</div>
      </header>
      <main className="content">
        <section className="chat-section">
          <div className="chat-window">
            {messages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.sender === 'user' ? 'user' : 'bot'}`}>{msg.text}</div>
            ))}
            <div ref={chatEndRef} />
          </div>
          <form onSubmit={handleSubmit} className="chat-form">
            <input
              type="text"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="Digite sua pergunta..."
              className="input"
              required
              disabled={loading}
              autoFocus
            />
            <button type="submit" className="button" disabled={loading || !question.trim()}>
              {loading ? '...' : 'Enviar'}
            </button>
          </form>
        </section>
      </main>
      <footer className="footer">
        <span>Desenvolvido por Nexus • 2025</span>
      </footer>
    </div>
  );
}

export default App;
