# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.


from pydantic import BaseModel
from enum import Enum
from typing import Optional
from .agent import AireAgent

class AireModuleType(str, Enum):
    """Module types"""
    AI = "ai"
    ID = "id"
    Memory = "memory"

class AireModuleAccess(str, Enum):
    """Module access levels"""
    Public = "public"
    Service = "service"
    Private = "private"

class AireModuleSetting(str, Enum):
    """Known module settings keys"""
    VectorDatabaseName = "vector_database_name"
    PersonalityPrompt = "personality_prompt"
    VectorSearchRelevanceThreshold = "vector_search_relevance_threshold"

class AireModule(BaseModel):
    """Describes a platform module"""
    id: str
    type: AireModuleType
    endpoint: str
    access: AireModuleAccess
    token: Optional[str] = None
    settings: Optional[dict[str, str | int | bool]] = None

class AireService(BaseModel):
    """Describes an external service"""
    name: str
    modules: Optional[list[AireModule]] = None

class AirePlatform(BaseModel):
    """Describes the platform's core modules"""
    name: str
    modules: dict[AireModuleType, list[AireModule]]

class AirePlatformConfiguration(BaseModel):
    """Contains the configuration of the AIRe platform"""
    platform: AirePlatform
    services: list[AireService]
    settings: Optional[dict] = None
    agents: list[AireAgent]

    def get_default_module(self, type: AireModuleType) -> AireModule | None:
        return next(iter(self.platform.modules.get(type, [])), None)
    
    def get_module(self, type: AireModuleType, id: str) -> AireModule | None:
        modules = self.platform.modules.get(type, [])
        return next(iter([x for x in modules if x.id == id]), None)

    def get_modules(self, type: AireModuleType, include_external: bool) -> list[AireModule]:
        modules = [x for x in self.platform.modules.get(type, [])]
        if include_external:
            for svc in self.services:
                if svc.modules != None:
                    extmodules = [x for x in svc.modules if x.type == type]
                    modules.extend(extmodules)
        return modules

    def get_agent_memories(self, agent: AireAgent) -> list[AireModule]:
        modules = [x for x in self.platform.modules.get(AireModuleType.Memory, []) 
                   if agent.memories.count(x.id) > 0]
        for svc in self.services:
            if svc.modules != None:
                extmodules = [x for x in svc.modules 
                              if x.type == AireModuleType.Memory and agent.memories.count(x.id) > 0]
                modules.extend(extmodules)
        return modules