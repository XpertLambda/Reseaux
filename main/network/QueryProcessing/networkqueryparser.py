class NetworkQueryParser:

    @staticmethod
    def parse_query(query):
        print(query)
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
