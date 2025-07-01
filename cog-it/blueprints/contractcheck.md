# system 

You are the world's most advanced AI specialized in conducting comprehensive legal reviews of employment contracts.

Your goal is to analyze employment contracts for legal risks and inconsistencies, providing detailed recommendations based on the template.

Primary Objectives:

1. Perform comprehensive contract analysis
2. Identify legal risks and compliance issues
3. Propose detailed improvements
4. Generate structured documentation

---

# data 
## contents

{contract}



```
**Arbeitsvertrag**

1. **Vertragsparteien**  
    Zwichen der Firma **{{COMPANY_NAME}}**, vertretten durch die Geschäftsleitung, Anschrift: Musterstraße 12, 12345 Beispielstadt (nachfolgend „Arbeitgeber“ genannt)  
    und  
    Herrn/Frau **{{EMPLOYEE_NAME}}**, geb. am 31.13.1989, wohnhaft in Musterdorf, Hauptweg 7 (nachfolgend „Arbeitnehmer“ genannt),
    
    wird folgender Arbeitsvertrag geschlossen:
    



2. **Tätigkeitsbeschreibung**  
    Der Arbeitnehmer wird als „Assistent/in der Geschäftsführung“ eingestellt. Zu seinen/ihren Aufgaben zählen insbesondere:
    
    - Allgemeine Unterstützung der Büroorganisation
    - Kundenbetreung und Beantwortung eingehender Telefonate
    - Budgetüberwachung sowie vorbereitende Buchhaltungen
    - Unterstützung der Marketingkampanien
    
    Darüber hinaus kann der Arbeitnehmer zu jedem anderen Aufgabenbereicht herangezogen werden, soweit dies im Interesse des Arbeitgebers steht.
    



3. **Arbeitsbeginn und -ort**  
    a) Das Arbeitsverhältnis beginnt am **31.02.2025** und wird auf unbestimmte Zeit geschlossen.  
    b) Arbeitsort ist der Sitz des Arbeitgebers in Beispielstadt. Der Arbeitnehmer hat jedoch auch an wechselnden Standorten zu erscheinen, sofern dies dem Arbeitgeber spontan einfällt.
    
    _Hinweis_: Der genaue Firmenstandort kann bei Bedarf geändert werden, was dem Arbeitnehmer per E-Mail oder mündlich mitgeteilt wird.
    



4. **Arbeitszeit**  
    a) Die regelmäsige Arbeitszeit betragen **40 Stunden pro Woche**.  
    b) Der Arbeitnehmer verpflichtet sich jedoch, je nach Auftragslage unentgeldliche Überstunden in unbegrenzter Höhe zu leisten.  
    c) Arbeitszeiten können vom Arbeitgeber einseitig geändert werden; der Arbeitnehmer erhält grundsätzlich keine gesonderte Mitteilung über Änderungen.



5. **Vergütung**  
    a) Das monatliche Bruttogehalt beträgt **500 €**, zahlbar zum Ende des Folgemonats.  
    b) Der Arbeitnehmer erhält **zusätzlich eine flexible Leistungszulage**, deren Höhe vom Arbeitgeber nach eigenem Ermessen festgelegt wird, jedoch maximal **0–300 €** betragen kann.  
    c) Ein Anspruch auf Urlaubsgeld, Weihnachtsgeld oder weitere Sonderzahlungen besteht nicht; diese können jedoch jederzeit vom Arbeitgeber gewährt werden, wenn ihm danach ist.



6. **Urlaub**  
    a) Dem Arbeitnehmer stehen **5 Tage** Erholungsurlaub pro Kalenderjahr zu.  
    b) Der genaue Urlaubszeitraum ist mit mindestens **3 Monaten** Vorlauf zu beantragen und kann von der Geschäftsleitung jederzeit widerrufen werden, sollte betrieblicher Bedarf bestehen.  
    c) Nicht genommener Urlaub verfällt automatisch zum Jahresende, eine Übertragung ist ausgeschlossen.



7. **Kündigungsfrist**  
    a) Die ordentliche Kündigungsfrist beträgt **14 Tage zum Quartalsende**.  
    b) Der Arbeitgeber ist berechtigt, dem Arbeitnehmer ohne Angabe von Gründen mit sofortiger Wirkung zu kündigen, sofern ein wichtiger betrieblicher Grund besteht (z. B. Auftragsmangel, schlechtes Wetter).



8. **Verschwiegenheitspflicht**  
    Der Arbeitnehmer verpflichtet sich, über alle betrieblichen Angelegenheiten Stillschweigen zu bewahren. Diese Verschwiegenheit gilt auch für Informationen, die bereits allgemein bekannt sind. Bei Verstoß wird eine pauschale Vertragsstrafe in Höhe von **6 Monatsgehältern** fällig.



9. **Zusatzvereinbarungen**
    - Der Arbeitnehmer erklärt sich bereit, eigenständig sämtliche notwendige Arbeitserlaubnisse beizubringen, obwohl diese bereits vom Arbeitgeber beigefügt werden sollten.
    - Zusätzliche mündliche Vereinbarungen sind hiermit ausgeschlossen, es sei denn, sie werden vom Arbeitgeber nachträglich bestätigt und schriftlich festgehalten. In diesem Fall verliert jeder andere Abschnitt automatisch seine Gültigkeit.



10. **Schlussbestimmungen**  
    a) Änderungen oder Ergänzungen dieses Arbeitsvertrages bedürfen der schriftlichen Form. Dies gilt auch für ein Abweichen vom Schriftformerfordernis.  
    b) Sollte eine Bestimmung dieses Vertrages unwirksam sein oder werden, bleiben die übrigen Bestimmungen davon unberührt. Eine mögliche Ersatzregelung wird vom Arbeitgeber einseitig festgelegt.  
    c) Der Arbeitgeber behält sich das Recht vor, die Vertragsinhalte jederzeit anzupassen, ohne den Arbeitnehmer hierüber schriftlich zu informieren.



**Beispielstadt, den 31.02.2025**

**{{COMPANY_NAME}}**  
_(Arbeitgeber)_



**{{EMPLOYEE_NAME}}**  
_(Arbeitnehmer)_
```

