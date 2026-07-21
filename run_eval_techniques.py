from test_data import test_cases
from prompting_techniques import classify_zero_shot, classify_few_shot, classify_CoT, client, MODEL, LABELS


# COMPARISON HARNESS — runs ANY of the three classify functions against the same test set, using the same accuracy
# logic, so results are directly comparable.

def evaluate_technique(classify_function, test_cases):
    correct = 0
    total = len(test_cases)

    for case in test_cases:

        result = classify_function(case["input"])

        # CoT returns a (reasoning, label) pair — unpack it to isolate just the label.The other two techniques already
        # return a clean label string.

        if classify_function == classify_CoT:
            reasoning, predicted = result

            if predicted == None:
                print(f"Skipped: could not read COT answer for {case["input"][:30]}")
                continue
        else:
            predicted = result

        expected = case["expected"]

        # Normalized comparison — ignores case/whitespace differences

        passed = predicted.lower().strip() == expected.lower().strip()
        correct += passed
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] expected: {expected}  got: {predicted}")

    # EXACT-MATCH CHECKER — calculate this technique's accuracy as a percentage

    accuracy = (correct / total) * 100
    print(f"Accuracy: {accuracy:.1f}%")
    return accuracy


if __name__ == "__main__":
    # Run the SAME test set through all three prompting techniques

    zero_shot_accuracy = evaluate_technique(classify_zero_shot, test_cases)
    few_shot_accuracy = evaluate_technique(classify_few_shot, test_cases)
    cot_accuracy = evaluate_technique(classify_CoT, test_cases)

    # Compare all three side by side

    print(f"Zero-shot accuracy: {zero_shot_accuracy}")
    print(f"Few-shot accuracy: {few_shot_accuracy}")
    print(f"CoT accuracy: {cot_accuracy}")
