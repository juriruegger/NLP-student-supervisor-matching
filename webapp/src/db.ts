"use server";

import { auth } from "@clerk/nextjs/server";
import { supabase } from "./utils/utils";
import { KeyWords, OrganisationalUnit, OrganisationalUnits, Suggestions, TopPaper } from "./lib/types";

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

export async function getSuggestions(): Promise<Suggestions> {
  const { userId } = await auth();
  const { data: suggestions, error } = await supabase
    .from("student_supervisor")
    .select(
      `similarity, 
      contacted, 
      supervisor_id,
      top_paper
      `,
    )
    .eq("student_id", userId);

  if (error) {
    throw Error("No suggestions found", error);
  }

  const supervisors: Suggestions = [];
  for (const suggestion of suggestions) {
    const researcher = await getPerson(suggestion.supervisor_id);
    const name = researcher.name?.firstName + " " + researcher.name?.lastName;
    const imageUrl = researcher.profilePhotos?.[0]?.url ?? "";

    const organisationSet = new Set<OrganisationalUnit>();
    const associations = researcher.staffOrganizationAssociations || [];
    for (const association of associations) {
      const organisationUUID = association.organization?.uuid;
      if (!organisationUUID) continue;

      const organisation = await getOrganisation(organisationUUID);
      organisationSet.add({
        name: organisation.name.en_GB,
        url: organisation.portalUrl,
      });
    }
    const organisations: OrganisationalUnits = Array.from(organisationSet); // There are dublicates for some researchers

    const keyWordGroups = researcher.keywordGroups;

    const keywordsSet = new Set<string>();

    if (keyWordGroups) {
      for (const group of keyWordGroups) {
        for (const keywordObj of group.keywords) {
          for (const keyword of keywordObj.freeKeywords) {
            keywordsSet.add(keyword);
          }
        }
      }
    }

    const keywords: KeyWords = Array.from(keywordsSet);

    let email = "";
    for (const association of associations) {
      const emails = association.emails;
      if (!emails) continue;
      if (emails.length > 0) {
        email = emails[0].value;
        break;
      }
    }

    supervisors.push({
      similarity: suggestion.similarity,
      contacted: suggestion.contacted,
      name: name,
      email: email,
      imageUrl: imageUrl,
      organisationalUnits: organisations,
      uuid: researcher.uuid,
      topPaper: suggestion.top_paper,
      keywords: keywords,
    });
  }

  return supervisors;
}

async function getPerson(uuid: string) {
  const API_KEY = process.env.PURE_API;
  const BASE_URL = process.env.PURE_BASE_URL;

  if (!API_KEY || !BASE_URL) {
    throw new Error(
      "Environment variables PURE_API and PURE_BASE_URL must be set",
    );
  }

  const response = await fetch(`${BASE_URL}/persons/${uuid}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      "api-key": API_KEY,
    },
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const person = await response.json();
  return person;
}

async function getOrganisation(uuid: string) {
  const API_KEY = process.env.PURE_API;
  const BASE_URL = process.env.PURE_BASE_URL;

  if (!API_KEY || !BASE_URL) {
    throw new Error(
      "Environment variables PURE_API and PURE_BASE_URL must be set",
    );
  }

  const response = await fetch(`${BASE_URL}/organizations/${uuid}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      "api-key": API_KEY,
    },
  });

  const organisation = await response.json();
  return organisation;
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
  topPaper: TopPaper,
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
      top_paper: topPaper,
    })
    .select();

  if (error) {
    throw Error("Failed to student-supervisor relationship");
  }

  return data;
}

export async function deleteStudentSupervisors(userId: string) {
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
