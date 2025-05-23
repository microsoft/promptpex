import type { PromptPexContext } from "./types.mts"
import * as fs from "fs/promises"

/**
 * Serializes the PromptPexContext to JSON and saves it to the specified file.
 * @param ctx The PromptPexContext to serialize
 * @param filename The file path to save the JSON
 */
export async function saveContextState(ctx: PromptPexContext, filename: string): Promise<void> {
    const json = JSON.stringify(ctx, null, 2)
    await fs.writeFile(filename, json, "utf-8")
}

/**
 * Loads the PromptPexContext from the specified JSON file.
 * @param filename The file path to load the JSON from
 * @returns The deserialized PromptPexContext
 */
export async function restoreContextState(filename: string): Promise<PromptPexContext> {
    const json = await fs.readFile(filename, "utf-8")
    return JSON.parse(json) as PromptPexContext
}
