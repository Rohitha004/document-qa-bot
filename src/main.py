import sys
import os

# Make sure src/ is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from query import query_rag_pipeline

def main():
    print("=" * 50)
    print("   Welcome to the Document Q&A Bot!")
    print("=" * 50)
    print("Type your question below. Type 'exit' to quit.\n")

    while True:
        user_query = input("You: ").strip()

        if not user_query:
            print("Please enter a valid question.\n")
            continue

        if user_query.lower() == "exit":
            print("Goodbye!")
            break

        print("\nSearching documents...\n")

        try:
            result = query_rag_pipeline(user_query)

            print("Answer:")
            print("-" * 40)
            print(result["answer"])

            print("\nCitations:")
            print("-" * 40)
            for citation in result["citations"]:
                print(f"  - {citation}")

            print("\n" + "=" * 50 + "\n")

        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()