/**
 * Regenerate src/content/docs/changelog.md from the git log.
 * Run via `pnpm run gen:changelog` (wired as a prebuild step).
 */
import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..", "..");
const target = resolve(here, "..", "src", "content", "docs", "changelog.md");

function gitLog(): string {
  try {
    return execFileSync(
      "git",
      ["log", "--pretty=format:- %s (%h)", "--max-count=20"],
      { cwd: repoRoot, encoding: "utf-8", stdio: ["ignore", "pipe", "ignore"], timeout: 10_000 },
    );
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`gen-changelog: git log failed: ${message}`);
  }
}

const body = [
  "---",
  "title: Changelog",
  "description: McCoy release history (generated from the git log).",
  "---",
  "",
  "<!-- This file is regenerated from the git log on every build via scripts/gen-changelog.ts. -->",
  "",
  gitLog().trim(),
  "",
  "See the [GitHub releases](https://github.com/nitishagar/mccoy/releases) for the full history.",
  "",
].join("\n");

writeFileSync(target, body);
console.log(`gen-changelog: wrote ${target}`);
