import asyncio
import json
from typing import Any

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


class MCPClient:
    """
    Client for communicating with the Enterprise Operations MCP Server.
    """

    def __init__(
        self,
        server_url: str = "http://localhost:8000/mcp",
    ):
        self.server_url = server_url

    async def _call_tool_async(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:

        async with streamable_http_client(
            self.server_url
        ) as (
            read_stream,
            write_stream,
            _,
        ):
            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    tool_name,
                    arguments,
                )

                if result.isError:
                    raise RuntimeError(
                        f"MCP tool '{tool_name}' returned an error."
                    )

                # MCP returns tool output as TextContent.
                # Convert JSON text into a normal Python dictionary.
                if result.content:
                    text = result.content[0].text
                    return json.loads(text)

                return {}

    def call_tool(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """
        Synchronous wrapper around the asynchronous MCP client.
        """

        return asyncio.run(
            self._call_tool_async(
                tool_name,
                arguments,
            )
        )