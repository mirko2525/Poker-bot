import React from 'react';
import { Card } from './ui/card';

const PokerCard = ({ card, className = "", size = "md" }) => {
  if (!card || card === "?") {
    return (
      <Card className={`${className} relative flex items-center justify-center bg-gradient-to-br from-blue-900 to-blue-800 border-2 border-blue-600/50 ${
        size === "sm" ? "w-12 h-16" : size === "lg" ? "w-20 h-28" : "w-16 h-22"
      }`}>
        <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent rounded-lg" />
        <div className="text-blue-200 text-lg font-bold opacity-60">?</div>
      </Card>
    );
  }

  const rank = card[0];
  const suit = card[1];
  
  const suitSymbols = {
    'h': '♥',
    'd': '♦', 
    'c': '♣',
    's': '♠'
  };
  
  const suitColors = {
    'h': 'text-red-500',
    'd': 'text-red-500',
    'c': 'text-gray-900',
    's': 'text-gray-900'
  };
  
  const displayRank = rank === 'T' ? '10' : rank;
  
  return (
    <Card className={`${className} relative flex flex-col items-center justify-center bg-white border-2 border-gray-300 shadow-elegant transition-transform hover:scale-105 ${
      size === "sm" ? "w-12 h-16 text-xs" : size === "lg" ? "w-20 h-28 text-xl" : "w-16 h-22 text-base"
    }`}>
      {/* Card corner rank/suit */}
      <div className="absolute top-1 left-1 flex flex-col items-center">
        <span className={`font-bold ${suitColors[suit]} ${
          size === "sm" ? "text-xs" : size === "lg" ? "text-lg" : "text-sm"
        }`}>
          {displayRank}
        </span>
        <span className={`${suitColors[suit]} card-suit ${
          size === "sm" ? "text-xs" : size === "lg" ? "text-lg" : "text-sm"
        }`}>
          {suitSymbols[suit]}
        </span>
      </div>
      
      {/* Center suit symbol */}
      <div className={`${suitColors[suit]} card-suit ${
        size === "sm" ? "text-lg" : size === "lg" ? "text-4xl" : "text-2xl"
      }`}>
        {suitSymbols[suit]}
      </div>
      
      {/* Card corner rank/suit (bottom right, rotated) */}
      <div className="absolute bottom-1 right-1 flex flex-col items-center transform rotate-180">
        <span className={`font-bold ${suitColors[suit]} ${
          size === "sm" ? "text-xs" : size === "lg" ? "text-lg" : "text-sm"
        }`}>
          {displayRank}
        </span>
        <span className={`${suitColors[suit]} card-suit ${
          size === "sm" ? "text-xs" : size === "lg" ? "text-lg" : "text-sm"
        }`}>
          {suitSymbols[suit]}
        </span>
      </div>
    </Card>
  );
};

export default PokerCard;