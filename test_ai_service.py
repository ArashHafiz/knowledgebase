from ai_service import generate_answer

test_question = "When did Brezhnev die?"

test_chunks = [
    {
        "filename": "1976 POD.txt",
        "doc_id": 2,
        "chunk_number": 3,
        "text": (
            "Leonid Brezhnev died on 26 January 1976. "
            "His death was followed by a period of political "
            "uncertainty within the Soviet leadership."
        )
    }
]

answer = generate_answer(test_question, test_chunks)

print("Question:", test_question)
print("\nGenerated answer:")
print(answer)