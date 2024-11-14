"use server";

import { getSuggestions } from "@/db";

export async function getUserSuggestions() {
  const suggestions = getSuggestions();

  return suggestions;
}
