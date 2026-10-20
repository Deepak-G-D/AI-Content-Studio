from scripts.my_llm import  generate_response

try:
    model = "google/gemma-4-e4b"
    print(f"Connected to LM Studio.")
    print(f"Model detected: {model}")

    answer = generate_response(
        system_prompt=(
            "You are a helpful marketing assistant. "
            "Keep responses concise."
        ),
        user_prompt=(
            "Write three catchy promotional hooks for a "
            "fictional mystery drama about a missing letter."
        ),
    )

    print("\nGenerated content:\n")
    print(answer)

except RuntimeError as exc:
    print(f"\nERROR: {exc}")
