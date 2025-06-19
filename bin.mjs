#!/usr/bin/env node
import { dirname, join } from "path"
import { fileURLToPath } from "url"
import { spawnSync } from "child_process"

const args = process.argv.slice(2)
const scriptDir = dirname(fileURLToPath(import.meta.url))
if ("configure" === args[0]) {
    const result = spawnSync("genaiscript", args, { stdio: "inherit" })
    if (result.error || result.status !== 0) process.exit(1)
} else if ("serve" === args[0]) {
    const genaiArgs = [
        "serve",
        //join(scriptDir, "src", "genaisrc", "promptpex.genai.mts"),
        ...args.slice(1)
    ]
    console.error(`genaiscript ${genaiArgs.join(" ")}`)
    const result = spawnSync("genaiscript", genaiArgs, { stdio: "inherit" })
    if (result.error || result.status !== 0) process.exit(1)
} else {
    const genaiArgs = [
        "run",
        join(scriptDir, "src", "genaisrc", "promptpex.genai.mts"),
        ...args,
        "--no-run-trace",
    ]
    console.error(`genaiscript ${genaiArgs.join(" ")}`)
    const result = spawnSync("genaiscript", genaiArgs, { stdio: "inherit" })
    if (result.error)
        console.error(result.error.message)
    if (result.error || result.status !== 0) process.exit(1)
}
