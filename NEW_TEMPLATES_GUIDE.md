# New Templates Guide

## 🆕 Business Planner Template

### Overview
The Business Planner template orchestrates four AI business experts to collaboratively develop comprehensive, professional business plans through iterative discussion.

### Participants

#### 1. Innovation Strategist (Temperature: 0.8)
**Role**: Generates and refines creative business ideas
**Focus Areas**:
- Unique value propositions
- Target market identification
- Competitive advantages
- Growth potential and scalability

**Communication Style**: Concise (3-4 key points), creative, strategic

#### 2. Financial Analyst (Temperature: 0.4)
**Role**: Evaluates financial viability and sustainability
**Focus Areas**:
- Revenue models and pricing strategies
- Cost structures and margins
- Funding requirements and ROI
- Financial projections and milestones

**Communication Style**: Concise (3-4 bullet points), data-driven, analytical

#### 3. Operations Planner (Temperature: 0.5)
**Role**: Translates strategy into executable plans
**Focus Areas**:
- Operational workflows and processes
- Resource requirements (team, tools, infrastructure)
- Implementation timeline and milestones
- Risk mitigation strategies

**Communication Style**: Concise (3-4 key areas), actionable, structured

#### 4. Market Researcher (Temperature: 0.6)
**Role**: Analyzes markets, customers, and competition
**Focus Areas**:
- Market size and opportunities
- Customer segments and pain points
- Competitive landscape analysis
- Market entry and positioning strategies

**Communication Style**: Concise (3-4 focused points), insight-driven, evidence-based

### Usage Tips

1. **Initial Prompt Format**:
   ```
   Business idea/prompt: [Describe your business idea or industry]
   
   Example: "A subscription-based meal kit service using locally-sourced, 
   organic ingredients, targeting busy professionals who value healthy eating"
   ```

2. **Let the Conversation Flow**:
   - Each expert will build on others' insights
   - After 3-4 rounds, you'll have a comprehensive plan covering:
     - Business model and value proposition
     - Financial projections and funding needs
     - Operational implementation plan
     - Market strategy and positioning

3. **Interrupt When Needed**:
   - Use manual mode to add specific requirements
   - Ask for deeper analysis on particular areas
   - Request refinements or alternatives

### Example Output Structure

**Round 1**: Innovation Strategist proposes core concept and unique value
**Round 2**: Financial Analyst evaluates revenue potential and costs
**Round 3**: Operations Planner outlines implementation steps
**Round 4**: Market Researcher provides market validation and positioning
**Rounds 5-8**: Iterative refinement and integration of all perspectives

---

## 🆕 Program Developer Template

### Overview
The Program Developer template brings together four AI developers to design, implement, test, and document complete software programs through collaborative development.

### Participants

#### 1. Software Architect (Temperature: 0.4)
**Role**: Designs system architecture and technology choices
**Deliverables**:
- Architecture diagrams (text/ASCII format)
- Technology stack recommendations
- Module/component breakdown
- Initial project structure and starter code

**Communication Style**: 
- **Explanations**: Brief (2-3 sentences)
- **Code**: Complete, well-structured implementations

#### 2. Full-Stack Developer (Temperature: 0.3)
**Role**: Implements features with production-ready code
**Deliverables**:
- Complete functions, classes, and modules
- Full file implementations (not snippets)
- Proper imports, error handling, and logging
- Type hints and comprehensive comments

**Communication Style**:
- **Explanations**: Minimal (1-2 sentences)
- **Code**: Comprehensive, runnable, production-quality

#### 3. Code Reviewer & Optimizer (Temperature: 0.3)
**Role**: Reviews, debugs, and optimizes code
**Deliverables**:
- Specific bug fixes with explanations
- Security vulnerability patches
- Performance optimizations
- Refactored code improvements
- Complete updated code (not just diffs)

**Communication Style**:
- **Reviews**: Focused (3-4 key points)
- **Code Fixes**: Complete, improved implementations

#### 4. Testing & Documentation Specialist (Temperature: 0.4)
**Role**: Creates comprehensive tests and documentation
**Deliverables**:
- Complete test suites (unit, integration, e2e)
- README with installation and usage
- API documentation
- Code examples and tutorials
- Deployment guides

