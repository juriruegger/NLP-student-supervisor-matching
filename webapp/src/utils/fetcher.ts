import fetch from "node-fetch";

/**
 * Fetches an image from a URL and converts it to a base64 data URL.
 * Uses PURE API key for authentication when fetching supervisor profile images.
 */
export async function fetchImage(imageUrl: string): Promise<string> {
  try {
    const response = await fetch(imageUrl, {
      headers: {
        "api-key": process.env.PURE_API || "",
      },
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch image. Status: ${response.status}`);
    }

    const imageBuffer = await response.arrayBuffer();
    const base64Image = Buffer.from(imageBuffer).toString("base64");
    return `data:image/jpeg;base64,${base64Image}`;
  } catch (error) {
    throw error;
  }
}
