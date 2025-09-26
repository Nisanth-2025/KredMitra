import React, { useState } from 'react';
import Onboarding from './components/Onboarding';
import ScoreResult from './components/ScoreResult';
import { UserData, ScoreData, LoanOption } from './types';
import { submitApplication } from './services/api';

type AppState = 'ONBOARDING' | 'PROCESSING' | 'SCORE_RESULT' | 'ERROR';

function App() {
  const [appState, setAppState] = useState<AppState>('ONBOARDING');
  const [scoreData, setScoreData] = useState<ScoreData | null>(null);
  const [loanOptions, setLoanOptions] = useState<LoanOption[]>([]);

  const handleOnboardingComplete = async (data: UserData) => {
    setAppState('PROCESSING');
    try {
      const result = await submitApplication(data);
      setScoreData(result.scoreData);
      setLoanOptions(result.loanOptions);
      setAppState('SCORE_RESULT');
    } catch (error) {
      console.error("Failed to process application:", error);
      setAppState('ERROR');
    }
  };
  
  const renderContent = () => {
    switch (appState) {
      case 'ONBOARDING':
        return <Onboarding onComplete={handleOnboardingComplete} />;
      case 'PROCESSING':
        return (
          <div className="text-center p-8 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-4">Processing Your Application...</h2>
            <p className="text-slate-600">Our AI agents are analyzing your data. This may take a moment.</p>
          </div>
        );
      case 'SCORE_RESULT':
        if (scoreData && loanOptions.length > 0) {
          return <ScoreResult scoreData={scoreData} loanOptions={loanOptions} />;
        }
        return <div className="text-center p-8">Error: Score data is missing.</div>;
       case 'ERROR':
         return (
           <div className="text-center p-8 bg-red-50 rounded-lg shadow-md">
             <h2 className="text-2xl font-bold mb-4 text-red-700">An Error Occurred</h2>
             <p className="text-red-600">We were unable to process your application. Please try again later.</p>
           </div>
         );
      default:
        return <Onboarding onComplete={handleOnboardingComplete} />;
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800">
      <header className="bg-white/80 backdrop-blur-lg border-b border-slate-200/80 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-slate-800 tracking-tight">
            KredMitra
          </h1>
        </div>
      </header>
      <main className="max-w-4xl mx-auto p-4 sm:p-6 lg:p-8">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
