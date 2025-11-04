#!/usr/bin/env python3

import re
from typing import Dict


def test_quick_answers():
    """Test the quick answer extraction with your specific format"""

    # Your sample format
    sample_text = "1. B2. A3. C4. B5. B6. B7. B8. C9. D10. A11. D12. C13. A14. C15. A16. C17. A18. C19. B20. D21. B22. C23. A24. A25. B26. A27. B28. A29. A30. B31. B32. A33. C34. B35. D36. A37. D38. C39. B40. A41. B42. B43. B44. B45. D46. C47. C48. A49. A50. C51. B52. B53. A54. A55. C56. D57. A58. C59. A60. D61. D62. C63. D64. B65. A66. A67. C68. D69. A70. B71. C72. A73. C74. A75. C76. C77. D78. D79. C80. B81. A82. C83. B84. A85. A86. A87. D88. C89. C90. C"

    answers = {}

    # Pattern for compact format: "1. B2. A3. C4. B5. B"
    pattern = r"(\d+)\.\s*([A-D])(?=\d+\.|\s|$)"
    matches = re.findall(pattern, sample_text)

    for q_num, answer in matches:
        answers[int(q_num)] = answer.strip()

    print(f"Extracted {len(answers)} quick answers:")
    for i in range(1, 11):  # Show first 10
        if i in answers:
            print(f"  {i}: {answers[i]}")
        else:
            print(f"  {i}: MISSING")

    return answers


def test_detailed_answers():
    """Test the detailed answer extraction"""

    sample_text = """1. Answer B is correct. The client with passive-aggressive personality disorder often has underlying hostility that is exhibited as acting-out behavior. Answers A, C, and D are incorrect. Although these individuals might have a high IQ, it cannot be said that they have superior intelligence. They also do not necessarily have dependence on others or an inability to share feelings.
2. Answer A is correct. Clients with antisocial personality disorder must have limits set on their behavior because they are artful in manipulating others. Answer B is not correct because they do express feelings and remorse. Answers C and D are incorrect because it is unnecessary to minimize interactions with others or encourage them to act out rage more than they already do.
3. Answer C is correct. To prevent the client from inducing vomiting after eating, the client should be observed for 1–2 hours after meals. Allowing privacy as stated in answer A will only give the client time to vomit. Praising the client for eating all of a meal does not correct the psychological aspects of the disease; thus, answer B is incorrect. Encouraging the client to choose favorite foods might increase stress and the chance of choosing foods that are low in calories and fats so D is not correct."""

    answers = {}

    # Pattern for your specific format
    pattern = r"(\d+)\.\s*Answer\s+([A-D])\s+is\s+correct\.\s*(.*?)(?=\d+\.\s*Answer\s+[A-D]\s+is\s+correct|$)"
    matches = re.findall(pattern, sample_text, re.DOTALL)

    for q_num, answer, rationale in matches:
        answers[int(q_num)] = {"answer": answer.strip(), "rationale": rationale.strip()}

    print(f"\nExtracted {len(answers)} detailed answers:")
    for i in range(1, 4):  # Show first 3
        if i in answers:
            print(f"  {i}: {answers[i]['answer']} - {answers[i]['rationale'][:100]}...")
        else:
            print(f"  {i}: MISSING")

    return answers


if __name__ == "__main__":
    print("Testing answer extraction patterns...")
    quick = test_quick_answers()
    detailed = test_detailed_answers()

    print(f"\nSummary:")
    print(f"Quick answers extracted: {len(quick)}")
    print(f"Detailed answers extracted: {len(detailed)}")
