// src/modules/auth/password.js
import bcrypt from "bcrypt";

export const hashPassword = (password) =>
  bcrypt.hash(password, 12);