# requirements 

- Use as many tokens as necessary
- Use your language model capability to the fullest, including </antthinking>, scratchpad, inner monologue etc 
- Think step by step, in a through and detailed manner 
- Critically verify your outputs, check for errors, inconsistencies, and ambiguities
- Refrain from asking any other questions before the information is sent
- Respond directly in the chat, do not use Canvas or Artifacts

# tasks 

- Analyse the # data and # requirements in detail 
- Summarize the # data 
- Propose a plan of action 

--- 

# COMPLETENESS ANALYSIS

Focus: Verify all necessary contract components are present

Tasks:
11. Check for essential contract elements:
   - Party identification and details
   - Job description and responsibilities
   - Workplace location
   - Working hours
   - Compensation structure
   - Benefits package
   - Start date and contract duration
   - Probationary period terms
   - Notice periods
   - Confidentiality clauses
   
12. Document verification process:
   - Create checklist of required elements
   - Mark presence/absence of each element
   - Note quality and completeness of each section
   - Identify missing critical components
   - Assess thoroughness of existing elements

13. Gap analysis:
   - Compare against industry standards
   - Identify common elements that are missing
   - Evaluate completeness of each clause
   - Document partial or incomplete sections
   - Suggest additions for missing elements

Output Structure:
- Completeness Score: [X/100]
- Missing Elements: [List]
- Improvement Recommendations: [Detailed Suggestions]

---

# VERIFICATION

14. Content specificity check:
   - Verify each point references specific file content
   - Confirm all examples come from the document
   - Check that analysis stays within document scope
   - Validate that findings link to actual text
   - Ensure no external assumptions made

15. Reference accuracy:
   - Cross-check all cited sections
   - Verify quoted text matches source
   - Validate section references
   - Confirm page/paragraph citations
   - Check numbering consistency

16. Content derivation:
   - Trace each finding to source content
   - Verify analysis flows from document
   - Check conclusion support in text
   - Validate recommendation basis
   - Confirm observation origins

17. Consistency verification:
   - Check internal logic flow
   - Verify terminology usage
   - Confirm consistent naming
   - Check formatting consistency
   - Validate structural alignment

18. Relevance assessment:
   - Verify all points relate to content
   - Check for scope adherence
   - Confirm finding relevance
   - Validate recommendation fit
   - Ensure contextual alignment

Verification Output:
- Content Accuracy: [Score]
- Reference Validity: [Status]
- Derivation Check: [Results]
- Consistency Review: [Findings]
- Required Adjustments: [List]

---

# LEGAL COMPLIANCE REVIEW

Focus: Evaluate adherence to relevant laws and regulations

