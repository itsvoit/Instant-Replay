# Main points

## On launch

* odpalanie w trayu / pokazywanie gui (opcja)
* po wlaczeniu automatycznie przychwytuje (opcja)
  * odpala sie z ustawieniami uzytkownika
  * zapisuje ostatnie _N_ sekund



## App

* klasa Capture
  * w konstruktorze wszystkie parametry
    * przechwytywany display (monitor)
    * ilosc klatek
    * dlugosc nagrania
    * jakosc (rozdzielczosc)
    * czy z dzwiekiem
  * nagrywanie
    * zapis klatek
    * usuniecie klatek
    * dostep do folderu na klatki (tmp)
  * eksport snapshota (powtorka)
  * screenshot
  
* klasa do zapisu pliku video
  * obsluga rozszerzenia
  * musi implementowac ustalony interfejs

* klasa Config
  * w konstruktorze plik .conf
    * import konfiguracji z pliku
    * brak danych w pliku = domyslne ustawienia (hard code)
    * eksport do pliku (po zmianach)
  * tworzy i przechowuje wszystkie ustawienia
  


## Gui

* Ustawienia (pliczek .conf)
  * przechwytywany display (ktory monitor / karta graficzna)
  * ilosc klatek
  * dlugosc nagrania
  * folder zapisu (zmienna srodowiskowa / pliczek .conf)
    * video 
    * screenshoty
  * jakosc (rozdzielczosc)
  * czy z dzwiekiem
  * rozszerzenie (?)
  * efekty (?)
    * czarno-biale
    * sepia, itd.
  * czy po przechwyceniu odpalac przycinanie (?)
  
* Przycinanie stworzonych powtorek (?)

* Przegladanie powtorek / screenshotow
  * master - detail (meta dane)
    * dlugosc
    * jakosc (rozdzielczosc)
    * fps
    * data stworzenia / data edycji
    * autor (?)
  * podglad
  


# Functionalities

## Model / Capture

* Start-up (taki jakby main)
  * zabezpieczenie czy juz nie jest odpalony ([link](https://stackoverflow.com/questions/9705982/pythonw-exe-or-python-exe))
  * odpalenie w trayu lub okna (gui) ([link](https://stackoverflow.com/questions/6389580/quick-and-easy-trayicon-with-python))
  * instancjonowanie klasy Capture z odpowiednimi ustawieniami
  * nasluchiwanie skrotow klawiszowych ([link](https://www.geeksforgeeks.org/how-to-create-a-hotkey-in-python/))
  
* Klasa Capture
  * obsluga klasy Config
  * nagrywanie (przechowywanie okreslonej liczby klatek)
  * eksport snapshota
  * screenshot
  
* Interface VideoEncoder
  * posiada funkcje przyjmujaca liste klatek i informacje o ilosci klatek na sekunde i zwraca przetworzony plik video w odpowiednim formacie 

* Klasa Mp4VideoEncoder (lub inne rozszerzenie)
  * implementuje interfejs VideoEncoder

* Klasa Config
  * z pliku czyta cala potrzebna konfiguracje aplikacji
  * eksport konfiguracji do pliku
  * przechowuje domyslne ustawienia


## Gui

* Wyswietlanie gui
* Obsluga eventow
* 


## Controller

* Logika systemu
* Polaczenie miedzy modelem i widokiem
