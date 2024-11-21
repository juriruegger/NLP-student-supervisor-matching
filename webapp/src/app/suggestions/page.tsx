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
  if (!userId) {
    throw Error("No user found");
  }

  return <Matches suggestions={suggestions} user={userId} />;
}
