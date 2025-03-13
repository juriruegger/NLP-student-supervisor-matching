"use server";

import Matches from "./matches";
import { getUserSuggestions } from "./actions";
import { getUserId } from "@/db";

export default async function Page() {
  const suggestions = await getUserSuggestions();
  if (!suggestions) {
    throw Error("No suggestions found");
  }

  const userId = await getUserId();

  return <Matches suggestions={suggestions} user={userId} />;
}
