import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";

interface GreetingsProps {
  onStart: (captainName: string) => void;
}

export default function GreetingsScreen({ onStart }: GreetingsProps) {
  const [name, setName] = useState("");

  const handleStart = () => {
    if (name.trim().length > 0) {
      onStart(name.trim());
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-black via-gray-900 to-black text-white p-4">
      <Card className="max-w-md w-full bg-gray-800 border border-gray-700 shadow-xl rounded-2xl p-6">
        <CardContent>
          <h1 className="text-2xl font-bold mb-4 text-center">Привет, Капитан!</h1>
          <p className="mb-6 text-sm text-gray-300 text-center">
            Введи имя, чтобы начать своё межгалактическое путешествие
          </p>
          <Input
            placeholder="Captain's Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="mb-4"
          />
          <Button
            className="w-full hover:bg-indigo-700"
            onClick={handleStart}
            disabled={!name.trim()}
          >
            Начать Миссию
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
