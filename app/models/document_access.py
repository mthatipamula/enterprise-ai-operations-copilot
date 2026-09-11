from dataclasses import dataclass, field


@dataclass
class DocumentAccess:
    department: str
    allowed_roles: list[str] = field(default_factory=list)