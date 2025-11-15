import React from 'react';
import PokerCard from './PokerCard';
import { Card, CardContent } from './ui/card';

const HandDisplay = ({ handState, className = "" }) => {
  if (!handState) return null;

  const { hero_cards, board_cards, phase } = handState;

  return (
    <div className={`${className} space-y-6`}>
      {/* Hero Cards */}
      <Card className="glass-card p-4">
        <CardContent className="p-0">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-heading text-lg font-semibold text-primary">Your Hand</h3>
            <div className="px-3 py-1 bg-primary/20 border border-primary/30 rounded-full">
              <span className="text-xs font-medium text-primary">{phase}</span>
            </div>
          </div>
          <div className="flex gap-3 justify-center">
            {hero_cards?.map((card, index) => (
              <PokerCard 
                key={index} 
                card={card} 
                size="lg"
                className="animate-glow"
              />
            )) || (
              <>  
                <PokerCard card="?" size="lg" />
                <PokerCard card="?" size="lg" />
              </>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Community Cards */}
      <Card className="glass-card p-4">
        <CardContent className="p-0">
          <h3 className="font-heading text-lg font-semibold text-foreground mb-4">Community Cards</h3>
          <div className="flex gap-2 justify-center flex-wrap">
            {/* Flop */}
            {Array.from({ length: 3 }).map((_, index) => (
              <PokerCard 
                key={`flop-${index}`}
                card={board_cards?.[index] || "?"} 
                size="md"
                className={board_cards?.[index] ? "" : "opacity-50"}
              />
            ))}
            
            {/* Turn */}
            <div className="w-2" /> {/* Spacer */}
            <PokerCard 
              card={board_cards?.[3] || "?"} 
              size="md"
              className={board_cards?.[3] ? "" : "opacity-50"}
            />
            
            {/* River */}
            <div className="w-2" /> {/* Spacer */}
            <PokerCard 
              card={board_cards?.[4] || "?"} 
              size="md"
              className={board_cards?.[4] ? "" : "opacity-50"}
            />
          </div>
          
          {/* Phase labels */}
          <div className="flex justify-center mt-3 gap-8 text-xs text-muted-foreground">
            <span className={board_cards?.length >= 3 ? "text-primary font-medium" : ""}>FLOP</span>
            <span className={board_cards?.length >= 4 ? "text-primary font-medium" : ""}>TURN</span>
            <span className={board_cards?.length >= 5 ? "text-primary font-medium" : ""}>RIVER</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default HandDisplay;