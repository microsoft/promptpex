#!/usr/bin/env node
import { dirname, join } from "path"
import { fileURLToPath } from "url"
import { spawnSync } from "child_process"

const cmd = "node_modules/.bin/genaiscript"
const args = process.argv.slice(2)
const scriptDir = dirname(fileURLToPath(import.meta.url))
if ("configure" === args[0]) {
    const result = spawnSync(cmd, args, { stdio: "inherit" })
    if (result.error || result.status !== 0) process.exit(1)
} else {
    const genaiArgs = [
        "run",
        join(scriptDir, "src", "genaisrc", "promptpex.genai.mts"),
        ...args,
        "--no-run-trace",
    ]
    console.error(`genaiscript ${genaiArgs.join(" ")}`)
    const result = spawnSync(cmd, genaiArgs, { stdio: "inherit" })
    if (result.error)
        console.error(result.error.message)
    if (result.error || result.status !== 0) process.exit(1)
}
