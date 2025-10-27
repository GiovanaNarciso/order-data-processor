# Order Data Processor

API REST que recebe um arquivo de pedidos desnormalizados, processa os dados e retorna uma estrutura JSON normalizada, agrupando usuários, pedidos e produtos.

Desenvolvido como parte do desafio técnico da vertical de logística da **LuizaLabs**.

---

## Requisitos funcionais

- Recebe via API REST um arquivo `.txt` com layout de largura fixa
- Normaliza os dados agrupando por `user → order → products`
- Suporta filtros opcionais para o método GET:
  - `order_id`
  - intervalo de `start_date` e `end_date`
- Retorna status HTTP 204 (No Content) quando nenhum dado for encontrado

---

## Arquitetura e linguagem

O projeto segue o padrão **arquitetura hexagonal** com separação clara entre domínio, casos de uso e interfaces externas. Testado e desenvolvido utilizando o python 3.12 e SQLAlchemy como ORM para persistência de dados em um DB SQLLite.

## Modelagem do Banco de Dados

```text
┌────────────┐
│ UserModel  │
│────────────│
│ id (PK)    │
│ name       │
└────────────┘
     │ 1
     │
     ▼ *
┌────────────┐
│ OrderModel │
│────────────│
│ id (PK)    │
│ user_id FK │
│ date       │
└────────────┘
     │ 1
     ▼ *
┌──────────────┐
│ ProductModel │
│──────────────│
│ id (PK)      │
│ order_id FK  │
│ product_id   │
│ value        │
└──────────────┘
```

## Como executar:

### 1. Instalar dependências

```bash
make install
```

### 2.1 Iniciar o servidor local
```bash
make local/run
```

### 2.2 Iniciar o servidor pelo Docker
```bash
make docker/build
```

```bash
make docker/run
```

Acesse: http://localhost:8000/docs


## Rotas Disponíveis
```bash
POST /api/orders
```

Recebe um arquivo .txt no formato fixo e persiste os dados no banco.
Body (form-data):

**file:** arquivo .txt

**Exemplo com CURL:**

```bash
curl -X 'POST' \
  'http://localhost:8000/api/orders' \             
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@docs/data_1.txt'
```

**Obs:** É possível fazer o input de um dos arquivos de teste disponíveis nesse repositório em **docs/**.

---

```bash
GET /api/orders
```

Retorna os pedidos já importados. Filtros opcionais disponíveis:

order_id

start_date (YYYY-MM-DD)

end_date (YYYY-MM-DD)

**Exemplo com CURL:**

```bash
curl -X 'GET' \
  'http://0.0.0.0:8000/api/orders' \
  -H 'accept: application/json'
```

**Exemplo de resposta**
```bash
[
  {
    "user_id": 70,
    "name": "Palmer Prosacco",
    "orders": [
      {
        "order_id": 753,
        "total": "1836.74",
        "date": "2021-03-08",
        "products": [
          {
            "product_id": 3,
            "value": "1836.74"
          }
        ]
      }
    ]
  }
]
```

## Testes, lint, coverage

**Rodar todos os testes:**

```bash
make test
```

**Rodar coverage:**

```bash
make cov
```

**Rodar lint com flake8:**

```bash
make lint
```

## Fixtures

Os testes utilizam o arquivo **fixtures/sample.txt**, que simula dados reais para validar os fluxos completos da API.
