# Touch Maker Lab

Touch Maker Lab est une carte d'extension pour Raspberry PI, pensée par des makers pour des makers, conçue pour faciliter la connexion et la programmation des entrées/sorties. Elle permet d’interagir avec le système grâce à ses 6 pads tactiles et de relier de 6 à 12 GPIO en quelques secondes grâce à ses 6 connecteurs jack. 
Fini la prise de tête avec le câblage — concentrez-vous sur le code, que ce soit sur Scratch ou en Python.

_by SLmediation &amp; F-ROBOTICS.FR_

### Objectif du projet

* réaliser une petite carte pour Raspberry PI permettant le raccordement simplifié d'actionneurs type bouton poussoir  ... et peut-être un peu plus !
* éliminer les nombreux fils "spaghetti" ( même si on les aime bien tout de même )  


### Quelques contraintes dans notre cahier des charges :

* une carte Fun, sympa, visuellement reconnaissable
* simple à utiliser 
* interfaçable naturellement avec Scratch
* offrant certaines possibilités d'évolution ou d'utilisation avancée

### TODO

* partager ce projet et nos réflexions à la communauté Maker
* Trouver un nom à cette petite carte 

_et également :_ 

* continuer à documenter 
* et proposer des activités ludiques 


<img src="images/20260318_183931_2.jpg" width="100%">

---

### Experimental Raspberry PI HAT - version 0.3

<table width="100%">
<td align="center"><img src="images/carte_1_no_bg.png" ></td>
<td align="center"><img src="images/carte_2_no_bg.png" ></td>
</table>

---

### Description de la carte 

la carte est composée de :

* 6 connecteurs type "Jack Stéréo 3.5mm"
    * chaque connecteur propose 2 Gpio + Gnd
    * possibilité d'utilisation en entrée ou en sortie 
* 6 Pads à détection capacitive
    * fonctionnent sans aucune programmation
    * disposent d'une LED témoin
* Gpios des bus I2C, SPI, UART en accès direct
    *  avec le +5v et Gnd

<br>

<img src="images/carte_desc-global.drawio.png">

---

### Connecteurs JACK

Possibilité d'utiliser des connecteurs Jack 3.5mm monos ou stéréos

* **Gpio 16 à 21** en entrée/sortie **primaires** , et reliés aux Pads
* **Gpio 22 à 27** en entrée/sortie **secondaires**
    * uniquement en utilisant un Jack Stéréo

<br>

<img src="images/carte_desc-Jack.drawio.png">

---

### Schéma simplifié

* les Gpio 16 à 21 dispose d'une résistance le pull-up de 10k
* les Gpio 16 à 27 sont protégés par une résistance de 470 ohms, en série, afin de limiter le courant de court circuit, en cas d'erreur de manipulation et/ou programmation

* Les Gpio des bus I2c, Spi, et Uart sont directement disponible

<br>

<img src="images/carte_desc-Gpio_protect.drawio.png">

### Schéma 

<table width="100%">
<td align="center"><img src="images/Schematic_2026-RPI-Hat-SLM-v0.3_2026-03-25.png" /td>
<td align="center"><img src="images/Capture_ecran_2026-02-25_171941.png" ></td>

</table>

### Design

* Dessin vectoriel
* Utilisation de Inkscape
* Import dans EasyEDA


<img src="images/PCB_Design.png">


















