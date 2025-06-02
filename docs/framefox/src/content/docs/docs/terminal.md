---
title: Terminal et commandes
description: Utilisez le terminal interactif et créez des commandes personnalisées dans Framefox
---

import { Tabs, TabItem } from '@astrojs/starlight/components';
import CodeBlock from '../../../components/CodeBlock.astro';

# Terminal et commandes

Framefox intègre un terminal interactif puissant qui vous permet d'effectuer des opérations courantes et d'automatiser des tâches. Vous pouvez également créer vos propres commandes pour étendre ses fonctionnalités.

## Terminal interactif

Le terminal interactif de Framefox vous donne accès à un ensemble de commandes pour gérer votre application :

<CodeBlock
  code={`framefox`}
  lang="bash"
/>

Cela ouvre le terminal interactif qui affiche la liste des commandes disponibles :

```
 🦊 Framefox Terminal v1.0.0
 ---------------------------
 
 Commandes disponibles :
   help                           Affiche l'aide pour toutes les commandes
   init                           Initialise un nouveau projet Framefox
   serve                          Démarre le serveur de développement
   create                         Assistant de création de composants
   migration                      Gestion des migrations de base de données
   cache                          Commandes liées au cache
   test                           Exécute les tests unitaires
   security                       Commandes liées à la sécurité
   debug                          Outils de débogage
```

## Commandes de base

### Initialisation d'un projet

Pour créer un nouveau projet Framefox :

<CodeBlock
  code={`framefox init`}
  lang="bash"
/>

Cette commande lance un assistant interactif qui vous guidera pour configurer votre projet :

```
🦊 Initialisation d'un nouveau projet Framefox
----------------------------------------------

Nom du projet [my-framefox-app]: blog
Type de projet:
  [1] Application web complète (recommandé)
  [2] API REST
  [3] Microservice
  [4] Projet minimal
Votre choix [1]: 1

Configuration de la base de données:
  [1] SQLite (recommandé pour démarrer)
  [2] PostgreSQL
  [3] MySQL
  [4] Aucune
Votre choix [1]: 2

Authentification:
  [1] Système complet (login/register)
  [2] API Token uniquement
  [3] Aucune authentification
Votre choix [1]: 1

✅ Projet 'blog' initialisé avec succès!
📁 Structure de base du projet créée
📦 Dépendances installées
📝 Configuration de base générée

Pour démarrer le serveur de développement:
  cd blog
  framefox serve
```

### Démarrage du serveur

Pour démarrer le serveur de développement :

<CodeBlock
  code={`framefox serve`}
  lang="bash"
/>

Options disponibles :

<CodeBlock
  code={`framefox serve --port 8080 --host 0.0.0.0 --reload`}
  lang="bash"
/>

- `--port` : Spécifie le port (8000 par défaut)
- `--host` : Spécifie l'hôte (127.0.0.1 par défaut)
- `--reload` : Active le rechargement automatique
- `--debug` : Active le mode débogage

## Création de composants

La commande `create` vous permet de générer rapidement divers composants :

<CodeBlock
  code={`framefox create controller`}
  lang="bash"
/>

Cela lance un assistant interactif :

```
🦊 Assistant de création de contrôleur
-------------------------------------

Nom du contrôleur: ProductController
Ajouter des routes:
  [1] Ajouter une route d'index (GET)
  [2] Ajouter des routes CRUD complètes
  [3] Aucune route prédéfinie
Votre choix [1]: 2

Entité associée: Product

✅ Contrôleur ProductController créé avec succès!
📁 Fichier: src/controllers/product_controller.py
```

Autres composants que vous pouvez créer :

<CodeBlock
  code={`framefox create entity       # Crée une nouvelle entité
framefox create form         # Crée un nouveau type de formulaire
framefox create repository   # Crée un repository personnalisé
framefox create service      # Crée un nouveau service
framefox create command      # Crée une commande personnalisée
framefox create middleware   # Crée un middleware
framefox create event        # Crée un écouteur d'événements`}
  lang="bash"
/>

## Gestion des migrations

Framefox utilise Alembic pour gérer les migrations de base de données :

<CodeBlock
  code={`framefox migration:generate   # Génère une migration à partir des changements détectés
framefox migration:run        # Exécute les migrations en attente
framefox migration:revert     # Annule la dernière migration
framefox migration:status     # Affiche l'état des migrations`}
  lang="bash"
/>

Exemple :

<CodeBlock
  code={`framefox migration:generate --message "Ajout de la table product"`}
  lang="bash"
/>

## Commandes de cache

<CodeBlock
  code={`framefox cache:clear          # Vide tous les caches
framefox cache:warmup         # Précharge les caches
framefox cache:status         # Affiche l'état du cache`}
  lang="bash"
