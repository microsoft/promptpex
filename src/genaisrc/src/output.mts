import { DOCS_GLOSSARY } from "./constants.mts"
import type { PromptPexOptions } from "./types.mts"
const { output } = env

export function outputGlossary(options: PromptPexOptions) {
    if (!options?.workflowDiagram) return
    output.details(`Glossary`, DOCS_GLOSSARY)
}

export function outputWorkflowDiagram(
    diagram: string,
    options: PromptPexOptions
) {
    if (!options?.workflowDiagram) return

    output.detailsFenced(
        `workflow`,
        `
graph TD
    ${diagram.trim().split(`\n`).join("\n    ")}
`,
        "mermaid"
    )
}

export async function outputPrompty(
    filename: string,
    options: PromptPexOptions
) {
    if (options?.outputPrompts)
        output.detailsFenced(
            filename,
            (await workspace.readText(filename)).content,
            "md"
        )
}

export function outputFile(file: WorkspaceFile) {
    const { output } = env
    const contentType = path.extname(file.filename)
    output.fence(file.content, contentType)
}

export function outputLines(file: WorkspaceFile, name: string) {
    const { output } = env
    const { content, filename } = file
    const contentType = path.extname(filename)
    const lines = content?.split("\n").map((line) => ({ [name]: line })) || []
    output.table(lines)
    output.detailsFenced(`data`, content, contentType)
}
