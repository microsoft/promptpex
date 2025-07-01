import { TEMPLATE_VARIABLE_RX } from "./constants.mts"

const dbg = host.logger("promptpex:template")

export function fillTemplateVariables(
    content: string,
    options: {
        variables: Record<string, string>
        idResolver: (id: string) => string
    }
) {
    if (!content) return content
    return content.replace(TEMPLATE_VARIABLE_RX, (_, id) => {
        const variable = options.variables?.[id]
        if (variable) {
            dbg(`inline ${id}`)
            return variable
        }
        return options.idResolver?.(id) ?? _
    })
}

/**
 * Replace {{...}} with [[...]] so that it does not get expanded
 * @param content
 */
export function hideTemplateVariables(content: string) {
    if (!content) return content
    return content.replace(TEMPLATE_VARIABLE_RX, (_, id) => {
        dbg(`hide ${id}`)
        return `[[${id}]]`
    })
}
