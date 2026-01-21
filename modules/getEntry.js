import { prisma } from "./prisma.js";
import { verifyAccessToken } from "./jwt.js";

export async function getEntry({ token, entryId }) {
  const payload = verifyAccessToken(token);
  const userId = payload.sub;

  const entry = await prisma.diary_entries.findFirst({
    where: { 
      id: entryId,
      user_id: userId
    }
  });

  if (!entry) {
    throw new Error("ENTRY_NOT_FOUND");
  }

  return {
    id: entry.id,
    title: entry.title,
    content: entry.content,
    imageUrl: entry.image_url,
    createdAt: entry.created_at,
    updatedAt: entry.updated_at
  };
}

