// This file defines the core data structures used throughout the frontend application.
// It ensures type safety and consistency when passing data between components and services.

export interface UserData {
  name: string;
  phone: string;
  aadhaar: string;
  profession: string;
  location: string;
  pincode: string;
  incomeType: string;
  financialStatement: string;
  // This would contain base64 encoded image data for uploads
  financialStatementImage?: {
    mimeType: string;
    data: string;
  };
}

export interface ScoreData {
  finalScore: number;
  scoreRationale: string;
  fraudRisk: 'Low' | 'Medium' | 'High';
  fraudRationale: string;
}

export interface LoanOption {
  name: string;
  amount: number;
  repayment: string;
  description: string;
}
