import crypto from "crypto";
import { prisma } from "./prisma.js";
import { verifyAccessToken } from "./jwt.js";
import { UTApi } from "uploadthing/server";

const utapi = new UTApi({ token: "sk_live_1d25d4b93e531005b1dbc586d103583f6c4288991ac20e8e84cf9350bee7dab2" });

export async function createEntry({ token, title, content, imageFile }) {
  const payload = verifyAccessToken(token);
  const userId = payload.sub;

  let imageUrl = null;

  if (imageFile) {
    const uploadResult = await utapi.uploadFiles(imageFile);
    if (uploadResult.data) {
      imageUrl = uploadResult.data.url;
    }
  }

  const entry = await prisma.diary_entries.create({
    data: {
      id: crypto.randomUUID(),
      user_id: userId,
      title: title || null,
      content,
      image_url: imageUrl,
      updated_at: new Date()
    }
  });

  return {
    id: entry.id,
    title: entry.title,
    content: entry.content,
    imageUrl: entry.image_url,
    createdAt: entry.created_at,
    updatedAt: entry.updated_at
  };
}

