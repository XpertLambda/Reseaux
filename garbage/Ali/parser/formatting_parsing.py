import ast

def puissance(num_list, puissance, rpr):
    result = 0
    for num in num_list:
        result += num ** puissance
    print(f"{rpr} => {result}")



class NetworkQueryFormatter:
    @staticmethod
    def format_puissance(num_list, puissance, rpr):
        # Pre-convert the list to string to avoid f-string overhead
        return f"A/puissance+{num_list}:{puissance}:{rpr}"

class NetworkQueryParser:

    @staticmethod
    def parse_request(query):
        # Use maxsplit parameter to limit unnecessary splits
        header_func = query.split("/", 1)
        headerf = header_func[0]

        func_args = header_func[1].split("+", 1)
        function_callf = func_args[0]
        function_argsf = func_args[1]

        return {
            "headerf": headerf,
            "callf": function_callf,
            "argsf": function_argsf
        }

class Exe:
    # Dictionary to map function names to handlers directly
    _handlers = {}

    @staticmethod
    def register_handler(call_name, handler_func):
        Exe._handlers[call_name] = handler_func

    @staticmethod
    def request_handler(query):
        parsed_query = NetworkQueryParser.parse_request(query)
        if parsed_query["headerf"] == "A":
            handler = Exe._handlers.get(parsed_query["callf"])
            if handler:
                handler(parsed_query["argsf"])

    @staticmethod
    def exe_puissance(argsf):
        # Split with maxsplit for efficiency
        args = argsf.split(":", 2) # 3 args
        puissance(
            ast.literal_eval(args[0]),  # num_list
            int(args[1]),               # puissance
            args[2]                     # rpr
        )

# Register handlers
Exe.register_handler("puissance", Exe.exe_puissance)

# Test
import time
start = time.time()
times = 3

l = [i for i in range(100)]
p = 5
r = "c"

for _ in range(times):
    request = NetworkQueryFormatter.format_puissance(l, p, r)
    Exe.request_handler(request)


print(f"proc time: {time.time() - start}")
