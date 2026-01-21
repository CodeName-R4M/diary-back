import 'dotenv/config';
import jwt from "jsonwebtoken";

const JWT_SECRET = process.env.JWT_SECRET;
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || "7d";

if (!JWT_SECRET) {
  throw new Error("JWT_SECRET is not defined");
}

export function createAccessToken({ userId }) {
  return jwt.sign(
    {
      sub: userId,
      typ: "access"
    },
    JWT_SECRET,
    { expiresIn: JWT_EXPIRES_IN }
  );
}

export function signJwt({ userId }) {
  return createAccessToken({ userId });
}

/**
 * Verify and decode JWT
 */
export function verifyAccessToken(token) {
  return jwt.verify(token, JWT_SECRET);
}

/**
 * Extract Bearer token from header
 */
export function extractTokenFromHeader(req) {
  const header = req.headers.authorization;
  if (!header) return null;

  const [type, token] = header.split(" ");
  if (type !== "Bearer" || !token) return null;

  return token;
}
