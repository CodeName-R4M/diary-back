import { prisma } from "./prisma.js";
import { verifyAccessToken } from "./jwt.js";
import { UTApi } from "uploadthing/server";
import { Blob } from "buffer";

const utapi = new UTApi();

export async function updateEntry({ token, entryId, title, content, imageFile, deleteImage }) {
  const payload = verifyAccessToken(token);
  const userId = payload.sub;

  const entry = await prisma.diary_entries.findFirst({
    where: { id: entryId, user_id: userId }
  });

  if (!entry) {
    throw new Error("ENTRY_NOT_FOUND");
  }

  let imageUrl = entry.image_url;

  // Handle explicit delete of existing image
  if (deleteImage === true || deleteImage === "true") {
    if (imageUrl) {
      try {
        const fileKey = imageUrl.split('/').pop();
        await utapi.deleteFiles(fileKey);
      } catch (err) {
        console.error("[updateEntry] Failed to delete existing image:", err);
      }
    }
    imageUrl = null;
  }

  // Handle replacement image upload
  if (imageFile) {
    // basic validations
    const mimeType = imageFile.mimetype || imageFile.type;
    if (!mimeType?.startsWith("image/")) {
      throw new Error("Only image files are allowed");
    }
    if (imageFile.size > 4 * 1024 * 1024) {
      throw new Error("File too large (max 4MB)");
    }

    try {
      // Prepare file for upload
      const blob = new Blob([imageFile.buffer], { type: mimeType });
      const fileForUpload = new File([blob], imageFile.originalname || imageFile.name, {
        type: mimeType,
        lastModified: Date.now(),
      });

      const uploadResult = await utapi.uploadFiles(fileForUpload);
      let result;
      if (Array.isArray(uploadResult)) {
        result = uploadResult[0];
      } else {
        result = uploadResult;
      }

      if (result.error) {
        throw new Error(result.error.message || "Upload failed");
      }

      if (!result.data?.url) {
        throw new Error("Upload succeeded but no URL returned");
      }

      // If there was a previous image, try to delete it
      if (entry.image_url) {
        try {
          const oldKey = entry.image_url.split('/').pop();
          await utapi.deleteFiles(oldKey);
        } catch (err) {
          console.warn("[updateEntry] Failed to delete previous image after upload:", err);
        }
      }

      imageUrl = result.data.url;
    } catch (err) {
      console.error("[updateEntry] Image upload failed:", err);
      throw err;
    }
  }

  const updated = await prisma.diary_entries.update({
    where: { id: entryId },
    data: {
      title: title ?? null,
      content: content ?? entry.content,
      image_url: imageUrl,
      updated_at: new Date(),
    }
  });

  return {
    id: updated.id,
    title: updated.title,
    content: updated.content,
    imageUrl: updated.image_url,
    createdAt: updated.created_at,
    updatedAt: updated.updated_at,
  };
}
