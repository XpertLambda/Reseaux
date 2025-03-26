from GLOBAL_VAR import *
from GLOBAL_IMPORT import *
from .game_event_handler import *
from .ai_profiles import *
from tkinter import messagebox, Button, Scale, Tk, Label, Frame, Grid, HORIZONTAL, N, W, E, S
from random import randint,seed

import time

from network.QueryProcessing.networkqueryformatter import NetworkQueryFormatter
from collections import deque # the queue of the user that contains the action to send


JSON_MAPPING['ArcheryRange'] = ArcheryRange
JSON_MAPPING['Barracks'] = Barracks
JSON_MAPPING['Camp'] = Camp
JSON_MAPPING['Keep'] = Keep
JSON_MAPPING['TownCenter'] = TownCenter
JSON_MAPPING['Farm'] = Farm
JSON_MAPPING['Gold'] = Gold
JSON_MAPPING['Tree'] = Tree
JSON_MAPPING['Stable'] = Stable
JSON_MAPPING['House'] = House
JSON_MAPPING['HorseMan'] = HorseMan
JSON_MAPPING['Archer'] = Archer
JSON_MAPPING['SwordMan'] = SwordMan
JSON_MAPPING['Villager'] = Villager
JSON_MAPPING['CavalryArcher'] = CavalryArcher
JSON_MAPPING['SpearMan'] = SpearMan
JSON_MAPPING['AxeMan'] = AxeMan
JSON_MAPPING['Projectile'] = Projectile
JSON_MAPPING['Arrow'] = Arrow
JSON_MAPPING['Spear'] = Spear
JSON_MAPPING['FireArrow'] = FireArrow
JSON_MAPPING['FireSpear'] = FireSpear
JSON_MAPPING['PVector2'] = PVector2
JSON_MAPPING['Storage'] = Storage
JSON_MAPPING['Habitat'] = Habitat

CLASS_MAPPING = {
    'A': ArcheryRange,
    'B': Barracks,
    'C': Camp,
    'K': Keep,
    'T': TownCenter,
    'F': Farm,
    'G': Gold,
    'W': Tree,
    'S': Stable,
    'H': House,
    'h': HorseMan,
    'a': Archer,
    's': SwordMan,
    'v': Villager,
    'c': CavalryArcher,
    'm':SpearMan,
    'x':AxeMan,
    'p': Projectile,
    'pa': Arrow,
    'ps':Spear,
    'fpa':FireArrow,
    'fps':FireSpear,
    'V': PVector2
}

class DecisionNode:
    def __init__(self, question, yes_action=None, no_action=None, priority=0):
        self.question = question
        self.yes_action = yes_action
        self.no_action = no_action
        self.priority = priority

    def decide(self, context, query_snd_queue):
        actions = []
        if self.question(context):
            if isinstance(self.yes_action, DecisionNode):
                actions.extend(self.yes_action.decide(context, query_snd_queue))
            else:
                if callable(self.yes_action):
                    result = self.yes_action(context,query_snd_queue)
                    actions.append((result, self.priority))
        else:
            if isinstance(self.no_action, DecisionNode):
                actions.extend(self.no_action.decide(context, query_snd_queue))
            else:
                if callable(self.no_action):
                    result = self.no_action(context, query_snd_queue)
                    actions.append((result, self.priority))

        actions.sort(key=lambda x: x[1], reverse=True)

        return [action if isinstance(action, str) else action[0] for action in actions]

# ---- Questions ----
def villagers_insufficient(context):
    villager_count = len(context['player'].get_entities_by_class(['v']))  # 'v' pour les villageois
    return villager_count < context['desired_villager_count'] and len(context['player'].get_entities_by_class(['F']))>=1

def has_farm(context):
    return len(context['player'].get_entities_by_class(['F']))>0

def resources_critical(context):
    resources = context['player'].get_current_resources()
    return resources['gold'] < 50 or resources['food'] < 50 or resources['wood'] < 50

def buildings_insufficient(context):
    return not context['buildings'].get('storage', False)

def has_enough_military(context):
    return context['ratio_military'] >= 0.5 or len(context['units']['villager']) <= 5