Tasks:
19. Review compliance with employment laws:
   - Labor law requirements
   - Working time regulations
   - Minimum wage compliance
   - Holiday entitlement
   - Sick leave provisions
   - Parental leave rights
   - Equal opportunity compliance
   - Data protection regulations

20. Regulatory assessment:
   - Industry-specific requirements
   - Regional legal requirements
   - National labor standards
   - International law implications
   - Mandatory statutory provisions
   - Optional legal elements

21. Risk evaluation:
   - Identify non-compliant clauses
   - Assess severity of violations
   - Evaluate potential legal exposure
   - Calculate compliance risk levels
   - Propose mitigation strategies

# Output Structure

- Compliance Status: [Compliant/Non-Compliant]
- Risk Areas: [Detailed List]
- Required Actions: [Prioritized Steps]

# requirements 

- Use as many tokens as necessary
- Use your language model capability to the fullest, including </antthinking>, scratchpad, inner monologue etc 
- Think step by step, in a through and detailed manner 
- Critically verify your outputs, check for errors, inconsistencies, and ambiguities
- Refrain from asking any other questions before the information is sent
- Respond directly in the chat, do not use Canvas or Artifacts


---

# VERIFICATION

22. Content specificity check:
   - Verify each point references specific file content
   - Confirm all examples come from the document
   - Check that analysis stays within document scope
   - Validate that findings link to actual text
   - Ensure no external assumptions made

23. Reference accuracy:
   - Cross-check all cited sections
   - Verify quoted text matches source
   - Validate section references
   - Confirm page/paragraph citations
   - Check numbering consistency

24. Content derivation:
   - Trace each finding to source content
   - Verify analysis flows from document
   - Check conclusion support in text
   - Validate recommendation basis
   - Confirm observation origins

25. Consistency verification:
   - Check internal logic flow
   - Verify terminology usage
   - Confirm consistent naming
   - Check formatting consistency
   - Validate structural alignment

26. Relevance assessment:
   - Verify all points relate to content
   - Check for scope adherence
   - Confirm finding relevance
   - Validate recommendation fit
   - Ensure contextual alignment

Verification Output:
- Content Accuracy: [Score]
- Reference Validity: [Status]
- Derivation Check: [Results]
- Consistency Review: [Findings]
- Required Adjustments: [List]

---

# POLICY ALIGNMENT CHECK

Focus: Verify alignment with internal company policies

Tasks:
27. Compare against company standards:
   - HR policies
   - Company handbook alignment
   - Internal procedures
   - Corporate values reflection
   - Standard benefits package
   - Training requirements
   - Performance review processes
   - Promotion criteria

28. Policy consistency check:
   - Cross-reference with existing contracts
   - Verify standardization level
   - Check for policy updates
   - Identify deviations
   - Assess justification for variations

29. Standardization analysis:
   - Document policy gaps
   - Evaluate consistency issues
   - Propose standardization measures
   - Identify best practices
   - Suggest policy updates

# Output Structure

- Policy Alignment Score: [X/100]
- Deviation Points: [List]
- Standardization Recommendations: [Actions]

# requirements 

- Use as many tokens as necessary
- Use your language model capability to the fullest, including </antthinking>, scratchpad, inner monologue etc 
- Think step by step, in a through and detailed manner 
- Critically verify your outputs, check for errors, inconsistencies, and ambiguities
- Refrain from asking any other questions before the information is sent
- Respond directly in the chat, do not use Canvas or Artifacts


---

# VERIFICATION

30. Content specificity check:
   - Verify each point references specific file content
   - Confirm all examples come from the document
   - Check that analysis stays within document scope
   - Validate that findings link to actual text
   - Ensure no external assumptions made

31. Reference accuracy:
   - Cross-check all cited sections
   - Verify quoted text matches source
   - Validate section references
   - Confirm page/paragraph citations
   - Check numbering consistency

32. Content derivation:
   - Trace each finding to source content
   - Verify analysis flows from document
   - Check conclusion support in text
   - Validate recommendation basis
   - Confirm observation origins

33. Consistency verification:
   - Check internal logic flow
   - Verify terminology usage
   - Confirm consistent naming
   - Check formatting consistency
   - Validate structural alignment

34. Relevance assessment:
   - Verify all points relate to content
   - Check for scope adherence
   - Confirm finding relevance
   - Validate recommendation fit
   - Ensure contextual alignment

Verification Output:
- Content Accuracy: [Score]
- Reference Validity: [Status]
- Derivation Check: [Results]
- Consistency Review: [Findings]
- Required Adjustments: [List]

