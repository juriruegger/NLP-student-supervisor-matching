"use server";

import Matches from "./matches";
import { getUserSuggestions } from "./actions";

export default async function Page() {
  const suggestions = await getUserSuggestions();
  if (!suggestions) {
    throw Error("No suggestions found");
  }

  return <Matches suggestions={suggestions} />;
}
