"use server";

import { auth } from "@clerk/nextjs/server";
import { supabase } from "./utils/utils";
import {
  KeyWords,
  Organisation,
  OrganisationalUnit,
  OrganisationalUnits,
  StaffOrganizationAssociation,
  Suggestions,
  TopPaper,
} from "./lib/types";

export async function setStudent(userId: string, text: string) {
  const { data, error } = await supabase
    .from("student")
    .upsert({ user_id: userId, text: text })
    .select();

  if (error) {
    throw Error("Failed to set student");
  }

  return data;
}

export async function getSuggestions(userId: string): Promise<Suggestions> {
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
    throw Error("No suggestions found (db)", error);
  }

  const supervisorsPromises = suggestions.map(async (suggestion) => {
    const researcher = await getPerson(suggestion.supervisor_id);
    const name = researcher.name?.firstName + " " + researcher.name?.lastName;
    const firstName = researcher.name?.firstName;
    const imageUrl = researcher.profilePhotos?.[0]?.url ?? "";

    const associations = researcher.staffOrganizationAssociations || [];
    const orgUUIDs = associations
      .map((assoc: StaffOrganizationAssociation) => assoc.organization?.uuid)
      .filter((uuid: string | undefined): uuid is string => !!uuid);

    const organisationsPromises = orgUUIDs.map((uuid: string) =>
      getOrganisation(uuid),
    );
    const organisationsData = await Promise.all(organisationsPromises);

    const organisationSet = new Set<OrganisationalUnit>();
    organisationsData.forEach((org: Organisation) => {
      if (org.name.en_GB) {
        organisationSet.add({
          name: org.name.en_GB,
          url: org.portalUrl,
        });
      }
    });
    const organisations: OrganisationalUnits = Array.from(organisationSet);

    const keyWordGroups = researcher.keywordGroups;
    const keywordsSet = new Set<string>();
    if (keyWordGroups) {
      for (const group of keyWordGroups) {
        for (const keywordObj of group.keywords) {
          for (const keyword of keywordObj.freeKeywords) {
            let newKeyword = "";
            const words = keyword.split(" ");
            for (const word of words) {
              newKeyword += word.charAt(0).toUpperCase() + word.slice(1);
              if (word !== words[words.length - 1]) {
                newKeyword += " ";
              }
            }
            keywordsSet.add(newKeyword);
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

    return {
      similarity: suggestion.similarity,
      contacted: suggestion.contacted,
      name: name,
      firstName: firstName,
      email: email,
      imageUrl: imageUrl,
      organisationalUnits: organisations,
      uuid: researcher.uuid,
      topPaper: suggestion.top_paper,
      keywords: keywords,
    };
  });

  const supervisors = await Promise.all(supervisorsPromises);
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

export async function setModel(model: string, userId: string) {
  const { data, error } = await supabase
    .from("student")
    .upsert({ user_id: userId, model: model })
    .select();

  if (error) {
    throw Error("Failed to set model");
  }

  return data;
}

export async function getModel(userId: string): Promise<string> {
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

export async function setContacted(userId: string, supervisorId: string) {
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
  userId: string,
  supervisorId: string,
  similarity: number,
  topPaper: TopPaper,
) {
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
