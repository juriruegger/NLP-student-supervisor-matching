"use client";

import { useSearchParams } from "next/navigation";
import Matches from "./matches";
import { getText } from "@/db/db";

export default function SuggestionsPage() {
  const searchParams = useSearchParams();
  const email = searchParams.get("email");

  if (!email || typeof email !== "string") {
    return <div>Missing email</div>;
  }

  const text = getText(email);

  /* getSuggestions(email); */

  <p>email</p>;

  return (
    <div>
      <h1>Suggestions</h1>
      <p>{text}</p>
      {/* <Matches /> */}
    </div>
  );
}
