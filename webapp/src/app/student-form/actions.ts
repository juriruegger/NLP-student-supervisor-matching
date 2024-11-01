import { setStudent } from "@/db";

export async function storeStudent(name: string, email: string, text: string) {
  await setStudent(name, email, text);
}
