# Workflow: Code Review
# Purpose: Systematic code review process for quality assurance

## Overview

This workflow guides a thorough code review covering functionality, style, security, and maintainability.

## When to Use

- Reviewing pull requests
- Auditing critical code paths
- Onboarding review for new contributors
- Pre-release validation

## Steps

### 1. High-Level Assessment

**Purpose**: Understand what the code does and why

- [ ] Read PR description and linked issues
- [ ] Understand the problem being solved
- [ ] Check overall approach and architecture
- [ ] Verify tests are included

**Questions to Answer**:
- Does this change solve the stated problem?
- Is the approach appropriate?
- Are there simpler alternatives?

### 2. Functionality Review

**Purpose**: Verify correctness and completeness

- [ ] Logic is correct for all edge cases
- [ ] Error handling is comprehensive
- [ ] Input validation is present
- [ ] No race conditions or concurrency issues
- [ ] Side effects are intentional and documented

**Red Flags**:
- Unclear variable/function names
- Missing error handling
- Hardcoded values without explanation
- TODO comments without issue references

### 3. Security Review

**Purpose**: Identify security vulnerabilities

- [ ] No hardcoded secrets or credentials
- [ ] Input sanitization for user data
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (output encoding)
- [ ] Proper authentication/authorization checks
- [ ] No sensitive data in logs

**Check for**:
- `eval()`, `exec()` usage
- Unsafe deserialization
- Path traversal vulnerabilities
- SSRF (Server-Side Request Forgery)

### 4. Performance Review

**Purpose**: Identify performance issues

- [ ] No N+1 query patterns
- [ ] Efficient algorithms used
- [ ] No unnecessary memory allocation
- [ ] Caching is appropriate
- [ ] Database queries are optimized

**Look for**:
- Unnecessary loops
- Redundant computations
- Memory leaks
- Blocking operations in async contexts

### 5. Style and Maintainability

**Purpose**: Ensure code quality and consistency

- [ ] Follows project style guidelines
- [ ] Functions are small and focused
- [ ] Classes/modules have single responsibility
- [ ] Comments explain "why", not "what"
- [ ] No dead code or unused imports

**Metrics**:
- Function length < 50 lines
- Cyclomatic complexity < 10
- No deeply nested conditions

### 6. Testing

**Purpose**: Verify adequate test coverage

- [ ] Tests cover new functionality
- [ ] Edge cases are tested
- [ ] Error paths are tested
- [ ] Tests are readable and maintainable
- [ ] Mocking is appropriate (not over-mocked)

**Coverage Requirements**:
- New code: >80% coverage
- Critical paths: >90% coverage
- Error handling: All branches tested

### 7. Documentation

**Purpose**: Verify documentation is adequate

- [ ] README updated if needed
- [ ] API documentation updated
- [ ] Complex logic has explanatory comments
- [ ] Breaking changes are documented
- [ ] Migration guide if applicable

## Review Checklist

```markdown
## Code Review: <PR Title>

### Summary
- **Scope**: 
- **Risk Level**: Low/Medium/High
- **Estimated Review Time**: 

### Review Results

#### ✅ Approved Items
- [ ] <item>

#### ⚠️ Suggestions (Non-blocking)
- [ ] <suggestion>

#### 🔴 Required Changes
- [ ] <issue>

### Security Check
- [ ] No vulnerabilities found
- [ ] Issues found (see above)

### Performance Check
- [ ] No concerns
- [ ] Issues noted above

### Testing
- [ ] Coverage adequate
- [ ] Tests pass
- [ ] Edge cases covered

### Verdict
- [ ] **Approve** - Ready to merge
- [ ] **Approve with suggestions** - Minor issues, can merge after consideration
- [ ] **Request changes** - Blocking issues must be addressed
- [ ] **Needs discussion** - Architectural concerns need team input
```

## Best Practices

1. **Be Constructive**: Offer solutions, not just criticism
2. **Explain Why**: Provide reasoning for suggestions
3. **Distinguish Severity**: Clearly mark blocking vs. optional issues
4. **Respond Timely**: Aim for review within 24 hours
5. **Learn Together**: Ask questions when unclear

## Escalation

Escalate to senior team member if:
- Security vulnerabilities found
- Architecture concerns
- Breaking changes impact unclear
- Performance impact significant
