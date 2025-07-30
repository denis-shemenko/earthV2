import type { CrewMember } from "@/types";

interface MissionOverviewPanelProps {
  captain: string;
  crew: CrewMember[];
}

export default function MissionOverviewPanel({ captain, crew }: MissionOverviewPanelProps) {
  return (
    <div className="bg-gray-800 text-white rounded-xl p-4 shadow-md border border-gray-700 w-full sm:max-w-xs">
      <h2 className="text-lg font-semibold mb-2">🪐 Обзор миссии</h2>
      <p className="text-sm mb-1">
        <span className="text-gray-400">Капитан:</span> {captain}
      </p>
      <div className="mt-2">
        <p className="text-sm text-gray-400 mb-1">Экипаж:</p>
        <ul className="space-y-1">
          {crew.map((member) => (
            <li key={member.id} className="text-sm">
              👩‍🚀 {member.name} — <span className="text-indigo-400">{member.specialty}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
