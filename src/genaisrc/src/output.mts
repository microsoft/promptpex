import { DOCS_GLOSSARY, DOCS_TEST_GENERATION_DIAGRAM } from "./constants.mts";
import type { PromptPexOptions } from "./types.mts";

export async function outputBackgroundInformation() {
    const { output } = env;
    output.startDetails(`information`);
    env.output.appendContent(
        `
\`\`\`mermaid
${DOCS_TEST_GENERATION_DIAGRAM}
\`\`\`

${DOCS_GLOSSARY}

`
    );
    output.endDetails();
}

export function outputWorkflowDiagram(
    diagram: string,
    options: PromptPexOptions
) {
    if (!options?.workflowDiagram) return;

    env.output.detailsFenced(
        `workflow`,
        `
graph TD
    ${diagram.trim().split(`\n`).join("\n    ")}
`,
        "mermaid"
    );
}

export async function outputPrompty(
    filename: string,
    options: PromptPexOptions
) {
    if (options?.outputPrompts)
        env.output.detailsFenced(
            filename,
            (await workspace.readText(filename)).content,
            "md"
        );
}

export function outputFile(file: WorkspaceFile) {
    const { output } = env;
    const contentType = path.extname(file.filename);
    output.fence(file.content, contentType);
}

export function outputLines(file: WorkspaceFile, name: string) {
    const { output } = env;
    const { content, filename } = file;
    const contentType = path.extname(filename);
    const lines = content?.split("\n").map((line) => ({ [name]: line })) || [];
    output.table(lines);
    output.detailsFenced(`data`, content, contentType);
}
