import React from 'react';
import { ScoreData, LoanOption } from '../types';

interface ScoreResultProps {
  scoreData: ScoreData;
  loanOptions: LoanOption[];
}

const ScoreResult: React.FC<ScoreResultProps> = ({ scoreData, loanOptions }) => {
  return (
    <div className="bg-white p-8 rounded-lg shadow-md border border-slate-200">
      <h2 className="text-2xl font-bold text-center mb-4 text-slate-800">Your Financial Report</h2>
      
      <div className="text-center my-8">
        <div className="text-6xl font-bold text-teal-600">{scoreData.finalScore}</div>
        <p className="text-slate-600 mt-2">{scoreData.scoreRationale}</p>
      </div>

      <div className="my-6 p-4 bg-slate-50 rounded-lg">
         <h3 className="text-lg font-semibold text-slate-700">Fraud Risk Assessment</h3>
         <p><span className="font-bold">{scoreData.fraudRisk}:</span> {scoreData.fraudRationale}</p>
      </div>
      
       <div className="my-6">
         <h3 className="text-xl font-bold text-slate-800 mb-4">Recommended Loan Options</h3>
         <div className="space-y-4">
            {loanOptions.map((loan, index) => (
                <div key={index} className="border border-slate-200 rounded-lg p-4 hover:shadow-lg transition-shadow">
                    <h4 className="font-bold text-teal-700">{loan.name}</h4>
                    <p className="text-slate-700 font-semibold">Amount: ₹{loan.amount.toLocaleString('en-IN')}</p>
                    <p className="text-slate-600">Repayment: {loan.repayment}</p>
                    <p className="text-slate-500 text-sm mt-1">{loan.description}</p>
                </div>
            ))}
         </div>
      </div>
    </div>
  );
};

export default ScoreResult;
