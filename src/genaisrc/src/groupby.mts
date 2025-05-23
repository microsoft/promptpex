export function groupBy<T, K extends string | number | symbol>(
    items: T[],
    callback: (item: T, index: number, array: T[]) => K
): Record<K, T[]> {
    return items.reduce(
        (acc, item, idx, arr) => {
            const key = callback(item, idx, arr)
            if (!acc[key]) acc[key] = []
            acc[key].push(item)
            return acc
        },
        {} as Record<K, T[]>
    )
}
