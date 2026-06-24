# Experimental Design Single-Call vs Multi-Agent

## Routes
['researcher', 'analyst', 'writer', 'critic', 'done']

## Sources (5)
- [PDF] When Do Multi-Agent LLM Systems Outperform Single ... - ECER 2026: https://ecer.pria.at/archive/ecer-2026/papers/When_Do_Multi-Agent_LLM_Systems_Outperform_Single-Agent_Approaches_An_Empirical_Comparison_Across_Different_Task_Types.pdf
- Single Agent vs Multi-Agent: When to Build a Multi-Agent System: https://towardsdatascience.com/single-agent-vs-multi-agent-when-to-build-a-multi-agent-system
- From single-agent to multi-agent: a comprehensive review of LLM-based legal agents: https://www.oaepublish.com/articles/aiagent.2025.06
- Exploring Design of Multi-Agent LLM Dialogues for Research ... - arXiv: https://arxiv.org/html/2507.08350v1
- Comparing Single-Agent and Multi-Agent Strategies in LLM-Based ...: https://www.mdpi.com/2079-9292/15/8/1661

## Final Answer

# Internal Lab Proposal: Experimental Plan for Comparing Single-Call LLM and Multi-Agent LLM Systems

## 1. Research Question
How do single-call LLM systems compare to multi-agent LLM systems in performing complex research tasks, particularly in terms of efficiency, accuracy, and task completion?

## 2. Hypotheses
- **H1**: Multi-agent LLM systems will outperform single-call LLM systems in complex research tasks due to their ability to decompose tasks and utilize specialized agents.
- **H2**: The performance gains of multi-agent systems will primarily stem from task decomposition rather than increased inference time.

## 3. Task Design
The experiment will involve a series of complex research tasks that require multiple steps and varying degrees of complexity. The tasks will include:
- Bug fixing in code
- Multi-file coding
- CSV data analysis
- Document question answering
- Web research
- Email-style workflow tasks

Each task will be designed to ensure a fair assessment of both systems, with complexity levels calibrated to avoid bias towards either system type.

## 4. Datasets or Source Materials
Datasets will be curated from:
- Publicly available coding repositories (e.g., GitHub)
- CSV datasets from Kaggle
- Document collections from academic journals
- Real-time information retrieval tasks through web scraping

These datasets will provide a diverse range of challenges suitable for evaluating both systems.

## 5. Fair Comparison Setup
To ensure a fair comparison:
- Both systems will operate under the same token budget for each task, ensuring that neither system can leverage more resources unfairly.
- The multi-agent system will be limited to a maximum of three agents to prevent overwhelming advantages.
- Each agent will be assigned specific roles (e.g., retrieval, writing, verification) to simulate real-world applications without excessive resource allocation.

## 6. Metrics
Performance will be evaluated using the following metrics:
- Task completion time
- Accuracy of results (correctness of answers, code functionality)
- User satisfaction ratings (via surveys)
- Resource usage (e.g., tokens consumed)

These metrics will provide a comprehensive view of both systems' performance.

## 7. Human Evaluation Criteria
Human evaluators will assess:
- Clarity and relevance of responses
- Creativity in problem-solving
- Overall effectiveness in task completion
- User experience and satisfaction

This qualitative assessment will complement the quantitative metrics.

## 8. Statistical or Methodological Considerations
- A balanced design will be employed to control for confounding variables, ensuring that both systems are tested under identical conditions.
- Statistical tests (e.g., t-tests, ANOVA) will be used to analyze performance differences, providing a rigorous framework for interpretation.
- Cross-validation will be implemented to ensure robustness of results, minimizing the risk of overfitting.

## 9. Expected Results and Alternative Interpretations
- **Expected Results**: Multi-agent systems are anticipated to show superior performance in complex tasks due to their collaborative nature and task decomposition capabilities.
- **Alternative Interpretations**: If single-call systems perform comparably, it may indicate that task complexity does not necessarily require multi-agent collaboration, or that the single-call system is sufficiently advanced to handle complex tasks independently.

## 10. Red-Team Section: Potential Misleading Aspects
- **Token Budget Manipulation**: If the multi-agent system is allowed to exceed the token budget through parallel processing, it could skew results and misrepresent the system's capabilities.
- **Task Complexity Bias**: If tasks are inherently more suited to multi-agent systems, results may not generalize to simpler tasks, leading to an unfair advantage.
- **Inference Time Advantage**: Longer inference times for multi-agent systems may lead to better results, misattributing success to the multi-agent architecture rather than task decomposition.
- **Agent Coordination Overhead**: The overhead of coordinating multiple agents might not be adequately accounted for, potentially skewing efficiency metrics.

## 11. Revised Experiment Design
To address the critiques from the red-team analysis:
- **Token Budget Enforcement**: Implement strict token limits for both systems, ensuring that the multi-agent system cannot exceed the budget through parallel processing or other means.
- **Task Complexity Balancing**: Design tasks that are equally challenging for both systems, ensuring that neither has an inherent advantage based on task type.
- **Controlled Inference Time**: Limit the total inference time for both systems to isolate performance gains from decomposition rather than time efficiency.
- **Agent Coordination Assessment**: Include metrics to evaluate the efficiency of agent coordination in the multi-agent system, ensuring that any overhead does not unfairly disadvantage the single-call system.

By incorporating these revisions, the experimental design will provide a more accurate and fair comparison of the capabilities of single-call and multi-agent LLM systems in complex research tasks.

### References
- [1] When Do Multi-Agent LLM Systems Outperform Single-Agent Approaches? - ECER 2026. 
- [2] Single Agent vs Multi-Agent: When to Build a Multi-Agent System. 
- [3] From single-agent to multi-agent: a comprehensive review of LLM-based legal agents. 
- [4] Exploring Design of Multi-Agent LLM Dialogues for Research. 
- [5] Comparing Single-Agent and Multi-Agent Strategies in LLM-Based Applications.
