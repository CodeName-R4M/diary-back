import { prisma } from "./prisma.js";
import { verifyAccessToken } from "./jwt.js";
import { UTApi } from "uploadthing/server";

const utapi = new UTApi({ token: "sk_live_1d25d4b93e531005b1dbc586d103583f6c4288991ac20e8e84cf9350bee7dab2" });

export async function deleteEntry({ token, entryId }) {
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

  if (entry.image_url) {
    try {
      const fileKey = entry.image_url.split('/').pop();
      await utapi.deleteFiles(fileKey);
    } catch (error) {
      console.error("Failed to delete image from uploadthing:", error);
    }
  }

  await prisma.diary_entries.delete({
    where: { id: entryId }
  });

  return { message: "Entry deleted successfully" };
}

