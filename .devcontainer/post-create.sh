pip install -r requirements.txt

# # ollama install and pull models 
# curl -fsSL https://ollama.com/install.sh | sh
# 
# ollama pull mistral:latest 
# ollama pull gemma2:9b 
# ollama pull gemma2:2b 
# ollama pull llama3.1:8b 
# ollama pull phi3:medium 
# ollama pull phi3:mini 
# ollama pull gemma2:latest 
# ollama pull llama3.1:latest 
# ollama pull phi3:latest 
# ollama pull phi3:medium-128k 
# 
# ollama serve & 

pushd app
streamlit run main.py &
popd