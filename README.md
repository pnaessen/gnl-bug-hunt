# Get Next Line Bug Hunt

Ce repository contient une version volontairement buggée de la fonction Get Next Line, dans le cadre d'un événement de debugging.

## Description

Get Next Line (GNL) est une fonction qui lit une ligne depuis un descripteur de fichier. Cette version contient plusieurs bugs que vous devez identifier et corriger le plus rapidement possible.

## Règles

- **Fonctions autorisées** : Uniquement `read`, `malloc` et `free`
- **Interdictions** :
  - Pas de malloc(50000) ou autres "dégueulasseries" similaires
  - Pas de fonctions de la libc non autorisées
  - Pas de modifications du prototype de `get_next_line`
  - Pas d'utilisation de variables globales
  - Pas de norme, mais le code doit rester propre
  - Fonctions externes autorisées read, malloc, free
 
## Liste des bugs connus

Cette version de GNL contient divers bugs, notamment:
- Fuites de mémoire
- Inversions de conditions
- Problèmes d'initialisation
- Erreurs de manipulation de buffer
- Et bien d'autres...

## Installation

Clonez le repository:

```bash
git@github.com:pnaessen/gnl-bug-hunt.git
cd gnl-bug-hunt
```

## Tests

Un script de test Python est fourni pour vérifier votre implémentation:

```bash
python3 tester.py
```

Ce script testera votre implementation avec différentes tailles de buffer et divers fichiers d'entrée.

## Exemples d'utilisation

Exemple d'utilisation de la fonction GNL dans votre propre programme:

```c
#include "get_next_line.h"
#include <fcntl.h>
#include <stdio.h>

int main(void)
{
    int     fd;
    char    *line;
    
    fd = open("test.txt", O_RDONLY);
    while ((line = get_next_line(fd)) != NULL)
    {
        printf("%s", line);
        free(line);
    }
    close(fd);
    return (0);
}
```

## Soumettre vos corrections

Une fois que tous les tests du tester sont passés avec succès, levez les bras et prévenez un des tuteurs pour vérifier si tout est bon.

Bonne chance!
