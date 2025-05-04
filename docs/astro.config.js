import { defineConfig, passthroughImageService } from "astro/config"
import starlight from "@astrojs/starlight"
import rehypeMermaid from "rehype-mermaid"
import starlightLinksValidator from "starlight-links-validator"

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
            plugins: [starlightLinksValidator()],
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
            sidebar: [
                {
                    label: "Start Here",
                    autogenerate: { directory: "getting-started" },
                },
            ],
        }),
    ],
})
