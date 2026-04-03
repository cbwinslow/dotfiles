"""
Intelligent Memory Management System for Letta Integration

Based on agent-zero patterns:
- Automatic recall before LLM calls
- Trigger-based memory saving
- Solution extraction
- Fragment memorization
- Cross-agent memory sharing

This module provides the "brain" that tells AI agents WHEN to save vs recall memories.
"""

import re
import json
import hashlib
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class MemoryTrigger(Enum):
    """Triggers that indicate something should be saved to memory"""
    SOLUTION_FOUND = "solution_found"          # Successful solution to problem
    ERROR_OCCURRED = "error_occurred"          # Error with solution
    IMPORTANT_FACT = "important_fact"          # Key information learned
    USER_PREFERENCE = "user_preference"        # User likes/dislikes
    CODE_SNIPPET = "code_snippet"              # Useful code example
    BEST_PRACTICE = "best_practice"            # Recommended approach
    CONTEXT_SWITCH = "context_switch"          # Moving to new topic
    SESSION_END = "session_end"                # Conversation ending
    TOOL_SUCCESS = "tool_success"              # Successful tool execution
    INSIGHT = "insight"                        # General insight/learning


@dataclass
class Memory:
    """Represents a memory entry"""
    content: str
    trigger: MemoryTrigger
    agent: str
    session_id: str
    timestamp: str
    tags: List[str]
    importance: int  # 1-10
    embedding_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "trigger": self.trigger.value
        }


class MemoryAnalyzer:
    """
    Analyzes conversations to determine WHEN to save memories.
    Implements agent-zero style trigger detection.
    """
    
    # Patterns that indicate important information
    SOLUTION_PATTERNS = [
        r"(solution|fix|resolved|works now|succeeded|completed successfully)",
        r"(here's how|to solve this|the answer is|working solution)",
        r"(final result|output shows|it now works)",
    ]
    
    ERROR_PATTERNS = [
        r"(error|exception|failed|crash|bug|issue|problem)",
        r"(doesn't work|not working|broken|fix needed)",
    ]
    
    INSIGHT_PATTERNS = [
        r"(discovered|realized|important|key insight|note that|remember)",
        r"(should know|keep in mind|don't forget|crucial)",
    ]
    
    CODE_PATTERNS = [
        r"```[\w]*\n",  # Code blocks
        r"(function|class|def |import |const |let |var )",
    ]
    
    PREFERENCE_PATTERNS = [
        r"(i prefer|i like|i want|don't like|hate|favorite)",
        r"(always use|never use|typically|usually|customize)",
    ]
    
    def __init__(self, agent_name: str = "unknown"):
        self.agent_name = agent_name
        self.recent_context: List[Dict] = []
        self.max_context = 10
    
    def analyze_for_triggers(self, user_input: str, agent_response: str) -> List[Tuple[MemoryTrigger, str, int]]:
        """
        Analyze conversation to find memory triggers.
        
        Returns: List of (trigger, content, importance) tuples
        """
        triggers = []
        full_text = f"{user_input} {agent_response}".lower()
        
        # Check for solutions
        if self._matches_patterns(full_text, self.SOLUTION_PATTERNS):
            triggers.append((
                MemoryTrigger.SOLUTION_FOUND,
                self._extract_solution(agent_response),
                9
            ))
        
        # Check for errors with solutions
        if self._matches_patterns(full_text, self.ERROR_PATTERNS):
            if "fix" in full_text or "solution" in full_text:
                triggers.append((
                    MemoryTrigger.ERROR_OCCURRED,
                    f"Error: {user_input}\nSolution: {agent_response}",
                    8
                ))
        
        # Check for insights
        if self._matches_patterns(full_text, self.INSIGHT_PATTERNS):
            triggers.append((
                MemoryTrigger.INSIGHT,
                self._extract_insight(agent_response),
                7
            ))
        
        # Check for code
        if self._matches_patterns(agent_response, self.CODE_PATTERNS):
            code = self._extract_code(agent_response)
            if code and len(code) > 50:
                triggers.append((
                    MemoryTrigger.CODE_SNIPPET,
                    code,
                    8
                ))
        
        # Check for preferences
        if self._matches_patterns(user_input, self.PREFERENCE_PATTERNS):
            triggers.append((
                MemoryTrigger.USER_PREFERENCE,
                f"User preference: {user_input}",
                6
            ))
        
        return triggers
    
    def _matches_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if text matches any pattern"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_solution(self, text: str) -> str:
        """Extract solution from response"""
        # Look for numbered lists or key paragraphs
        lines = text.split('\n')
        solution_lines = []
        
        for line in lines:
            if re.match(r'^(\d+\.|\-|\*|Solution:|Fix:|Answer:)', line.strip()):
                solution_lines.append(line)
        
        if solution_lines:
            return '\n'.join(solution_lines[:5])  # Top 5 lines
        
        # Return first substantial paragraph
        for line in lines:
            if len(line.strip()) > 30:
                return line[:500]
        
        return text[:500]
    
    def _extract_insight(self, text: str) -> str:
        """Extract key insight from text"""
        # Look for sentences with insight keywords
        sentences = re.split(r'[.!?]+', text)
        
        for sent in sentences:
            if any(kw in sent.lower() for kw in ['important', 'key', 'crucial', 'remember', 'note']):
                return sent.strip()[:400]
        
        return text[:400]
    
    def _extract_code(self, text: str) -> str:
        """Extract code blocks from text"""
        # Find code blocks
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', text, re.DOTALL)
        
        if code_blocks:
            return code_blocks[0][:1000]  # First code block
        
        return ""
    
    def should_recall_memories(self, user_input: str) -> Tuple[bool, str]:
        """
        Determine if we should search memories before responding.
        Returns: (should_recall, search_query)
        """
        # Always recall for questions
        if '?' in user_input:
            return True, user_input.replace('?', '').strip()
        
        # Recall for task descriptions
        task_words = ['how', 'what', 'why', 'explain', 'help', 'solve', 'fix']
        if any(word in user_input.lower() for word in task_words):
            return True, user_input
        
        # Recall for specific topics
        specific_topics = ['error', 'bug', 'issue', 'problem', 'configure', 'setup']
        if any(topic in user_input.lower() for topic in specific_topics):
            return True, user_input
        
        return False, ""
    
    def get_importance_reason(self, trigger: MemoryTrigger) -> str:
        """Get human-readable reason for importance"""
        reasons = {
            MemoryTrigger.SOLUTION_FOUND: "Valuable solution that may help future similar tasks",
            MemoryTrigger.ERROR_OCCURRED: "Error pattern and fix that prevents future issues",
            MemoryTrigger.IMPORTANT_FACT: "Critical information for future reference",
            MemoryTrigger.USER_PREFERENCE: "Personal preference to customize future interactions",
            MemoryTrigger.CODE_SNIPPET: "Reusable code example",
            MemoryTrigger.BEST_PRACTICE: "Recommended approach for similar situations",
            MemoryTrigger.CONTEXT_SWITCH: "Topic change marker",
            MemoryTrigger.SESSION_END: "Session summary for continuity",
            MemoryTrigger.TOOL_SUCCESS: "Successful tool execution pattern",
            MemoryTrigger.INSIGHT: "General learning that improves performance",
        }
        return reasons.get(trigger, "General memory")


