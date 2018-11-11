#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# -*- coding: utf-8 -*-


import math
import random
from PIL import Image, ImageDraw # pour installer la librairie PIL, de laquelle on importe les modules Image (permet d'ouvrir des images), et Imagedraw (permet de déssiner et modifier)

class Boule():
	"""
	Définition du premier objet : la boule, capable de
	- se placer sur le billard,
	- de définir aléatoirement la première direction qu'elle va prendre,
	- de se déplacer
	"""
	RAYON = 5 # rayon de la boule

	def __init__(self):
		"""Constructeur de la boule"""
		self.placer()
		self.definir_la_direction()

	def placer(self):
		"""Définition de l'emplacement initial de la boule"""
		self.x = float(random.randint(0, Flipper.LARGEUR - 1)) # On définit de facon aléatoire l'abscisse et l'ordonnée de la boule
		self.y = float(random.randint(0, Flipper.HAUTEUR - 1)) # -1 permet de prendre en compte la largeur du trait
		self.x_initial = self.x 							   # self.x et self.y sont les abscisse et ordonnée de la boule à chaque instant
		self.y_initial = self.y # variables utiles pour le debut du dessin (cf fonction dessine)

	def definir_la_direction(self):
		"""Définition de la direction du déplacement initial de la boule"""
		direction = 2.0 * math.pi * random.random()		# On choisit un point aléatoire du cercle trigonométrique
		self.abscisse_direction = math.sin(direction)	# self.abscisse_direction (resp. ordonnées) est la variable qui s'ajoute à l'abscisse (resp. à l'ordonnée)
		self.ordonnee_direction = math.cos(direction)	# pour que la boule se déplace

	def deplacer(self, xnew, ynew):
		"""
		Modifie les coordonnées de la boule durant son déplacement
		Entrées :
		- xnew : nouvelle abscisse
		- ynew : nouvelle ordonnée
		Le déplacement est modélisé comme une étape infinitésimale, xnew et ynew sont strès proches de x et y.
		"""
		self.x = xnew 
		self.y = ynew

