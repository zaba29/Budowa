# Budowa

Aplikacja internetowa do rejestrowania wydatków związanych z budową wraz z prostym logowaniem.

## Wymagania

- Python 3.11 lub nowszy
- Pip (menedżer pakietów Pythona)

## Instalacja

1. Sklonuj repozytorium lub pobierz je jako archiwum ZIP.
2. W terminalu przejdź do katalogu projektu.
3. (Opcjonalnie) utwórz i aktywuj wirtualne środowisko:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # w systemie Windows: .venv\\Scripts\\activate
   ```
4. Zainstaluj zależności:
   ```bash
   pip install -r requirements.txt
   ```

## Uruchomienie

1. Ustaw zmienną środowiskową `FLASK_APP`:
   ```bash
   export FLASK_APP=app.py  # Windows (PowerShell): $env:FLASK_APP = "app.py"
   ```
2. Uruchom serwer deweloperski:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```
3. Wejdź na adres [http://localhost:5000](http://localhost:5000) w przeglądarce.
4. Zaloguj się używając:
   - użytkownik: `lukasz`
   - hasło: `lukasz29`

Dane są przechowywane w pliku `expenses.db` w katalogu projektu.

## Konfiguracja

- Domyślne dane logowania można nadpisać przez ustawienie zmiennych środowiskowych `APP_USERNAME` i `APP_PASSWORD`.
- Do generowania innego klucza sesji ustaw zmienną `SECRET_KEY`.

## Funkcje aplikacji

- Panel główny z formularzem dodawania wydatków, podsumowaniem według etapów (ETAP 0–ETAP 5) i typów (Materiały, Zaliczka, Usługa, Robocizna, Inne).
- Osobna zakładka **Historia wydatków** z możliwością sortowania, edycji, przeciągania pozycji, importu z Excela i eksportu do Excela.
- Import wymaga pliku `.xlsx` z nagłówkami w pierwszym wierszu: `Data`, `Odbiorca`, `Kwota`, `Etap`, `Typ wydatku`, `Notatki`, `Bank`, `Opis`.
- Eksport jednym kliknięciem zapisuje wszystkie wydatki w pliku `wydatki_budowa.xlsx` gotowym do otwarcia w Excelu.
- Panel administracyjny do zarządzania użytkownikami i uprawnieniami oraz strona raportów z wykresami (Chart.js).

## Instrukcja krok po kroku dla macOS (dla początkujących)

1. **Otwórz Terminal.** Kliknij lupę Spotlight (w prawym górnym rogu ekranu), wpisz `Terminal` i naciśnij Enter.
2. **Sprawdź wersję Pythona.** W Terminalu wpisz `python3 --version` i naciśnij Enter. Jeśli zobaczysz wersję `3.11` lub nowszą, możesz iść dalej. Jeśli wersja jest starsza, zainstaluj najnowszego Pythona z [https://www.python.org/downloads/](https://www.python.org/downloads/).
3. **Pobierz projekt.** Kliknij przycisk „Code” na stronie repozytorium i wybierz „Download ZIP”. Rozpakuj pobrany plik ZIP (podwójne kliknięcie utworzy folder).
4. **Przejdź do katalogu projektu.** W Terminalu wpisz `cd ` (zostawiając spację), a następnie przeciągnij folder projektu do okna Terminala i naciśnij Enter. Komenda powinna wyglądać podobnie do `cd /Users/twoja_nazwa_uzytkownika/Pobrane/Budowa-main`.
5. **(Opcjonalnie) Utwórz wirtualne środowisko.** Wpisz `python3 -m venv .venv` i naciśnij Enter. Następnie aktywuj środowisko poleceniem `source .venv/bin/activate`. W Terminalu pojawi się prefix `(.venv)`.
6. **Zainstaluj wymagane biblioteki.** Wpisz `pip install -r requirements.txt` i naciśnij Enter. Poczekaj, aż instalacja się zakończy.
7. **Ustaw zmienną środowiskową FLASK_APP.** Wpisz `export FLASK_APP=app.py` i naciśnij Enter. (Ta komenda działa tylko w obecnym oknie Terminala, więc wykonaj ją każdorazowo przed uruchomieniem aplikacji.)
8. **Uruchom aplikację.** Wpisz `flask run --host=0.0.0.0 --port=5000` i naciśnij Enter. Terminal pokaże komunikat `Running on http://127.0.0.1:5000`.
9. **Otwórz przeglądarkę.** Wpisz w pasku adresu `http://localhost:5000` i naciśnij Enter. Pojawi się strona logowania.
10. **Zaloguj się.** Użyj danych `lukasz` / `lukasz29`. Po zalogowaniu możesz dodawać wydatki i obserwować podsumowania.
11. **Zatrzymaj aplikację.** Wróć do Terminala i naciśnij jednocześnie klawisze `Ctrl` + `C`. Jeśli masz aktywne środowisko `(.venv)`, wyłącz je poleceniem `deactivate`.

Jeżeli kiedykolwiek zamkniesz Terminal, a później chcesz ponownie uruchomić aplikację, powtórz kroki 4, 5 (jeśli używasz środowiska wirtualnego – w tym przypadku tylko `source .venv/bin/activate`), 6 (tylko gdy instalacja pakietów jest potrzebna ponownie), 7 i 8.
