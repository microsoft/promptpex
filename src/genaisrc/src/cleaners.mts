export function deleteFalsyValues<T extends Record<string, any>>(o: T): T {
    if (typeof o === "object")
        for (const k in o) {
            const v = o[k]
            if (
                v === undefined ||
                v === null ||
                v === "" ||
                v === false ||
                (Array.isArray(v) && !v.length)
            )
                delete o[k]
        }
    return o
}

export function deleteUndefinedOrEmptyValues<T>(o: T): T {
    for (const k in o) {
        const v = o[k]
        if (v === undefined || v === null || v === "") delete o[k]
    }
    return o
}
