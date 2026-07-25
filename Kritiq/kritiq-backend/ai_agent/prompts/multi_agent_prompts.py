def build_reviewer_prompt(code: str, language: str = "python") -> str:
    """
    Builds the reviewer prompt for Agent 1.
    Instructs Gemini to review the code and output a list of short 1-2 sentence issues.
    """
    prompt = f"""
You are a careful, experienced code reviewer.
Review the following {language} code and identify any issues.

For each issue you find, provide a short description.
Keep each issue brief—exactly 1 to 2 sentences. Do not write full prose paragraphs or deep explanations.

Structure your response as a simple list of issues:
Issues:
- <issue 1: short 1-2 sentence description>
- <issue 2: short 1-2 sentence description>

Code:
{code}
"""
    return prompt.strip()


def build_verifier_prompt(code: str, language: str, issues: str) -> str:
    """
    Builds the verifier prompt for Agent 2.
    Instructs Groq to check the issues against the code and only return confirmed issues,
    prefixed with '[VERIFIED BY A SECOND MODEL]'.
    """
    prompt = f"""
You are a critical, independent code verifier.
Analyze the following {language} code and check the list of potential issues identified by another reviewer.

Determine if each issue is a real, valid problem in the code, or if it is a false positive / non-issue.
Only return issues that you confirm are real, valid problems. Drop any issues you disagree with or believe are false positives.

For each confirmed issue, you must prefix it clearly with "[VERIFIED BY A SECOND MODEL]". Keep the explanation brief (1-2 sentences).

Format your response as a simple list of verified issues:
1. [VERIFIED BY A SECOND MODEL] <verified issue and brief explanation>
2. [VERIFIED BY A SECOND MODEL] <verified issue and brief explanation>

Original Code:
{code}

Potential Issues List:
{issues}
"""
    return prompt.strip()
