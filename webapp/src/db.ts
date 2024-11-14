"use server";

import { auth } from "@clerk/nextjs/server";
import { createClient } from "@supabase/supabase-js";

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

if (!supabaseUrl) {
  throw new Error("Missing env.NEXT_PUBLIC_SUPABASE_URL");
}

if (!supabaseKey) {
  throw new Error("Missing env.NEXT_PUBLIC_SUPABASE_ANON_KEY");
}

const supabase = createClient(supabaseUrl, supabaseKey, {
  global: {
    fetch: (url, options = {}) => {
      return fetch(url, { ...options, cache: "no-store" });
    },
  },
});

export async function setStudent(text: string, suggestions: string[]) {
  const { userId } = await auth();
  if (!userId) {
    throw Error("No user found");
  }
  const { data, error } = await supabase
    .from("new_students")
    .upsert({ userId: userId, text: text, suggestions: suggestions })
    .select();

  if (error) {
    throw Error("Failed to set student");
  }

  return data;
}

export async function getSuggestions() {
  const { userId } = await auth();
  const { data: student, error } = await supabase
    .from("new_students")
    .select("suggestions")
    .eq("userId", `${userId}`)
    .single();

  if (error) {
    throw Error("here was an error fetching the suggestions for the student");
  }

  const toReturn = [];

  for (const suggestion of student?.suggestions) {
    const { data: supervisor, error } = await supabase
      .from("supervisors")
      .select("name, email")
      .eq("name", `${suggestion}`)
      .single();

    if (error) {
      throw Error("There was an error fetching the suggestions");
    }
    toReturn.push(supervisor);
  }

  return toReturn;
}

export async function getSupervisors() {
  const { data: embeddings, error } = await supabase
    .from("supervisors")
    .select("email, name, embedding_bert_768");

  if (error) {
    throw Error("No supervisors found");
  }

  if (!embeddings || embeddings.length === 0) {
    console.log("No embeddings found");
  }

  return embeddings;
}
