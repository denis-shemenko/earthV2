import { useEffect, useState, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import type { GraphNode, GraphLink, KnowledgeGraph } from "../types";
import { getGraphBySession } from "../api";

const SESSION_ID = "d5657a67-943f-41f4-8a73-202c03ac93c4"; // потом возьмем из глобального состояния или storage

export default function GraphView() {
  const [graphData, setGraphData] = useState<KnowledgeGraph | null>(null);
  const fgRef = useRef<any>(null);
  const isFlying = useRef(false);

  // 🪂 Анимация перелёта камеры к ответу
  const flyToNode = (nodeId: string) => {
    const node = fgRef.current?.graphData().nodes.find((n: GraphNode) => n.id === nodeId);
    if (node) {
      fgRef.current.cameraPosition(
        { x: node.x, y: node.y, z: 150 },
        undefined,
        1500
      );
    }
  };

  const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

  const handleNodeClick = async (node: GraphNode) => {
    if (isFlying.current || node.type !== "answer") return;
    isFlying.current = true;

    // 🚀 Перелетаем к выбранному ответу
    flyToNode(node.id);
    await delay(1500); // дождаться окончания анимации

    // 📡 Отправляем ответ на сервер
    await fetch("http://localhost:8000/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: SESSION_ID,
        chosen_answer: node.label, // или node.id
        question_text: node.question,
      }),
    });

    // 🔄 Загружаем обновлённый граф
    const updatedGraph = await getGraphBySession(SESSION_ID);
    setGraphData(updatedGraph);

    isFlying.current = false;
  };

  useEffect(() => {
    getGraphBySession(SESSION_ID).then(setGraphData);
  }, []);

  const nodeColor = (node: GraphNode) => {
    if (node.type === "question") return "#FFA500";
    if (node.type === "answer") return node.selected ? "#48BB78" : "#CBD5E0";
    return "#999";
  };

  const nodeSize = (node: GraphNode) => {
    if (node.type === "home") return 12;
    if (node.type === "answer") return 8;
    if (node.isCurrent) return 10;
    return 6;
  };

  const nodeLabel = (node: GraphNode) => {
    if (node.type === "home") return "🌍 Дом";
    return node.label;
  };

  const linkColor = (link: GraphLink) => {
    if (link.label === "SELECTED") return "#38A169";
    if (link.label === "NEXT") return "#4299E1";
    return "#A0AEC0";
  };

  const linkWidth = (link: GraphLink) => (link.label === "SELECTED" ? 3 : 1.5);

  return (
    <div className="h-screen bg-gray-900 text-white">
      <h1 className="text-2xl p-4 font-bold text-center">🧠 EARTH</h1>
      {graphData && (
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeLabel={nodeLabel}
          nodeAutoColorBy="type"
          nodeCanvasObject={(node, ctx, globalScale) => {
            const fontSize = 10 / globalScale;
            ctx.font = `${fontSize}px Sans-Serif`;

            ctx.fillStyle = nodeColor(node as GraphNode);
            ctx.beginPath();
            ctx.arc(node.x!, node.y!, nodeSize(node as GraphNode), 0, 2 * Math.PI, false);
            ctx.fill();

            ctx.fillStyle = "white";
            ctx.fillText(nodeLabel(node as GraphNode), node.x! + 10, node.y! + 4);
          }}
          linkDirectionalArrowLength={4}
          linkDirectionalArrowRelPos={1}
          linkWidth={linkWidth}
          linkColor={linkColor}
          onNodeClick={handleNodeClick}
        />
      )}
    </div>
  );
}