def can_we_attack(context):
    return len(context['units']['villager']) > 5 and context['units']['military_free']

def check_housing(context):
    return (context['player'].current_population >= context['player'].get_current_population_capacity())

# ---- Actions ----
def train_villager(context, query_snd_queue): #==============================================
    for towncenter_id in context['player'].get_entities_by_class(['T']):
        towncenter=context['player'].linked_map.get_entity_by_id(towncenter_id)

        if towncenter.train_unit(context['player'],'v', query_snd_queue = query_snd_queue) == TRAIN_SUCCESS:
            query_snd_queue.append(NetworkQueryFormatter.format_train_unit(context['player'].linked_map.id_generator, towncenter.id, context['player'].team, 'v'))


        if context['player'].get_current_resources()['food']<50:
            gather_resources(context, query_snd_queue)
    return "Training villagers!"

def gather_resources(context, query_snd_queue): #==============================================
    resources_to_collect=("wood",'W')
    for temp_resources in [("gold",'G'),("food",'F')]:
        if context['resources'][temp_resources[0]]<context['resources'][resources_to_collect[0]]:
            resources_to_collect=temp_resources
    v_ids = context['player'].get_entities_by_class(['v'],is_free=True)
    c_ids = context['player'].ect(resources_to_collect[1], context['player'].cell_Y, context['player'].cell_X)
    counter = 0
    c_pointer = 0
    for id in v_ids:
        v = context['player'].linked_map.get_entity_by_id(id)
        if not v.is_full():
            if counter == 3:
                counter = 0
                if c_pointer<len(c_ids)-1:
                    c_pointer += 1

            if v.collect_entity(c_ids[c_pointer]):
                query_snd_queue.append(NetworkQueryFormatter.format_collect_entity(v.id, c_ids[c_pointer]))

            counter += 1
        else:
            drop_resources(context, query_snd_queue)
    return "Gathering resources!"

def train_military(context, query_snd_queue): #==============================================
    return "Train military units!"

def attack(context, query_snd_queue): #==============================================
    return "Attacking the enemy!"

def drop_resources(context, query_snd_queue): #==============================================
    for unit in [context['player'].linked_map.get_entity_by_id(v_id) for v_id in context['player'].get_entities_by_class(['v'],is_free=True)]:

        if unit.is_full():
            drop_target_id = context['player'].entity_closest_to(["T","C"], unit.cell_Y, unit.cell_X, is_dead = True)
            unit.drop_to_entity(drop_target_id)
            query_snd_queue.append(NetworkQueryFormatter.format_drop_to_entity(unit.id, drop_target_id))

    return "Dropping off resources!"


def build_structure(context, query_snd_queue): #==============================================
    return "Building structure!"

def housing_crisis(context, query_snd_queue): #==============================================
    villager_id_list = context['player'].get_entities_by_class(['v'],is_free=True)

    context['player'].build_entity(villager_id_list, 'H', query_snd_queue = query_snd_queue)
    #query_snd_queue.append(NetworkQueryFormatter.format_player_build_entity(context['player'].linked_map.id_generator, context['player'].team, villager_id_list, 'H', None))
    return "Building House!"

# ---- Arbre de décision ----
tree = DecisionNode(
    # villagers_insufficient,
    # yes_action=train_villagers,
    has_farm,
    no_action=build_structure,
    yes_action=DecisionNode(
    resources_critical,
    yes_action=DecisionNode(
        buildings_insufficient,
        yes_action=drop_resources,
        no_action=gather_resources,
        priority=6
        ),
    no_action=DecisionNode(
        check_housing,
        yes_action=housing_crisis,
        no_action=DecisionNode(
            villagers_insufficient,
            yes_action=train_villager,
            no_action=DecisionNode(
                has_enough_military,
                no_action=train_military,
                yes_action=DecisionNode(
                    can_we_attack,
                    yes_action=attack,
                    no_action=build_structure,
                    priority=8
                ),
                priority=7
            ),
            priority=6
        ),
    priority=5
    )
)
)

