import json


def parse_ai_response(
        response_text: str,
        question: str
) -> dict:
    result = {
        "question": "",
        "answer": "",
        "sources": []
    }

    # Strategy 1: Try JSON
    try:
        data = json.loads(response_text)

        # Standard format
        if "ANSWER" in data:
            result["question"] = data.get(
                "QUESTION",
                question
            )

            result["answer"] = data.get(
                "ANSWER",
                ""
            )

            sources = data.get(
                "SOURCES",
                []
            )

            if isinstance(sources, str):
                result["sources"] = [
                    source.strip()
                    for source in sources.split(",")
                    if source.strip()
                ]

            elif isinstance(sources, list):
                result["sources"] = sources

            return result

        if len(data) == 1:
            key = list(data.keys())[0]

            result["question"] = key
            result["answer"] = data[key]

            return result

    except Exception:
        pass

    # Strategy 2: QUESTION / ANSWER / SOURCES parser
    current_section = None

    for line in response_text.splitlines():
        line = line.strip()

        if line.startswith("QUESTION:"):
            current_section = "question"
            value = line.replace(
                "QUESTION:",
                "",
                1
            ).strip()

            if value:
                result["question"] = value

            continue

        if line.startswith("ANSWER:"):
            current_section = "answer"
            value = line.replace(
                "ANSWER:",
                "",
                1
            ).strip()

            if value:
                result["answer"] = value

            continue

        if line.startswith("SOURCES:"):
            current_section = "sources"

            value = line.replace(
                "SOURCES:",
                "",
                1
            ).strip()

            if value:
                result["sources"] = [
                    source.strip()
                    for source in value.split(",")
                ]
            continue

        if current_section == "question":
            result["question"] += (
                ("\n" if result["question"] else "")
                + line
            )

        elif current_section == "answer":
            result["answer"] += (
                ("\n" if result["answer"] else "")
                + line
            )

        elif current_section == "sources":
            if line:
                if "," in line:
                    result["sources"].extend(
                        [
                            source.strip()
                            for source in line.split(",")
                        ]
                    )
                else:
                    result["sources"].append(
                        line
                    )

    if not result["question"]:
        result["question"] = question

    print(result)

    return result
