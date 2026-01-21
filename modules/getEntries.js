import { prisma } from "./prisma.js";
import { verifyAccessToken } from "./jwt.js";

export async function getEntries({ token }) {
  const payload = verifyAccessToken(token);
  const userId = payload.sub;

  const entries = await prisma.diary_entries.findMany({
    where: { user_id: userId },
    orderBy: { created_at: 'desc' }
  });

  return entries.map(entry => ({
    id: entry.id,
    title: entry.title,
    content: entry.content,
    imageUrl: entry.image_url,
    createdAt: entry.created_at,
    updatedAt: entry.updated_at
  }));
}

