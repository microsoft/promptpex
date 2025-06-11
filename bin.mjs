#!/usr/bin/env node
import { dirname, join } from "path"
import { fileURLToPath } from "url"
import { spawnSync } from "child_process"

const args = process.argv.slice(2)
const scriptDir = dirname(fileURLToPath(import.meta.url))
if (args[0] === "configure") {
    const result = spawnSync("genaiscript", ["configure"], { stdio: "inherit" })
    if (result.error || result.status !== 0) process.exit(1)
} else {
    const genaiArgs = [
        "run",
        join(scriptDir, "src", "genaisrc", "promptpex.genai.mts"),
        "--no-run-trace",
        "--model-alias",
        "rules=large",
        "evals=large",
        "baseline=large",
        "--",
        ...args,
    ]
    console.error(`genaiscript ${genaiArgs.join(" ")}`)
    const result = spawnSync("genaiscript", genaiArgs, { stdio: "inherit" })
    if (result.error || result.status !== 0) process.exit(1)
}
