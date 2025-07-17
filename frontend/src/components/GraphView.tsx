import { useEffect, useState, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import type { GraphNode, GraphLink, KnowledgeGraph } from "../types";
import { fetchStart, getGraphBySession, postFirstQuestion } from "../api";

//const SESSION_ID = "d5657a67-943f-41f4-8a73-202c03ac93c4"; // потом возьмем из глобального состояния или storage

type FloatingScore = {
    id: string;         // ID ноды (узла)
    value: number;      // количество очков
    x: number;
    y: number;
};

export default function GraphView() {
    const [stars, setStars] = useState<number[]>([]);
    const [graphData, setGraphData] = useState<KnowledgeGraph | null>(null);
    const [sessionId, setSessionId] = useState<string>("");
    const [score, setScore] = useState(0);
    const [questionStartTime, setQuestionStartTime] = useState<number | null>(null);
    const [elapsedTime, setElapsedTime] = useState<number>(0);
    const [floatingScores, setFloatingScores] = useState<FloatingScore[]>([]);
    const fgRef = useRef<any>(null);

    const handleNodeClick = (node: GraphNode) => {
        const now = Date.now();
        const timeTaken = questionStartTime ? (now - questionStartTime) / 1000 : 0;

        const baseScore = 100;
        const bonus = Math.max(0, 60 - timeTaken * 2); // До 50 бонусных очков за скорость
        setQuestionStartTime(null); // сброс

        // Стартовая тема
        if (node.type === "answer" && node.topic) {
            const topic = node.label;
            postFirstQuestion(sessionId, topic)
                .then(() => {
                    // перезагрузить граф
                    getGraphBySession(sessionId).then(setGraphData);
                    setQuestionStartTime(Date.now());
                });
            return;
        } else if (node.type === "answer") {
            const total = node.correct ? Math.floor(baseScore + bonus) : -baseScore;
            const coords = fgRef.current?.graph2ScreenCoords(node.x, node.y);
            //console.log("Getting node coords: x=" + node.x + " y=" + node.y);
            if (coords) {
                setFloatingScores(prev => [
                    ...prev,
                    {
                        id: node.id,
                        value: total,       // твои рассчитанные очки
                        x: coords.x,
                        y: coords.y
                    }
                ]);
            }

            setScore(prev => prev + total);

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
                    setQuestionStartTime(Date.now());
                });
        }
    };

    // 1. Set stars count and start session on mount
    useEffect(() => {
        const starCount = Math.floor(Math.random() * 70) + 30;
        setStars(Array.from({ length: starCount }, (_, i) => i));

        fetchStart().then(({ session_id }) => setSessionId(session_id));
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

    // 4. Таймер
    useEffect(() => {
        let interval: ReturnType<typeof setInterval>;

        if (questionStartTime !== null) {
            interval = setInterval(() => {
                setElapsedTime(Math.floor((Date.now() - questionStartTime) / 1000));
            }, 500); // можно 1000 для 1 сек
        } else {
            setElapsedTime(0);
        }

        return () => clearInterval(interval);
    }, [questionStartTime]);

    // 5. Анимация Начисления очков
    useEffect(() => {
        if (floatingScores.length > 0) {
            const timer = setTimeout(() => {
                setFloatingScores([]);
            }, 2000);
            return () => clearTimeout(timer);
        }
    }, [floatingScores]);

    const nodeColor = (node: GraphNode) => {
        if (node.type === "question") return "#FFA500";
        if (node.type === "answer") {
            if (node.selected && node.correct === false) return "#F56565"; // Red for incorrect selected
            if (node.selected && node.correct === true) return "#48BB78";  // Green for correct selected
            if (node.selected) return "#48BB78"; // fallback
            return "#CBD5E0";
        }
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

    //console.log("Current graphData:", graphData);

    return (
        <div className="relative h-screen w-full bg-black overflow-hidden">
            {stars.map(i => (
                <div key={i} className="star absolute"></div>
            ))}
            <div className="absolute top-4 left-4 text-white z-50 bg-black/50 px-4 py-2 rounded-lg">
                <div>Очки: {score}</div>
                {questionStartTime && <div>⏱ {elapsedTime} сек.</div>}
            </div>
            <div className="absolute inset-0 z-10">
                {graphData && (
                    <ForceGraph2D
                        ref={fgRef}
                        graphData={graphData}
                        nodeLabel={(node: GraphNode) => nodeLabel(node)} // full text for tooltip
                        nodeAutoColorBy="type"
                        nodeCanvasObject={(node, ctx, globalScale) => {
                            let label = typeof node.label === "string" && node.label.length > 30
                                ? node.label.slice(0, 30) + "…"
                                : node.label;

                            ctx.fillStyle = nodeColor(node as GraphNode);
                            ctx.beginPath();
                            ctx.arc(node.x!, node.y!, nodeSize(node as GraphNode), 0, 2 * Math.PI, false);
                            ctx.fill();

                            ctx.fillStyle = "rgb(204, 204, 255, 0.3)";
                            const fontSize = 14 / globalScale;
                            ctx.font = `${fontSize}px Sans-Serif`;
                            const textWidth = ctx.measureText(label).width;
                            const padding = fontSize * 0.2;
                            const bckgWidth = textWidth + padding;
                            const bckgHeight = fontSize + padding;
                            ctx.fillRect(
                                node.x! - bckgWidth / 2,
                                node.y! - bckgHeight / 2,
                                bckgWidth,
                                bckgHeight
                            );

                            ctx.fillStyle = "rgb(5, 89, 255)";
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'middle';
                            ctx.fillText(label, node.x!, node.y!);
                        }}
                        linkDirectionalArrowLength={4}
                        linkDirectionalArrowRelPos={1}
                        linkWidth={linkWidth}
                        linkColor={linkColor}
                        onNodeClick={handleNodeClick}
                    />
                )}
            </div>
            {floatingScores.map((score, idx) => (
                <div
                    key={idx}
                    className="fixed text-yellow-600 text-xl font-bold animate-float-score pointer-events-none"
                    style={{
                        left: score.x,
                        top: score.y,
                        transform: "translate(-50%, -50%)",
                        zIndex: 1000
                    }}
                >
                    {score.value}
                </div>
            ))}
        </div>
    );
}
