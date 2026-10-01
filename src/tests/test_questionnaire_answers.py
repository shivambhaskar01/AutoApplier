import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.client.job_client import build_questionnaire_answers


def test_experience_questions_use_profile_experience_value():
    questionnaire = [
        {
            "questionId": "q1",
            "questionName": "What is your total experience?",
            "questionType": "text box",
            "answerOption": {},
        },
        {
            "questionId": "q2",
            "questionName": "Do you have experience with AWS?",
            "questionType": "radio",
            "answerOption": {"1": "Yes", "2": "No"},
        },
        {
            "questionId": "q3",
            "questionName": "Are you comfortable with Docker?",
            "questionType": "radio",
            "answerOption": {"1": "Yes", "2": "No"},
        },
        {
            "questionId": "q4",
            "questionName": "Years of experience in Kubernetes?",
            "questionType": "text box",
            "answerOption": {},
        },
        {
            "questionId": "q5",
            "questionName": "Experience in Terraform",
            "questionType": "dropdown",
            "answerOption": {
                "1": "1-2 years",
                "2": "3-5 years",
                "3": "6-8 years",
                "4": "8+ years",
            },
        },
    ]

    profile = {
        "current_ctc": "50",
        "expected_ctc": "70",
        "exp_total": "8",
        "exp_node": "8",
        "exp_python": "8",
        "notice_days": 60,
        "skills": ["aws", "docker", "kubernetes", "ci/cd", "jenkins", "terraform"],
    }

    answers = build_questionnaire_answers(questionnaire, profile)

    assert answers["q1"] == "8 years"
    assert answers["q2"] == ["1"]
    assert answers["q3"] == ["1"]
    assert answers["q4"] == "8 years"
    assert answers["q5"] == ["4"]
