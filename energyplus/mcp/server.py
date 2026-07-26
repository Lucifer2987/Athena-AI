from mcp.protocol import ToolResult


class MCPServer:

    def __init__(self, registry):

        self.registry = registry

    def execute(self, tool_name, **kwargs):

        try:

            result = self.registry.execute(
                tool_name,
                **kwargs
            )

            return ToolResult(

                success=True,

                data=result

            )

        except Exception as e:

            return ToolResult(

                success=False,

                data=None,

                message=str(e)

            )