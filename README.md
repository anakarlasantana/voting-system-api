# Voting System API

## Visão Geral

Esta API implementa o backend para um sistema de votação online para pautas de assembleia, permitindo o cadastro de usuários, criação de pautas, abertura de sessões de votação, registro de votos e consulta de resultados. A autenticação é feita via JWT.

---

## Tecnologias

- Python 3.x
- Django 4.x
- Django REST Framework
- djangorestframework-simplejwt (JWT Authentication)
- drf-spectacular (Documentação OpenAPI/Swagger)
- Banco de dados: SQLite (pode ser configurado para PostgreSQL)
- Testes automatizados com `django.test` e `rest_framework.test`

---

## Endpoints Principais

### Autenticação

- `POST /register/`  
  Cadastro de usuário (campos: `cpf`, `name`, `password`).

- `POST /login/`  
  Login com `cpf` e `password`, retorna tokens JWT (`access` e `refresh`).

- `GET /me/`  
  Retorna dados do usuário autenticado (token obrigatório).

---

### Pautas

- `GET /topics/`  
  Lista todas as pautas cadastradas (público).

- `POST /topics/`  
  Cria uma nova pauta (token obrigatório).

---

### Sessão de Votação

- `POST /topics/{topic_id}/session/`  
  Abre uma sessão de votação para a pauta informada.  
  Parâmetro opcional na query: `duration_minutes` (padrão: 1 minuto).  
  Token obrigatório.

---

### Registro de Votos

- `POST /topics/{topic_id}/vote/`  
  Registra voto do usuário autenticado (`choice`: `"Sim"` ou `"Não"`).  
  Cada usuário só pode votar uma vez por pauta.

---

### Resultado da Votação

- `GET /topics/{topic_id}/result/`  
  Retorna o resultado da votação (total, votos "Sim" e "Não").  
  Disponível somente após o encerramento da sessão (público).

---

## Regras de Negócio

- Usuário deve estar autenticado para criar pautas, abrir sessões e votar.
- Pauta criada inicia com status "Aguardando Abertura".
- Sessão de votação pode ter duração personalizada; padrão de 1 minuto.
- Não é possível abrir mais de uma sessão por pauta.
- Voto inválido (diferente de "Sim" ou "Não") é rejeitado.
- Usuário não pode votar mais de uma vez na mesma pauta.
- Resultado só pode ser consultado após o término da sessão.

---

## Testes

- Testes unitários implementados para autenticação, gerenciamento de pautas, sessões e votação.
- Executar testes:

  ```bash
  python manage.py test apps.authentication.tests
  python manage.py test apps.voting.tests


  ```
