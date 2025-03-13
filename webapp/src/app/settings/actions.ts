import { getDBAvailability, storeDBAvailability } from "@/db";

export async function storeAvailability(available: boolean) {
  await storeDBAvailability(available);
}

export async function getAvailability() {
  const availability = await getDBAvailability();
  return availability;
}
