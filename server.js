import "dotenv/config";
import express from "express";
import cors from "cors";
import multer from "multer";
import serverless from "serverless-http";

import { registerUser } from "./modules/register.js";
import { loginUser } from "./modules/login.js";
import { myself } from "./modules/myself.js";
import { extractTokenFromHeader } from "./modules/jwt.js";
import { createEntry } from "./modules/createEntry.js";
import { getEntries } from "./modules/getEntries.js";
import { getEntry } from "./modules/getEntry.js";
import { deleteEntry } from "./modules/deleteEntry.js";

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

/* ======================================================
   ✅ CORS (MUST COME FIRST)
   Handles OPTIONS automatically (Node 24 safe)
====================================================== */
app.use(
  cors({
    origin: [
      "https://diary-app-mu-azure.vercel.app",
      "http://localhost:5173",
    ],
    methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowedHeaders: ["Content-Type", "Authorization"],
  })
);

/* ======================================================
   BODY PARSERS
====================================================== */
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

/* ======================================================
   HEALTH CHECK
====================================================== */
app.get("/", (req, res) => {
  res.json({ message: "Personal Diary API", status: "running" });
});

/* ======================================================
   AUTH ROUTES
====================================================== */
app.post("/api/auth/register", async (req, res) => {
  try {
    const result = await registerUser(req.body);
    res.json({
      access_token: result.token,
      token_type: "bearer",
    });
  } catch (error) {
    if (error.message === "EMAIL_EXISTS") {
      return res.status(400).json({ detail: "Email already registered" });
    }
    console.error("🔥 REGISTER ERROR:", error);
    res.status(500).json({ detail: "Internal server error" });
  }
});

app.post("/api/auth/login", async (req, res) => {
  try {
    const result = await loginUser(req.body);
    res.json({
      access_token: result.token,
      token_type: "bearer",
    });
  } catch (error) {
    if (
      error.message === "USER_NOT_FOUND" ||
      error.message === "INVALID_PASSWORD"
    ) {
      return res.status(400).json({ detail: "Invalid email or password" });
    }
    console.error("🔥 LOGIN ERROR:", error);
    res.status(500).json({ detail: "Internal server error" });
  }
});

app.get("/api/auth/me", async (req, res) => {
  try {
    const token = extractTokenFromHeader(req);
    if (!token) {
      return res.status(401).json({ detail: "No token provided" });
    }
    const user = await myself({ token });
    res.json(user);
  } catch {
    res.status(401).json({ detail: "Invalid authentication credentials" });
  }
});

/* ======================================================
   DIARY ROUTES
====================================================== */
app.post("/api/diary/entries", upload.single("image"), async (req, res) => {
  try {
    const token = extractTokenFromHeader(req);
    if (!token) {
      return res.status(401).json({ detail: "No token provided" });
    }

    const { title, content } = req.body;
    const imageFile = req.file;

    const entry = await createEntry({
      token,
      title,
      content,
      imageFile,
    });

    res.status(201).json(entry);
  } catch (error) {
    console.error("🔥 CREATE ENTRY ERROR:", error);
    res.status(500).json({ detail: "Internal server error" });
  }
});

app.get("/api/diary/entries", async (req, res) => {
  try {
    const token = extractTokenFromHeader(req);
    if (!token) {
      return res.status(401).json({ detail: "No token provided" });
    }
    const entries = await getEntries({ token });
    res.json(entries);
  } catch {
    res.status(401).json({ detail: "Invalid authentication credentials" });
  }
});

app.get("/api/diary/entries/:id", async (req, res) => {
  try {
    const token = extractTokenFromHeader(req);
    if (!token) {
      return res.status(401).json({ detail: "No token provided" });
    }
    const entry = await getEntry({
      token,
      entryId: req.params.id,
    });
    res.json(entry);
  } catch (error) {
    if (error.message === "ENTRY_NOT_FOUND") {
      return res.status(404).json({ detail: "Entry not found" });
    }
    res.status(401).json({ detail: "Invalid authentication credentials" });
  }
});

app.delete("/api/diary/entries/:id", async (req, res) => {
  try {
    const token = extractTokenFromHeader(req);
    if (!token) {
      return res.status(401).json({ detail: "No token provided" });
    }
    const result = await deleteEntry({
      token,
      entryId: req.params.id,
    });
    res.json(result);
  } catch (error) {
    if (error.message === "ENTRY_NOT_FOUND") {
      return res.status(404).json({ detail: "Entry not found" });
    }
    res.status(500).json({ detail: "Internal server error" });
  }
});

/* ======================================================
   ❗ SERVERLESS EXPORT (NO app.listen)
====================================================== */
export default serverless(app);