/>

## Commandes de sécurité

<CodeBlock
  code={`framefox security:encode-password   # Encode un mot de passe
framefox security:generate-keys     # Génère des clés de sécurité
framefox security:audit             # Audit de sécurité de l'application`}
  lang="bash"
/>

## Commandes de débogage

<CodeBlock
  code={`framefox debug:router         # Affiche toutes les routes de l'application
framefox debug:container       # Affiche tous les services du conteneur
framefox debug:config          # Affiche la configuration actuelle
framefox debug:twig            # Liste les templates disponibles`}
  lang="bash"
/>

## Création de commandes personnalisées

Vous pouvez créer vos propres commandes pour automatiser des tâches spécifiques à votre application :

<CodeBlock
  code={`from framefox.core.command.abstract_command import AbstractCommand
from framefox.core.command.input import Input
from framefox.core.command.output import Output

class ImportDataCommand(AbstractCommand):
    def get_name(self):
        return "app:import-data"
    
    def get_description(self):
        return "Importe des données depuis un fichier CSV"
    
    def configure(self):
        self.add_argument("file", "Chemin vers le fichier CSV à importer")
        self.add_option("--force", "f", "Écraser les données existantes")
        self.add_option("--dry-run", None, "Simulation sans modification")
    
    async def execute(self, input: Input, output: Output):
        file_path = input.get_argument("file")
        force = input.get_option("force")
        dry_run = input.get_option("dry-run")
        
        output.write_line(f"Importation depuis {file_path}")
        
        if dry_run:
            output.write_line("<info>Mode simulation activé</info>")
        
        # Logique d'importation
        try:
            # Récupérer les services nécessaires
            entity_manager = self.get_container().get("entity_manager")
            import_service = self.get_container().get("app.import_service")
            
            # Lire le fichier CSV
            import csv
            
            with open(file_path, "r") as csv_file:
                reader = csv.DictReader(csv_file)
                
                # Créer une barre de progression
                count = sum(1 for _ in open(file_path)) - 1  # Nombre de lignes - en-tête
                progress = output.create_progress_bar(count)
                progress.start()
                
                for i, row in enumerate(reader):
                    # Traiter chaque ligne
                    if not dry_run:
                        await import_service.import_row(row, force=force)
                    
                    # Mettre à jour la progression
                    progress.advance()
                
                progress.finish()
            
            output.write_line("<info>Importation terminée avec succès!</info>")
            return 0
            
        except Exception as e:
            output.write_line(f"<error>Erreur lors de l'importation: {str(e)}</error>")
            return 1`}
  lang="python"
  filename="src/command/import_data_command.py"
/>

### Enregistrement de la commande

Pour rendre votre commande disponible, vous devez l'enregistrer dans la configuration :

<CodeBlock
  code={`# config/services.yaml
services:
  app.command.import_data:
    class: src.command.import_data_command.ImportDataCommand
    tags: ["console.command"]`}
  lang="yaml"
  filename="config/services.yaml"
/>

### Utilisation de la commande

Vous pouvez maintenant utiliser votre commande :

<CodeBlock
  code={`framefox app:import-data data/products.csv --force`}
  lang="bash"
/>

## Formatage avancé des sorties

Les commandes Framefox supportent un formatage riche pour les sorties :

<CodeBlock
  code={`async def execute(self, input: Input, output: Output):
    # Texte avec des styles
    output.write_line("<info>Opération réussie</info>")
    output.write_line("<error>Erreur critique</error>")
    output.write_line("<warning>Attention</warning>")
    output.write_line("<question>Continuer?</question>")
    
    # Tableaux
    table = output.create_table()
    table.set_headers(["ID", "Nom", "Prix"])
    table.add_row(["1", "Produit A", "19.99€"])
    table.add_row(["2", "Produit B", "29.99€"])
    table.render()
    
    # Demander une entrée utilisateur
    name = output.ask("Quel est votre nom?")
    password = output.ask_hidden("Mot de passe:")
    
    choice = output.choice(
        "Choisissez une option:",
        ["Option 1", "Option 2", "Option 3"],
        default=0
    )
    
    # Confirmation
    if output.confirm("Êtes-vous sûr?", default=False):
        output.write_line("Action confirmée!")`}
  lang="python"
/>

## Tâches planifiées

Framefox permet d'exécuter des commandes selon un planning grâce à l'intégration de cron. Configurez les tâches dans `config/tasks.yaml` :

