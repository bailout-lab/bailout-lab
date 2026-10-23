#!/usr/bin/env bash
# Controlli di base del repo: file obbligatori presenti, nessun segreto o dato pesante tracciato.
# Dal passo P04 si affiancano i test Python.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

errori=0
errore() { echo "ERRORE: $*"; errori=$((errori + 1)); }

for f in README.md ROADMAP.md CONTRIBUTING.md CODE_OF_CONDUCT.md SECURITY.md \
         LICENSE LICENSE-CC-BY-4.0.txt .gitignore .env.example \
         .github/PULL_REQUEST_TEMPLATE.md; do
  [ -s "$f" ] || errore "manca o è vuoto: $f"
done

# .env.example contiene solo nomi: ogni riga NOME= deve restare senza valore
while IFS= read -r riga; do
  errore ".env.example ha un valore: ${riga%%=*}"
done < <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=.+' .env.example || true)

# File che non devono mai essere tracciati
while IFS= read -r f; do
  case "$f" in
    .env.example) ;;
    .env|.env.*|*.pem|*.key|*.parquet|*.duckdb|*.sqlite|*.db) errore "file vietato nel repo: $f" ;;
  esac
done < <(git ls-files)

# Niente file oltre 5 MB: i dati pesanti restano fuori dal repo
while IFS= read -r f; do
  [ -f "$f" ] || continue
  dimensione=$(wc -c < "$f")
  [ "$dimensione" -le 5242880 ] || errore "file oltre 5 MB: $f"
done < <(git ls-files)

if [ "$errori" -gt 0 ]; then
  echo "$errori problemi trovati."
  exit 1
fi
echo "Controlli del repo: tutto a posto."
