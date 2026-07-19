/**
 * Regenerate src/content/docs/cli.md from `uv run mccoy --help` and each subcommand's --help.
 * Run via `pnpm run gen:cli-ref` (wired as a prebuild step).
 *
 * Edits to the CLI reference should be made in src/mccoy/cli.py docstrings, not in cli.md.
 */
import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..", "..");
const target = resolve(here, "..", "src", "content", "docs", "cli.md");

function run(cmd: string): string {
  try {
    return execFileSync("uv", ["run", cmd], {
      cwd: repoRoot,
      encoding: "utf-8",
      stdio: ["ignore", "pipe", "ignore"],
      timeout: 30_000,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`gen-cli-ref: failed to run '${cmd}': ${message}`);
  }
}

function help(args: string[]): string {
  return execFileSync("uv", ["run", "mccoy", ...args, "--help"], {
    cwd: repoRoot,
    encoding: "utf-8",
    stdio: ["ignore", "pipe", "ignore"],
    timeout: 30_000,
  });
}

const subcommands = ["scan", "fix"] as const;
const blocks: string[] = [];

blocks.push("---\ntitle: CLI reference\ndescription: McCoy command-line interface (generated from --help).\n---\n");
blocks.push(
  "<!-- This file is regenerated from `uv run mccoy --help` on every build via scripts/gen-cli-ref.ts.\n" +
    "     Edit the CLI docstrings in src/mccoy/cli.py, not this file. -->\n",
);

blocks.push("## `mccoy`\n\n```text");
blocks.push(help([]).trim());
blocks.push("```\n");

for (const sub of subcommands) {
  blocks.push(`## \`mccoy ${sub}\`\n\n\`\`\`text`);
  blocks.push(help([sub]).trim());
  blocks.push("```\n");
}

writeFileSync(target, blocks.join("\n"));
console.log(`gen-cli-ref: wrote ${target}`);
