"""
Analyzer module that uses Anthropic AI to detect broken access control vulnerabilities.
"""
import json
import re
from pathlib import Path

from anthropic import Anthropic

from broken_access_control_scanner.models import Severity, VulnerabilityResult


SYSTEM_PROMPT = """You are an expert security analyst specializing in detecting broken access control vulnerabilities in source code.

Broken access control vulnerabilities occur when:
- Users can access resources they shouldn't have permission to access
- Authorization checks are missing or improperly implemented
- Direct object references (IDOR) allow unauthorized data access
- Privilege escalation is possible through API manipulation
- Role-based access control (RBAC) is not properly enforced
- Missing function-level access control
- Insecure direct object references
- Path traversal vulnerabilities
- Missing or improper authentication checks

When analyzing code, consider:
1. Whether proper authentication is enforced
2. Whether authorization checks verify the user has permission for the specific resource
3. Whether user input is validated before accessing resources
4. Whether there are any bypass possibilities

You must respond ONLY with a valid JSON array containing vulnerability findings. Each finding should have this format:
{
    "endpoint": "Name or route of the endpoint/function",
    "severity": "NONE|LOW|MEDIUM|HIGH|CRITICAL",
    "description": "Brief description of the vulnerability or why it's safe"
}

Severity guidelines:
- NONE: No access control issues found, proper checks in place
- LOW: Minor issues, unlikely to be exploitable
- MEDIUM: Access control weakness that could be exploited under certain conditions
- HIGH: Clear access control vulnerability that can likely be exploited
- CRITICAL: Severe access control vulnerability with high impact, easily exploitable

Return one finding per endpoint/handler found in the code. If no endpoints are found, return an empty array: []"""


def analyze_file(
    client: Anthropic,
    file_path: Path,
    data_model: str,
    model: str = "claude-sonnet-4-20250514"
) -> list[VulnerabilityResult]:
    """
    Analyze a source file for broken access control vulnerabilities using Anthropic AI.

    Args:
        client: Anthropic API client.
        file_path: Path to the source file to analyze.
        data_model: Description of the data model/context.
        model: Anthropic model to use.

    Returns:
        List of VulnerabilityResult with severity and description for each endpoint.
    """
    source_code = file_path.read_text(encoding="utf-8")

    response_text = ""
    with client.messages.stream(
        model=model,
        max_tokens=64000,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Analyze the following source code file for broken access control vulnerabilities.\n\nData Model Context:\n{data_model}\n\nSource Code ({file_path.name}):\n```\n{source_code}\n```\n\nIdentify all endpoints/handlers and analyze each one. Respond with a JSON array of findings.",
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            response_text += text

    json_match = re.search(r'\[.*]', response_text, re.DOTALL)
    findings = json.loads(json_match.group())

    results = []
    for finding in findings:
        results.append(VulnerabilityResult(
            endpoint=finding["endpoint"],
            severity=Severity(finding["severity"].upper()),
            description=finding["description"]
        ))

    return results
