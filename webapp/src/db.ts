"use server";

import { auth, currentUser } from "@clerk/nextjs/server";
import { supabase } from "./utils/utils";
import {
  KeyWords,
  Organisation,
  OrganisationalUnit,
  OrganisationalUnits,
  StaffOrganizationAssociation,
  Suggestions,
  Topic,
  TopPaper,
} from "./lib/types";

/**
 * Creates or updates a student record in the database.
 */
export async function setStudent(userId: string) {
  const { data, error } = await supabase
    .from("student")
    .upsert({ user_id: userId })
    .select();

  if (error) {
    throw Error("Failed to set student");
  }

  return data;
}

/**
 * Retrieves and processes supervisor suggestions for a given student.
 * Fetches supervisor details from PURE API and maps them to suggestion format.
 */
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
    let topPaper;
    if (suggestion.top_paper) {
      topPaper = await getPaper(suggestion.top_paper);
    }
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
      topPaper: topPaper,
      keywords: keywords,
    };
  });

  const supervisors = await Promise.all(supervisorsPromises);
  return supervisors;
}

/**
 * Fetches person details from the PURE.
 */
async function getPerson(uuid: string) {
  const { API_KEY, BASE_URL } = await getPure();

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

/**
 * Retrieves research paper details from PURE by the UUID of the research output.
 */
async function getPaper(uuid: string) {
  const { API_KEY, BASE_URL } = await getPure();

  const response = await fetch(`${BASE_URL}/research-outputs/${uuid}`, {
    method: "GET",
    headers: {
      Accept: "application/json",
      "api-key": API_KEY,
    },
  });
  if (!response.ok) {
    throw new Error(`Fetching error for getPaper: ${response.status}`);
  }

  const paper = await response.json();
  const title = paper.title.value;
  const url = paper.portalUrl;

  const paperToReturn: TopPaper = {
    title: title,
    url: url,
  };
  return paperToReturn;
}

/**
 * Fetches organization details from PURE by UUID.
 */
async function getOrganisation(uuid: string) {
  const { API_KEY, BASE_URL } = await getPure();

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

/**
 * Marks a supervisor as contacted by a specific student.
 * Updates the student-supervisor relationship in the database.
 */
export async function setContacted(userId: string, supervisorId: string) {
  const { data: contacted, error } = await supabase
    .from("student_supervisor")
    .upsert({
      student_id: userId,
      supervisor_id: supervisorId,
      contacted: true,
    });

  if (error) {
    throw Error("Failed to set contacted", error);
  }

  return contacted;
}

type setStudentSupervisorType = {
  userId: string;
  supervisorId: string;
  similarity: number;
  topPaper?: string;
};

/**
 * Creates or updates a student-supervisor relationship with similarity score.
 */
export async function setStudentSupervisor({
  userId,
  supervisorId,
  similarity,
  topPaper,
}: setStudentSupervisorType) {
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

/**
 * Removes all supervisor suggestions for a specific student.
 * Used when generating new suggestions to clear old ones.
 */
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

/**
 * Retrieves the current authenticated user's ID from Clerk.
 */
export async function getUserId() {
  const { userId } = await auth();
  if (!userId) {
    throw new Error("No user found");
  }
  return userId;
}

/**
 * Fetches all available topics from the database.
 * Maps database field names to TypeScript property names.
 */
export async function getDbTopics() {
  const { data: topics, error } = await supabase.from("topic").select("*");

  if (error) {
    throw Error("Failed to get topics");
  }

  const mappedTopics = topics.map((topic) => ({
    ...topic,
    topicId: topic.topic_id,
  }));

  return mappedTopics as Topic[];
}

/**
 * Retrieves the availability status for the current supervisor.
 */
export async function getDBAvailability() {
  const email = await getEmail();

  const { data, error } = await supabase
    .from("supervisor")
    .select("available")
    .eq("email", email)
    .single();

  if (error) {
    console.error("Failed to get availability", error);
  }

  return data?.available;
}

/**
 * Updates or creates a supervisor's availability status in the database.
 */
export async function storeDBAvailability(available: boolean) {
  const email = await getEmail();
  const { data, error } = await supabase
    .from("supervisor")
    .upsert({ available: available })
    .eq("email", email)
    .select();

  if (error) {
    throw Error("Failed to set available");
  }

  return data;
}

/**
 * Gets the email address of the currently authenticated user (used to authorize Supervisor availability).
 */
export async function getEmail() {
  const user = await currentUser();
  return user?.emailAddresses[0].emailAddress;
}

/**
 * Retrieves PURE API credentials from environment variables.
 */
async function getPure() {
  const API_KEY = process.env.PURE_API;
  const BASE_URL = process.env.PURE_BASE_URL;

  if (!API_KEY || !BASE_URL) {
    throw new Error(
      "Environment variables PURE_API and PURE_BASE_URL must be set",
    );
  }

  return { API_KEY, BASE_URL };
}
