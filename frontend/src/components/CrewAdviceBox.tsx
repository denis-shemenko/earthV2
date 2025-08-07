interface CrewMember {
    id: string;
    name: string;
    specialty: string;
}

interface CrewAdviceBoxProps {
    crew: CrewMember[];
    question: string;
}

const mockAdvice = (member: CrewMember, question: string): string => {
    const base = `${member.name} (${member.specialty}) says:`;
    const comment =
        member.specialty.includes("Физика") ? "Hmm... I'd say it's Mars." :
            member.specialty.includes("История") ? "I recall something about ancient Martian studies..." :
                member.specialty.includes("Технологии") ? "Sensor analysis suggests Mars is likely." :
                    "Not sure, Captain, but my gut says Mars.";

    return `${base} ${comment}`;
};

export default function CrewAdviceBox({ crew, question }: CrewAdviceBoxProps) {
    return (
        <div className="absolute top-0 right-0 mt-8 bg-gray-800 border border-indigo-600 rounded-xl p-4 space-y-3">
            <h4 className="text-white text-sm mb-2 font-semibold">👨‍🚀 Crew Suggestions:</h4>
            <ul className="space-y-2 text-sm text-yellow-600">
                {crew.map((member) => (
                    <li key={member.id} className="bg-gray-900 p-3 rounded-lg border border-gray-700">
                        {mockAdvice(member, question)}
                    </li>
                ))}
            </ul>
        </div>
    );
}
