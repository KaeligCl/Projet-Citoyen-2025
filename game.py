import pygame
import pytmx
import pyscroll
import os

from player import Player


class Game:

    def __init__(self):
        # Démarrage
        self.running = True
        self.map = "world"

        # Affichage de la fenêtre
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("La ferme des des fruits et légumes")

        # Charger la carte clasique
        base_path = os.path.dirname(__file__)
        tmx_path = os.path.join(base_path, "carte.tmx")
        tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 2

        # Générer le joueur
        player_position = tmx_data.get_object_by_name("player")
        self.player = Player(player_position.x, player_position.y)
        self.can_interact = False
        
        # Inventaire du joueur
        self.inventory = ["Graine_Tomate", "", "", ""]
        self.current_inventory_place = 0
        self.graine_type = ["Graine_Tomate",
                            "Graine_Maïs",
                            "Graine_Blé",
                            "Graine_Salade",
                            "Graine_Carrote"]

        # Définir le logo du jeu
        pygame.display.set_icon(self.player.get())

        # Les collisions
        self.walls = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Dessiner les différents calques
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=5)
        self.group.add(self.player)

        # Porte de la maison
        enter_house = tmx_data.get_object_by_name("enter_house")
        self.enter_house_rect = pygame.Rect(enter_house.x, enter_house.y, enter_house.width, enter_house.height)
        
        # Proximité des différents champ
        self.champ_rect = []
        for i in range(5):
            enter_champ = tmx_data.get_object_by_name(str("champ"+str(i+1)))
            self.champ_rect.append(pygame.Rect(enter_champ.x, enter_champ.y, enter_champ.width, enter_champ.height))
        print(self.champ_rect)
        
        # Proximité des différents distributeur
        base_path = os.path.dirname(__file__)
        tmx_path = os.path.join(base_path, "house.tmx")
        tmx_house_data = pytmx.util_pygame.load_pygame(tmx_path)
        self.distrib_rect = []
        for i in range(5):
            enter_distrib = tmx_house_data.get_object_by_name(str("graine"+str(i+1)))
            self.distrib_rect.append(pygame.Rect(enter_distrib.x, enter_distrib.y, enter_distrib.width, enter_distrib.height))
        
        enter_trash = tmx_house_data.get_object_by_name("trash")
        self.trash = pygame.Rect(enter_trash.x, enter_trash.y, enter_trash.width, enter_trash.height)
        
        # différentes graine de plantes     Temps necessaire
        self.plants = { "Graine_Tomate":    60*10,
                        "Graine_Maïs":      60*10,
                        "Graine_Blé":       60*10,
                        "Graine_Salade":    60*10,
                        "Graine_Carrote":   60*10}

        # emplacement des plantations
        self.place = 0
        self.type = ""
        self.growth = [-1,-1,-1,-1,-1]
        self.growth_type = ["","","","",""]
        
        # Dictionaire de transformation
        self.growth_dict = {"Graine_Tomate":    "Tomate",
                            "Graine_Maïs":      "Maïs",
                            "Graine_Blé":       "Blé",
                            "Graine_Salade":    "Salade",
                            "Graine_Carrote":   "Carrote"}

    def handle_input(self, events):
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and self.can_interact > 0:
                    if self.map == 'world':
                        self.planter(self.can_interact, self.inventory[self.current_inventory_place])
                    if self.map == 'house':
                        self.distrib(self.can_interact)
                
                #inventory slide left
                if event.key == pygame.K_q:
                    if self.current_inventory_place != 0:
                        self.current_inventory_place -= 1
                
                
                if event.key == pygame.K_d:
                    #inventory slide right
                    if self.current_inventory_place != len(self.inventory):
                        self.current_inventory_place += 1
                    
        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_ESCAPE]:
            self.running = False
        elif pressed[pygame.K_UP]:
            self.player.move_player("up")
        elif pressed[pygame.K_DOWN]:
            self.player.move_player("down")
        elif pressed[pygame.K_RIGHT]:
            self.player.move_player("right")
        elif pressed[pygame.K_LEFT]:
            self.player.move_player("left")
    
        print(self.growth,
            self.growth_type,
            self.inventory)
        
    
    def planter(self, place, type):
        #Si   (le champ est libre)    et (on possède un element dans notre main d'inventaire qui est une graine) :
        if self.growth[place-1] == -1 and self.inventory[self.current_inventory_place] in self.graine_type:
            #on met dans le champ adéquoit le temps de notre plante
            self.growth[place-1] = self.plants[type]
            #on met dans le champ corespondant le type de notre plante
            self.growth_type[place-1] = type
            #on utilise la graine dans notre inventaire
            self.inventory[self.current_inventory_place] = ""
        
        #Si  la plante a fini de pousser:
        if self.growth[place-1] == 0:
            # variable barrière (empèche le fait de récupérer avec un inventaire plein)
            passe = False
            #On cherche un emplacment libre dans notre inventaire
            for i in range(len(self.inventory)):
                if self.inventory[i] == '':
                    self.inventory[i] = self.growth_dict[self.growth_type[place-1]]
                    passe = True
                    break
            if passe:
                # champ à nouveau libre
                self.growth[place-1] = -1
                self.growth_type[place-1] = ''
    
    def distrib(self, place):
        if self.inventory[self.current_inventory_place] == "":
            self.inventory[self.current_inventory_place] = self.graine_type[place-1]
        elif place < 6:
            for i in range(len(self.inventory)):
                if self.inventory[i] == '':
                    self.inventory[i] = self.graine_type[place-1]
                    break
                
        elif place == 6:
            self.inventory[self.current_inventory_place] = ""

    def switch_house(self):
        self.map = "house"

        # Charger la carte clasique
        base_path = os.path.dirname(__file__)
        tmx_path = os.path.join(base_path, "house.tmx")
        tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 2

        # Les collisions
        self.walls = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Dessiner les différents calques
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=5)
        self.group.add(self.player)

        # Porte de la maison
        enter_house = tmx_data.get_object_by_name("exit_house")
        self.enter_house_rect = pygame.Rect(enter_house.x, enter_house.y, enter_house.width, enter_house.height)

        # Intérieur
        spawn_house_point = tmx_data.get_object_by_name("spawn_house")
        self.player.position[0] = spawn_house_point.x
        self.player.position[1] = spawn_house_point.y - 20

    def switch_world(self):
        self.map = "world"

        # Charger la carte clasique
        base_path = os.path.dirname(__file__)
        tmx_path = os.path.join(base_path, "carte.tmx")
        tmx_data = pytmx.util_pygame.load_pygame(tmx_path)
        map_data = pyscroll.data.TiledMapData(tmx_data)
        map_layer = pyscroll.orthographic.BufferedRenderer(map_data, self.screen.get_size())
        map_layer.zoom = 2

        # Les collisions
        self.walls = []

        for obj in tmx_data.objects:
            if obj.type == "collision":
                self.walls.append(pygame.Rect(obj.x, obj.y, obj.width, obj.height))

        # Dessiner les différents calques
        self.group = pyscroll.PyscrollGroup(map_layer=map_layer, default_layer=5)
        self.group.add(self.player)

        # Porte de la maison
        enter_house = tmx_data.get_object_by_name("enter_house")
        self.enter_house_rect = pygame.Rect(enter_house.x, enter_house.y, enter_house.width, enter_house.height)

        # Intérieur
        spawn_house_point = tmx_data.get_object_by_name("enter_house_exit")
        self.player.position[0] = spawn_house_point.x
        self.player.position[1] = spawn_house_point.y + 20

    def update(self):
        self.group.update()

        # Vérifier l'entrer de la maison
        if self.map == "world" and self.player.feet.colliderect(self.enter_house_rect):
            self.switch_house()

        if self.map == "house" and self.player.feet.colliderect(self.enter_house_rect):
            self.switch_world()
        
        # Interaction avec les différents champs
        if self.map == "world":
            for i in range(5):
                if self.player.feet.colliderect(self.champ_rect[i]):
                    self.can_interact = i+1
                    break
                else:
                    self.can_interact = 0
        else:
            # Interaction avec les différents distributeur
            for i in range(5):
                if self.player.feet.colliderect(self.distrib_rect[i]):
                    self.can_interact = i+1
                    break
                else:
                    self.can_interact = 0
            
            if self.player.feet.colliderect(self.trash):
                self.can_interact = 6
        
        # Pousse des plants
        for i in range(len(self.growth)):
            if self.growth[i] > 0:
                self.growth[i] -= 1
           
        # Vérification des collisions
        for sprite in self.group.sprites():
            if sprite.feet.collidelist(self.walls) > -1:
                sprite.move_back()

    def run(self):
        clock = pygame.time.Clock()

        # Clock
        while self.running:

            self.player.save_location()
            
            events = pygame.event.get()
            self.handle_input(events)
            
            self.update()
            self.group.center(self.player.rect.center)
            self.group.draw(self.screen)
            pygame.display.flip()

            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            clock.tick(60)

        pygame.quit()
