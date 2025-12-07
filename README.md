# Application Microservices Bookstore

## Table des matières

1. [Présentation du projet](#présentation-du-projet)  
2. [Architecture](#architecture)  
3. [Structure du projet](#structure-du-projet)  
4. [Description des services](#description-des-services)  
5. [Base de données](#base-de-données)  
6. [Déploiement](#déploiement)  
7. [Tests](#tests)  
8. [Captures d’écran](#captures-décran)  
9. [Apprentissages clés](#apprentissages-clés)  
10. [Fonctionnalités bonus](#fonctionnalités-bonus)
    
## Présentation du projet

Ce projet illustre une **architecture microservices pour une librairie en ligne**. Le backend monolithique a été décomposé en trois microservices indépendants :

- **API Gateway** : point d’entrée central, routage des requêtes, agrégation des statuts de santé des services.  
- **Book Service** : gestion du catalogue de livres, opérations CRUD, gestion des stocks.  
- **Order Service** : traitement des commandes clients, communication avec Book Service pour réserver le stock.

# Architecture 
## Vue globale du cluster K3s

```
┌─────────────────────────────────────────────────────────┐
│                         K3s Cluster                     │
│                                                         │
│  ┌──────────────────────────────┐                       │
│  │        Frontend (Nginx)      │                       │
│  │       NodePort: 30080        │                       │
│  └───────────────┬──────────────┘                       │
│                  │ HTTP                                 │
│                  ▼                                     │
│  ┌──────────────────────────────┐                       │
│  │        API Gateway            │                       │
│  │        Port: 5000             │                       │
│  │ - Routage des requêtes        │                       │
│  │ - Agrégation des statuts      │                       │
│  │ - Load balancing              │                       │
│  │ - Journalisation              │                       │
│  │ ClusterIP                     │                       │
│  └───────────┬─────────────┬────┘                       │
│              │             │                              │
│              ▼             ▼                              │
│  ┌───────────────┐   ┌───────────────┐                  │
│  │ Book Service  │   │ Order Service │                  │
│  │ Port: 5001    │◄──┤ Port: 5002    │                  │
│  │ ClusterIP     │   │ ClusterIP     │                  │
│  └─────┬─────────┘   └─────┬─────────┘                  │
│        │                   │                            │
│        ▼                   │                            │
│  ┌──────────────────────────────┐                       │
│  │        PostgreSQL             │                       │
│  │        Port: 5432             │                       │
│  │        ClusterIP              │                       │
│  └──────────────────────────────┘                       │
└─────────────────────────────────────────────────────────┘
