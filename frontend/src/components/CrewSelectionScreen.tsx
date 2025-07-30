import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { CrewMember, Trait } from "../types";
import { v4 as uuidv4 } from "uuid";
import { CATEGORIES, TRAITS } from "@/constants";

interface CrewSelectionProps {
  onCrewSelected: (crew: CrewMember[]) => void;
}

function getRandomTraits(): Trait[] {
  return TRAITS.sort(() => 0.5 - Math.random()).slice(0, 2);
}

function getRandomName(): string {
  const firstNames = ["Nova", "Artem", "Lyra", "Kai", "Rhea", "Orion", "Zane", "Mira"];
  const lastNames = ["Storm", "Ray", "Drift", "Quill", "Flint", "Vega", "Chrome", "Dash"];
  return `${firstNames[Math.floor(Math.random() * firstNames.length)]} ${lastNames[Math.floor(Math.random() * lastNames.length)]}`;
}

function generateCrew(): CrewMember[] {
  return Array.from({ length: 8 }).map(() => ({
    id: uuidv4(),
    name: getRandomName(),
    specialty: CATEGORIES[Math.floor(Math.random() * CATEGORIES.length)],
    traits: getRandomTraits(),
  }));
}

export default function CrewSelectionScreen({ onCrewSelected }: CrewSelectionProps) {
  const [crew, setCrew] = useState<CrewMember[]>([]);
  const [selected, setSelected] = useState<string[]>([]);

  useEffect(() => {
    setCrew(generateCrew());
  }, []);

  const toggleSelect = (id: string) => {
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((sid) => sid !== id) : prev.length < 2 ? [...prev, id] : prev
    );
  };

  const handleConfirm = () => {
    const selectedCrew = crew.filter((c) => selected.includes(c.id));
    onCrewSelected(selectedCrew);
  };

  return (
    <div className="min-h-screen bg-black text-white p-6">
      <h1 className="text-2xl mb-4 text-center">Выбери команду (2 персонажа)</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {crew.map((member) => (
          <Card
            key={member.id}
            className={`p-4 cursor-pointer border-2 ${selected.includes(member.id) ? "border-indigo-500" : "border-gray-700"} bg-gray-900 rounded-2xl`}
            onClick={() => toggleSelect(member.id)}
          >
            <h2 className="text-lg font-bold mb-1">{member.name}</h2>
            <p className="text-sm text-gray-400">Специальность: {member.specialty}</p>
            <p className="text-sm text-gray-500">Черты: {member.traits.join(", ")}</p>
          </Card>
        ))}
      </div>
      <div className="mt-6 text-center">
        <Button
          onClick={handleConfirm}
          disabled={selected.length !== 2}
          className="bg-indigo-600 hover:bg-indigo-700"
        >
          Подтвердить выбор
        </Button>
      </div>
    </div>
  );
}