**Communication Style**:
- **Explanations**: Brief (2-3 sentences)
- **Deliverables**: Complete, ready-to-use

### Usage Tips

1. **Initial Prompt Format**:
   ```
   Program idea/requirement: [Describe what you want to build]
   
   Example: "A Python CLI tool for managing TODO lists with categories, 
   priorities, due dates, and export to JSON/CSV. Include colored terminal 
   output and persistent storage."
   ```

2. **Development Workflow**:
   - **Round 1**: Architect designs structure and provides starter code
   - **Round 2**: Developer implements core features
   - **Round 3**: Reviewer identifies issues and optimizes
   - **Round 4**: Testing specialist adds tests and docs
   - **Rounds 5+**: Iterative enhancement and feature addition

3. **Best Practices**:
   - Let all four participants contribute before requesting changes
   - Each round builds incrementally on previous code
   - Request specific features or modules one at a time
   - Use manual mode to guide development direction

4. **Getting Complete Programs**:
   - The template is optimized for COMPLETE code output
   - Explanations are minimal to maximize code in context
   - After 4-6 rounds, you'll have a production-ready program

### Example Development Cycle

```
Round 1 (Architect):
- Project structure
- Technology choices (e.g., Click for CLI, SQLite for storage)
- Base classes and interfaces
- Starter code skeleton

Round 2 (Developer):
- Complete implementation of core features
- Full CLI commands with argparse/click
- Database operations
- Error handling

Round 3 (Reviewer):
- Security fixes (input validation, SQL injection prevention)
- Performance improvements (caching, query optimization)
- Code quality improvements (refactoring, patterns)
- Complete updated codebase

Round 4 (Testing):
- pytest test suite with fixtures
- Unit tests for all functions
- Integration tests for workflows
- README with examples
- requirements.txt

Round 5+ (Iterative):
- Add new features (export, import, search)
- Enhance UI (colors, formatting)
- Add advanced capabilities
```

### What You Get

After a complete session, you'll have:
- ✅ Full source code (all files)
- ✅ Comprehensive test suite
- ✅ Complete documentation
- ✅ Installation/deployment guide
- ✅ Production-ready, working program

---

## 🎯 When to Use Each Template

### Use Business Planner When:
- ✅ Validating a business idea
- ✅ Creating a startup pitch deck
- ✅ Planning market entry strategy
- ✅ Evaluating business opportunities
- ✅ Developing go-to-market plans
- ✅ Analyzing competitive positioning

### Use Program Developer When:
- ✅ Building a new tool or application
- ✅ Prototyping an idea quickly
- ✅ Generating boilerplate code
- ✅ Learning new frameworks/technologies
- ✅ Creating proof-of-concepts
- ✅ Automating tasks with custom scripts

---

## 💡 Pro Tips

### For Business Planning:
1. Start broad, then narrow focus based on expert feedback
2. Let the conversation run 6-8 rounds for comprehensive coverage
3. Ask for specific sections (e.g., "Focus on customer acquisition strategy")
4. Request financial models or market sizing calculations

### For Program Development:
1. Be specific about requirements upfront
2. Mention preferred libraries/frameworks if you have preferences
3. Let all 4 experts contribute before interrupting
4. Ask for specific features incrementally
5. Request explanations of architectural decisions when needed
6. Copy code directly from responses - it's ready to run!

---

## 🔧 Customization

Both templates use **Gemini 2.0 Flash** as the default model for:
- ✅ Fast response times
- ✅ High-quality output
- ✅ Cost-effectiveness
- ✅ Large context windows (perfect for code)

You can modify the templates to use different models by editing the JSON files in `templates_config/`.

---

## 📊 Expected Results

### Business Planner Output (after 6-8 rounds):
- Executive summary and value proposition
- Market analysis and target customers
- Financial projections (3-5 year outlook)
- Operational plan with milestones
- Competitive analysis and positioning
- Risk assessment and mitigation
- Go-to-market strategy

### Program Developer Output (after 4-6 rounds):
- Complete, working source code
- All necessary files and structure
- Comprehensive test coverage
- Full documentation
- Installation/deployment instructions
- Example usage and tutorials
- Production-ready application

---

*Happy planning and coding! 🚀*
