script({ title: "shorten", 
    model: "gpt-4o", 
    group: "text", 
    system: ["system"]})
    
$`
Rewrite the following content in 300 words or less preserving all the information in the original:

Memory allocation performance
Dr. Zorn’s early research focused on the performance of memory allocation and garbage collection, which included understanding memory system effects, behavior prediction, and customization approaches.  His 2002 OOPSLA paper “Reconsidering Custom Memory Allocation” (246 citations) received the OOPSLA 2012 Most Influential Paper Award. From the citation: “Until 2002, it was taken for granted that application-specific memory allocators were superior to general purpose libraries. Berger, Zorn and McKinley’s paper demonstrated through a rigorous empirical study that this assumption is not well-founded…”
Security
Building on his understanding of garbage collection and memory allocation, Dr. Zorn explored the related security implications.  His 2006 paper “DieHard: probabilistic memory safety for unsafe languages” (651 citations), received the PLDI 2016 Most Influential Paper Award and introduced the concept of probabilistic memory safety.  Quoting a 2024 IEEE journal article: “DieHard pioneered probabilistic memory protection for the heap. Other researchers soon seized on the idea of combining randomization and replication more generally”.  
Dr. Zorn also explored JavaScript-based malware attacks.  His Nozzle project (NOZZLE: A Defense Against Heap-spraying Code Injection Attacks, Usenix Security 2009, 324 citations), pioneered mitigations against heap spraying, a new attack launched via JavaScript embedded in web pages.  Related projects describing defenses against other JavaScript-based attacks are also widely cited (ZOZZLE, Usenix Security 2011, 406 citations; Rozzle, 2012 IEEE Symposium on Security and Privacy, 257 citations).
Programming usability
Dr. Zorn foresaw the impact that program synthesis and AI would have on making programming more accessible.  He understood that one of the primary paths for this impact was through spreadsheets.  He was involved in the original collaboration between Microsoft Research and Excel that resulted in Excel Flash Fill.  His 2015 CACM article “Inductive programming meets the real world” on programming by example highlighted the importance that the expanding research area of program synthesis would have in practice. 
When code-generating LLMs became available, Dr. Zorn co-led the CodeExcel project which explored using LLMs to translate natural language into code.  His CHI’23 paper "What It Wants Me To Say": Bridging the Abstraction Gap Between End-User Programmers and Code-Generating Large Language Models” received a Best Paper Honorable Mention and explores how to leverage user knowledge to synthesize correct formulas.   CodeExcel was a significant influence on the Generate Formula feature in the Excel Copilot product release. 
Approximate computing
Dr. Zorn understood that increasingly computation would be about acceptable approximations and not exact computations.  His Flikker project (“Flikker: Saving DRAM Refresh-power through Critical Data Partitioning “, ASPLOS, 2011, 650 citations) was one of the first to explore the approach of trading off reliability for power.   

`

