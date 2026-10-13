import random


def caesar_cipher(text: str, shift: int) -> str:
    result = []

    for char in text:
        if "A" <= char <= "Z":
            base = ord("A")
            result.append(chr((ord(char) - base + shift) % 26 + base))
        elif "a" <= char <= "z":
            base = ord("a")
            result.append(chr((ord(char) - base + shift) % 26 + base))
        else:
            # Preserva espaços, números e pontuação.
            result.append(char)

    return "".join(result)


def brute_force_caesar(ciphertext: str):
    print(f"Texto cifrado: {ciphertext}\n")

    for shift in range(26):
        candidate = caesar_cipher(ciphertext, -shift)
        print(f"Deslocamento {shift:2}: {candidate}")


if __name__ == "__main__":
    ciphered_mail = caesar_cipher("joao@exemplo.com", random.randint(1, 26))
    brute_force_caesar(ciphered_mail)