<CodeBlock
  code={`# config/tasks.yaml
tasks:
  # Exécuté tous les jours à minuit
  daily_cleanup:
    command: "app:cleanup-old-data"
    schedule: "0 0 * * *"
    
  # Exécuté toutes les 5 minutes
  sync_data:
    command: "app:sync-external-data"
    schedule: "*/5 * * * *"
    
  # Exécuté tous les lundis à 9h
  weekly_report:
    command: "app:generate-report --type=weekly"
    schedule: "0 9 * * 1"`}
  lang="yaml"
  filename="config/tasks.yaml"
/>

Pour démarrer le planificateur de tâches :

<CodeBlock
  code={`framefox tasks:run`}
  lang="bash"
/>

## Commandes interactives complexes

Vous pouvez créer des commandes interactives avancées :

<CodeBlock
  code={`async def execute(self, input: Input, output: Output):
    # Menu interactif
    output.title("Assistant de configuration")
    
    name = output.ask("Nom du projet:")
    
    env = output.choice(
        "Environnement:",
        ["Développement", "Test", "Production"],
        default=0
    )
    
    features = output.multiple_choice(
        "Fonctionnalités à activer:",
        [
            "API REST",
            "Interface d'administration",
            "Authentification",
            "Envoi d'emails",
            "Notifications push"
        ]
    )
    
    # Traitement des options sélectionnées
    output.section("Résumé de la configuration")
    output.write_line(f"Projet: <info>{name}</info>")
    output.write_line(f"Environnement: <info>{env}</info>")
    
    output.write_line("Fonctionnalités activées:")
    for feature in features:
        output.write_line(f" - <info>{feature}</info>")
    
    # Confirmation finale
    if not output.confirm("Appliquer cette configuration?", default=True):
        output.write_line("<warning>Configuration annulée.</warning>")
        return 1
    
    # Traitement...
    progress = output.create_progress_bar(5)
    progress.start()
    
    output.write_line("Génération des fichiers de configuration...")
    await self.generate_config_files(name, env, features)
    progress.advance()
    
    output.write_line("Installation des dépendances...")
    await self.install_dependencies(features)
    progress.advance()
    
    # ... autres étapes
    
    progress.finish()
    
    output.success("Configuration appliquée avec succès!")
    return 0`}
  lang="python"
/>

## Commandes avec arguments JSON

Pour les cas plus complexes, vous pouvez accepter des données JSON :

<CodeBlock
  code={`from framefox.core.command.abstract_command import AbstractCommand
from framefox.core.command.input import Input
from framefox.core.command.output import Output
import json

class ImportComplexDataCommand(AbstractCommand):
    def get_name(self):
        return "app:import-complex-data"
    
    def get_description(self):
        return "Importe des données complexes depuis un fichier JSON"
    
    def configure(self):
        self.add_argument("file", "Fichier JSON contenant les données")
        self.add_option("--config", "c", "Fichier de configuration pour l'import")
    
    async def execute(self, input: Input, output: Output):
        file_path = input.get_argument("file")
        config_path = input.get_option("config")
        
        # Charger le fichier JSON
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            # Charger la configuration si spécifiée
            config = None
            if config_path:
                with open(config_path, "r") as f:
                    config = json.load(f)
            
            # Traiter les données
            output.write_line(f"Importation de {len(data)} éléments...")
            
            # Logique d'importation...
            
            output.success("Importation terminée!")
            return 0
            
        except json.JSONDecodeError:
            output.error(f"Le fichier {file_path} n'est pas un JSON valide")
            return 1
        except FileNotFoundError:
            output.error(f"Fichier non trouvé: {file_path}")
            return 1`}
  lang="python"
/>

## Sortie dans différents formats

Vous pouvez adapter la sortie en fonction du format demandé :

<CodeBlock
  code={`async def execute(self, input: Input, output: Output):
    # Récupérer des données
    data = await self.get_data()
    
    # Déterminer le format de sortie
    format = input.get_option("format") or "table"
    
    if format == "json":
        # Sortie JSON
        import json
        output.write(json.dumps(data, indent=2))
    
    elif format == "csv":
        # Sortie CSV
        import csv
        import io
        
        csv_output = io.StringIO()
        writer = csv.DictWriter(csv_output, fieldnames=data[0].keys())
        
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        
        output.write(csv_output.getvalue())
    
    elif format == "xml":
        # Sortie XML
        import dicttoxml
        xml = dicttoxml.dicttoxml(data)
        output.write(xml.decode())
    
    else:
        # Sortie table par défaut
        table = output.create_table()
        
        # Définir les en-têtes
        headers = list(data[0].keys())
        table.set_headers(headers)
        
        # Ajouter les lignes
        for item in data:
            table.add_row([str(item[key]) for key in headers])
        
        table.render()`}
  lang="python"
/>

Le terminal et les commandes de Framefox offrent un moyen puissant d'automatiser les tâches récurrentes, d'effectuer des opérations de maintenance et de construire rapidement des composants pour votre application.