class IntelligentMemoryManager:
    """
    High-level memory manager that orchestrates save/recall decisions.
    Implements agent-zero style automatic memory management.
    """
    
    def __init__(self, letta_integration, agent_name: str):
        self.letta = letta_integration
        self.agent_name = agent_name
        self.analyzer = MemoryAnalyzer(agent_name)
        self.session_id = self._generate_session_id()
        self.interaction_count = 0
        self.memories_saved = 0
        
        # Stats for reporting
        self.trigger_counts = {trigger: 0 for trigger in MemoryTrigger}
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_hash = hashlib.md5(
            f"{self.agent_name}{timestamp}".encode()
        ).hexdigest()[:8]
        return f"{self.agent_name}_{timestamp}_{random_hash}"
    
    def before_llm_call(self, user_input: str) -> List[Dict]:
        """
        Called BEFORE LLM call to recall relevant memories.
        Implements agent-zero's automatic recall pattern.
        """
        should_recall, query = self.analyzer.should_recall_memories(user_input)
        
        if not should_recall:
            return []
        
        try:
            # Search for relevant memories
            results = self.letta.search_archival(
                query=query,
                limit=5
            )
            
            if results:
                print(f"🧠 Recalled {len(results)} relevant memories for: {query[:50]}...")
            
            return results
        except Exception as e:
            print(f"⚠️ Memory recall failed: {e}")
            return []
    
    def after_llm_call(self, user_input: str, agent_response: str, 
                      tool_calls: Optional[List[Dict]] = None):
        """
        Called AFTER LLM call to analyze and save important memories.
        Implements agent-zero's fragment memorization and solution extraction.
        """
        self.interaction_count += 1
        
        # Analyze for triggers
        triggers = self.analyzer.analyze_for_triggers(user_input, agent_response)
        
        saved_memories = []
        
        for trigger, content, importance in triggers:
            memory = Memory(
                content=content,
                trigger=trigger,
                agent=self.agent_name,
                session_id=self.session_id,
                timestamp=datetime.now().isoformat(),
                tags=[trigger.value, self.agent_name, f"interaction_{self.interaction_count}"],
                importance=importance
            )
            
            # Save to Letta
            try:
                success = self._save_memory(memory)
                if success:
                    saved_memories.append(memory)
                    self.trigger_counts[trigger] += 1
                    self.memories_saved += 1
                    
                    # Log what was saved
                    reason = self.analyzer.get_importance_reason(trigger)
                    print(f"💾 Saved {trigger.value} (importance: {importance}): {reason[:60]}...")
            except Exception as e:
                print(f"⚠️ Failed to save memory: {e}")
        
        # Also save tool calls if successful
        if tool_calls:
            for tool in tool_calls:
                if tool.get('success', False):
                    self._save_tool_memory(tool, user_input)
        
        return saved_memories
    
    def _save_memory(self, memory: Memory) -> bool:
        """Save memory to Letta archival storage"""
        try:
            # Format as structured JSON
            memory_text = json.dumps(memory.to_dict(), indent=2)
            
            return self.letta.save_to_archival(
                text=memory_text,
                tags=memory.tags,
                agent_id=self.letta.agent_id
            )
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def _save_tool_memory(self, tool: Dict, context: str):
        """Save successful tool execution as memory"""
        tool_name = tool.get('tool', 'unknown')
        tool_input = tool.get('input', {})
        tool_output = str(tool.get('output', ''))[:200]
        
        memory = Memory(
            content=f"Tool {tool_name} succeeded with input {tool_input}. Output: {tool_output}",
            trigger=MemoryTrigger.TOOL_SUCCESS,
            agent=self.agent_name,
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            tags=["tool_success", tool_name, self.agent_name],
            importance=5
        )
        
        self._save_memory(memory)
    
    def end_session(self, summary: str = ""):
        """Save session summary and report stats"""
        # Save session summary as memory
        session_memory = Memory(
            content=f"Session Summary: {summary}\nTotal interactions: {self.interaction_count}\nMemories saved: {self.memories_saved}",
            trigger=MemoryTrigger.SESSION_END,
            agent=self.agent_name,
            session_id=self.session_id,
            timestamp=datetime.now().isoformat(),
            tags=["session_summary", self.agent_name],
            importance=7
        )
        
        self._save_memory(session_memory)
        
        # Print stats
        print(f"\n📊 Session Memory Report:")
        print(f"   Session ID: {self.session_id}")
        print(f"   Interactions: {self.interaction_count}")
        print(f"   Memories Saved: {self.memories_saved}")
        print(f"   Trigger Breakdown:")
        for trigger, count in self.trigger_counts.items():
            if count > 0:
                print(f"      - {trigger.value}: {count}")
        
        return {
            "session_id": self.session_id,
            "interactions": self.interaction_count,
            "memories_saved": self.memories_saved,
            "trigger_counts": self.trigger_counts
        }
    
    def search_similar_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar past memories"""
        return self.letta.search_archival(query, limit=limit)
    
    def get_session_memories(self) -> List[Dict]:
        """Get all memories from current session"""
        return self.letta.search_archival(
            query=f"session_id:{self.session_id}",
            limit=50
        )


# Convenience function for one-shot memory analysis
def analyze_and_save(user_input: str, agent_response: str, 
                     letta_integration, agent_name: str = "unknown") -> List[MemoryTrigger]:
    """
    One-shot function to analyze conversation and save important memories.
    
    Returns list of triggers that were detected and saved.
    """
    manager = IntelligentMemoryManager(letta_integration, agent_name)
    
    # Simulate after_llm_call
    saved = manager.after_llm_call(user_input, agent_response)
    
    return [MemoryTrigger(m.trigger) for m in saved]


def should_recall_before_llm(user_input: str) -> Tuple[bool, str]:
    """
    Quick check if memories should be recalled before LLM call.
    
    Returns: (should_recall, search_query)
    """
    analyzer = MemoryAnalyzer()
    return analyzer.should_recall_memories(user_input)
