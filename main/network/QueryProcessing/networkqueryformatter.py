
class NetworkQueryFormatter:

    # All units
    @staticmethod
    def format_attack_entity(actor_id, target_id):
        """
        actor_id : unit performing the action
        build_target_id : enemy to attack

        initial call is unit.attack_entity(target_id)
        """

        return f"A/ae+{actor_id}:{target_id}" # ae :attack_entity easier and lighter to send in the packet

    # villager
    @staticmethod
    def format_villager_build_entity(actor_id, build_target_id): # we named it villager so that it is different from the player build_entity_function
        """
        actor_id : villager performing the action
        build_target_id : drop_target to collect

        initial call is villager.build_entity(build_target_id)
        """
        return f"A/vbe+{actor_id}:{build_target_id}" #vbe : villager_build_entity

    @staticmethod
    def format_drop_to_entity(actor_id, drop_target_id):
        """
        actor_id : villager performing the action
        drop_target_id : resource drop point

        initial call is villager.drop_to_entity(drop_target_id)
        """
        return f"A/dte+{actor_id}:{drop_target_id}" # dte : drop_to_entity

    @staticmethod
    def format_collect_entity(actor_id, resource_target_id):
        """
        actor_id : villager performing the action
        resource_target_id : resource to collect

        initial call is villager.collect_entity(resource_target_id)
        """
        return f"A/ce+{actor_id}:{resource_target_id}" # ce : collect_entity

    # traning building
    @staticmethod
    def format_train_unit(actor_id, player_team, entity_repr):
        """
        actor_id : building performing the action
        player_id : team number of the player so we can get the player object from the map
        entity_repr : type of unit to train

        initial call is building.train_unit(player, entity_repr)
        """
        return f"A/tu+{actor_id}:{player_team}:{entity_repr}" # tu : train_unit

    # player
    @staticmethod
    def format_player_build_entity(player_team, actors_id, representation = "", entity_id = None):
        """

        player_team : team number of the player so we can get the player object from the MAP
        actors_id : villagers id to perform the building
        representation : the type of the building, by default it is "" but why ?
        entity_id : when the representation is "" that means we want to continue the building of buildin that were being built, so give the id, and by default it is None means that we want to create a new one based on the representation

        initial call player.build_entity(villager_id_list, representation = "", entity_id = None)
        """

        return f"A/pbe+{player_team}:{actors_id}:{representation}:{entity_id}" # pbe : player_build_entity

    @staticmethod
    def format_config_req():

        return f"C/config_req+{None}"

    @staticmethod
    def format_config_resp(seed, cellY, cellX, num_players, mode):

        """
        seed : map seed
        cellY : height of the map
        cellX : width of the map
        num_players : number of players
        mode : starting mode of the game

        """

        return f"C/config_resp+{seed}:{cellY}:{cellX}:{num_players}:{mode}"
