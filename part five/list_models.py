import toml
from openai import OpenAI

try:
    secrets = toml.load(".streamlit/secrets.toml")
    client = OpenAI(
        api_key=secrets["OPENAI_API_KEY"],
        base_url=secrets["OPENAI_BASE_URL"]
    )

    print(f"Checking models at {secrets['OPENAI_BASE_URL']}...")
    models = client.models.list()
    print("\n✅ Available Models:")
    for m in models:
        print(f"- {m.id}")
        
except Exception as e:
    print(f"\n❌ Failed to list models: {e}")
