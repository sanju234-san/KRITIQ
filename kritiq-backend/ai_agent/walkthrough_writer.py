import os
import re
from datetime import datetime

def parse_review_result(review_result: str):
    """
    Parses Gemini's review result to extract the summary and list of numbered issues.
    """
    summary = ""
    issues = []
    
    # Split into lines
    lines = review_result.splitlines()
    
    # Find headers
    issues_header_index = -1
    summary_header_index = -1
    
    for i, line in enumerate(lines):
        if re.match(r'(?i)^\s*summary\s*:', line):
            summary_header_index = i
        elif re.match(r'(?i)^\s*issues\s*:', line):
            issues_header_index = i
            
    # Extract summary
    if summary_header_index != -1:
        summary_end = issues_header_index if issues_header_index != -1 else len(lines)
        summary_lines = lines[summary_header_index + 1 : summary_end]
        first_line = lines[summary_header_index]
        summary_first_part = re.sub(r'(?i)^\s*summary\s*:\s*', '', first_line).strip()
        summary_rest = "\n".join(summary_lines).strip()
        summary = (summary_first_part + "\n" + summary_rest).strip() if summary_first_part else summary_rest
    else:
        # Check if first line contains Summary without explicit header block
        if issues_header_index != -1 and issues_header_index > 0:
            summary = "\n".join(lines[:issues_header_index]).strip()
            summary = re.sub(r'(?i)^\s*summary\s*:\s*', '', summary).strip()
            
    # Extract issues
    if issues_header_index != -1:
        issues_text = "\n".join(lines[issues_header_index + 1 :])
        parts = re.split(r'\n\s*(\d+)\.\s+', '\n' + issues_text)
        if len(parts) > 1:
            for idx in range(1, len(parts), 2):
                num = parts[idx]
                content = parts[idx+1].strip() if idx+1 < len(parts) else ""
                if content:
                    issues.append((num, content))
                    
    if not issues:
        # Fallback: check if there are numbered lists in the whole review_result
        parts = re.split(r'\n\s*(\d+)\.\s+', '\n' + review_result)
        if len(parts) > 1:
            for idx in range(1, len(parts), 2):
                num = parts[idx]
                content = parts[idx+1].strip() if idx+1 < len(parts) else ""
                if content:
                    issues.append((num, content))
                    
    return summary.strip(), issues


