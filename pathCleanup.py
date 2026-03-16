import winreg
import pyperclip
import re

def get_system_path() -> str:
    reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
        value, _ = winreg.QueryValueEx(key, "Path")
    return value

def clean_path(path_string: str) -> str:
    """Usuwa duplikaty, puste wpisy i zbędne znaki w PATH."""
    seen = set()
    cleaned = []
    for entry in path_string.split(";"):
        # Usuń spacje i znaki kontrolne
        entry = entry.strip()
        entry = re.sub(r'[\r\n\t]+', '', entry)  # usuwa \n, \r, tabulatory
        entry = entry.replace('\\\\', '\\')      # podwójne backslashe → pojedynczy
        # Usuń końcowy backslash, jeśli nie jest rootem dysku (np. C:\)
        if entry.endswith("\\") and not re.match(r"^[A-Za-z]:\\$", entry):
            entry = entry.rstrip("\\")
        if entry and entry not in seen:
            seen.add(entry)
            cleaned.append(entry)
    return ";".join(cleaned)

if __name__ == "__main__":
    raw_path = get_system_path()
    cleaned_path = clean_path(raw_path)

    # Rozbij na listy
    raw_list = raw_path.split(";")
    cleaned_list = cleaned_path.split(";")

    # Wyświetl oba w formie list
    print("===== Oryginalny PATH (lista) =====")
    for i, p in enumerate(raw_list, 1):
        print(f"{i:3}. {p}")

    print(f"\nDługość oryginalnego PATH: {len(raw_path)} znaków")
    print(f"Liczba wpisów: {len(raw_list)}")

    print("\n===== Oczyszczony PATH (lista) =====")
    for i, p in enumerate(cleaned_list, 1):
        print(f"{i:3}. {p}")

    print(f"\nDługość oczyszczonego PATH: {len(cleaned_path)} znaków")
    print(f"Liczba wpisów: {len(cleaned_list)}")

    # Skopiuj nowy do schowka
    pyperclip.copy(cleaned_path)
    print("\n(Oczyszczony PATH został skopiowany do schowka jako ciąg)")