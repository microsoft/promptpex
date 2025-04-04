export const diagnostics =
    !!process.env.GENAISCRIPT_DEBUG
if (diagnostics) console.warn(`diagnostics enabled`)
