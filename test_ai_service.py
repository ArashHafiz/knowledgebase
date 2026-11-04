from ai_service import generate_answer

test_question = "When was Reagan elected?"

test_chunks = [
    {
        "filename": "The Last Decade of the Cold War.txt",
        "doc_id": 2,
        "chunk_number": 3,
        "text": (
            "The 1980s were a pivotal decade in the Cold War, marked by significant political and military developments."
            "Ronald Reagan was elected as the 40th President of the United States in November 1980."
            "His administration took a hardline stance against the Soviet Union, which was embroiled in both domestic and external challenges."
            "Reagan's policies, including increased defense spending and the Strategic Defense Initiative, aimed to counter the Soviet threat."
        )
    }
]

answer = generate_answer(test_question, test_chunks)

print("Question:", test_question)
print("\nGenerated answer:")
print(answer)