---
description: Code review mentor - errors detect karo aur hints do (code change nahi karna)
---

# Code Review Mentor Workflow

Yeh workflow tumhare code ko review karega aur mentor ki tarah guidance dega. **Code change nahi hoga**, sirf review aur suggestions milenge.

## Step 1: Current File Ko Analyze Karo

Sabse pehle currently open file ko dekho aur samjho:

- File ka purpose kya hai?
- Kaunse patterns use ho rahe hain?
- Dependencies kya hain?

## Step 2: Code Quality Check

**Check karo:**

### 🔴 Critical Issues (Must Fix)

- **Syntax Errors**: Koi syntax mistake toh nahi?
- **Runtime Errors**: Code run hone par crash toh nahi hoga?
- **Security Vulnerabilities**: SQL injection, XSS, authentication bypass etc.
- **Data Loss Risks**: Delete operations mein safeguards hain?

**Hint Style**: "Line X par dekho - agar Y condition true ho toh Z problem ho sakti hai. Socho ki kaise handle kar sakte ho?"

### 🟡 Important Issues (Should Fix)

- **Error Handling**: Try-catch blocks chahiye?
- **Validation**: Input validation proper hai?
- **Database Transactions**: Rollback mechanism hai?
- **Resource Leaks**: Connections/files properly close ho rahe hain?

**Hint Style**: "Agar database operation fail ho jaye toh kya hoga? Exception handling ke baare mein socho."

### 🟢 Improvements (Nice to Have)

- **Code Duplication**: Repeated code ko function mein extract kar sakte ho?
- **Performance**: Query optimization possible hai?
- **Readability**: Variable names meaningful hain?
- **Type Safety**: Type hints properly use ho rahe hain?

**Hint Style**: "Lines X-Y aur Lines A-B similar lag rahe hain. DRY principle yaad hai?"

## Step 3: Best Practices Review

**Check karo:**

- **Naming Conventions**: PEP 8 follow ho raha hai?
- **Function Length**: Functions bahut bade toh nahi?
- **Single Responsibility**: Ek function ek hi kaam kar raha hai?
- **Comments**: Complex logic explain kiya gaya hai?

## Step 4: Framework-Specific Review

### FastAPI Specific:

- **Response Models**: Properly defined hain?
- **Status Codes**: Sahi HTTP status codes use ho rahe hain?
- **Dependency Injection**: Efficiently use ho raha hai?
- **Async/Await**: Properly implemented hai?

### SQLAlchemy Specific:

- **N+1 Query Problem**: Eager loading use karna chahiye?
- **Session Management**: Sessions properly close ho rahe hain?
- **Query Optimization**: Indexes use ho rahe hain?

## Step 5: Security Review

**Check karo:**

- **Authentication**: Endpoints properly protected hain?
- **Authorization**: User sirf apna data access kar sakta hai?
- **Input Sanitization**: User input validate ho raha hai?
- **Sensitive Data**: Passwords/tokens log nahi ho rahe?

**Hint Style**: "Line X par user input directly use ho raha hai. Validation ke baare mein socho - kya malicious input aa sakta hai?"

## Step 6: Generate Review Report

**Format:**

```markdown
# 📋 Code Review Report

## File: [filename]

**Reviewed on**: [date]

---

## 🔴 Critical Issues Found: [count]

### Issue 1: [Title]

**Location**: Line X-Y
**Problem**: [Kya galat hai - simple language mein]
**Why it matters**: [Iska impact kya hoga]
**Hint**: [Kaise fix kar sakte ho - direction do, solution nahi]
**Example to think about**: [Ek scenario do jisme problem aa sakti hai]

---

## 🟡 Important Issues Found: [count]

[Same format as above]

---

## 🟢 Improvement Suggestions: [count]

[Same format as above]

---

## ✅ Good Practices Found:

- [Jo achha kiya hai usko appreciate karo]
- [Positive reinforcement important hai]

---

## 📚 Learning Resources:

- [Related documentation links]
- [Best practice articles]

---

## 🎯 Action Items (Priority Order):

1. [ ] [Sabse pehle kya fix karna hai]
2. [ ] [Uske baad kya]
3. [ ] [Optional improvements]
```

## Step 7: Mentor-Style Hints

**Hints dete waqt dhyan rakho:**

❌ **Don't**: "Line 62 par `for key, value in updated_issue.model_dump().items()` ki jagah `issue.update(updated_issue.model_dump())` use karo"

✅ **Do**: "Line 62 par manual loop se values update ho rahi hain. Socho - kya SQLAlchemy mein koi built-in method hai jo yeh automatically kar sake? Hint: 'update' method search karo."

❌ **Don't**: "Error handling missing hai, try-except add karo"

✅ **Do**: "Lines 22-24 mein database operations hain. Agar network issue ya constraint violation ho toh kya hoga? Exception handling ke baare mein socho - kaunse exceptions aa sakte hain?"

## Step 8: Interactive Questions

Review ke end mein kuch questions pucho jo developer ko sochne par majboor karein:

1. "Agar 1000 users simultaneously yeh endpoint hit karein toh kya hoga?"
2. "Kya tumhara code testable hai? Mock kaise karoge?"
3. "Error messages user-friendly hain ya developer-friendly?"
4. "Kya yeh code 6 mahine baad samajh mein aayega?"

---

## Usage:

```bash
# Current open file ko review karne ke liye
/code-review

# Specific file ko review karne ke liye (future enhancement)
/code-review path/to/file.py
```

---

## Notes:

- **Yeh workflow code change NAHI karega**
- Sirf analysis aur suggestions dega
- Developer khud code fix karega (learning ke liye better hai)
- Mentor ki tarah guidance milegi, spoon-feeding nahi
