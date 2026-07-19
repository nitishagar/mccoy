"""Minimal clean MCP server used to prove the CLI's zero exit-code contract."""

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict

mcp = FastMCP("McCoy clean fixture")


class EchoInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str


@mcp.tool(description="Echo a caller-provided message.")
def echo(data: EchoInput) -> str:
    return data.message


if __name__ == "__main__":
    mcp.run()
