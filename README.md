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
- Osobna zakładka **Historia wydatków** z możliwością sortowania, edycji, przeciągania pozycji, importu z pliku CSV lub poprzez kopiuj-wklej oraz eksportu do CSV.
- Do każdego wydatku możesz dołączyć paragon lub fakturę (PDF, zdjęcie). Informacja „Zdjęcie dostępne” pojawia się w historii i pozwala pobrać plik jednym kliknięciem.
- Import i eksport korzystają z formatu `.csv` z nagłówkami w pierwszym wierszu: `Data`, `Odbiorca`, `Kwota`, `Etap`, `Typ wydatku`, `Notatki`, `Bank`, `Opis`.
- Eksport jednym kliknięciem zapisuje wszystkie wydatki w pliku `wydatki_budowa.csv` (kodowanie UTF-8 z BOM), który otworzysz w Excelu lub Numbers.
- Panel administracyjny do zarządzania użytkownikami i uprawnieniami oraz zaawansowane centrum raportów z filtrowaniem wielokryterialnym, interaktywnymi wykresami (Chart.js), tabelą z przeciąganiem kolumn/wierszy (Tabulator) i eksportem do PDF lub Excel.

## Import/eksport danych – krok po kroku

1. **Eksport danych:**
   - Wejdź do zakładki **Historia wydatków**.
   - Kliknij przycisk **Eksportuj do CSV**. Plik `wydatki_budowa.csv` zostanie zapisany na dysku i możesz go otworzyć w Excelu.

2. **Przygotowanie pliku do importu w Excelu (macOS/Windows):**
   - Otwórz swój arkusz z wydatkami lub plik `wydatki_budowa.csv` w Excelu.
   - Upewnij się, że pierwszy wiersz zawiera nagłówki dokładnie w kolejności: `Data`, `Odbiorca`, `Kwota`, `Etap`, `Typ wydatku`, `Notatki`, `Bank`, `Opis`.
   - W kolumnie „Etap” używaj wartości `ETAP 0`–`ETAP 5`, a w kolumnie „Typ wydatku” jednej z opcji: `Materialy`, `Zaliczka`, `Usluga`, `Robocizna`, `Inne`.
   - Usuń symbole walut (np. `zł`, `PLN`) – aplikacja poradzi sobie ze spacjami i separatorami tysięcy.
   - Jeśli w kolumnie „Kwota” używasz przecinka jako separatora dziesiętnego, Excel automatycznie zapisze liczbę w poprawnym formacie.
   - Wybierz **Plik → Zapisz jako** (lub **Eksportuj**), ustaw format **CSV UTF-8 (rozdzielany przecinkami)**. W polskiej wersji Excela możesz też wybrać **CSV (rozdzielany średnikami)**.
   - Zamknij zapisany plik w Excelu, aby nie blokował odczytu podczas importu w aplikacji.

3. **Import danych do aplikacji:**
   - Przejdź do zakładki **Historia wydatków** i kliknij **Importuj dane**.
   - Wybierz zakładkę **Plik CSV**, wskaż przygotowany plik `.csv` i potwierdź import **lub** wybierz zakładkę **Kopiuj / wklej z Excela**, skopiuj wiersze (razem z nagłówkiem) bezpośrednio z Excela i wklej w oknie dialogowym.
   - Po zatwierdzeniu aplikacja poda liczbę dodanych pozycji oraz informację o ewentualnych pominiętych wierszach (np. z brakującymi danymi).

## Generowanie raportów i wykresów

1. **Wejdź do zakładki „Raporty”.** Górny panel pokazuje łączną kwotę, najdroższy etap oraz dominujący typ wydatku.
2. **Skonfiguruj filtry.** W lewej kolumnie wybierzesz zakres dat, etapy (ETAP 0–5), typy wydatków, banki, kontrahentów, przedziały kwotowe oraz opcję ograniczenia do pozycji z/bez załączników. Po kliknięciu **Zastosuj** wszystkie wykresy, podsumowania i tabela z wynikami odświeżą się.
3. **Korzystaj z tabeli wyników.** Tabela umożliwia sortowanie wielu kolumn, zaznaczanie wierszy, przeciąganie kolumn i wierszy oraz szybkie wyszukiwanie (pole „Szybkie wyszukiwanie” nad filtrami).
4. **Eksportuj raport.**
   - **PDF** – kliknij **Pobierz raport PDF**, aby wygenerować czytelny raport tekstowy z tabelą danych i (opcjonalnie) wykresami. Plik nadaje się do wydruku i wysyłki do kontrahentów.
   - **Excel (XLSX)** – przycisk **Eksportuj do Excel** zapisuje aktualny widok tabeli w formacie obsługiwanym przez Excel/Numbers. Jeśli zaznaczysz konkretne wiersze, eksport obejmie tylko wybrane pozycje.
   - **Druk** – przycisk **Drukuj** otwiera podgląd drukowania w przeglądarce z aktualnym układem raportu.
5. **Tryb LIVE.** Zaznacz pole „Tryb LIVE”, a następnie klikaj wiersze w tabeli. Interaktywna infografika i podsumowanie „Wybrane dane” z boku będą aktualizować się w czasie rzeczywistym, prezentując tylko wskazane pozycje.
6. **Animowane wizualizacje.** Trzy podstawowe wykresy (etapy, typy, aktywność miesięczna) oraz kołowy wykres LIVE bazują na bibliotece Chart.js – reagują na zmiany filtrów oraz zaznaczenia.

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
