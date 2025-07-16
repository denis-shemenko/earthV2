// hooks/useAnswerFlow.ts
import { useRef } from "react";
import type { GraphNode, GraphLink, KnowledgeGraph } from "../types";

export function useAnswerFlow(graphRef, setGraphData) {
  const isFlyingRef = useRef(false);

  const flyToNode = (nodeId: string, graphData) => {
    const node = graphData.nodes.find(n => n.id === nodeId);
    if (!node || !graphRef.current) return;

    graphRef.current.cameraPosition(
      { x: node.x, y: node.y, z: 150 }, // z — высота камеры
      undefined,
      1500 // длительность перелёта
    );
  };

  const handleAnswerClick = async ({
    sessionId,
    questionText,
    chosenAnswer,
    answerNodeId,
    graphData
  }) => {
    if (isFlyingRef.current) return;
    isFlyingRef.current = true;

    flyToNode(answerNodeId, graphData);

    await new Promise(r => setTimeout(r, 1500)); // Ждём окончания перелёта

    const response = await fetch("http://localhost:8000/answer", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        session_id: sessionId,
        question_text: questionText,
        chosen_answer: chosenAnswer
      })
    });

    if (!response.ok) {
      console.error("Ошибка при отправке ответа");
      isFlyingRef.current = false;
      return;
    }

    const newGraph = await fetch(`http://localhost:8000/graph/${sessionId}`).then(r => r.json());
    setGraphData(newGraph);

    isFlyingRef.current = false;
  };

  return { handleAnswerClick };
}
