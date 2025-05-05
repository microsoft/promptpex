import { defineConfig, passthroughImageService } from "astro/config"
import starlight from "@astrojs/starlight"
import rehypeMermaid from "rehype-mermaid"
import starlightLinksValidator from "starlight-links-validator"
import starlightLlmsTxt from "starlight-llms-txt"

// https://astro.build/config
export default defineConfig({
    site: "https://microsoft.github.io",
    base: "/promptpex",
    image: {
        service: passthroughImageService(),
    },
    markdown: {
        rehypePlugins: [[rehypeMermaid, { strategy: "img-svg", dark: true }]],
    },
    integrations: [
        starlight({
            title: "PromptPex",
            plugins: [
                starlightLlmsTxt({
                    pageSeparator: "\n\n=|=|=|=|=|=\n\n",
                    minify: {
                        customSelectors: ["picture"],
                    },
                }),
                starlightLinksValidator(),
            ],
            components: {
                Head: "./src/components/Head.astro",
                Footer: "./src/components/Footer.astro",
            },
            social: [
                {
                    icon: "github",
                    label: "GitHub",
                    href: "https://github.com/microsoft/promptpex",
                },
            ],
            editLink: {
                baseUrl:
                    "https://github.com/microsoft/promptpex/edit/main/docs/",
            },
        }),
    ],
})
