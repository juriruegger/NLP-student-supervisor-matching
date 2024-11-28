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
    .from("new_students")
    .upsert({ userId: userId, text: text })
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
      supervisors(
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
    .from("supervisors")
    .select(`email, name, embedding_${model}_768`);

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
    .from("new_students")
    .upsert({ userId: userId, model: model })
    .select();

  if (error) {
    throw Error("Failed to set model");
  }

  return data;
}

export async function getModel(): Promise<string> {
  const { userId } = await auth();
  const { data: model, error } = await supabase
    .from("new_students")
    .select("model")
    .eq("userId", `${userId}`)
    .single();

  if (error) {
    throw Error("There was an error fetching the model for the student");
  }

  return model.model ?? "bert";
}

export async function setContacted(supervisorName: string) {
  const { userId } = await auth();

  console.log(userId);
  console.log(supervisorName);

  const { data, error } = await supabase
    .from("student_supervisor")
    .upsert({
      student_id: userId,
      supervisor_name: supervisorName,
      contacted: true,
    })
    .select();

  if (error) {
    console.log(error);
    throw Error("Failed to set contacted");
  }

  return data;
}

export async function setStudentSupervisor(
  supervisorName: string,
  supervisorEmail: string,
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
      supervisor_name: supervisorName,
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
  console.log("userId", userId);
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
