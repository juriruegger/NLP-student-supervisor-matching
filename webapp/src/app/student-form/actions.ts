import { setText } from "@/db/db";

export async function storeStudent(email: string, text: string){
    await setText(email, text);
}