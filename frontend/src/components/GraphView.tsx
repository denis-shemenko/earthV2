import { useEffect, useState, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import type { GraphNode, GraphLink, KnowledgeGraph } from "../types";
import { getGraphBySession } from "../api";

const SESSION_ID = "2eb46e83-b95c-4971-b2a3-34823e1a8cc3"; // потом возьмем из глобального состояния или storage

export default function GraphView() {
  const [graphData, setGraphData] = useState<KnowledgeGraph | null>(null);
  const fgRef = useRef<any>(null);

  const handleNodeClick = (node: GraphNode) => {
    if (node.type === "answer") {
      fetch("http://localhost:8000/answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: SESSION_ID,
          chosen_answer: node.label // или node.id, если так храним
        })
      })
        .then((res) => res.json())
        .then(() => {
          // перезагрузить граф
          getGraphBySession(SESSION_ID).then(setGraphData);
        });
    }
  };

  useEffect(() => {
    getGraphBySession(SESSION_ID).then(setGraphData);
  }, []);

  const nodeColor = (node: GraphNode) => {
    if (node.type === "home") return "#00BFFF";
    if (node.type === "answer") return "#48BB78"; // зелёные планеты
    if (node.isCurrent) return "#FFA500";
    return "#6C63FF";
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
          linkAutoColorBy="type"
          onNodeClick={handleNodeClick}
        />
      )}
    </div>
  );
}
