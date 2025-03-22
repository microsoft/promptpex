import { performance } from "perf_hooks"
import { createWriteStream, WriteStream } from "fs"

let output: OutputTrace
let writer: WriteStream

const totals: Record<string, number> = {}

export function initPerf(options: { filename?: string; output?: OutputTrace }) {
    const { filename } = options
    if (filename) {
        writer = createWriteStream(filename)
        writer.write("id,duration\n")
    }
    output = options.output
}

export function start(id: string) {
    const uid = id + Math.random().toString(36).substring(7)
    const start = performance.mark(uid + ".start")
    return () => {
        const end = performance.mark(uid + ".end")
        performance.measure(uid, start.name, end.name)
        const duration = Math.ceil(end.startTime - start.startTime)
        totals[id] = (totals[id] || 0) + duration

        if (writer) writer.write(`${id},${duration}\n`)
        if (output) output.itemValue(id, `${duration}ms`)
        else console.debug(`${id}: ${duration}ms`)
    }
}

export async function measure<T>(
    id: string,
    fn: () => Awaitable<T>
): Promise<T> {
    const end = start(id)
    try {
        return await fn()
    } finally {
        end()
    }
}

export function reportPerf() {
    if (!output) return

    output.heading(3, "Performance")
    output.fence(
        JSON.stringify(
            Object.entries(totals).map(([id, duration]) => ({
                id,
                duration: Math.ceil(duration),
            })),
            null,
            2
        ),
        "barchart"
    )
}
