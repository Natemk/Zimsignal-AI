import { existsSync } from "node:fs";
import { spawn } from "node:child_process";
import { resolve } from "node:path";
import dotenv from "dotenv";

dotenv.config({ path: resolve(process.cwd(), ".env") });

const pythonPath = resolve(
  process.cwd(),
  process.platform === "win32"
    ? ".venv/Scripts/python.exe"
    : ".venv/bin/python",
);

if (!existsSync(pythonPath)) {
  console.error(`Project virtual-environment Python not found: ${pythonPath}`);
  console.error("Create it and install dependencies with: python -m pip install -e .[dev]");
  process.exit(1);
}

const server = spawn(
  pythonPath,
  ["-m", "uvicorn", "api.main:app", "--reload"],
  { stdio: "inherit", env: process.env },
);

server.on("error", (error) => {
  console.error(`Could not start the API: ${error.message}`);
  process.exitCode = 1;
});

server.on("exit", (code) => {
  process.exitCode = code ?? 1;
});