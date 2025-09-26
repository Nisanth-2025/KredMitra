import { UserData, ScoreData, LoanOption } from '../types';

// The base URL for the backend orchestrator API.
// This would be an environment variable in a real application.
const API_BASE_URL = 'http://localhost:8080/api'; // Dummy URL for local Flask dev

/**
 * Submits the user's application data to the backend orchestrator.
 * In a real app, this would make an HTTP POST request.
 * @param userData The collected user data from the onboarding form.
 * @returns A promise that resolves to the analysis result from the backend.
 */
export const submitApplication = async (userData: UserData): Promise<{ scoreData: ScoreData, loanOptions: LoanOption[] }> => {
  console.log('Submitting application to backend:', userData);

  // In a real application, you would use fetch or axios.
  // This simulates the call to the Flask Orchestrator API.
  try {
    const response = await fetch(`${API_BASE_URL}/application`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Network response was not ok');
    }
    return response.json();
  } catch (error) {
     console.error("API call failed:", error);
     // For demo purposes, if the local backend isn't running, return a dummy response.
     console.log("Falling back to dummy data because the backend is not available.");
     return getDummyResponse();
  }
};

/**
 * Provides a dummy response for frontend development when the backend is not running.
 */
const getDummyResponse = (): Promise<{ scoreData: ScoreData, loanOptions: LoanOption[] }> => {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        scoreData: {
          finalScore: 680,
          scoreRationale: 'DUMMY DATA: Stable income patterns observed, with moderate community trust signals.',
          fraudRisk: 'Low',
          fraudRationale: 'DUMMY DATA: No anomalies detected in provided data.',
        },
        loanOptions: [
          {
            name: 'Harvest Cycle Loan (Dummy)',
            amount: 15000,
            repayment: 'After harvest season in October',
            description: 'A flexible loan to cover costs until your crops are sold.',
          },
          {
            name: 'Gig Worker Float (Dummy)',
            amount: 5000,
            repayment: 'Small weekly payments of ₹500',
            description: 'A small loan to manage cash flow between gigs.',
          },
        ],
      });
    }, 1500); // 1.5-second delay
  });
}
