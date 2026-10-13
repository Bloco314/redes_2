# gerando a chave jwt (execute antes de rodar a aplicação em si)

$env:JWT_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"

# Para rodar (http):

python -m uvicorn app.main:app --reload

# A api estará disponivel em:

http://localhost:8000/docs

# Criar um certificado local

mkcert localhost 127.0.0.1 ::1

# executar usando o certificado (execução https)

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --ssl-certfile="localhost+2.pem" --ssl-keyfile="localhost+2-key.pem"

# executar ataque de força bruta

cd \redes_2\app\attackers

python force_brute.py --email "joao@exemplo.com" -n 4 --max-attempts 1000

python force_brute2.py --email "joao@exemplo.com" -n 4 --max-attempts 1000
