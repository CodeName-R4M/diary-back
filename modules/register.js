
import crypto from "crypto";
import { prisma } from "./prisma.js";
import { hashPassword } from "./password.js";
import { signJwt } from "./jwt.js";

export async function registerUser({ email, password, displayName }) {
  const existing = await prisma.users.findUnique({
    where: { email }
  });

  if (existing) {
    throw new Error("EMAIL_EXISTS");
  }

  const password_hash = await hashPassword(password);

  const user = await prisma.users.create({
    data: {
      id: crypto.randomUUID(),
      email,
      password_hash,
      displayName
    }
  });

  const token = signJwt({ userId: user.id });

  return {
    token,
    user: {
      id: user.id,
      email: user.email,
      displayName: user.displayName
    }
  };
}
