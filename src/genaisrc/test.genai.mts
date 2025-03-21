import { loadPromptFiles } from "./src/loaders.mts"
import { initPerf } from "./src/perf.mts"

script({
    title: "test suite assuming very limited access to models",
})

const { output, vars } = env

initPerf({ output })
const demo = await workspace.readText("samples/demo/demo.prompty")
const files = await loadPromptFiles(demo)
