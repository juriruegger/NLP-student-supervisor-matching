import { setModel, getUserId } from "@/db";

export async function storeModel(model: string) {
  const userId = await getUserId();
  await setModel(model, userId);
}