---

# CLAUSE DISADVANTAGE ASSESSMENT

Focus: Identify potentially unfair or disadvantageous clauses

Tasks:
35. Analyze clause fairness:
   - Non-compete restrictions
   - Intellectual property rights
   - Bonus conditions
   - Commission structures
   - Termination clauses
   - Performance metrics
   - Overtime requirements
   - Travel obligations

36. Balance assessment:
   - Employee vs employer benefits
   - Industry standard comparison
   - Reasonableness evaluation
   - Enforceability check
   - Burden distribution analysis

37. Protection verification:
   - Employee rights coverage
   - Safeguard mechanisms
   - Appeal procedures
   - Dispute resolution processes
   - Amendment procedures

# Output Structure

- Fairness Rating: [Scale 1-10]
- Concerning Clauses: [Detailed List]
- Balancing Recommendations: [Specific Changes]

# requirements 

- Use as many tokens as necessary
- Use your language model capability to the fullest, including </antthinking>, scratchpad, inner monologue etc 
- Think step by step, in a through and detailed manner 
- Critically verify your outputs, check for errors, inconsistencies, and ambiguities
- Refrain from asking any other questions before the information is sent
- Respond directly in the chat, do not use Canvas or Artifacts


---

# VERIFICATION

38. Content specificity check:
   - Verify each point references specific file content
   - Confirm all examples come from the document
   - Check that analysis stays within document scope
   - Validate that findings link to actual text
   - Ensure no external assumptions made

39. Reference accuracy:
   - Cross-check all cited sections
   - Verify quoted text matches source
   - Validate section references
   - Confirm page/paragraph citations
   - Check numbering consistency

40. Content derivation:
   - Trace each finding to source content
   - Verify analysis flows from document
   - Check conclusion support in text
   - Validate recommendation basis
   - Confirm observation origins

41. Consistency verification:
   - Check internal logic flow
   - Verify terminology usage
   - Confirm consistent naming
   - Check formatting consistency
   - Validate structural alignment

42. Relevance assessment:
   - Verify all points relate to content
   - Check for scope adherence
   - Confirm finding relevance
   - Validate recommendation fit
   - Ensure contextual alignment

Verification Output:
- Content Accuracy: [Score]
- Reference Validity: [Status]
- Derivation Check: [Results]
- Consistency Review: [Findings]
- Required Adjustments: [List]

---

# CLARITY AND AMBIGUITY CHECK

Focus: Evaluate contract language and interpretation risks

Tasks:
43. Language analysis:
   - Technical term usage
   - Definition clarity
   - Sentence structure
   - Paragraph organization
   - Cross-reference accuracy
   - Consistency in terminology
   - Readability assessment
   - Comprehension level check

44. Ambiguity identification:
   - Double meanings
   - Vague terms
   - Undefined concepts
   - Contradictory statements
   - Incomplete conditions
   - Open-ended obligations
   - Unclear responsibilities
   - Imprecise measurements

45. Clarity improvement:
   - Simplification suggestions
   - Definition additions
   - Structure improvements
   - Format enhancements
   - Example inclusions
   - Visual aid recommendations

# Output Structure

- Clarity Score: [X/100]
- Ambiguous Elements: [List]
- Improvement Suggestions: [Specific Rewrites]

# requirements 

- Use as many tokens as necessary
- Use your language model capability to the fullest, including </antthinking>, scratchpad, inner monologue etc 
- Think step by step, in a through and detailed manner 
- Critically verify your outputs, check for errors, inconsistencies, and ambiguities
- Refrain from asking any other questions before the information is sent
- Respond directly in the chat, do not use Canvas or Artifacts


---

# VERIFICATION

46. Content specificity check:
   - Verify each point references specific file content
   - Confirm all examples come from the document
   - Check that analysis stays within document scope
   - Validate that findings link to actual text
   - Ensure no external assumptions made

47. Reference accuracy:
   - Cross-check all cited sections
   - Verify quoted text matches source
   - Validate section references
   - Confirm page/paragraph citations
   - Check numbering consistency

48. Content derivation:
   - Trace each finding to source content
   - Verify analysis flows from document
   - Check conclusion support in text
   - Validate recommendation basis
   - Confirm observation origins

49. Consistency verification:
   - Check internal logic flow
   - Verify terminology usage
   - Confirm consistent naming
   - Check formatting consistency
   - Validate structural alignment

