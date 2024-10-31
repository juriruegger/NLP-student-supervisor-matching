import { getText } from "@/db/db";

export async function getSuggestions(email: string) {
    const studentText = await getText(email);

    /* if (!studentText) {
        return;
    }

    const embed = await pipeline('feature-extraction', 'bert-base-uncased');

    const embeddings = await embed(studentText);

    console.log(embeddings); */
}