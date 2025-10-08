# Functions that are shared with all the agents 
from typing import Protocol, List, Dict, Any

class AgentProtocol(Protocol):
    def get_response(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        pass