import { readdir, readFile, writeFile } from "node:fs/promises"
import type { PromptPexContext, PromptPexLoaderOptions } from "./types.mts"
import { loadPromptContext } from "./loaders.mts"

const { output } = env

export async function fabricLoadPrompts(
    branch: string,
    options?: PromptPexLoaderOptions
): Promise<PromptPexContext[]> {
    output.itemValue("fabric version", branch)

    const fabricGit = await git.shallowClone("danielmiessler/fabric", {
        branch,
        force: true,
    })
    const fabricDir = path.join(fabricGit.cwd, "patterns")
    const patterns = (await readdir(fabricDir, { withFileTypes: true })).filter(
        (f) => f.isDirectory()
    )
    output.itemValue("fabric patterns", patterns.length)

    const res: WorkspaceFile[] = []
    for (const pattern of patterns) {
        const patternDir = path.join(fabricDir, pattern.name)
        const files = await readdir(patternDir)
        const system = files.find((f) => f === "system.md")
        const systemText = system
            ? await readFile(path.join(patternDir, system), "utf-8")
            : ""
        const user = files.find((f) => f === "user.md")
        const userText = user
            ? await readFile(path.join(patternDir, user), "utf-8")
            : ""
        const prompty = `---
name: ${pattern.name}
tags:
    - fabric
    - unlisted
---
${
    systemText
        ? `system:
${systemText}
`
        : ""
}
${
    userText
        ? `user:
${userText}
`
        : ""
}
`
        const file = {
            filename: path.relative(
                process.cwd(),
                path.join(patternDir, `${pattern.name}.prompty`)
            ),
            content: prompty,
        } satisfies WorkspaceFile
        await writeFile(file.filename, prompty)
        res.push(file)
    }

    return loadPromptContext(res, options)
}
