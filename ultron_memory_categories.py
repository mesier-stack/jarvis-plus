from __future__ import annotations

import re
from jarvis_core import AssistantReply, JarvisBrain

CATEGORIES = ("project", "preference", "task", "person", "general")


def install_memory_category_patch() -> None:
    if getattr(JarvisBrain, "_ultron_memory_categories_installed", False):
        return
    original = JarvisBrain.handle

    def wrapped(self: JarvisBrain, raw: str) -> AssistantReply:
        text = raw.strip()
        low = text.lower().strip(" .!?¿¡")

        m = re.match(r"^(?:remember|recuerda)\s+(project|preference|task|person|general|proyecto|preferencia|tarea|persona)\s*:\s*(.+)$", text, re.I)
        if m:
            category = m.group(1).lower()
            category = {"proyecto":"project","preferencia":"preference","tarea":"task","persona":"person"}.get(category, category)
            fact = m.group(2).strip()
            self.memory.remember(f"[{category}] {fact}")
            return AssistantReply(f"Stored in {category} memory.", "memory")

        m = re.match(r"^(?:show|muestra)\s+(project|preference|task|person|general|proyecto|preferencia|tarea|persona)\s+(?:memories|memory|recuerdos|recuerdo)$", low)
        if m:
            category = m.group(1)
            category = {"proyecto":"project","preferencia":"preference","tarea":"task","persona":"person"}.get(category, category)
            items = [x for x in self.memory.list_memories(200) if x.lower().startswith(f"[{category}] ")]
            if not items:
                return AssistantReply(f"No {category} memories stored.", "memory")
            clean = [x.split("] ",1)[1] if "] " in x else x for x in items]
            return AssistantReply(f"{category.title()} memories:\n• " + "\n• ".join(clean), "memory")

        return original(self, raw)

    JarvisBrain.handle = wrapped
    JarvisBrain._ultron_memory_categories_installed = True
