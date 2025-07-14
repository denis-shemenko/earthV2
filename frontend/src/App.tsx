// import { useEffect, useState } from "react";
// import { fetchStart, sendAnswer } from "./api";
// import type { Question } from "./types";
// import QuestionCard from "./components/QuestionCard";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import GraphView from "./components/GraphView";
//import Game from "./Game"; // старый App с квизом

export default function App() {
  return (
    <Router>
      <nav className="p-4 bg-gray-800 text-white flex gap-4 justify-center">
        <Link to="/">🧠 Игра</Link>
        <Link to="/help">📍 Помощь</Link>
      </nav>
      <Routes>
        <Route path="/" element={<GraphView />} />
        <Route path="/help" element={<GraphView />} />
      </Routes>
    </Router>
  );
}

// function App() {
//   const [question, setQuestion] = useState<Question | null>(null);
//   const [selected, setSelected] = useState<string | null>(null);
//   const [disabled, setDisabled] = useState(false);

//   const loadStart = async () => {
//     const q = await fetchStart();
//     setQuestion(q);
//     setSelected(null);
//     setDisabled(false);
//   };

//   const handleAnswer = async (answer: string) => {
//     if (!question) return;
//     setSelected(answer);
//     setDisabled(true);

//     setTimeout(async () => {
//       const next = await sendAnswer(question.session_id, answer);
//       setQuestion(next);
//       setSelected(null);
//       setDisabled(false);
//     }, 1500);
//   };

//   useEffect(() => {
//     loadStart();
//   }, []);

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-purple-100 to-indigo-200 p-6">
//       <h1 className="text-3xl font-bold text-center mb-6">🧠 Путь Знаний</h1>
//       {question ? (
//         <QuestionCard
//           data={question}
//           onAnswer={handleAnswer}
//           disabled={disabled}
//           selected={selected}
//         />
//       ) : (
//         <p className="text-center">Загрузка...</p>
//       )}
//     </div>
//   );
// }

// export default App;
