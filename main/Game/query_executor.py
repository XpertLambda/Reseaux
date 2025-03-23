from GameField.map import *


import ast

class QueryExecutor:

    @staticmethod
    def exe_attack_entity(game_map, argsf):
        args = argsf.split(":", 1) # 2 args

        actor_id = int(args[0]) # int actor_id
        target_id = int(args[1]) # int target_id

        game_map.get_entity_by_id(actor_id).attack_entity(target_id)

    @staticmethod
    def exe_villager_build_entity(game_map, argsf):

        args = argsf.split(":", 1) # 2 args

        actor_id = int(args[0]) # int actor_id
        build_target_id = int(args[1]) # int build_target_id

        game_map.get_entity_by_id(actor_id).build_entity(build_target_id)

    @staticmethod
    def exe_drop_to_entity(game_map, argsf):

        args = argsf.split(":", 1) # 2 args

        actor_id = int(args[0]) # int actor_id
        drop_target_id = int(args[1]) # int drop_target_id

        game_map.get_entity_by_id(actor_id).drop_to_entity(drop_target_id)


    @staticmethod
    def exe_collect_entity(game_map, argsf):
        args = argsf.split(":", 1) # 2 args

        actor_id = int(args[0])

        resource_target_id = int(args[1])

        game_map.get_entity_by_id(actor_id).collect_entity(resource_target_id)

    @staticmethod
    def exe_train_unit(game_map, argsf):
        args = argsf.split(":", 2) # 3 args

        actor_id = int(args[0]) # int actor_id
        player_team = int(args[1]) # int player_team
        entity_repr = args[2] # char entity_rper

        game_map.get_entity_by_id(actor_id).train_unit(game_map.get_player_by_team(player_team), entity_repr)

    @staticmethod
    def exe_player_build_entity(game_map, argsf):

        args = argsf.split(":", 3) # 4 args

        player_team = int(args[0]) # int player_team
        villager_id_list = ast.literal_eval(args[1]) # int[] villager id list
        _representation = args[2] # char represenation = ""
        _entity_id = ast.literal_eval(args[3]) # entity_id = None

        game_map.get_player_by_team(player_team).build_entity(villager_id_list, representation = _representation, entity_id = _entity_id )


    _fct_map = {
            "ae": exe_attack_entity,
            "vbe": exe_villager_build_entity,
            "dte": exe_drop_to_entity,
            "ce": exe_collect_entity,
            "tu": exe_train_unit,
            "pbe": exe_player_build_entity
        }

    @staticmethod
    def handle_query(game_map, queryf):

        if queryf["headerf"] == "A": # action type queries
            fct = QueryExecutor._fct_map.get(queryf["callf"], None)

            if fct != None:
                fct(game_map, queryf["argsf"])