def choose_strategy(Player):
    answer = messagebox.askyesno(
        message='Do you want to choose the IA type for Player'+ str(Player.team)+'?',
        icon='question',
        title='AIge Of EmpAIres II'
    )

    if answer:
        global result
        result = []
        def get_ia_values():
            # Récupérer les valeurs des sliders lorsqu'on appuie sur le bouton
            agressive_select = agressive.get()
            defense_select = defense.get()
            if defense_select >= agressive_select-0.5 and defense_select <= agressive_select+0.5 :
                result.append("balanced")
                result.append(agressive_select)
                result.append(defense_select)
            elif defense_select > agressive_select:
                result.append("defensive")
                result.append(agressive_select)
                result.append(defense_select)
            else:
                result.append("aggressive")
                result.append(agressive_select)
                result.append(defense_select)



        def on_button_click():
            get_ia_values()
            root.destroy()  # Ferme la fenêtre après validation
        # Création de l'interface
        root = Tk()
        root.title("Choose the Strategy")
        mainframe = Frame(root)
        root.title("IA Player "+str(Player.team))
        mainframe.grid(column=0, row=0, sticky=(W, E, S))

        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        # Titre et slider "Agressive"
        Label(mainframe, text="Agressive").grid(column=1, row=1, sticky=W)
        agressive = Scale(mainframe, from_=1, to=3, orient=HORIZONTAL, resolution=0.1)
        agressive.grid(column=1, row=2, sticky=(W, E))

        # Titre et slider "Defense"
        Label(mainframe, text="Defense").grid(column=2, row=1, sticky=W)
        defense = Scale(mainframe, from_=1, to=3, orient=HORIZONTAL, resolution=0.1)
        defense.grid(column=2, row=2, sticky=(W, E))

        # Bouton de validation
        Button(mainframe, text="Confirm", command=on_button_click).grid(column=3, row=2, sticky=(W, E))

        root.mainloop()
        return result
    else:
        # Choix aléatoire si l'utilisateur refuse de configurer l'IA
        seed(time.perf_counter())
        agressive = float(randint(10,30))/10
        defense = float(randint(10,30))/10
        result = []
        if defense >= agressive-0.5 and defense <= agressive+0.5 :
            result.append("balanced")
            result.append(agressive)
            result.append(defense)
        elif defense > agressive:
            result.append("defensive")
            result.append(agressive)
            result.append(defense)
        else:
            result.append("aggressive")
            result.append(agressive)
            result.append(defense)
        return result















