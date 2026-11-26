# Przetwarzanie Obrazów Cyfrowych

[![Licencja: CC BY-NC 4.0](https://img.shields.io/badge/Licencja-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/deed.pl)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)

Desktopowa aplikacja z graficznym interfejsem (Tkinter) do podstawowego przetwarzania obrazów cyfrowych: transformacji punktowych, mieszania obrazów, operacji na histogramie oraz filtrów splotowych i statystycznych. Algorytmy są zaimplementowane ręcznie, piksel po pikselu, z wykorzystaniem biblioteki Pillow do wczytywania, zapisu i wyświetlania obrazów.

## Funkcje

### Transformacje

| Transformacja | Opis | Parametry |
|---|---|---|
| Liniowa | `g = α·f + β` z obcięciem do 0–255 | α (0,1–3,0), β (−100–100) |
| Potęgowa | korekcja gamma | γ (0,1–3,0) |
| Mieszanie | łączenie dwóch obrazów (drugi jest skalowany do rozmiaru pierwszego) | tryb, α |
| Kontrast | `128 + c·(p − 128)` dla każdego kanału | c (0,1–3,0) |
| Wyrównanie histogramu | wyrównanie histogramu obrazu | – |
| Skalowanie histogramu | liniowe rozciągnięcie zakresu każdego kanału do `[min, max]` | min, max (0–255) |

**Tryby mieszania (16):** `additive`, `subtractive`, `difference`, `multiply`, `screen`, `negation`, `darken`, `lighten`, `exclusion`, `overlay`, `hard_light`, `soft_light`, `color_dodge`, `color_burn`, `reflect`, `transparency`.

### Filtry

| Filtr | Opis | Parametry |
|---|---|---|
| Dolnoprzepustowy | uśrednianie w oknie (rozmywanie) | rozmiar jądra: 3, 5, 7, 9 |
| Górnoprzepustowy | wykrywanie krawędzi na obrazie w skali szarości | operator: Roberts, Prewitt, Sobel, Laplace; kierunek: `x`, `y`, `both` (dla Laplace'a: `4neighbors`, `8neighbors`, `diagonal`) |
| Statystyczny | filtr rangowy w oknie | typ: `min`, `max`, `median`; rozmiar jądra: 3, 5, 7 |

Brzegi obrazu są dopełniane metodą `replicate` (powielenie skrajnych pikseli). W kodzie dostępne są też strategie `reflect` i `zero`.

### Pozostałe

- podgląd obrazu oryginalnego, drugiego i przetworzonego,
- znormalizowane histogramy składowych RGB dla każdego z trzech obrazów (matplotlib),
- wczytywanie plików `.jpg`, `.jpeg`, `.png`, `.bmp`,
- zapis wyniku do `.png` lub `.jpg`.

## Wymagania

- Python 3.8 lub nowszy
- [Pillow](https://pypi.org/project/pillow/)
- [matplotlib](https://pypi.org/project/matplotlib/)
- Tkinter (w standardowej instalacji Pythona na Windows i macOS; na Linuksie może wymagać osobnego pakietu, np. `sudo apt install python3-tk`)

## Instalacja i uruchomienie

```bash
git clone https://github.com/<twoja-nazwa-uzytkownika>/<nazwa-repozytorium>.git
cd <nazwa-repozytorium>

pip install pillow matplotlib

python Filters.py
```

## Obsługa

1. Kliknij **Wczytaj obraz** i wybierz plik.
2. (Opcjonalnie) kliknij **Wczytaj drugi obraz**, jeśli chcesz użyć transformacji *Mieszanie*.
3. Wybierz transformację lub filtr z listy rozwijanej i ustaw parametry.
4. Kliknij **Zastosuj**. Wynik i jego histogram pojawią się w trzeciej kolumnie.
5. Kliknij **Zapisz obraz**, aby zapisać wynik.

Przyciski **Wyczyść** i **Wyczyść wybory** resetują odpowiednio całą aplikację lub tylko wybrane operacje.

## Znane ograniczenia

- **Wydajność.** Operacje są liczone w czystym Pythonie, pętlami po pikselach, więc na dużych obrazach (np. kilka megapikseli) mogą trwać dłuższą chwilę. Okno aplikacji nie odpowiada podczas obliczeń.
- **Brak łączenia operacji.** Jeśli wybierzesz jednocześnie transformację i filtr, filtr jest liczony od obrazu oryginalnego, więc widoczny jest tylko jego wynik. Aby połączyć operacje, zapisz wynik pierwszej i wczytaj go ponownie.
- **Filtr górnoprzepustowy** zawsze zwraca obraz w skali szarości.

## Struktura kodu

- `ImageProcessor` – logika przetwarzania (transformacje, filtry, histogramy), niezależna od interfejsu,
- `ImageProcessorApp` – interfejs graficzny w Tkinter.

## Licencja

Projekt jest udostępniony na licencji [Creative Commons Uznanie autorstwa – Użycie niekomercyjne 4.0 (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/deed.pl).

Możesz:

- **kopiować i modyfikować** program oraz tworzyć na jego podstawie własne wersje,
- **udostępniać** go dalej,

pod warunkiem, że:

- **podasz autora** i odnośnik do licencji oraz zaznaczysz wprowadzone zmiany,
- **nie wykorzystasz go w celach komercyjnych**, czyli głównie z zamiarem osiągnięcia korzyści majątkowej (m.in. sprzedaż programu lub jego zmodyfikowanych wersji, dołączanie do płatnych produktów i usług).

Pełny tekst licencji znajduje się w pliku [LICENSE](LICENSE). Zastosowania komercyjne wymagają odrębnej zgody autora.

## Autor

© 2025 Daniel Postolowicz
