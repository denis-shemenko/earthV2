// 📁 frontend/components/ShipHud.tsx
import React from 'react';
import '../styles/ship-hud.css';

export interface ShipStatus {
  fuel: number;
  score: number;
  resources: {
    iron: number;
    crystal: number;
    artifact: number;
  };
}

interface Props {
  status: ShipStatus;
}

const ShipHud: React.FC<Props> = ({ status }) => {
  return (
    <div className="ship-hud">
      <div className="ship-score">🚀 Очки: {status.score}</div>
      <div className="ship-fuel">⛽ Топливо: {status.fuel}</div>
      <div className="ship-resources">
        🪨 {status.resources.iron} | 💎 {status.resources.crystal} | 🧬 {status.resources.artifact}
      </div>
    </div>
  );
};

export default ShipHud;
