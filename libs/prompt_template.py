from libs.pandascore.pandascore_libs import get_active_match_dict

active_games_template = """
Na podstawie przesłanego słownika: {games_dict}

Zwróć zestawienie 10 najbliższych meczy ze statusem ('not_started'), wraz z planowanymi datami i godzinami rozgrywek z gry Counter Strike 2.
Odpowiedź ma być dostosowana do czytania przez człowieka, nie wrzucaj raw data ze słownika.

Schemat odpowiedzi:

Aktualne rozgrywki e-sportowe z Counter Strike 2:
- (<id rozgrywki>) <nazwa rozgrywki> | <data meczu> <godzina meczu>
"""
