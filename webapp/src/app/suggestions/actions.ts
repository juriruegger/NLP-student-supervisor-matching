"use server";

import { getSuggestions, setContacted } from "@/db";
import { fetchImage } from "@/utils/fetcher";

export async function getUserSuggestions() {
  const suggestions = await getSuggestions();

  const sortedSuggestions = suggestions.sort(
    (a, b) => b.similarity - a.similarity,
  );

  const suggestionsWithImage = await Promise.all(
    // we are fetching the supervisor images from Pure.
    sortedSuggestions.map(async (suggestion) => {
      if (suggestion.supervisor.image_url) {
        suggestion.supervisor.image_url = await fetchImage(
          suggestion.supervisor.image_url,
        );
      }
      return suggestion;
    }),
  );

  return suggestionsWithImage;
}

export async function contactSupervisor(supervisor: string) {
  await setContacted(supervisor);
}
