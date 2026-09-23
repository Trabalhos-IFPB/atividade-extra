# Sistema de Apoio à Monitoria

## Integrante
- Davi Leite Alencar Bezerra

## Contas de teste
- Superusuário: `admin` / `Admin@12345`
- Aluno 2: `aluno2` / `Aluno2@12345`
- Aluno 3: `aluno3` / `Aluno3@12345`
- Monitor 4: `monitor4` / `Monitor4@12345`
- Professor 5: `prof5` / `Prof5@12345`

## Disciplinas e monitoria
- `RAD101` — Rapid Application Development — monitor: `monitor4`
- `POO101` — Programação Orientada a Objetos — sem monitor vinculado
- `WEB999` — Laboratório Web Inativa — disciplina inativa

## Requisitos pendentes
- Nenhum requisito pendente.

## Execução
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
