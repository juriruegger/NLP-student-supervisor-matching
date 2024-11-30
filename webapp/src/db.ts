"use server";

import { auth } from "@clerk/nextjs/server";
import { Suggestions } from "./lib/types";
import { supabase } from "./utils/utils";

export async function setStudent(text: string) {
  const { userId } = await auth();
  if (!userId) {
    throw Error("No user found");
  }
  const { data, error } = await supabase
    .from("student")
    .upsert({ user_id: userId, text: text })
    .select();

  if (error) {
    throw Error("Failed to set student");
  }

  return data;
}

export async function getSuggestions() {
  const { userId } = await auth();
  const { data: suggestions, error } = await supabase
    .from("student_supervisor")
    .select(
      `similarity, 
      contacted, 
      supervisor(
        uuid,
        name,
        email,
        organisational_units, 
        image_url
      )`,
    )
    .eq("student_id", userId);

  if (error) {
    throw Error("No suggestions found");
  }

  return suggestions as unknown as Suggestions; // very hacky
}

export async function getSupervisors() {
  const model = await getModel();
  const { data: embeddings, error } = await supabase
    .from("supervisor")
    .select(`uuid, email, name, embedding_${model}_768`);

  if (error) {
    throw Error("No supervisors found");
  }

  return embeddings;
}

export async function setModel(model: string) {
  const { userId } = await auth();
  if (!userId) {
    throw Error("No user found");
  }
  const { data, error } = await supabase
    .from("student")
    .upsert({ user_id: userId, model: model })
    .select();

  if (error) {
    throw Error("Failed to set model");
  }

  return data;
}

export async function getModel(): Promise<string> {
  const { userId } = await auth();
  const { data: model, error } = await supabase
    .from("student")
    .select("model")
    .eq("user_id", `${userId}`)
    .single();

  if (!model || error) {
    return "scibert";
  }
  return model.model;
}

export async function setContacted(supervisorId: string) {
  const { userId } = await auth();

  const { data, error } = await supabase.from("student_supervisor").upsert({
    student_id: userId,
    supervisor_id: supervisorId,
    contacted: true,
  });

  if (error) {
    throw Error("Failed to set contacted", error);
  }

  return data;
}

export async function setStudentSupervisor(
  supervisorId: string,
  similarity: number,
) {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("No user found");
  }
  const { data, error } = await supabase
    .from("student_supervisor")
    .upsert({
      student_id: userId,
      supervisor_id: supervisorId,
      similarity: similarity,
    })
    .select();

  if (error) {
    throw Error("Failed to set similarity score");
  }

  return data;
}

export async function deleteStudentSupervisors() {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("No user found");
  }

  const { data, error } = await supabase
    .from("student_supervisor")
    .delete()
    .eq("student_id", userId)
    .select();

  if (error) {
    throw Error("Failed to delete supervisors");
  }

  return { data };
}

export async function getUserId() {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("No user found");
  }
  return userId;
}
