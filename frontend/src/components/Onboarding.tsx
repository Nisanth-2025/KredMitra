import React, { useState } from 'react';
import { UserData } from '../types';

interface OnboardingProps {
  onComplete: (data: UserData) => void;
}

const Onboarding: React.FC<OnboardingProps> = ({ onComplete }) => {
  const [formData, setFormData] = useState<Partial<UserData>>({
    name: 'Ramesh Kumar',
    phone: '9876543210',
    aadhaar: '123412341234',
    profession: 'Small Farmer',
    location: 'Nalegaon, Maharashtra',
    pincode: '413521',
    incomeType: 'Seasonal/Irregular',
    financialStatement: 'I am a small farmer with 5 acres of land. I grow sugarcane and my income is seasonal, mostly after the harvest in October. I need a small loan for seeds and fertilizer for the next cycle.',
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Basic validation
    if (Object.values(formData).some(value => typeof value === 'string' && !value.trim())) {
        alert("Please fill out all fields.");
        return;
    }
    onComplete(formData as UserData);
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md border border-slate-200">
      <h2 className="text-2xl font-bold mb-4 text-slate-800">Start Your Application</h2>
      <p className="text-slate-600 mb-6">Fill in your details to begin the analysis process. (Demo data pre-filled)</p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-slate-700">Full Name</label>
          <input type="text" name="name" id="name" value={formData.name} onChange={handleChange} className="mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-teal-500 focus:border-teal-500" required />
        </div>
         <div>
          <label htmlFor="phone" className="block text-sm font-medium text-slate-700">Phone Number</label>
          <input type="text" name="phone" id="phone" value={formData.phone} onChange={handleChange} className="mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-teal-500 focus:border-teal-500" required />
        </div>
        <div>
          <label htmlFor="financialStatement" className="block text-sm font-medium text-slate-700">Tell us about your financial situation</label>
          <textarea name="financialStatement" id="financialStatement" value={formData.financialStatement} rows={4} onChange={handleChange} className="mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-teal-500 focus:border-teal-500" required />
        </div>
        <button type="submit" className="w-full bg-teal-600 text-white font-bold py-3 px-4 rounded-lg hover:bg-teal-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-teal-500">
          Submit for Analysis
        </button>
      </form>
    </div>
  );
};

export default Onboarding;
