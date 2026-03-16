import winreg
import pyperclip
import re
import os

def get_system_environment() -> dict:
    """Pobiera wszystkie zmienne systemowe bezpośrednio z rejestru."""
    env_vars = {}
    reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(key, i)
                    # Ignorujemy samą zmienną Path, by nie zapętlić logiki
                    if name.upper() != "PATH":
                        env_vars[name] = str(value)
                    i += 1
                except OSError:
                    break
    except Exception as e:
        print(f"Błąd podczas odczytu rejestru: {e}")
    return env_vars

def get_system_path() -> str:
    reg_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
        value, _ = winreg.QueryValueEx(key, "Path")
    return value

def parametrize_path(path_string: str, env_vars: dict) -> str:
    """Zamienia sztywne ścieżki na zmienne systemowe, np. C:\\Windows -> %SystemRoot%."""
    entries = path_string.split(";")
    new_entries = []

    # Sortujemy zmienne według długości wartości (malejąco)
    # Dzięki temu najpierw dopasujemy dłuższą ścieżkę (np. VULKAN_SDK) 
    # zanim dopasujemy krótszą (np. SYSTEMROOT)
    sorted_vars = sorted(env_vars.items(), key=lambda x: len(x[1]), reverse=True)

    for entry in entries:
        entry = entry.strip()
        if not entry:
            continue
            
        replaced = False
        for var_name, var_value in sorted_vars:
            # Pomijamy puste zmienne lub zbyt krótkie (np. pojedyncze litery)
            if len(var_value) < 3:
                continue
            
            # Sprawdzamy czy wpis w PATH zaczyna się od wartości zmiennej (case-insensitive)
            if entry.lower().startswith(var_value.lower()):
                # Podmieniamy fizyczną ścieżkę na %NAZWA_ZMIENNEJ%
                entry = entry.replace(entry[:len(var_value)], f"%{var_name}%")
                replaced = True
                # Po pierwszej trafionej długiej zmiennej przerywamy dla tego wpisu
                break 
        
        new_entries.append(entry)
    
    return ";".join(new_entries)

def clean_path(path_string: str) -> str:
    """Standardowe czyszczenie duplikatów i białych znaków."""
    seen = set()
    cleaned = []
    for entry in path_string.split(";"):
        entry = entry.strip()
        entry = re.sub(r'[\r\n\t]+', '', entry)
        entry = entry.replace('\\\\', '\\')
        
        if entry.endswith("\\") and not re.match(r"^[A-Za-z]:\\$", entry):
            entry = entry.rstrip("\\")
            
        if entry and entry not in seen:
            seen.add(entry)
            cleaned.append(entry)
    return ";".join(cleaned)

if __name__ == "__main__":
    # 1. Pobierz surowy PATH i wszystkie zmienne
    raw_path = get_system_path()
    all_vars = get_system_environment()
    
    # 2. Najpierw parametryzujemy (podstawiamy %VAR%)
    parametrized = parametrize_path(raw_path, all_vars)
    
    # 3. Potem czyścimy z duplikatów
    final_path = clean_path(parametrized)

    # Wyświetlanie wyników
    print("===== ZMIENNE UŻYTE DO PODMIANY =====")
    print(f"Znaleziono {len(all_vars)} zmiennych systemowych.\n")

    print("===== NOWY PATH Z %ZMIENNYMI% =====")
    final_list = final_path.split(";")
    for i, p in enumerate(final_list, 1):
        print(f"{i:3}. {p}")

    print(f"\nOryginalna długość: {len(raw_path)}")
    print(f"Nowa długość: {len(final_path)}")

    # Skopiuj do schowka
    pyperclip.copy(final_path)
    print("\n(Zoptymalizowany PATH został skopiowany do schowka)")