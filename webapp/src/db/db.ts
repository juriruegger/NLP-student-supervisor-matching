import { Redis } from "@upstash/redis";

const kv = Redis.fromEnv();

export async function setText(email: string, text: string) {
  await kv.set(email, text);
}

export async function getText(email: string): Promise<string | null> {
  const result = await kv.get(email);
  return result as string | null;
}
