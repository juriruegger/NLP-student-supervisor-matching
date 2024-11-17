"use server";

import { getModel, getSupervisors, setStudent } from "@/db";
import { auth } from "@clerk/nextjs/server";

export async function storeSuggestions(text: string) {
  const { userId } = await auth();
  if (!userId) {
    throw Error("No user found");
  }
  const supervisors = await getSupervisors();

  const dbmodel = await getModel();
  const bertModel = await modelSwitch(dbmodel);

  const res = await fetch("http://127.0.0.1:5000/api", {
    cache: "no-store",
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ text, supervisors, bertModel }),
  });

  if (!res.ok) {
    throw Error("Fething suggestions failed");
  }

  const suggestions = await res.json();

  const topThree = await suggestions
    .slice(0, 3)
    .map((suggestion: { supervisor: string }) => suggestion.supervisor);

  await setStudent(text, topThree);
}

const modelSwitch = async (model: string) => {
  switch (model) {
    case "bert":
      return "bert-base-uncased";
    case "scibert":
      return "allenai/scibert_scivocab_uncased";
    default:
      throw new Error("Unknown model");
  }
};
