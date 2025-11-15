import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

const ActionDecision = ({ decision, className = "" }) => {
  if (!decision) return null;

  const { action, raise_amount, reason, equity } = decision;
  
  const getActionStyle = () => {
    switch (action) {
      case 'FOLD':
        return {
          bg: 'action-fold',
          text: 'destructive-foreground',
          border: 'border-destructive',
          icon: '❌'
        };
      case 'CALL':
        return {
          bg: 'action-call', 
          text: 'warning-foreground',
          border: 'border-warning',
          icon: '📞'
        };
      case 'RAISE':
        return {
          bg: 'action-raise',
          text: 'success-foreground', 
          border: 'border-success',
          icon: '🚀'
        };
      default:
        return {
          bg: 'bg-secondary',
          text: 'secondary-foreground',
          border: 'border-secondary',
          icon: '❓'
        };
    }
  };
  
  const actionStyle = getActionStyle();
  
  return (
    <Card className={`${className} glass-card border-2 ${actionStyle.border} shadow-glow`}>
      <CardHeader className="pb-3">
        <CardTitle className="font-heading text-xl flex items-center justify-between">
          <span className="flex items-center gap-3">
            <span className="text-2xl">{actionStyle.icon}</span>
            <span className="text-primary">Bot Recommendation</span>
          </span>
          <Badge variant="secondary" className="bg-primary/20 text-primary">
            {equity.toFixed(1)}% equity
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Main Action Button */}
        <div className="text-center">
          <Button 
            className={`${actionStyle.bg} text-3xl font-bold py-6 px-8 w-full text-${actionStyle.text} transition-spring hover:scale-105`}
            size="lg"
          >
            {action}
            {action === 'RAISE' && raise_amount > 0 && (
              <span className="ml-3 text-xl">
                ${raise_amount.toFixed(2)}
              </span>
            )}
          </Button>
        </div>
        
        {/* Raise Amount Details */}
        {action === 'RAISE' && raise_amount > 0 && (
          <div className="bg-success/10 border border-success/30 rounded-lg p-3">
            <div className="text-sm text-success-foreground">
              <div className="font-medium mb-1">Suggested Raise Amount:</div>
              <div className="font-mono text-lg font-bold">
                ${raise_amount.toFixed(2)}
              </div>
            </div>
          </div>
        )}
        
        {/* Reasoning */}
        {reason && (
          <div className="bg-muted/50 border border-border rounded-lg p-3">
            <div className="text-xs text-muted-foreground mb-1 font-medium uppercase tracking-wide">
              Analysis
            </div>
            <div className="text-sm text-foreground leading-relaxed">
              {reason}
            </div>
          </div>
        )}
        
        {/* Action Summary */}
        <div className="flex justify-between items-center text-xs text-muted-foreground pt-2 border-t border-border">
          <span>Confidence: High</span>
          <span>Based on equity vs pot odds</span>
        </div>
      </CardContent>
    </Card>
  );
};

export default ActionDecision;