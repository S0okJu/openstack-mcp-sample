def extract_error_patterns(log_content: str) -> Dict[str, Any]:
    """기본적인 에러 패턴 추출 (LLM 분석용 데이터 준비)"""
    if not log_content:
        return {"has_errors": False, "error_lines": []}
    
    error_indicators = [
        r'error', r'fail', r'panic', r'critical', r'fatal', r'emergency', 
        r'alert', r'warning', r'exception', r'segfault', r'oops', r'bug',
        r'cannot', r'unable', r'timeout', r'refused', r'denied'
    ]
    
    pattern = '|'.join(error_indicators)
    error_lines = []
    log_lines = log_content.split('\n')
    
    for i, line in enumerate(log_lines):
        if re.search(pattern, line, re.IGNORECASE):
            context = {
                "line_number": i + 1,
                "content": line.strip(),
                "context_before": [l.strip() for l in log_lines[max(0, i-2):i] if l.strip()],
                "context_after": [l.strip() for l in log_lines[i+1:min(len(log_lines), i+3)] if l.strip()]
            }
            error_lines.append(context)
    
    return {
        "has_errors": len(error_lines) > 0,
        "error_count": len(error_lines),
        "error_lines": error_lines[:15],  # 처음 15개 에러만
        "total_lines": len(log_lines)
    }
