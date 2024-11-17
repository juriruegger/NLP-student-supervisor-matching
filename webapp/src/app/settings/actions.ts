import { setModel } from "@/db";

export async function storeModel(model: string) {
  await setModel(model);
}
