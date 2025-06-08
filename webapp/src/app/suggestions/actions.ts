"use server";

import { getSuggestions, getUserId, setContacted } from "@/db";
import { Suggestion, Suggestions } from "@/lib/types";
import { fetchImage } from "@/utils/fetcher";

/**
 * Retrieves supervisor suggestions, processes their images, and sorts them by similarity.
 */
export async function getUserSuggestions(): Promise<Suggestions> {
  const userId = await getUserId();
  const suggestions = await getSuggestions(userId);

  const imageProcessingPromises = suggestions
    .filter((suggestion) => suggestion.imageUrl)
    .map(async (suggestion) => {
      const processedImageUrl = await fetchImage(suggestion.imageUrl);
      return { suggestion, processedImageUrl };
    });

  const processedImages = await Promise.all(imageProcessingPromises);

  processedImages.forEach(
    ({
      suggestion,
      processedImageUrl,
    }: {
      suggestion: Suggestion;
      processedImageUrl: string;
    }) => {
      suggestion.imageUrl = processedImageUrl;
    },
  );

  suggestions.sort((a, b) => b.similarity - a.similarity);

  return suggestions;
}

/**
 * Marks a supervisor as contacted by the current user.
 */
export async function contactSupervisor(supervisor: string) {
  const userId = await getUserId();
  await setContacted(userId, supervisor);
}
