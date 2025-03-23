import ast
import time

def puissance(num_list, puissance, rpr):
    for num in num_list:
        print(f"{rpr} => {num**puissance}")

# Dictionary-based approach
class DictNetworkRequestFormatter:
    @staticmethod
    def format_puissance(num_list, puissance, rpr):
        args = {
            "num_list": num_list,
            "puissance": puissance,
            "rpr": rpr
        }
        return f"A/puissance+{args}"

class DictNetworkRequestParser:
    # Queries format : [query_header]/[function_call]+[function_args]
    @staticmethod
    def parse_request(request):
        parsed_cnt = request.split("/")
        headerf = parsed_cnt[0]
        function = parsed_cnt[1].split("+")
        function_callf = function[0]
        function_argsf = function[1]
        return {
            "headerf": headerf,
            "callf": function_callf,
            "argsf": function_argsf
        }

class DictExe:
    @staticmethod
    def request_handler(request):
        query = DictNetworkRequestParser.parse_request(request)
        if query["headerf"] == "A":
            if query["callf"] == "puissance":
                DictExe.exe_puissance(query["argsf"])

    @staticmethod
    def exe_puissance(argsf):
        args = ast.literal_eval(argsf)
        puissance(
            args.get("num_list", None),
            args.get("puissance", None),
            args.get("rpr", None)
        )

# Simple delimiter approach
class SimpleNetworkRequestFormatter:
    @staticmethod
    def format_puissance(num_list, puissance, rpr):
        return f"A/puissance+{num_list}:{puissance}:{rpr}"

class SimpleNetworkRequestParser:
    # Queries format : [query_header]/[function_call]+[arg1:arg2:arg3]
    @staticmethod
    def parse_request(request):
        parsed_cnt = request.split("/")
        headerf = parsed_cnt[0]
        function = parsed_cnt[1].split("+")
        function_callf = function[0]
        function_argsf = function[1]
        return {
            "headerf": headerf,
            "callf": function_callf,
            "argsf": function_argsf
        }

class SimpleExe:
    @staticmethod
    def request_handler(request):
        query = SimpleNetworkRequestParser.parse_request(request)
        if query["headerf"] == "A":
            if query["callf"] == "puissance":
                SimpleExe.exe_puissance(query["argsf"])

    @staticmethod
    def exe_puissance(argsf):
        args = argsf.split(":")
        puissance(
            ast.literal_eval(args[0]),  # num_list
            int(args[1]),               # puissance
            args[2]                     # rpr
        )

# Performance test
def run_performance_test(iterations=10000):
    print("Running performance test...")

    # Dictionary approach timing
    dict_start = time.time()
    for _ in range(iterations):
        request = DictNetworkRequestFormatter.format_puissance([1, 5, 23, 4], 2, "c")
        DictExe.request_handler(request)
    dict_end = time.time()
    dict_time = dict_end - dict_start

    # Simple delimiter approach timing
    simple_start = time.time()
    for _ in range(iterations):
        request = SimpleNetworkRequestFormatter.format_puissance([1, 5, 23, 4], 2, "c")
        SimpleExe.request_handler(request)
    simple_end = time.time()
    simple_time = simple_end - simple_start

    print(f"\nPerformance Results for {iterations} iterations:")
    print(f"Dictionary approach: {dict_time:.6f} seconds")
    print(f"Simple delimiter approach: {simple_time:.6f} seconds")
    print(f"Difference: {dict_time - simple_time:.6f} seconds")

    if dict_time < simple_time:
        print(f"Dictionary approach is faster by {(simple_time / dict_time - 1) * 100:.2f}%")
    else:
        print(f"Simple delimiter approach is faster by {(dict_time / simple_time - 1) * 100:.2f}%")

# Test with individual requests
"""
print("Testing dictionary approach:")
request = DictNetworkRequestFormatter.format_puissance([1, 5, 23, 4], 2, "c")
print(f"Request: {request}")
DictExe.request_handler(request)

print("\nTesting simple delimiter approach:")
request = SimpleNetworkRequestFormatter.format_puissance([1, 5, 23, 4], 2, "c")
print(f"Request: {request}")
SimpleExe.request_handler(request)
"""
# Comment out the performance test if you don't want to run it
run_performance_test(10000)  # Adjust the number of iterations as needed
