import argparse
import time
from itertools import product
from statistics import median

import httpx


def main():
    start_total = time.perf_counter()

    parser = argparse.ArgumentParser(
        description="Teste controlado de autenticação da SecureBank"
    )
    parser.add_argument("--url", default="http://127.0.0.1:8000/auth/login")
    parser.add_argument("--email", required=True)
    parser.add_argument("-n", "--digits", type=int, default=4)
    parser.add_argument("--max-attempts", type=int, default=10)
    parser.add_argument("--delay", type=float, default=0.2)

    args = parser.parse_args()

    if args.digits < 1:
        parser.error("--digits deve ser maior que zero")
    if args.max_attempts < 1:
        parser.error("--max-attempts deve ser maior que zero")
    if args.delay < 0:
        parser.error("--delay não pode ser negativo")

    timings = []
    digits = "0123456789"

    print(f"Endpoint: {args.url}")
    print(f"E-mail de teste: {args.email}")
    print(f"Limite de tentativas: {args.max_attempts}")
    print("-" * 55)

    with httpx.Client(timeout=5.0) as client:
        for attempt, combination in enumerate(
            product(digits, repeat=args.digits), start=1
        ):
            if attempt > args.max_attempts:
                break

            password = "".join(combination)
            payload = {
                "email": args.email,
                "password": password,
            }

            start = time.perf_counter()

            try:
                response = client.post(args.url, json=payload)
                elapsed = time.perf_counter() - start
                timings.append(elapsed)

                print(
                    f"Tentativa {attempt:02d} | "
                    f"HTTP {response.status_code} | "
                    f"{elapsed * 1000:.2f} ms"
                )

                # Interrompe ao detectar limitação de requisições.
                if response.status_code == 429:
                    print("Limite de requisições detectado (HTTP 429).")
                    break

                # Não exibe nem armazena a senha encontrada.
                if response.is_success:
                    print("Resposta de sucesso recebida; teste interrompido.")
                    break

            except httpx.RequestError as exc:
                print(f"Erro de conexão: {exc}")
                break

            if attempt < args.max_attempts:
                time.sleep(args.delay)

    if timings:
        elapsed_total = time.perf_counter() - start_total
        print(f"Tempo real total: {elapsed_total:.2f} segundos")
        print(f"Tempo real total: {elapsed_total / 60:.2f} minutos")

        print("-" * 55)
        print(f"Requisições concluídas: {len(timings)}")
        print(f"Tempo total: {sum(timings):.2f} s")
        print(f"Tempo médio: {sum(timings) / len(timings) * 1000:.2f} ms")
        print(f"Mediana: {median(timings) * 1000:.2f} ms")


if __name__ == "__main__":
    main()
