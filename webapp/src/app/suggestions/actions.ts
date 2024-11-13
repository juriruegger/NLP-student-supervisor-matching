"use server";

import { getSupervisors, getText } from "@/db";

export async function getSuggestions(email: string) {
  const text = await getText(email);
  const supervisors = await getSupervisors();

  if (!text) {
    throw Error("No text found");
  }

  if (!supervisors) {
    throw Error("No supervisors found");
  }

  const res = await fetch("http://127.0.0.1:5000/api", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    cache: "no-store",
    body: JSON.stringify({ text, supervisors }),
  });

  if (!res.ok || res === null || res === undefined) {
    throw Error("Fething suggestions failed");
  }

  const suggestions = await res.json();

  return suggestions;
}
