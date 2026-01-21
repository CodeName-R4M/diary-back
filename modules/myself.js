import { prisma } from "./prisma.js";
import { verifyAccessToken } from "./jwt.js";

export async function myself({ token }) {
  const payload = verifyAccessToken(token);
  const existing = await prisma.users.findUnique({
    where: { id: payload.sub }
  });
    if (!existing) {
    throw new Error("USER_NOT_FOUND");
  }
  return {
      id: existing.id,
      email: existing.email,
      displayName: existing.displayName
  };
}
