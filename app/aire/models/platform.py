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

class AireModuleClientCredentials(BaseModel):
    """Module client credentials"""
    client_id: Optional[str] = None
    client_secret: Optional[str] = None

class AireModule(BaseModel):
    """Describes a platform module"""
    id: str
    type: AireModuleType
    endpoint: str
    access: AireModuleAccess
    settings: Optional[dict[str, str | int | bool]] = None
    credentials: Optional[AireModuleClientCredentials] = None

class AireService(BaseModel):
    """Describes an external service"""
    name: str
    modules: Optional[list[AireModule]] = None

class AirePlatform(BaseModel):
    """Describes the platform's core modules"""
    name: str
    modules: dict[AireModuleType, list[AireModule]]

class AireServiceModule(BaseModel):
    service_name: str
    external: bool
    module: AireModule

class AirePlatformConfiguration(BaseModel):
    """Contains the configuration of the AIRe platform"""
    platform: AirePlatform
    services: list[AireService]
    settings: Optional[dict] = None
    agents: list[AireAgent]

    def get_default_module(self, type: AireModuleType) -> AireServiceModule | None:
        module = next(iter(self.platform.modules.get(type, [])), None)
        if module != None:
            return AireServiceModule(service_name=self.platform.name, external=False, module=module)
        else:
            return None
    
    def get_platform_module(self, type: AireModuleType, id: str) -> AireServiceModule | None:
        modules = self.platform.modules.get(type, [])
        return next(iter([AireServiceModule(
            service_name=self.platform.name, 
            external=False, 
            module=x
        ) for x in modules if x.id == id]), None)

    def get_modules(self, type: AireModuleType, include_external: bool) -> list[AireServiceModule]:
        modules = [
            AireServiceModule(
                service_name=self.platform.name, 
                external=False, 
                module=x
            ) for x in self.platform.modules.get(type, [])
        ]

        if include_external:
            for svc in self.services:
                if svc.modules != None:
                    extmodules = [
                        AireServiceModule(
                            service_name=svc.name, 
                            external=True, 
                            module=x
                        ) for x in svc.modules if x.type == type
                    ]
                    modules.extend(extmodules)
        return modules

    def get_agent_memories(self, agent: AireAgent) -> list[AireServiceModule]:
        modules = [
            x for x in self.get_modules(AireModuleType.Memory, True)
            if agent.memories.count(x.module.id) > 0
        ]
        return modules