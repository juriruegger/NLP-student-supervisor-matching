"use server";

import {
  deleteStudentSupervisors,
  getModel,
  getSupervisors,
  setStudent,
  setStudentSupervisor,
} from "@/db";
import { auth } from "@clerk/nextjs/server";

export async function storeSuggestions(text: string) {
  const { userId } = await auth();
  if (!userId) {
    throw Error("No user found");
  }

  await deleteStudentSupervisors();

  const supervisors = await getSupervisors();
  const model = await getModel();

  const res = await fetch("http://127.0.0.1:5000/api", {
    cache: "no-store",
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text, supervisors, model }),
  });

  if (!res.ok) {
    throw Error("Fething suggestions failed");
  }

  const suggestions = await res.json();
  const topSuggestions = await suggestions.slice(0, 5);

  await setStudent(text);

  for (const suggestion of topSuggestions) {
    await setStudentSupervisor(suggestion.supervisor, suggestion.similarity);
  }
}
