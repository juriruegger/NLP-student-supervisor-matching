'use server';

import { getSupervisors, getText, } from "@/db";

export async function getSuggestions(email: string) {
  const text = await getText(email);
  const supervisors = await getSupervisors();

  if (!text) {
    return Error("No text found");
  }
  
  const res = await fetch('http://127.0.0.1:5000/api', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text, supervisors }),
  });

  if (!res.ok) {
    return Error("Fething suggestions failed");
  }

  const suggestions = await res.json();
  
  return suggestions;
}
