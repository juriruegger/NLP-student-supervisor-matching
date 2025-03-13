"use server";

import {
  deleteStudentSupervisors,
  getDbTopics,
  getUserId,
  setStudent,
  setStudentSupervisor,
} from "@/db";
import { Topic } from "@/lib/types";
export async function storeTextSuggestions({
  text,
  projectType,
}: {
  text: string;
  projectType?: string;
}) {
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

export async function storeTopicSuggestions({
  topics,
  projectType,
}: {
  topics: Topic[];
  projectType?: string;
}) {
  console.log("topic stuff not done yet")
}

export async function getTopics() {
  const topics = await getDbTopics();
  return topics;
}
