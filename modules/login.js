import { prisma } from "./prisma.js";
import { signJwt } from "./jwt.js";
import bcrypt from "bcrypt";

export async function loginUser({ email, password }) {
  const existing = await prisma.users.findUnique({
    where: { email }
  });

  if (!existing) {
    throw new Error("USER_NOT_FOUND");
  }
  const isPasswordValid = await bcrypt.compare(password, existing.password_hash);

  if (!isPasswordValid) {
    throw new Error("INVALID_PASSWORD");
  }

  const token = signJwt({ userId: existing.id });

  return {
    token,
    existing: {
      id: existing.id,
      email: existing.email,
      displayName: existing.displayName
    }
  };
}
