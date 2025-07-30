import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { CATEGORIES } from "../constants";
import MissionOverviewPanel from "@/components/MissionOverviewPanel";
import type { CrewMember } from "@/types";

interface MissionSelectionProps {
  onMissionSelected: (category: string) => void;
  captain: string;
  crew: CrewMember[];
}

export default function MissionSelectionScreen({ onMissionSelected, captain, crew }: MissionSelectionProps) {
  const [options, setOptions] = useState<string[]>([]);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    const shuffled = [...CATEGORIES].sort(() => 0.5 - Math.random()).slice(0, 4);
    setOptions(shuffled);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-b from-black to-gray-900 text-white p-6">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row gap-6">
        <div className="w-full sm:w-1/3">
          <MissionOverviewPanel captain={captain} crew={crew} />
        </div>
        <div className="w-full sm:w-2/3">
          <h1 className="text-2xl text-center mb-6">Выбери стартовое направление миссии</h1>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            {options.map((cat) => (
              <Card
                key={cat}
                className={`p-6 rounded-2xl cursor-pointer text-center text-lg font-semibold transition-all
                  ${selected === cat ? "border-2 border-indigo-500 bg-gray-800" : "border border-gray-700 bg-gray-900"}`}
                onClick={() => setSelected(cat)}
              >
                🌌 {cat}
              </Card>
            ))}
          </div>
          <div className="text-center mt-8">
            <Button
              disabled={!selected}
              onClick={() => onMissionSelected(selected!)}
              className="bg-indigo-600 hover:bg-indigo-700"
            >
              Начать миссию
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