class Flipper():
	"""
	Définition du deuxième objet : le flipper, capable de définir ses obstacles aléatoirement, de se faire déplacer une boule,
	et d'enregistrer des photos des étapes du déplacement de la boule dans un fichier.
	"""
	# on définit comme des constantes toutes les valeurs qui ne seront pas modifiées
	# DOSSIER_RESULTAT = "Billard" # nom du dossier dans lequel on stocke les images qui sont générées
	LARGEUR = 500 # largeur du flipper
	HAUTEUR = 800 # hauteur du flipper
	COULEUR_DEPART = (30, 169, 46) # vert clair
	COULEUR_ARRIVEE = (255, 0, 0) # rouge foncé
	COULEUR_OBSTACLES = (255,255,255) # blanc
	NB_OBSTACLES = 7 # nombre d'obstables fixes circulaires
	RAYON_OBSTACLE = 50 # rayon d'un obstacle
	NB_MAX_ETAPES = 20000 # nombre d'étapes de déplacement de la boule

	def __init__(self):
		"""Constructeur du flipper"""
		self.execution()
		self.rebonds = [] # matrice des coordonnées des points de rebonds ex: [(x1, y1), (x2, y2)]
		self.boule = Boule() # Importation de l'objet boule
		self.placer_les_obstacles()
		self.lancer_la_boule()
		self.dessiner()
		

	def placer_les_obstacles(self):
		"""Création des obstacles circulaires"""
		self.liste_centres_abscisses = [] # Liste des abscisses du centre des obstacles
		self.liste_centres_ordonnees = [] # Liste des ordonnées du centre des obstacles

		for obstacle_courant in range(self.NB_OBSTACLES): # On place successivement chacun des obstacles

			chevauchement = True 	# On suppose a priori qu'il y'a chevauchement pour le placement de l'obstacle en cours

			while(chevauchement): 	# Tant qu'il y'a chevauchement, on ne définit pas la position définitive de l'obstacle
				abscisse_centre = random.randint(self.RAYON_OBSTACLE, self.LARGEUR - 1 - self.RAYON_OBSTACLE) 	# abscisse du centre du cercle (-1 pour l'epaisseur du trait) choisie aléatoirement
				ordonnee_centre = random.randint(self.RAYON_OBSTACLE, self.HAUTEUR - 1 - self.RAYON_OBSTACLE) 	# ordonnée du centre du cercle choisie aléatoirement
				chevauchement = False 	# pour mettre fin a la boucle dans le cas où il n'y aurait déjà la boule ou d'autres obstacles

				if math.hypot(self.boule.x - abscisse_centre, self.boule.y - ordonnee_centre) <= self.RAYON_OBSTACLE: 	# On test le chevauchement de l'obstacle en cours avec la boule
					chevauchement = True 	# Si la distance est inferieur a la somme du rayon de l'obstacle et de la boule, il y'a chevauchement

				elif obstacle_courant > 0:	 # à partir du deuxième obstcale il faut vérifier que l'obstacle en cours ne chavauche pas ceux qui ont déjà étés placés
					for j in range(obstacle_courant): # pour chaque obstacles déjà créés on vérifie que celui en cours de création ne les chevauche pas
						if math.hypot(abscisse_centre - self.liste_centres_abscisses[j], ordonnee_centre - self.liste_centres_ordonnees[j]) < self.RAYON_OBSTACLE * 2:
							# on vérifie que la distance entre le centre de la boule que l'on place et le centre de toutes les autres boules n'est pas inférieure
							# au double du rayon, auquel cas les boules se chevaucheraient
							chevauchement = True

							break # pour ne pas continuer à vérifier pour les autres obstacles si un seul chevauchement a été constaté
			
			self.liste_centres_abscisses.append(abscisse_centre) # on stock les coordonnées des centres de chaque obstacles (une fois que les tests de chevauchement on été réalisés)
			self.liste_centres_ordonnees.append(ordonnee_centre)

	def lancer_la_boule(self):
		"""Déplacement de la boule"""
		for chaque_etape in range(self.NB_MAX_ETAPES):
			xnew = self.boule.x + self.boule.abscisse_direction # xnew et ynew sont les abscisses et ordonnées potentielles qui remplaceront
			ynew = self.boule.y + self.boule.ordonnee_direction # les abscisses et ordonnées réelles une fois les tests de rebonds éfféctués

			xnew, ynew = self.rebond_contre_parois(xnew, ynew) 	# On test si il doit y avoir rebond
			xnew, ynew = self.rebond_contre_obstacle(xnew, ynew)

			self.boule.deplacer(xnew, ynew) # On sauvegarde les nouvelles coordonnées de la boule

	def rebond_contre_parois(self, xnew, ynew):
		"""
		Test d'un éventuel rebond contre les parois
		Entrées:
		- xnew : potentielle nouvelle abscisse
		- ynew : potentielle nouvelle ordonnée
		Sorties :
		- xnew : nouvelle abscisse
		- ynew : nouvelle ordonnée
		"""
		if (xnew - Boule.RAYON < 0) or (xnew + Boule.RAYON > self.LARGEUR - 1): # On test si l'abscisse potentielle ne sort pas à gauche ou à droite du cadre
			self.boule.abscisse_direction = -self.boule.abscisse_direction 		# Si c'est le cas, on inverse l'oronnée "boule.abscisse_direction" ce qui a pour effet de modéliser un rebond
			xnew = self.boule.x 												# avec le même angle de rebond que l'angle d'incidence
			self.ajoute_rebond(xnew, ynew)
		
		if (ynew - Boule.RAYON < 0) or (ynew + Boule.RAYON > self.HAUTEUR - 1): # On test si l'ordonnée potentielle ne sort pas en haut ou en bas du cadre
			self.boule.ordonnee_direction = -self.boule.ordonnee_direction 		# Le cas est analogue au test précédent
			ynew = self.boule.y 			# dans le cas où on a percuté une paroi "on revient à l'étape d'avant", en remplacant les coordonnées potentielles par les coordonnées 
											# réelles lorsque l'on a pas encore percuté la paroi
			self.ajoute_rebond(xnew, ynew) # On ajoute les coordonnées de rebond dans la matrice des rebonds qui seront utiles dans la fonction dessine

		return (xnew, ynew)

	def rebond_contre_obstacle(self, xnew, ynew):
		"""
		Test d'un éventuel rebond contre les obstacles
		Entrées :
		- xnew : potentielle nouvelle abscisse
		- ynew : potentielle nouvelle ordonnée
		Sorties :
		- xnew : nouvelle abscisse
		- ynew : nouvelle ordonnée
		"""
		for i in range(self.NB_OBSTACLES):
			if math.hypot(xnew - self.liste_centres_abscisses[i], ynew - self.liste_centres_ordonnees[i]) <= self.RAYON_OBSTACLE + Boule.RAYON : # Si l'abscisse et l'ordonnée potentielle sont
																																				 # dans un obstacle
				angle_theorique = math.atan2(ynew - self.liste_centres_ordonnees[i], xnew - self.liste_centres_abscisses[i]) # angle "entre le point et le centre du cercle"		
				
				angle_incidence = math.atan2(-self.boule.ordonnee_direction, -self.boule.abscisse_direction) # opposé de l'angle d'incidence
				
				angle_rebond = angle_incidence + (angle_theorique - angle_incidence) * 2 # Par le calcul on trouve l'angle de facon à modéliser un rebond contre
																						 # une paroi qui serait la tangeante au cercle au point d'impact
				self.boule.ordonnee_direction = math.sin(angle_rebond) # On modifie les coordonnées qui s'ajoutent à chaque étape, une fois la nouvelle direction définie
				self.boule.abscisse_direction = math.cos(angle_rebond)

				xnew = self.boule.x # dans le cas où on a percuté une boule "on revient à l'étape d'avant" lorsque l'on a pas encore percuté l'obstacle
				ynew = self.boule.y

				self.ajoute_rebond(xnew, ynew) # On ajoute les coordonnées de rebond dans la matrice des rebonds qui seront utiles dans la fonction dessine

		return (xnew, ynew)

	def ajoute_rebond(self, xnew, ynew):
		"""
		Ajoute les coordonnées des rebonds dans la matrice des coordonnées de rebond
		Entrées :
		- xnew : abscisse du rebond
		- ynew : ordonnée du rebond
		"""
		self.rebonds.append((xnew, ynew))

	def dessiner(self):
		""" Méthode de dessin du résultat de la simulation """
		image  = Image.new("RGB", (self.LARGEUR, self.HAUTEUR)) # crée une image en couleur de taille définie selon les constantes de la classe
		dessin = ImageDraw.Draw(image) # débute le dessin de l'image
		compteur = 0 # sert à nommer les fichiers images différement à chaque rebond
		debut_trait_x = self.boule.x_initial # Abscisses et ordonnées du début de tracé
		debut_trait_y = self.boule.y_initial
		nb_rebonds = len(self.rebonds)

		for obstacle in range(self.NB_OBSTACLES): # On dessine tous les obstacles
			dessin.ellipse((self.liste_centres_abscisses[obstacle] - self.RAYON_OBSTACLE, # La fonction elllipse permet de dessiner une ellipse (ici un disque)
							self.liste_centres_ordonnees[obstacle] - self.RAYON_OBSTACLE, # en connaissant ces quatres points cardinaux
							self.liste_centres_abscisses[obstacle] + self.RAYON_OBSTACLE,
							self.liste_centres_ordonnees[obstacle] + self.RAYON_OBSTACLE),
							fill = self.COULEUR_OBSTACLES) # On remplit l'obstacle avec la couleur

		for coordonnees in self.rebonds: # On trace des traits entre chaque points ou il y'a eu rebond ce qui dessine la trajectoire
			compteur += 1
			fin_trait_x, fin_trait_y = coordonnees
			epaisseur_trait = Boule.RAYON * 2 + 2 # le diamiètre de la boule + 2 pixels pour l'epaisseur de chaque bordure
			couleur_trait = self.couleur_aleatoire()

			dessin.ellipse((debut_trait_x - Boule.RAYON, # On dessine la boule au début du trait (arrondi l'angle du trait)
							debut_trait_y - Boule.RAYON,
							debut_trait_x + Boule.RAYON,
							debut_trait_y + Boule.RAYON),
							fill = couleur_trait)
			
			dessin.line((int(debut_trait_x), # On trace le trait entre les rebonds
						 int(debut_trait_y),
						 int(fin_trait_x),
						 int(fin_trait_y)),
						 couleur_trait,
						 width = epaisseur_trait)
			
			dessin.ellipse((fin_trait_x - Boule.RAYON, # On dessine la boule à la fin du trait pour arrondir à nouveau l'angle
							fin_trait_y - Boule.RAYON,
							fin_trait_x + Boule.RAYON,
							fin_trait_y + Boule.RAYON),
							fill = couleur_trait)
			
			image.save(self.dossier_resultat + "/flipper " + str(compteur) + ".png", "PNG") # génère l'image dans le dossier "resultat" avec pour nom "flipper_X.png" où X varie de 1 à n rebonds
			
			debut_trait_x = fin_trait_x # on transforme le bout du trait que l'on
			debut_trait_y = fin_trait_y # vient de tracer en début du trait suivant

	def couleur_aleatoire(self):
		"""
		Génère un code couleur RGB aléatoire
		Sorties :
		- R : nombre aléatoire entre 0 et 255 qui determine la "teneur en rouge
		- G : nombre aléatoire entre 0 et 255 qui determine la "teneur en vert
		- B : nombre aléatoire entre 0 et 255 qui determine la "teneur en bleu
		"""
		return (random.randint(0,255), random.randint(0,255), random.randint(0,255))

	def execution(self):
		self.dossier_resultat = raw_input ("Apres avoir cree un dossier vide, veuillez saisir le nom de ce dossier dans lequel vous souhaitez enregistrer les images de la simulation : \n ")

 
Flipper() # Créé un flipper et lance la simulation


# In[ ]:




