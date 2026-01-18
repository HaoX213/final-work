import os
import toml
from openai import OpenAI

# 1. 读取 Secrets
try:
    secrets = toml.load(".streamlit/secrets.toml")
    api_key = secrets.get("OPENAI_API_KEY")
    base_url = secrets.get("OPENAI_BASE_URL", "https://api.openai.com/v1")     
    print(f"🔑 API Key Loaded: {api_key[:8]}...{api_key[-4:] if api_key else 'None'}")
    print(f"🌐 Base URL: {base_url}")
except Exception as e:
    print(f"❌ Error reading secrets: {e}")
    exit(1)

if not api_key:
    print("❌ OPENAI_API_KEY not found in .streamlit/secrets.toml")
    exit(1)

# 2. 初始化 Client
try:
    client = OpenAI(api_key=api_key, base_url=base_url)
    print("✅ Client initialized. Attempting request...")
except Exception as e:
    print(f"❌ Client init failed: {e}")
    exit(1)

# 3. 发送测试请求
try:
    model_name = secrets.get("OPENAI_MODEL", "gpt-3.5-turbo")
    print(f"🤖 Using Model: {model_name}")
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": "Test connection. Say Hi."}],
        timeout=10 # Set a short timeout
    )
    print("🎉 Success! Response:")
    print(response.choices[0].message.content)
except Exception as e:
    print("\n❌ Request Failed!")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error Details: {e}")
    
    if "401" in str(e):
        print("\n💡 分析 (Analysis): 401 错误通常意味着 API Key 无效，或者该 Key 不适用于当前的 Base URL。")
        print("   如果你使用的是国内转发服务 (如 OhMyGPT, AIProxy 等)，你需要同时配置 'OPENAI_BASE_URL'。")
