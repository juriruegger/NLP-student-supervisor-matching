"use server";

import { getSuggestions, setContacted } from "@/db";
import { Suggestions } from "@/lib/types";
import { fetchImage } from "@/utils/fetcher";

export async function getUserSuggestions(): Promise<Suggestions> {
  const suggestions = await getSuggestions();

  const sortedSuggestions = suggestions.sort(
    (a, b) => b.similarity - a.similarity,
  );

  const suggestionsWithImage = await Promise.all(
    // we are fetching the supervisor images from Pure.
    sortedSuggestions.map(async (suggestion) => {
      if (suggestion.imageUrl) {
        suggestion.imageUrl = await fetchImage(suggestion.imageUrl);
      }
      return suggestion;
    }),
  );

  return suggestionsWithImage;
}

export async function contactSupervisor(supervisor: string) {
  await setContacted(supervisor);
}
