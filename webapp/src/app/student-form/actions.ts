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

/**
 * Stores supervisor suggestions for a student based on provided project details.
 *
 * This function performs the following steps:
 * 1. Deletes any existing supervisor suggestions for the user.
 * 2. Sends a POST request to the backend with the student's project text, topics, and project type.
 * 3. Parses the returned suggestions and associates each suggested supervisor with the student.
 */
export async function storeSuggestions({
  text,
  topics,
  projectType,
}: textSuggestionType) {
  const userId = await getUserId();

  await deleteStudentSupervisors(userId);

  const URL = process.env.BACKEND_URL;
  if (!URL) {
    throw new Error("BACKEND_URL is not defined");
  }

  const res = await fetch(URL, {
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
  await setStudent(userId);

  for (const suggestion of suggestions) {
    await setStudentSupervisor({
      userId: userId,
      supervisorId: suggestion.supervisor,
      similarity: suggestion.similarity,
      topPaper: suggestion.top_paper?.uuid,
    });
  }
}

/**
 * Retrieves the list of topics from the database.
 */
export async function getTopics() {
  const topics = await getDbTopics();
  const sortedTopics = topics.sort((a, b) => a.label.localeCompare(b.label));
  return sortedTopics;
}
