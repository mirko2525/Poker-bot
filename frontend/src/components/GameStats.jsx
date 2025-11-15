import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';

const GameStats = ({ handState, decision, className = "" }) => {
  if (!handState || !decision) return null;

  const { pot_size, hero_stack, to_call, big_blind, players_in_hand } = handState;
  const { equity, pot_odds } = decision;
  
  const stackInBB = hero_stack / big_blind;
  const potOddsFormatted = pot_odds ? `${pot_odds.toFixed(1)}%` : 'N/A';
  
  return (
    <Card className={`${className} glass-card`}>
      <CardHeader className="pb-3">
        <CardTitle className="font-heading text-xl text-primary flex items-center gap-2">
          <div className="w-3 h-3 bg-primary rounded-full animate-pulse-slow"></div>
          Game Statistics
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Equity Display */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Hand Equity</span>
            <Badge variant="secondary" className="bg-primary/20 text-primary font-mono">
              {equity.toFixed(1)}%
            </Badge>
          </div>
          <Progress value={equity} className="h-3" />
        </div>
        
        {/* Pot Information */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="text-xs text-muted-foreground">Pot Size</div>
            <div className="font-mono text-lg font-semibold text-primary">
              ${pot_size.toFixed(2)}
            </div>
          </div>
          
          <div className="space-y-1">
            <div className="text-xs text-muted-foreground">To Call</div>
            <div className="font-mono text-lg font-semibold text-warning">
              ${to_call.toFixed(2)}
            </div>
          </div>
        </div>
        
        {/* Stack and Blinds */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="text-xs text-muted-foreground">Your Stack</div>
            <div className="font-mono text-sm text-foreground">
              ${hero_stack.toFixed(2)}
              <span className="text-xs text-muted-foreground ml-1">
                ({stackInBB.toFixed(1)} BB)
              </span>
            </div>
          </div>
          
          <div className="space-y-1">
            <div className="text-xs text-muted-foreground">Big Blind</div>
            <div className="font-mono text-sm text-foreground">
              ${big_blind.toFixed(2)}
            </div>
          </div>
        </div>
        
        {/* Pot Odds and Players */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-1">
            <div className="text-xs text-muted-foreground">Pot Odds</div>
            <div className="font-mono text-sm text-accent">
              {potOddsFormatted}
            </div>
          </div>
          
          <div className="space-y-1">
            <div className="text-xs text-muted-foreground">Players</div>
            <div className="font-mono text-sm text-foreground">
              {players_in_hand}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default GameStats;