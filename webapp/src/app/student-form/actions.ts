"use server";

import {
  deleteStudentSupervisors,
  getDbTopics,
  getUserId,
  setStudent,
  setStudentSupervisor,
} from "@/db";
import { ProjectType, Topic } from "@/lib/types";

type textSuggestionType = {
  text?: string;
  topics?: Topic[];
  projectType?: ProjectType;
};

export async function storeSuggestions({
  text,
  topics,
  projectType,
}: textSuggestionType) {
  const userId = await getUserId();

  await deleteStudentSupervisors(userId);

  const res = await fetch("http://127.0.0.1:5000/api", {
    cache: "no-store",
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text, topics, projectType }),
  });

  if (!res.ok) {
    throw Error("Fetching suggestions failed");
  }

  const suggestions = await res.json();
  console.log("Suggestions", suggestions);
  const topSuggestions = suggestions.slice(0, 5);
  if (text) {
    await setStudent(userId, text);
  }

  for (const suggestion of topSuggestions) {
    await setStudentSupervisor({
      userId: userId,
      supervisorId: suggestion.supervisor,
      similarity: suggestion.similarity,
      topPaper: suggestion.top_paper,
    });
  }
}

export async function getTopics() {
  const topics = await getDbTopics();
  return topics;
}
