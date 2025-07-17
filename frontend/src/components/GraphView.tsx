import { useEffect, useState, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import type { GraphNode, GraphLink, KnowledgeGraph, QuestionOption } from "../types";
import { fetchStart, getGraphBySession, postFirstQuestion } from "../api";

//const SESSION_ID = "d5657a67-943f-41f4-8a73-202c03ac93c4"; // потом возьмем из глобального состояния или storage

export default function GraphView() {
    const [stars, setStars] = useState<number[]>([]);
    const [graphData, setGraphData] = useState<KnowledgeGraph | null>(null);
    const [sessionId, setSessionId] = useState<string>("");
    const fgRef = useRef<any>(null);

    const handleNodeClick = (node: GraphNode) => {
        // Стартовая тема
        if (node.type === "answer" && node.topic) {
            const topic = node.label;
            postFirstQuestion(sessionId, topic).then(({ question, options }) => {
                // Генерируем ноды и связи вручную:
                const qNode: GraphNode = {
                    id: `q_${Date.now()}`,
                    label: question,
                    type: "question",
                    question: question,
                    selected: false
                };

                const answerNodes: GraphNode[] = (options as any[]).map((a, index) => ({
                    id: `a_${Date.now()}_${index}`,
                    label: a.text || a, // Handle both QuestionOption and string
                    type: "answer",
                    question: "",
                    selected: false
                }));

                const links: GraphLink[] = [
                    ...answerNodes.map((a) => ({ source: qNode.id, target: a.id, label: "HAS_OPTION" })),
                    { source: node.id, target: qNode.id, label: "NEXT" }
                ];

                setGraphData(prev => prev ? ({
                    nodes: [...prev.nodes, qNode, ...answerNodes],
                    links: [...prev.links, ...links]
                }) : null);
            });

            return;
        } else if (node.type === "answer") {
            fetch("http://localhost:8000/answer", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: sessionId,
                    chosen_answer: node.label, // или node.id, если так храним
                    question_text: node.question,
                })
            })
                .then((res) => res.json())
                .then(() => {
                    // перезагрузить граф
                    getGraphBySession(sessionId).then(setGraphData);
                });
        }
    };

    // 1. Set stars count and start session on mount
    useEffect(() => {
        const starCount = Math.floor(Math.random() * 70) + 30;
        setStars(Array.from({ length: starCount }, (_, i) => i));

        fetchStart().then(({session_id}) => setSessionId(session_id));
    }, []);

    // 2. Fetch graph when sessionId is available
    useEffect(() => {
        if (sessionId) {
            console.log("Fetching graph for sessionId:", sessionId);
            getGraphBySession(sessionId).then(data => {
                console.log("Graph data received:", data);
                setGraphData(data);
            }).catch(error => {
                console.error("Error fetching graph:", error);
            });
        }
    }, [sessionId]);

    // 3. Manipulate DOM after stars are rendered
    useEffect(() => {
        if (stars.length === 0) return;
        const starsEls = document.querySelectorAll('.star');
        starsEls.forEach(star => {
            const el = star as HTMLElement;
            const top = Math.random() * 97 + 2;
            const left = Math.random() * 97 + 2;
            const duration = 1.5 + Math.random() * 2;
            el.style.top = `${top}%`;
            el.style.left = `${left}%`;
            el.style.animationDuration = `${duration}s`;
        });
    }, [stars]);

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
        if (link.label === "SELECTED") return "#38A169"; // ярко-зелёный
        if (link.label === "NEXT") return "#4299E1";     // синий
        return "#A0AEC0";                                // серый
    };

    const linkWidth = (link: GraphLink) => (link.label === "SELECTED" ? 3 : 1.5);

    console.log("Current graphData:", graphData);

    return (
        <div className="relative h-screen w-full bg-black overflow-hidden">
            {stars.map(i => (
                <div key={i} className="star absolute"></div>
            ))}
            <div className="absolute inset-0 z-10">
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
                        //linkAutoColorBy="type"
                        linkWidth={linkWidth}
                        linkColor={linkColor}
                        onNodeClick={handleNodeClick}
                    />
                )}
            </div>
        </div>
    );
}
