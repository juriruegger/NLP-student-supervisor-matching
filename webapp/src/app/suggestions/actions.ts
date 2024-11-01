"use server";

import { getText } from "@/db";

export async function logText(email: string) {
  const text = await getText(email);
  if (!text) {
    return;
  }
  return text;
}
