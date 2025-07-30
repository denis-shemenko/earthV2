import { useState } from "react";
import GreetingsScreen from "./components/GreetingsScreen";
import CrewSelectionScreen from "@/components/CrewSelectionScreen";
import MissionSelectionScreen from "@/components/MissionSelectionScreen";
import type { CrewMember } from "@/types";

export default function App() {
  const [captainName, setCaptainName] = useState<string | null>(null);
  const [crew, setCrew] = useState<CrewMember[] | null>(null);
  const [missionTopic, setMissionTopic] = useState<string | null>(null);

  const handleStart = (name: string) => {
    setCaptainName(name);
  };

  return (
    <>
      {!captainName ? (
        <GreetingsScreen onStart={handleStart} />
      ) : !crew ? (
        <CrewSelectionScreen onCrewSelected={setCrew} />
      ) : !missionTopic ? (
        <MissionSelectionScreen onMissionSelected={setMissionTopic} captain={captainName} crew={crew} />
      ) : (
        <div>{/* Step 4 - Arrival at Planet (Trivia Question) */}</div>
      )}
    </>
  );
}