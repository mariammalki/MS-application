# Application Microservices Bookstore

## Table des matières

1. [Présentation du projet](#présentation-du-projet)  
2. [Architecture](#architecture)  
3. [Structure du projet](#structure-du-projet)  
4. [Description des services](#description-des-services)  
5. [Base de données](#base-de-données)  
6. [Déploiement](#déploiement)  
7. [Tests](#tests)  

    
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


## Structure du projet
microservices-bookstore/
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── html/
│       └── index.html
├── services/
│   ├── api-gateway/
│   │   ├── Dockerfile
│   │   ├── gateway.py
│   │   └── requirements.txt
│   ├── book-service/
│   │   ├── Dockerfile
│   │   ├── book_service.py
│   │   └── requirements.txt
│   └── order-service/
│       ├── Dockerfile
│       ├── order_service.py
│       └── requirements.txt
├── k8s/
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── database.yaml
│   ├── api-gateway.yaml
│   ├── book-service.yaml
│   ├── order-service.yaml
│   └── frontend.yaml
├── scripts/
│   ├── deploy.sh
│   ├── test-microservices.sh
│   └── seed-data.sh
└── README.md

## Description des services
1. API Gateway

Routage des requêtes vers Book Service et Order Service

Agrégation de l’état de santé via /health

Journalisation de toutes les requêtes

Gestion des erreurs et indisponibilités des services

2. Book Service

Opérations CRUD complètes pour les livres

Gestion des stocks (/reserve, /release)

Validation des entrées et gestion des erreurs

3. Order Service

Création de commandes clients

Communication avec Book Service pour vérifier la disponibilité

Suivi du statut des commandes et historique des commandes

## Base de données
Tables PostgreSQL

Books

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    author VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    stock INTEGER NOT NULL DEFAULT 0,
    isbn VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


Orders

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    customer_email VARCHAR(100) NOT NULL,
    book_id INTEGER NOT NULL,
    book_title VARCHAR(200),
    quantity INTEGER NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

## Déploiement

Cluster Kubernetes K3s

Construction des images Docker
docker build -t bookstore-api-gateway ./services/api-gateway
docker build -t bookstore-book-service ./services/book-service
docker build -t bookstore-order-service ./services/order-service
docker build -t bookstore-frontend ./frontend

Pousser les images vers un registre
docker tag bookstore-api-gateway mariem507/bookstore-api-gateway:latest
docker push mariem507/bookstore-api-gateway:latest
# Répéter pour les autres services

Déploiement sur K3s
kubectl apply -f k8s/

Vérification des pods et services
kubectl get pods
kubectl get svc

Tests
1. Ajouter un livre

curl -X POST http://<node-ip>:30080/api/books \
-H "Content-Type: application/json" \
-d '{
  "title": "Clean Code",
  "author": "Robert Martin",
  "price": 29.99,
  "stock": 10,
  "isbn": "978-0132350884"
}'

2. Lister les livres
curl http://<node-ip>:30080/api/books

3. Créer une commande
curl -X POST http://<node-ip>:30080/api/orders \
-H "Content-Type: application/json" \
-d '{
  "customer_name": "John Doe",
  "customer_email": "john@example.com",
  "book_id": 1,
  "quantity": 2
}'

4. Vérifier le stock
curl http://<node-ip>:30080/api/books/1


