# diary-back

A backend API for a personal diary application.

## Overview
This project serves as the backend API for a personal diary application. It provides endpoints for user authentication, managing diary entries, and user-specific operations.

## Features
- User registration and login
- Create, read, update, and delete diary entries
- Token-based authentication using JWT
- CORS configuration for secure communication

## Tech Stack / Built With
- TypeScript
- Node.js
- Express.js
- Prisma
- PostgreSQL
- JWT for authentication
- Multer for file uploads
- CORS for cross-origin resource sharing

## Installation & Setup
```shell
git clone https://github.com/CodeName-R4M/diary-back.git
cd diary-back
npm install
```

## Usage
```javascript
// Register a new user
app.post("/register", registerUser);

// Login user
app.post("/login", loginUser);

// Create a new diary entry
app.post("/entries", extractTokenFromHeader, upload.single("attachment"), createEntry);

// Get all diary entries
app.get("/entries", extractTokenFromHeader, getEntries);

// Get a specific diary entry
app.get("/entries/:id", extractTokenFromHeader, getEntry);

// Update a diary entry
app.put("/entries/:id", extractTokenFromHeader, updateEntry);

// Delete a diary entry
app.delete("/entries/:id", extractTokenFromHeader, deleteEntry);
```

## Project Structure
```
├── .env
├── .gitignore
├── generated
├── modules
├── package-lock.json
├── package.json
├── prisma
├── server.js
└── vercel.json
```

## Contributing
Contributions are welcome. Feel free to open an issue or submit a pull request.

## License
This project is licensed under the MIT License.