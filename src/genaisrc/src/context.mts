import type { PromptPexContext } from "./types.mts"

/**
 * Serializes the PromptPexContext to JSON and saves it to the specified file.
 * @param ctx The PromptPexContext to serialize
 * @param filename The file path to save the JSON
 */
export async function saveContextState(
    ctx: PromptPexContext,
    filename: string
): Promise<void> {
    const json = JSON.stringify(ctx, null, 2)
    await workspace.writeText(filename, json)
}