def write_review_walkthrough(file_path: str, language: str, review_result: str, output_dir: str = "walkthroughs") -> str:
    """
    Creates output_dir if it doesn't exist, parses the review result,
    builds a rich walkthrough markdown document, and saves it.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_review.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Parse review result
        summary = ""
        issues = []
        try:
            summary, issues = parse_review_result(review_result)
        except Exception:
            # parsing failed, fall back
            summary = ""
            issues = []
            
        # Overall verdict / intro
        if summary:
            intro = summary
        else:
            intro = f"A code review of `{filename}` was performed using the AI agent."
            
        # Issues count
        issues_count = len(issues)
        if issues_count == 0:
            # Fallback issue count check
            issues_count = len(re.findall(r'\n\s*\d+\.\s+', "\n" + review_result))
            
        # Format Issues Identified section
        if issues:
            parsed_issues_md = []
            for num, content in issues:
                first_line = content.splitlines()[0] if content else ""
                if " - " in first_line:
                    title, rest = first_line.split(" - ", 1)
                    title = title.strip()
                    body = rest.strip() + "\n" + "\n".join(content.splitlines()[1:])
                else:
                    if ":" in first_line and len(first_line.split(":", 1)[0]) < 40:
                        title, rest = first_line.split(":", 1)
                        title = title.strip()
                        body = rest.strip() + "\n" + "\n".join(content.splitlines()[1:])
                    elif len(first_line) < 60:
                        title = first_line.strip()
                        body = "\n".join(content.splitlines()[1:])
                    else:
                        title = "Issue Details"
                        body = content
                
                # Format bold labels
                body = re.sub(r'(?i)\bexplanation\s*:', '**Explanation:**', body)
                body = re.sub(r'(?i)\bsuggested fix\s*:', '**Suggested Fix:**', body)
                body = re.sub(r'(?i)\brecommendation\s*:', '**Recommendation:**', body)
                
                parsed_issues_md.append(f"### {num}. {title}\n\n{body.strip()}")
            issues_identified = "\n\n".join(parsed_issues_md)
        else:
            # Fallback format: print raw review_result but replace labels with bold format
            formatted_result = re.sub(r'(?i)\bexplanation\s*:', '**Explanation:**', review_result)
            formatted_result = re.sub(r'(?i)\bsuggested fix\s*:', '**Suggested Fix:**', formatted_result)
            formatted_result = re.sub(r'(?i)\brecommendation\s*:', '**Recommendation:**', formatted_result)
            issues_identified = formatted_result
            
        # Build the final document using concatenated f-strings for robust formatting
        md_content = (
            f"# Walkthrough — Code Review: `{filename}`\n\n"
            f"{intro}\n\n"
            f"## 📋 Overview\n\n"
            f"| | |\n"
            f"|---|---|\n"
            f"| **File** | `{file_path}` |\n"
            f"| **Language** | {language} |\n"
            f"| **Reviewed On** | {timestamp} |\n"
            f"| **Issues Found** | {issues_count} |\n\n"
            f"## 🔍 Issues Identified\n\n"
            f"{issues_identified}\n\n"
            f"## ✅ Recommended Next Steps\n"
            f"- [ ] Review the recommendations and warning flags raised above.\n"
            f"- [ ] Implement the suggested optimizations or refactoring steps.\n"
            f"- [ ] Re-run the code review to verify improvements.\n\n"
            f"---\n"
            f"*Generated automatically by Kritiq's AI Review Agent — {timestamp}*\n"
        )
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        full_path = os.path.abspath(output_path)
        print(f"Code review walkthrough generated successfully: {full_path}")
        return full_path
    except Exception as e:
        raise RuntimeError(f"Failed to write review walkthrough: {e}")


def write_translation_walkthrough(file_path: str, source_language: str, target_language: str, translated_code: str, output_dir: str = "walkthroughs") -> str:
    """
    Creates output_dir if it doesn't exist, builds a walkthrough markdown document
    summarizing the code translation, saves it to a file, and returns the full path.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        filename = os.path.basename(file_path)
        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_translation.md"
        output_path = os.path.join(output_dir, output_filename)
        
        # Map common languages to standard markdown highlighting tags
        lang_tag = target_language.lower().strip()
        lang_mappings = {
            "python": "python",
            "py": "python",
            "javascript": "javascript",
            "js": "javascript",
            "typescript": "typescript",
            "ts": "typescript",
            "c++": "cpp",
            "cpp": "cpp",
            "java": "java",
            "go": "go",
            "rust": "rust",
            "ruby": "ruby",
            "html": "html",
            "css": "css"
        }
        lang_tag = lang_mappings.get(lang_tag, lang_tag)
        
        # Build the final document using concatenated f-strings for robust formatting
        md_content = (
            f"# Walkthrough — Code Translation: `{filename}`\n\n"
            f"Translated `{filename}` from {source_language} to {target_language}.\n\n"
            f"## 📋 Overview\n\n"
            f"| | |\n"
            f"|---|---|\n"
            f"| **Source File** | `{file_path}` |\n"
            f"| **From** | {source_language} |\n"
            f"| **To** | {target_language} |\n"
            f"| **Translated On** | {timestamp} |\n\n"
            f"## 💻 Translated Code\n\n"
            f"```{lang_tag}\n"
            f"{translated_code}\n"
            f"```\n\n"
            f"## ✅ Recommended Next Steps\n"
            f"- [ ] Verify the translated code syntax and logic in the target environment.\n"
            f"- [ ] Compile or run tests to ensure behavioral equivalence with the original source code.\n\n"
            f"---\n"
            f"*Generated automatically by Kritiq's AI Translation Agent — {timestamp}*\n"
        )
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        full_path = os.path.abspath(output_path)
        print(f"Code translation walkthrough generated successfully: {full_path}")
        return full_path
    except Exception as e:
        raise RuntimeError(f"Failed to write translation walkthrough: {e}")