class Player:

    def __init__(self, cell_Y, cell_X, team):
        self.team = team
        self.cell_Y = cell_Y
        self.cell_X = cell_X
        self.storages_id = set() # resource storages
        self.houses_id = set() # towncenters and habitats

        self.current_population = 0
        self.homeless_units = 0

        self.entities_dict = {}
        self.linked_map = None


        self.decision_tree= tree
        strat = choose_strategy(self)
        print(f"[+] Player n : {team}, strat : {'aggressive'}")
        self.ai_profile = AIProfile(strategy = "aggressive", aggressiveness= strat[1], defense = strat[2])
        self.game_handler = GameEventHandler(self.linked_map,self,self.ai_profile)

        self.refl_acc = 0
        self.is_busy = False

        self.life_time = 0

    def add_entity(self, entity):


        entity.netp = self.team

        entity_dict = self.entities_dict.get(entity.representation, None)

        if entity_dict == None:
            self.entities_dict[entity.representation] = {}
            entity_dict = self.entities_dict.get(entity.representation, None)

        entity_dict[entity.id] = entity

        is_habitat = False
        is_storage = False

        if entity.representation in ['C', 'T']:
            is_storage = True
        if entity.representation in ['T', 'H']:
            is_habitat = True
        if is_storage:
            self.storages_id.add(entity.id)
        if is_habitat:
            self.houses_id.add(entity.id)

    def remove_entity(self, entity):

        entity_dict = self.entities_dict.get(entity.representation, None)
        if entity_dict:
            entity_dict.pop(entity.id, None)

            if not entity_dict: # if empty remove
                self.entities_dict.pop(entity.representation, None)
            is_habitat = False
            is_storage = False


            if isinstance(entity, Unit):
                if self.current_population <= self.get_current_population_capacity():
                    self.remove_population()
                else:
                    self.homeless_units -= 1
                self.current_population -= 1
            if entity.representation in ['C', 'T']:
                is_storage = True
            if entity.representation in ['T', 'H']:
                is_habitat = True
            if is_storage:
                #if entity.id in self.storages_id:
                self.storages_id.remove(entity.id)
            if is_habitat:
                #if entity.id in self.houses_id in self.houses_id:
                entity_population = entity.habitat.current_population
                self.houses_id.remove(entity.id)
                for _ in range(entity_population):
                    self.add_population()


            return 1
        return 0

    def can_afford(self, representation):

        if representation in CLASS_MAPPING:
            InstClass = CLASS_MAPPING.get(representation, None)

            Instance = InstClass(IdGenerator(), None, None, None, self.team) # fake instance

            return Instance.affordable_by(self.get_current_resources())

    def get_entities_by_class(self, representations, is_free = False): # list of representations for exemple : ['a', 'h', 'v']

        id_list = []

        for representation in representations:
            entity_dict = self.entities_dict.get(representation, None)

            if entity_dict:

                for entity_id in entity_dict:
                    entity = self.linked_map.get_entity_by_id(entity_id)
                    add = True

                    if is_free and not(entity.is_free()):
                        add = False
                    if add:
                        id_list.append(entity_id)

        return id_list

    def build_entity(self, villager_id_list, representation = "", entity_id = None, query_snd_queue = None):
        if villager_id_list:
            if entity_id == None:
                if (representation in ["T","H"]) and (len(self.get_entities_by_class(["T","H"])) * 5) >= MAX_UNIT_POPULATION:
                    return BUILDING_POPULATION_MAX_LIMIT

                BuildingClass = CLASS_MAPPING.get(representation, None)
                Instance = BuildingClass(self.linked_map.id_generator,None, None, None, self.team)

                if isinstance(Instance, Building) and Instance.affordable_by(self.get_current_resources()):
                    
                    self.remove_resources(Instance.cost)
                    self.inform_storages(query_snd_queue)
                    Instance.netp = self.team
                    Instance.state = BUILDING_INPROGRESS
                    self.linked_map.add_entity_to_closest(Instance, self.cell_Y, self.cell_X, random_padding = 0x0, query_snd_q = query_snd_queue)

                    for villager_id in villager_id_list:
                        villager = self.linked_map.get_entity_by_id(villager_id)

                        if villager != None:
                            villager.build_entity(Instance.id)

                            if query_snd_queue != None:
                                query_snd_queue.append(NetworkQueryFormatter.format_villager_build_entity(villager.id, Instance.id))

                    return BUILDING_SUCCESS
                """
                else:
                    self.linked_map.id_generator.free_ticket(Instance.id)
                """
                return 0
            else:
                for villager_id in villager_id_list:
                    villager = self.linked_map.get_entity_by_id(villager_id)

                    if villager != None:
                        villager.build_entity(entity_id)
                return 1
        else:
            return 0

    def inform_habitats(self, query_snd_queue):

        if query_snd_queue != None:
            for hid in self.houses_id:
                entity = self.linked_map.get_entity_by_id(hid)
                print(f"hello habitat {entity}")
                query_snd_queue.append(NetworkQueryFormatter.format_create_entity_rep(self.linked_map.id_generator, self.team, entity.to_json()))


    def inform_storages(self, query_snd_queue):
        
        if query_snd_queue != None:
            print("===>>> INFORMAT")
            for storage_id in self.storages_id:

                entity = self.linked_map.get_entity_by_id(storage_id)
                print(f"hello storage {entity}")
                query_snd_queue.append(NetworkQueryFormatter.format_create_entity_rep(self.linked_map.id_generator, self.team, entity.to_json()))

    def distribute_evenly(self, resource_type, amount):

        actual_ids = set()

        for storage_id in self.storages_id:
            current_storage = self.linked_map.get_entity_by_id(storage_id)
            if current_storage.state == BUILDING_ACTIVE:
                actual_ids.add(storage_id)

        num_storages = len(actual_ids)
        if num_storages == 0:
            return amount  # No storages to distribute to

        per_storage = amount // num_storages
        leftover = amount % num_storages

        for storage_id in actual_ids:
            current_storage = self.linked_map.get_entity_by_id(storage_id)

            current_storage.storage.add_resource(resource_type, per_storage + (1 if leftover > 0 else 0))
            if leftover > 0:
                leftover -= 1

        return 0  # No leftover since there's no capacity limit

    def remove_from_largest(self, resource_type, amount):
        actual_ids = set()

        for storage_id in self.storages_id:
            current_storage = self.linked_map.get_entity_by_id(storage_id)
            if current_storage.state == BUILDING_ACTIVE:
                actual_ids.add(storage_id)

        needed = amount
        while needed > 0:
            # Find the storage with the most of the resource
            largest_storage_id = max(actual_ids, key=lambda s_id: self.linked_map.get_entity_by_id(s_id).storage.resources.get(resource_type, 0), default=None)
            largest_storage = self.linked_map.get_entity_by_id(largest_storage_id)
            if not largest_storage or largest_storage.storage.resources.get(resource_type, 0) == 0:
                break  # No more resources available

            removed = largest_storage.storage.remove_resource(resource_type, needed)
            needed -= removed

        return amount - needed  # Amount successfully removed

    def add_resources(self, resources):

        for resource, amount in resources.items():
            self.distribute_evenly(resource, amount)


    def remove_resources(self, resources):
        for resource, amount in resources.items():
            self.remove_from_largest(resource, amount)

    def get_current_resources(self):

        resources = {"gold":0,"wood":0,"food":0}
        actual_ids = set()

        for storage_id in self.storages_id:
            current_storage = self.linked_map.get_entity_by_id(storage_id)
            if current_storage.state == BUILDING_ACTIVE:
                actual_ids.add(storage_id)

        for storage_id in actual_ids:
            current_storage = self.linked_map.get_entity_by_id(storage_id)

            if current_storage:
                for resource, amount in current_storage.storage.resources.items():
                    resources[resource] += amount
        return resources
    """
    def remove_storage(self, toremove_storage_id):
        toremove_storage = self.linked_map.get_entity_by_id(toremove_storage_id)
        resources = toremove_storage.storage.resources

        self.storages_id.remove(toremove_storage_id)

        return resources
    """

    def get_current_population_capacity(self):
        current_capacity = 0
        actual_ids = set()

        for house_id in self.houses_id:
            current_habitat = self.linked_map.get_entity_by_id(house_id)
            if current_habitat.state == BUILDING_ACTIVE:
                actual_ids.add(house_id)

        for habitat_id in actual_ids:

            current_habitat = self.linked_map.get_entity_by_id(habitat_id)

            if current_habitat:
                current_capacity += current_habitat.habitat.capacity

        return current_capacity



    def add_population(self):
        actual_ids = set()

        for house_id in self.houses_id:
            current_habitat = self.linked_map.get_entity_by_id(house_id)
            if current_habitat.state == BUILDING_ACTIVE:
                actual_ids.add(house_id)

        for habitat_id in actual_ids:

            current_habitat = self.linked_map.get_entity_by_id(habitat_id)

            if current_habitat:
                if current_habitat.habitat.add_population():
                    return True

        return False

    def remove_population(self):
        actual_ids = set()
        for house_id in self.houses_id:
            current_habitat = self.linked_map.get_entity_by_id(house_id)
            if current_habitat.state == BUILDING_ACTIVE:
                actual_ids.add(house_id)

        for habitat_id in actual_ids:

            current_habitat = self.linked_map.get_entity_by_id(habitat_id)

            if current_habitat:
                if current_habitat.habitat.remove_population():
                    return True
        return False

    def update_population(self,dt):
        pop = self.current_population
        cpop = self.get_current_population_capacity()
        if pop > cpop:
            self.homeless_units = pop - cpop

        elif pop < cpop and self.homeless_units > 0:
            range_val = self.homeless_units
            for _ in range(range_val):

                if not(self.add_population()):
                    break
                else:
                    self.homeless_units -= 1

    def entity_closest_to(self, ent_repr_list, cell_Y, cell_X, is_dead = False): # we give the ent_repr for the entity we want and then we give a certain position and we will return the closest entity of the given type to the cell_X, cell_Y
        closest_id = None
        ent_ids = None

        for ent_repr in ent_repr_list:
            if ent_repr not in ["W", "G"]:
                ent_ids = self.get_entities_by_class(ent_repr)
            else:
                ent_ids = self.linked_map.resource_id_dict.get(ent_repr, None)

            if ent_ids:

                closest_dist = float('inf')

                for ent_id in ent_ids:

                    current_entity = self.linked_map.get_entity_by_id(ent_id)
                    if current_entity:
                        compute = True

                        if is_dead and current_entity.is_dead():
                            compute = False

                        if compute:
                            current_dist = math.dist([current_entity.cell_X, current_entity.cell_Y], [cell_X, cell_Y])

                            if current_dist < closest_dist:
                                closest_id = current_entity.id
                                closest_dist = current_dist

        return closest_id


    def ect(self, ent_repr_list, cell_Y, cell_X, is_dead = False):
        entity_distances = []

        for ent_repr in ent_repr_list:
            if ent_repr not in ["W", "G"]:
                ent_ids = self.get_entities_by_class(ent_repr)
            else:
                ent_ids = self.linked_map.resource_id_dict.get(ent_repr, None)

            if ent_ids:
                for ent_id in ent_ids:
                    current_entity = self.linked_map.get_entity_by_id(ent_id)
                    if current_entity:
                        compute = True
                        if is_dead and current_entity.is_dead():
                            compute = False

                        if compute:
                            current_dist = math.dist([current_entity.cell_X, current_entity.cell_Y], [cell_X, cell_Y])
                            entity_distances.append((current_entity.id, current_dist))

        sorted_entities = sorted(entity_distances, key=lambda x: x[1])
        return [entity_id for entity_id, _ in sorted_entities]

    def is_free(self):
        return 'is_free'

    def is_dead(self):
        return not(self.entities_dict)

    def get_buildings(self, is_free = False):
        return self.get_entities_by_class(["T","C","H","K","F","S","B","A"], is_free)

    def update(self, dt):
        self.life_time += dt/ONE_SEC


        # 200004
        self.update_population(dt)


    def think(self, dt, query_snd_queue):#==============================================
        self.refl_acc +=dt
        if self.refl_acc>ONE_SEC:
            self.player_turn(dt, query_snd_queue)
            self.refl_acc=0

    def player_turn(self,dt, query_snd_queue):#==============================================
        decision = self.game_handler.process_ai_decisions(self.decision_tree, query_snd_queue) #==============================================





        # # decision = self.ai_profile.decide_action(self.decision_tree, context)
        # return decision

    # def set_build(self, villager_id_list):
    #     i = 0
    #     while(i < 4):
    #         villager_id_list.append(self.villager_free[i])
    #         i += 1
    #     self.build_entity(villager_id_list, 'B')
    #     print(f"Before remove: villager_free = {self.villager_free}, attempting to remove {villager_id_list}")
    #     for villager_id in villager_id_list:
    #         if villager_id in self.villager_free:
    #             self.villager_free.remove(villager_id)
    #     self.villager_occupied.append(villager_id_list)


    # def set_resources(self, collector_id):
    #     drop_build_id = self.entity_closest_to('T', self.entities_dict['v'][collector_id].cell_Y, self.entities_dict['v'][collector_id].cell_X)
    #     object = self.linked_map.get_entity_by_id(drop_build_id)
    #     resource_id = self.entity_closet_to('G', object.cell_Y, object.cell_X)
    #     self.villager_free.remove(collector_id)
    #     self.set_collect(object,resource_id)
    #     self.villager_occupied.append(collector_id)

    # def set_collect(self, villager, entity_id):
    #     if not villager.is_full():
    #         villager.move_to(entity_id.position)
    #         villager.collect_entity(entity_id)