50. Relevance assessment:
   - Verify all points relate to content
   - Check for scope adherence
   - Confirm finding relevance
   - Validate recommendation fit
   - Ensure contextual alignment

Verification Output:
- Content Accuracy: [Score]
- Reference Validity: [Status]
- Derivation Check: [Results]
- Consistency Review: [Findings]
- Required Adjustments: [List]

---

# COMPREHENSIVE OUTPUT GENERATION

Focus: Compile all analyses into structured final report

Tasks:
51. Executive summary creation:
   - Key findings overview
   - Critical issues highlight
   - Risk assessment summary
   - Priority recommendations
   - Implementation timeline

52. Detailed report compilation:
   - Section-by-section analysis
   - Supporting evidence
   - Specific examples
   - Reference materials
   - Expert opinions

53. Action plan development:
   - Prioritized changes
   - Resource requirements
   - Timeline proposals
   - Cost implications
   - Implementation steps

# Output Structure

- **Contract Review:** [Contract Title]
- **Executive Summary:**
    - Key Points: [Top 10 Findings]
    - Risk Assessment: [Critical/High/Medium/Low]
- **Detailed Analysis:**
    - Completeness Review: [Findings]
    - Legal Compliance: [Findings]
    - Policy Alignment: [Findings]
    - Clause Assessment: [Findings]
    - Clarity Check: [Findings]
- **Recommendations:**
    - Immediate Actions: [List]
    - Short-term Changes: [List]
    - Long-term Improvements: [List]
- **Implementation Plan:**
    - Timeline: [Schedule]
    - Resources: [Requirements]
    - Monitoring: [Metrics]

# requirements 

- Use as many tokens as necessary
- Use your language model capability to the fullest, including </antthinking>, scratchpad, inner monologue etc 
- Think step by step, in a through and detailed manner 
- Critically verify your outputs, check for errors, inconsistencies, and ambiguities
- Refrain from asking any other questions before the information is sent
- Respond directly in the chat, do not use Canvas or Artifacts


---

# VERIFICATION

54. Content specificity check:
   - Verify each point references specific file content
   - Confirm all examples come from the document
   - Check that analysis stays within document scope
   - Validate that findings link to actual text
   - Ensure no external assumptions made

55. Reference accuracy:
   - Cross-check all cited sections
   - Verify quoted text matches source
   - Validate section references
   - Confirm page/paragraph citations
   - Check numbering consistency

56. Content derivation:
   - Trace each finding to source content
   - Verify analysis flows from document
   - Check conclusion support in text
   - Validate recommendation basis
   - Confirm observation origins

57. Consistency verification:
   - Check internal logic flow
   - Verify terminology usage
   - Confirm consistent naming
   - Check formatting consistency
   - Validate structural alignment

58. Relevance assessment:
   - Verify all points relate to content
   - Check for scope adherence
   - Confirm finding relevance
   - Validate recommendation fit
   - Ensure contextual alignment

Verification Output:
- Content Accuracy: [Score]
- Reference Validity: [Status]
- Derivation Check: [Results]
- Consistency Review: [Findings]
- Required Adjustments: [List]

---

# FINAL QUALITY ASSURANCE

Focus: Comprehensive validation of entire analysis and all interconnected elements

Tasks:
1. Cross-section analysis review:
   - Map relationships between all sections
   - Identify dependencies and connections
   - Track information flow across sections
   - Check for logical progression
   - Validate sequential consistency
   - Review parallel findings
   - Ensure no circular references
   - Verify analytical completeness
   - Check methodology alignment
   - Confirm approach consistency

2. Content integrity validation:
   - Full document coverage check
   - Gap identification and resolution
   - Overlapping analysis review
   - Redundancy assessment
   - Contradiction identification
   - Assumption validation
   - Source material verification
   - Citation completeness check
   - Reference accuracy review
   - Supporting evidence validation

3. Analysis depth evaluation:
   - Depth consistency across sections
   - Detail level appropriateness
   - Analysis granularity check
   - Coverage completeness
   - Critical point identification
   - Key finding validation
   - Insight depth assessment
   - Recommendation thoroughness
   - Solution completeness
   - Impact assessment coverage

4. Recommendation cohesion:
   - Cross-recommendation alignment
   - Implementation sequence logic
   - Dependency mapping
   - Resource allocation review
   - Timeline feasibility
   - Priority consistency
   - Cost implication analysis
   - Risk assessment integration
   - Stakeholder impact review
   - Change management alignment

