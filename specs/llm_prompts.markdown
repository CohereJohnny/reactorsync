# LLM Prompts for ReactorSync (Cohere Integration)

## Diagnostic Prompt (Command A)
"Given reactor telemetry: {data}, and fault: {fault}, generate a step-by-step diagnostic report. Base on nuclear best practices for CANDU/SMR."

## Search Prompt (Embed/Rerank)
"Embed this query for semantic search on Conexus knowledge base: {query}. Rerank results for relevance to SMR deployment risks."

## Generation Prompt (Command A for Reports)
"Summarize anomaly: {anomaly} into a regulatory-compliant report, citing CNSC guidelines."

## Best Practices
- Include safeguards: "Output only factual, simulated data."
- Chain in Haystack: Embed → Rerank → Command A.