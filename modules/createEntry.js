import crypto from "crypto";
import { prisma } from "./prisma.js";
import { verifyAccessToken } from "./jwt.js";
import { UTApi } from "uploadthing/server";
import { Blob } from "buffer";
import 'dotenv/config';

const utapi = new UTApi();

export async function createEntry({ token, title, content, imageFile }) {
  console.log("[createEntry] Starting - user token received", {
    hasToken: !!token,
    titleProvided: !!title,
    contentLength: content?.length || 0,
    hasImage: !!imageFile,
  });

  let userId;
  try {
    const payload = verifyAccessToken(token);
    userId = payload.sub;
    console.log("[createEntry] Token verified successfully", { userId });
  } catch (err) {
    console.error("[createEntry] Token verification failed", {
      error: err.message,
      stack: err.stack?.split("\n")[0],
    });
    throw new Error("Invalid or expired token");
  }

  let imageUrl = null;

  if (imageFile) {
    console.log("[createEntry] Processing image upload", {
      fileName: imageFile.originalname || imageFile.name || "(missing name)",
      fileSize: imageFile.size,
      fileType: imageFile.mimetype || imageFile.type || "(missing type)",
    });

    // Handle multer file object (from frontend FormData)
    const fileBuffer = imageFile.buffer;
    const fileName = imageFile.originalname || imageFile.name;
    const mimeType = imageFile.mimetype || imageFile.type;

    if (!mimeType?.startsWith("image/")) {
      console.error("[createEntry] Invalid file type", { type: mimeType });
      throw new Error("Only image files are allowed");
    }

    if (imageFile.size > 4 * 1024 * 1024) {
      console.error("[createEntry] File too large", { size: imageFile.size });
      throw new Error("File too large (max 4MB)");
    }

    try {
      console.log("[createEntry] Starting UploadThing upload...");
      const startTime = Date.now();

      // Create a proper Blob from the buffer
      const blob = new Blob([fileBuffer], { type: mimeType });
      
      // Create a File from the Blob with proper metadata
      const fileForUpload = new File([blob], fileName, {
        type: mimeType,
        lastModified: Date.now(),
      });

      console.log("[createEntry] Prepared file for upload", {
        name: fileForUpload.name,
        size: fileForUpload.size,
        type: fileForUpload.type,
        constructor: fileForUpload.constructor.name,
      });

      // Upload the file - single file returns object, not array
      const uploadResult = await utapi.uploadFiles(fileForUpload);

      const duration = Date.now() - startTime;

      // Log raw result for debugging
      console.log("[createEntry] UploadThing raw response:", {
        durationMs: duration,
        isArray: Array.isArray(uploadResult),
        raw: JSON.stringify(uploadResult, null, 2),
      });

      // Handle single file response (object) vs array response
      let result;
      if (Array.isArray(uploadResult)) {
        if (uploadResult.length === 0) {
          throw new Error("UploadThing returned empty array");
        }
        result = uploadResult[0];
      } else {
        // Single file upload returns object directly
        result = uploadResult;
      }

      if (result.error) {
        console.error("[createEntry] UploadThing reported error", {
          code: result.error.code,
          message: result.error.message,
          data: result.error.data,
        });
        throw new Error(`Upload failed: ${result.error.message || result.error.code || "Unknown error"}`);
      }

      if (!result.data?.url) {
        console.error("[createEntry] Upload OK but missing URL", { result });
        throw new Error("Upload succeeded but no file URL was returned");
      }

      imageUrl = result.data.url;
      console.log("[createEntry] Image uploaded successfully", {
        url: imageUrl,
        key: result.data.key,
        name: result.data.name,
        size: result.data.size,
        durationMs: duration,
      });
    } catch (uploadErr) {
      console.error("[createEntry] Upload exception", {
        message: uploadErr.message,
        stack: uploadErr.stack,
        name: uploadErr.name,
      });
      throw uploadErr;
    }
  } else {
    console.log("[createEntry] No image provided - skipping upload");
  }

  try {
    console.log("[createEntry] Creating diary entry in Prisma", {
      userId,
      title: title ?? null,
      contentPreview: content?.substring(0, 100) + (content?.length > 100 ? "..." : ""),
      hasImageUrl: !!imageUrl,
    });

    const entry = await prisma.diary_entries.create({
      data: {
        id: crypto.randomUUID(),
        user_id: userId,
        title: title ?? null,
        content,
        image_url: imageUrl,
        created_at: new Date(),     // explicit (safe even if schema has @default(now()))
        updated_at: new Date(),
      },
    });

    console.log("[createEntry] Entry created successfully", { entryId: entry.id });

    const response = {
      id: entry.id,
      title: entry.title,
      content: entry.content,
      imageUrl: entry.image_url,
      createdAt: entry.created_at,
      updatedAt: entry.updated_at,
    };

    console.log("[createEntry] Returning response", response);
    return response;
  } catch (prismaErr) {
    console.error("[createEntry] Prisma create failed", {
      message: prismaErr.message,
      code: prismaErr.code,
      meta: prismaErr.meta,
    });
    throw prismaErr;
  }
}