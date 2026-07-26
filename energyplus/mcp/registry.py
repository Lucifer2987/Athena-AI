class MCPRegistry:

    def __init__(self):

        self.tools = {}

    def register(self, name, func, description):

        self.tools[name] = {

            "function": func,

            "description": description

        }

    def execute(self, name, *args, **kwargs):

        if name not in self.tools:

            raise ValueError(f"Tool '{name}' not registered.")

        return self.tools[name]["function"](*args, **kwargs)

    def list_tools(self):

        return {

            name: tool["description"]

            for name, tool in self.tools.items()

        }