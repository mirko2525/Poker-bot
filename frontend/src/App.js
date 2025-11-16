import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import HandDisplay from './components/HandDisplay';
import GameStats from './components/GameStats';
import ActionDecision from './components/ActionDecision';
import { toast } from 'sonner';
import { Toaster } from './components/ui/sonner';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const PokerBotDemo = () => {
  const [currentHand, setCurrentHand] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [demoStarted, setDemoStarted] = useState(false);
  const [handNumber, setHandNumber] = useState(0);
  const [hasNext, setHasNext] = useState(true);

  const startDemo = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API}/poker/demo/start`);
      toast.success(response.data.message);
      setDemoStarted(true);
      setHandNumber(0);
      setCurrentHand(null);
      setHasNext(true);
    } catch (error) {
      console.error('Error starting demo:', error);
      toast.error('Failed to start demo');
    } finally {
      setIsLoading(false);
    }
  };

  const getNextHand = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API}/poker/demo/next`);
      const { hand_number, hand_state, decision, has_next } = response.data;
      
      setCurrentHand({ hand_state, decision });
      setHandNumber(hand_number);
      setHasNext(has_next);
      
      toast.success(`Hand ${hand_number} analyzed: ${decision.action}`);
    } catch (error) {
      console.error('Error getting next hand:', error);
      if (error.response?.status === 404) {
        toast.info('Demo completed - no more hands available');
        setHasNext(false);
      } else {
        toast.error('Failed to get next hand');
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-start demo on component mount
  useEffect(() => {
    const initDemo = async () => {
      try {
        const response = await axios.get(`${API}/`);
        console.log('API Ready:', response.data.message);
      } catch (error) {
        console.error('API connection error:', error);
        toast.error('Failed to connect to poker bot API');
      }
    };
    
    initDemo();
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-heading text-4xl font-bold text-gradient">
                🃏 Poker Bot Demo
              </h1>
              <p className="text-muted-foreground mt-2">
                DEMO 1: Mock Workflow V1 - Console Logic with Web Interface
              </p>
            </div>
            <div className="flex items-center gap-4">
              {demoStarted && (
                <Badge variant="secondary" className="px-3 py-1">
                  Hand {handNumber} of 8
                </Badge>
              )}
              <Button 
                onClick={demoStarted ? getNextHand : startDemo}
                disabled={isLoading || (!hasNext && demoStarted)}
                className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-6"
              >
                {isLoading ? (
                  <div className="flex items-center gap-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-background border-t-transparent"></div>
                    Processing...
                  </div>
                ) : !demoStarted ? (
                  'Start Demo'
                ) : hasNext ? (
                  'Next Hand'
                ) : (
                  'Demo Complete'
                )}
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        {!demoStarted ? (
          /* Welcome Screen */
          <div className="max-w-4xl mx-auto text-center">
            <Card className="glass-card p-8 poker-table">
              <CardHeader>
                <CardTitle className="font-heading text-3xl text-primary mb-4">
                  ===================================<br/>
                  DEMO BOT POKER – MOCK WORKFLOW V1<br/>
                  ===================================
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="text-lg text-muted-foreground max-w-2xl mx-auto leading-relaxed">
                  This demo simulates the complete logical workflow of our Texas Hold'em poker analysis bot. 
                  It uses <strong>mock data only</strong> (no screenshots, OCR, or computer vision) to demonstrate 
                  the four core modules working together.
                </div>
                
                <div className="grid md:grid-cols-2 gap-6 mt-8">
                  <Card className="glass-card p-4">
                    <h3 className="font-heading font-semibold text-primary mb-3">🎯 Demo Features</h3>
                    <ul className="text-sm space-y-2 text-left">
                      <li>• Mock State Provider (predefined hands)</li>
                      <li>• Equity Engine (simulated calculations)</li>
                      <li>• Decision Engine (FOLD/CALL/RAISE logic)</li>
                      <li>• Real-time hand analysis</li>
                    </ul>
                  </Card>
                  
                  <Card className="glass-card p-4">
                    <h3 className="font-heading font-semibold text-primary mb-3">📊 What You'll See</h3>
                    <ul className="text-sm space-y-2 text-left">
                      <li>• 6 different poker scenarios</li>
                      <li>• Equity calculations (10-95%)</li>
                      <li>• Action recommendations with reasoning</li>
                      <li>• Pot odds vs equity analysis</li>
                    </ul>
                  </Card>
                </div>
                
                <div className="pt-6">
                  <Button 
                    onClick={startDemo}
                    disabled={isLoading}
                    size="lg"
                    className="bg-primary hover:bg-primary/90 text-primary-foreground font-bold text-xl px-8 py-4 animate-glow"
                  >
                    🚀 Start Poker Bot Demo
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        ) : (
          /* Demo Interface */
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Left Column - Hand Display */}
            <div className="lg:col-span-2">
              <HandDisplay 
                handState={currentHand?.hand_state} 
                className="mb-6"
              />
              
              {/* Action Decision */}
              {currentHand?.decision && (
                <ActionDecision 
                  decision={currentHand.decision}
                  className="mb-6"
                />
              )}
              
              {/* Next Hand Button */}
              <div className="text-center">
                {hasNext ? (
                  <Button 
                    onClick={getNextHand}
                    disabled={isLoading}
                    size="lg"
                    className="bg-primary hover:bg-primary/90 text-primary-foreground font-bold px-8 py-4"
                  >
                    {isLoading ? 'Analyzing...' : 'Next Hand →'}
                  </Button>
                ) : (
                  <Card className="glass-card p-6">
                    <CardContent className="p-0 text-center">
                      <h3 className="font-heading text-xl font-bold text-primary mb-2">
                        🎉 Demo Complete!
                      </h3>
                      <p className="text-muted-foreground mb-4">
                        Fine DEMO 1 – Nessun'altra mano disponibile.
                      </p>
                      <Button 
                        onClick={startDemo}
                        className="bg-primary hover:bg-primary/90 text-primary-foreground"
                      >
                        Restart Demo
                      </Button>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
            
            {/* Right Column - Stats */}
            <div>
              {currentHand && (
                <GameStats 
                  handState={currentHand.hand_state}
                  decision={currentHand.decision}
                  className="mb-6"
                />
              )}
              
              {/* Module Status */}
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="font-heading text-lg text-primary">
                    🔧 Module Status
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Mock State Provider</span>
                    <Badge variant="secondary" className="bg-success/20 text-success">Active</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Equity Engine</span>
                    <Badge variant="secondary" className="bg-success/20 text-success">Running</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Decision Engine</span>
                    <Badge variant="secondary" className="bg-success/20 text-success">Online</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">UI Demo</span>
                    <Badge variant="secondary" className="bg-success/20 text-success">Connected</Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </div>
      
      <Toaster position="top-right" richColors />
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<PokerBotDemo />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;