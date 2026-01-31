import 'dotenv/config';
import express from 'express';

import multer from 'multer';
import { registerUser } from "./modules/register.js";
import { loginUser } from "./modules/login.js";
import { myself } from "./modules/myself.js";
import { extractTokenFromHeader } from "./modules/jwt.js";
import { createEntry } from "./modules/createEntry.js";
import { getEntries } from "./modules/getEntries.js";
import { getEntry } from "./modules/getEntry.js";
import { deleteEntry } from "./modules/deleteEntry.js";

const upload = multer({ storage: multer.memoryStorage() });

const app = express();
const port = process.env.PORT || 8000;

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.get("/", (req, res) => {
  res.json({ message: "Personal Diary API", status: "running" });
});

app.post('/api/auth/register', async (req, res) => {
  try {
    const result = await registerUser(req.body);
    res.json({ access_token: result.token, token_type: "bearer" });
  } catch (error) {
    if (error.message === "EMAIL_EXISTS") {
      return res.status(400).json({ detail: "Email already registered" });
    }
    res.status(500).json({ detail: error.message });
  }
});

app.post('/api/auth/login', async (req, res) => {
  try {
    const result = await loginUser(req.body);
    res.json({ access_token: result.token, token_type: "bearer" });
  } catch (error) {
    if (error.message === "USER_NOT_FOUND" || error.message === "INVALID_PASSWORD") {
      return res.status(400).json({ detail: "Invalid email or password" });
    }
    res.status(500).json({ detail: error.message });
  }
});

app.get('/api/auth/me', async (req, res) => {
  try {
    const token = extractTokenFromHeader(req);
    if (!token) {
      return res.status(401).json({ detail: "No token provided" });
    }
    const user = await myself({ token });
    res.json(user);
  } catch (error) {
    res.status(401).json({ detail: "Invalid authentication credentials" });
  }
});

app.post('/api/diary/entries', upload.single('image'), async (req, res) => {
  try {
    console.log('[server] Received diary entry request', {
      hasToken: !!req.headers.authorization,
      hasTitle: !!req.body.title,
      hasContent: !!req.body.content,
      hasImage: !!req.file,
      imageDetails: req.file ? {
        originalname: req.file.originalname,
        mimetype: req.file.mimetype,
        size: req.file.size,
        hasBuffer: !!req.file.buffer,
      } : null,
    });

    const token = extractTokenFromHeader(req);
    if (!token) {
      return res.status(401).json({ detail: "No token provided" });
    }
    const { title, content } = req.body;
    const imageFile = req.file;

    console.log('[server] Calling createEntry with:', {
      hasToken: !!token,
      title: title || '(none)',
      contentLength: content?.length || 0,
      hasImageFile: !!imageFile,
    });

    const entry = await createEntry({ token, title, content, imageFile });
    res.status(201).json(entry);
  } catch (error) {
    console.error('[server] Error creating diary entry:', {
      message: error.message,
      stack: error.stack,
      name: error.name,
    });
    res.status(500).json({ detail: error.message });
  }
});

app.get('/api/diary/entries', async (req, res) => {
  try {
    const token = extractTokenFromHeader(req);
    if (!token) {
      return res.status(401).json({ detail: "No token provided" });
    }
    const entries = await getEntries({ token });
    res.json(entries);
  } catch (error) {
    res.status(401).json({ detail: "Invalid authentication credentials" });
  }
});

app.get('/api/diary/entries/:id', async (req, res) => {
  try {
    const token = extractTokenFromHeader(req);
    if (!token) {
      return res.status(401).json({ detail: "No token provided" });
    }
    const entry = await getEntry({ token, entryId: req.params.id });
    res.json(entry);
  } catch (error) {
    if (error.message === "ENTRY_NOT_FOUND") {
      return res.status(404).json({ detail: "Entry not found" });
    }
    res.status(401).json({ detail: "Invalid authentication credentials" });
  }
});

app.delete('/api/diary/entries/:id', async (req, res) => {
  try {
    const token = extractTokenFromHeader(req);
    if (!token) {
      return res.status(401).json({ detail: "No token provided" });
    }
    const result = await deleteEntry({ token, entryId: req.params.id });
    res.json(result);
  } catch (error) {
    if (error.message === "ENTRY_NOT_FOUND") {
      return res.status(404).json({ detail: "Entry not found" });
    }
    res.status(500).json({ detail: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server is running on http://127.0.0.1:${port}`);

});