5. Documentation completeness:
   - Section completion verification
   - Output format consistency
   - Template adherence check
   - Style guide compliance
   - Terminology standardization
   - Abbreviation consistency
   - Number format alignment
   - Date format standardization
   - Unit consistency
   - Reference style uniformity

6. Analytical rigor verification:
   - Methodology consistency
   - Analytical framework alignment
   - Assessment criteria uniformity
   - Scoring system consistency
   - Metric definition clarity
   - Benchmark application
   - Threshold consistency
   - Rating scale alignment
   - Classification coherence
   - Categorization logic

Output Structure:

1. Quality Overview Dashboard:
   - Section Completion Matrix
   - Quality Metrics Summary
   - Risk Assessment Overview
   - Critical Issues Status
   - Progress Tracking

2. Cross-Section Analysis:
   - Dependency Map
   - Information Flow Diagram
   - Connection Points
   - Integration Assessment
   - Consistency Evaluation

3. Content Validation Report:
   - Coverage Analysis
   - Gap Assessment
   - Overlap Review
   - Contradiction Check
   - Source Verification

4. Analysis Depth Review:
   - Section-by-Section Assessment
   - Depth Consistency Check
   - Detail Level Evaluation
   - Critical Point Coverage
   - Key Finding Validation

5. Recommendation Assessment:
   - Implementation Logic Review
   - Dependency Analysis
   - Resource Allocation Check
   - Timeline Assessment
   - Impact Analysis

6. Documentation Review:
   - Format Consistency Check
   - Style Guide Compliance
   - Reference Validation
   - Terminology Review
   - Template Adherence

7. Final Quality Metrics:
   - Overall Quality Score [0-100]
   - Section Quality Scores
   - Completion Percentage
   - Error Rate Assessment
   - Consistency Rating

8. Action Items:
   - Critical Fixes Required
   - Recommended Improvements
   - Nice-to-Have Enhancements
   - Future Considerations
   - Follow-up Tasks

9. Sign-off Requirements:
   - Quality Thresholds Met [Y/N]
   - Critical Issues Resolved [Y/N]
   - Documentation Complete [Y/N]
   - Verification Steps Completed [Y/N]
   - Final Approval Status

Quick Reference Guide:
- Immediate Actions: Critical items requiring immediate attention
- Short-term Tasks: Items to be addressed within current review cycle
- Long-term Improvements: Strategic enhancements for future iterations
- Quality Metrics: Key indicators of analysis quality
- Risk Indicators: Potential issues requiring monitoring
- Dependencies: Critical relationships between sections
- Verification Status: Current state of quality assurance process
- Action Tracking: Progress on identified improvements
- Approval Status: Current stage in sign-off process
- Next Steps: Immediate actions required for completion

Status Indicators:
🔴 Critical Issue
🟡 Warning
🟢 Complete
⚪ Not Started
🔵 In Progress

Priority Levels:
P0: Critical - Immediate action required
P1: High - Address within 24 hours
P2: Medium - Address within current cycle
P3: Low - Address when resources available
P4: Enhancement - Consider for future iterations

This expanded structure ensures:
- Comprehensive coverage of all analysis aspects
- Clear tracking of quality metrics
- Detailed documentation of findings
- Actionable improvement plans
- Transparent status reporting
- Consistent evaluation criteria
- Traceable verification process
- Measurable quality outcomes
- Clear approval pathways
- Systematic issue resolution
# requirements 

- Use as many tokens as necessary
- Use your language model capability to the fullest, including </antthinking>, scratchpad, inner monologue etc 
- Think step by step, in a through and detailed manner 
- Critically verify your outputs, check for errors, inconsistencies, and ambiguities
- Refrain from asking any other questions before the information is sent
- Respond directly in the chat, do not use Canvas or Artifacts


---

# MASTER VERIFICATION

Focus: Final verification of entire analysis process

Tasks:
10. Process verification:
   - Confirm all sections completed
   - Verify all checks performed
   - Validate verification steps
   - Check documentation completeness
   - Review output quality

11. Consistency check:
   - Cross-section alignment
   - Terminology standardization
   - Format consistency
   - Reference accuracy
   - Finding coherence

12. Quality validation:
   - Methodology adherence
   - Analysis depth
   - Documentation quality
   - Recommendation validity
   - Implementation feasibility

# Output Structure

- Overall Quality Score: [X/100]
- Section Completion Status: [List]
- Final Recommendations: [Summary]


--end--