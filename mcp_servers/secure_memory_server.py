#!/usr/bin/env python3
"""
Secure Claude Memory MCP Server
Implements security classification for sensitive data protection
"""

import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from secure_memory import SecureMemorySystem, SecurityLevel
from security_auditor import SecurityAuditor
from knowledge_pipeline import KnowledgePipeline
from mcp.server.fastmcp import FastMCP

# Initialize secure MCP server
mcp = FastMCP(
    "Secure Claude Memory",
    instructions="Provides secure access to classified persistent memory. "
    "Public memories auto-load. Private/confidential/secret require explicit access."
)

# Initialize secure memory system and auditor
memory = SecureMemorySystem()
auditor = SecurityAuditor()
pipeline = KnowledgePipeline(Path("/Users/yourox/AI-Workspace"))


@mcp.resource("memory://public")
def get_public_memory() -> str:
    """
    Get public memories - safe for auto-loading.
    Contains general conversation history and non-sensitive information.
    """
    return memory.load_safe_context(include_private=False)


@mcp.resource("memory://private")
def get_private_memory() -> str:
    """
    Get private memories - personal information.
    Requires explicit access, not auto-loaded.
    """
    return memory.load_safe_context(include_private=True)


@mcp.tool()
def save_memory(
    text: str,
    level: str = "public",
    memory_type: str = "conversation"
) -> str:
    """
    Save a new memory with security classification.
    
    Args:
        text: The memory text to save
        level: Security level (public, private, confidential, secret)
        memory_type: Type of memory (default: "conversation")
    
    Returns:
        Confirmation message
    
    Security Levels:
    - public: Safe to share, auto-loads (default)
    - private: Personal info, explicit access only
    - confidential: Sensitive business data, protected
    - secret: API keys, passwords, NEVER auto-loaded
    """
    try:
        sec_level = SecurityLevel(level.lower())
    except ValueError:
        return f"❌ Invalid security level. Use: public, private, confidential, or secret"
    
    mem = memory.save_memory(text, sec_level, memory_type)
    auditor.log_access("write", f"memory:{sec_level.value}:{mem['id']}", sec_level.value, details=memory_type)
    
    warnings = {
        SecurityLevel.PUBLIC: "",
        SecurityLevel.PRIVATE: " (Not auto-loaded)",
        SecurityLevel.CONFIDENTIAL: " (Protected - explicit access only)",
        SecurityLevel.SECRET: " (🔒 Highly Protected - NEVER auto-loaded)"
    }
    
    return f"✓ Memory saved as {sec_level.value} (ID: {mem['id']}){warnings[sec_level]}"


@mcp.tool()
def search_memories(
    query: str,
    level: str | None = None
) -> str:
    """
    Search memories with security level filtering.
    
    Args:
        query: Search term
        level: Optional security level to search (public, private, confidential, secret)
    
    Returns:
        Matching memories
    
    Note: Searching confidential/secret requires explicit level specification
    """
    sec_level = SecurityLevel(level.lower()) if level else None
    
    # Prevent accidental secret exposure
    results = memory.search_memories(query, sec_level)
    auditor.log_access(
        "read",
        f"search:{query}",
        sec_level.value if sec_level else "mixed",
        details=f"results={len(results)}"
    )
    
    if not results:
        return f"No memories found matching '{query}'"
    
    lines = [f"Found {len(results)} memories:", ""]
    for r in results[-10:]:
        date = r['timestamp'].split('T')[0]
        level_icon = {"public": "📢", "private": "🔒", "confidential": "⚠️", "secret": "🔐"}
        icon = level_icon.get(r['level'], "📝")
        lines.append(f"{icon} [{date}] {r['text']}")
        lines.append("")
    
    return "\n".join(lines)


@mcp.tool()
def get_secret(secret_name: str) -> str:
    """
    Retrieve a secret (API key, password, etc.) by name.
    
    Args:
        secret_name: Name/description of the secret
    
    Returns:
        The secret value if found
    
    Security: This tool provides explicit access to secrets.
    Only use when you need to retrieve sensitive credentials.
    """
    secrets = memory.load_memories(SecurityLevel.SECRET)
    auditor.log_access("read", f"secret:{secret_name}", SecurityLevel.SECRET.value)
    
    # Search for secret by name
    query_lower = secret_name.lower()
    matches = [s for s in secrets if query_lower in s['text'].lower()]
    
    if not matches:
        return f"🔐 No secret found matching '{secret_name}'"
    
    if len(matches) > 1:
        lines = [f"🔐 Multiple secrets found. Be more specific:", ""]
        for m in matches:
            # Show only partial info for security
            preview = m['text'][:50] + "..." if len(m['text']) > 50 else m['text']
            lines.append(f"  - {preview}")
        return "\n".join(lines)
    
    # Return the secret
    return f"🔐 Secret: {matches[0]['text']}"


@mcp.tool()
def get_memory_stats() -> dict:
    """
    Get statistics about the secure memory system.
    
    Returns:
        Memory counts by security level
    """
    stats = memory.get_stats()
    stats["warning"] = "Confidential and secret memories are protected"
    return stats


@mcp.tool()
def get_security_audit(limit: int = 50) -> list:
    """Return recent security audit entries."""
    return auditor.get_recent_logs(limit)


@mcp.tool()
def run_secure_pipeline(domain_key: str) -> dict:
    """Trigger pipeline run with audit logging."""
    auditor.log_access("write", f"pipeline:{domain_key}", "public", details="triggered via secure server")
    return pipeline.run(domain_key)


@mcp.tool()
def list_api_keys() -> str:
    """
    List available API keys (names only, not values).
    
    Returns:
        List of API key names for reference
    
    Use get_secret(name) to retrieve actual values.
    """
    secrets = memory.load_memories(SecurityLevel.SECRET)
    
    if not secrets:
        return "No API keys stored yet"
    
    lines = ["🔐 Available API Keys (use get_secret to retrieve):", ""]
    for s in secrets:
        # Extract first line or first 40 chars as name
        name = s['text'].split('\n')[0][:40]
        lines.append(f"  - {name}")
    
    return "\n".join(lines)


if __name__ == "__main__":
    # Run with stdio transport for Claude Desktop
    mcp.run(transport="stdio")
