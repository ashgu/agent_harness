#!bin
# 1. Confirm Ollama is up and list available models
curl -s localhost:11434/api/tags | python3 -m json.tool

# 2. Pick your tool-capable model (look at the list above).
#    Common good choices: llama3.1, qwen2.5:7b, mistral-nemo
#    Set it as the default for all later commands:
export OLLAMA_MODEL="qwen3.8:latest"   # <-- change to whatever you see in the list

# 3. One-shot chat to confirm the model responds
curl -s localhost:11434/api/chat \
  -d '{"model":"'"$OLLAMA_MODEL"'","stream":false,"messages":[{"role":"user","content":"Reply with exactly: PONG"}]}' | python3 -m json.tool

# 4. Quick tool-calling probe (does this model actually support tools?)
curl -s localhost:11434/api/chat \
  -d '{"model":"'"$OLLAMA_MODEL"'","stream":false,"messages":[{"role":"user","content":"What is 2+2? Use the tool."}],"tools":[{"type":"function","function":{"name":"add","description":"Add two numbers","parameters":{"type":"object","properties":{"a":{"type":"integer"},"b":{"type":"integer"}},"required":["a","b"]}}}]}' | python3 -m json.tool