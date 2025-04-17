"use server";

import {
  deleteStudentSupervisors,
  getUserId,
  setStudent,
  setStudentSupervisor,
} from "@/db";

export async function storeSuggestions(text: string, projectType?: string) {
  const userId = await getUserId();

  await deleteStudentSupervisors(userId);
  
  const res = await fetch("http://127.0.0.1:5000/api", {
    cache: "no-store",
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text, projectType }),
  });

  if (!res.ok) {
    throw Error("Fetching suggestions failed");
  }

  const suggestions = await res.json();
  const topSuggestions = suggestions.slice(0, 5);
  await setStudent(userId, text);

  for (const suggestion of topSuggestions) {
    await setStudentSupervisor(
      userId,
      suggestion.supervisor,
      suggestion.similarity,
      suggestion.top_paper,
    );
  }
}
