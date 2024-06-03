from tabulate import tabulate
from roman import toRoman
import shelve


def calculate_ranks(teams):
    sorted_teams = sorted(teams.values(), key=lambda x: (-x['points'], x['name']))
    current_rank = 1
    current_points = sorted_teams[0]['points']
    ranked_teams = []

    for i, team in enumerate(sorted_teams):
        if team['points'] < current_points:
            current_rank = i + 1
            current_points = team['points']
        team['rank'] = current_rank
        ranked_teams.append(team)

    rank_counts = {}
    for team in ranked_teams:
        if team['rank'] in rank_counts:
            rank_counts[team['rank']].append(team)
        else:
            rank_counts[team['rank']] = [team]

    for rank, teams in rank_counts.items():
        if len(teams) > 1:
            rank_str = f"{toRoman(rank)} - {toRoman(rank + len(teams) - 1)}"
            for team in teams:
                team['rank'] = rank_str

    return ranked_teams


def print_tournament_table(teams):
    ranked_teams = calculate_ranks(teams)
    table_data = []

    for team in ranked_teams:
        draws = team['matches'] - team['wins'] - team['losses']
        rank = team['rank']

        if isinstance(rank, int) and rank <= 3:
            rank = toRoman(rank)

        table_data.append([rank, team['name'], team['points'], team['wins'], team['losses'], draws])

    table_headers = ["Место", "Команда", "Баллы", "Победы", "Поражения", "Ничьи"]
    table = tabulate(table_data, headers=table_headers, tablefmt="pretty")
    print(table)


def create_file():
    db = shelve.open('tournament_data.db', writeback=True)
    db['teams'] = {}
    db.close()
    print("Файл данных о турнире создан.")


def open_file():
    db = shelve.open('tournament_data.db')
    teams = db['teams']
    db.close()
    print_tournament_table(teams)


def convert_to_shelve():
    with open("champ.txt", "r", encoding="utf-8") as champ_file:
        champ_data = champ_file.read().split('\n')

    db = shelve.open('tournament_data.db', writeback=True)
    teams = db['teams']

    for line in champ_data:
        parts = line.split(';')
        if len(parts) == 4:
            team1_id = int(parts[1])
            team2_id = int(parts[2])
            scores = parts[3].split(':')
            if len(scores) == 2:
                score_team1 = int(scores[0])
                score_team2 = int(scores[1])

                if team1_id not in teams:
                    teams[team1_id] = {'name': f'Команда {team1_id}', 'points': 0, 'wins': 0, 'losses': 0, 'matches': 0}
                if team2_id not in teams:
                    teams[team2_id] = {'name': f'Команда {team2_id}', 'points': 0, 'wins': 0, 'losses': 0, 'matches': 0}

                if score_team1 > score_team2:
                    teams[team1_id]['points'] += 3
                    teams[team1_id]['wins'] += 1
                    teams[team2_id]['losses'] += 1
                elif score_team1 < score_team2:
                    teams[team2_id]['points'] += 3
                    teams[team2_id]['wins'] += 1
                    teams[team1_id]['losses'] += 1
                else:
                    teams[team1_id]['points'] += 1
                    teams[team2_id]['points'] += 1

                teams[team1_id]['matches'] += 1
                teams[team2_id]['matches'] += 1

    db['teams'] = teams
    db.close()
    print("Данные из champ.txt преобразованы в Shelve.")


def add_string():
    db = shelve.open('tournament_data.db', writeback=True)
    teams = db['teams']

    team_id, name = input('Введите ID команды и имя: ').split()
    team_id = int(team_id)
    if team_id not in teams:
        teams[team_id] = {'name': name, 'points': 0, 'wins': 0, 'losses': 0, 'matches': 0}

    db['teams'] = teams
    db.close()
    print("Команда добавлена.")


def to_html():
    db = shelve.open('tournament_data.db')
    teams = db['teams']
    db.close()

    table_data = []
    for team_id, team_info in teams.items():
        table_data.append([team_id, team_info['name'], team_info['points'], team_info['wins'], team_info['losses'],
                           team_info['matches']])

    table_headers = ["ID команды", "Имя", "Баллы", "Победы", "Поражения", "Матчи"]
    table = tabulate(table_data, headers=table_headers, tablefmt="html")

    with open('tournament_table.html', 'w', encoding='utf-8') as html_file:
        html_file.write(f"<html><body><pre>{table}</pre></body></html>")
    print("Турнирная таблица экспортирована в HTML (tournament_table.html).")


def main():
    while True:
        print("Меню управления турниром:")
        print("1. Создать файл данных о турнире")
        print("2. Загрузить данные о турнире из champ.txt")
        print("3. Открыть файл данных о турнире")
        print("4. Добавить команду")
        print("5. Экспортировать турнирную таблицу в HTML")
        print("0. Выйти")
        choice = input("Введите номер выбранного действия: ")

        if choice == '1':
            create_file()
        elif choice == '2':
            convert_to_shelve()
        elif choice == '3':
            open_file()
        elif choice == '4':
            add_string()
        elif choice == '5':
            to_html()
        elif choice == '0':
            break
        else:
            print("Неверный выбор. Пожалуйста, выберите действие из списка.")


if __name__ == "__main__":
    main()


