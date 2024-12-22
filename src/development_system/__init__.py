"""
This module contains the implementation of the Development System
"""
from development_system.development_system_orchestrator import DevelopmentSystemOrchestrator

if __name__ == "__main__":
    app = DevelopmentSystemOrchestrator()
    app.run()
