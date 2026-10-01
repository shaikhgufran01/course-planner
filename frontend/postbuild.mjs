import { cpSync, rmSync, mkdirSync, renameSync, existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

const dist = "dist";
const staticDir = "../static";
const templatesDir = "../templates";

rmSync(staticDir, { recursive: true, force: true });
mkdirSync(staticDir, { recursive: true });
mkdirSync(templatesDir, { recursive: true });

for (const entry of readdirSync(dist)) {
  if (entry === "index.html") continue;
  cpSync(join(dist, entry), join(staticDir, entry), { recursive: true });
}
cpSync(join(dist, "index.html"), join(templatesDir, "index.html"));

console.log("Copied build output -> ../static and ../templates/index.html");
