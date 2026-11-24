import os
import sys

# Adiciona a pasta kit ao caminho do Python
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "kit"))
from black_box import *

# Caminho do report.txt, na mesma pasta deste main.py
REPORT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report.txt")

# ENTRADA DE DADOS

# Pede o nome de uma pasta e só aceita quando ela for válida.
def ask_folder():

    show_folders()

    folder = input("Digite o nome da pasta (ex: street, animals, sports): ").strip()

    while folder == "" or not folder_exists(folder) or total_photos(folder) == 0:
        print("Pasta inválida. Tente novamente.")
        folder = input("Digite o nome da pasta (ex: street, animals, sports): ").strip()

    return folder

# Pede pasta + número da foto (os dois validados) e devolve o caminho da foto.
def ask_photo():

    folder = ask_folder()

    total = total_photos(folder)
    print(f"A pasta '{folder}' tem {total} fotos.")

    # Começa em 0 de propósito: 0 é inválido e força o laço a rodar.
    number = 0

    while number < 1 or number > total:
        typed = input(f"Escolha o número da foto (1 a {total}): ").strip()

        # int() dá ValueError se o texto não for inteiro.
        try:
            number = int(typed)
        except ValueError:
            number = 0

        if number < 1 or number > total:
            print(f"Número inválido. Digite um número inteiro de 1 a {total}.")

    return photo_name(folder, number)

# CARGA, FILTRO E INVENTÁRIO

# Percorre todas as pastas e fotos.
def load_collection():

    results = {}
    folder_photos = {}

    for folder in list_folders():

        folder_photos[folder] = list_photos(folder)

        for photo in folder_photos[folder]:
            results[photo] = detect(photo)

    return results, folder_photos

# Mostra a quantidade de pastas, fotos e detecções.
def show_summary(results, folder_photos, min_conf):

    total_detections = 0
    filtered_detections = 0

    for photo in results:

        total_detections = total_detections + len(results[photo])

        filtered_detections = filtered_detections + len(
            filter_detections(results[photo], min_conf))

    print("\n--- Resumo do acervo ---")
    print(f"Pastas: {len(folder_photos)}")
    print(f"Fotos: {len(results)}")
    print(f"Detecções (a partir de 0.25): {total_detections}")
    print(f"Detecções com confiança >= {min_conf}: {filtered_detections}")

# Devolve uma NOVA lista só com as detecções com confiança >= min_conf.
def filter_detections(detections, min_conf):

    filtered = []

    for class_name, confidence in detections:

        if confidence >= min_conf:
            filtered.append((class_name, confidence))

    return filtered

# Monta o dicionário {classe: quantidade} para a lista de fotos recebida.
def build_inventory(results, photos, min_conf):

    inventory = {}

    for photo in photos:

        filtered = filter_detections(results[photo], min_conf)

        for class_name, confidence in filtered:

            if class_name in inventory:
                inventory[class_name] = inventory[class_name] + 1
            else:
                inventory[class_name] = 1

    return inventory

def show_inventory(inventory, title):

    print(f"\n--- Inventário: {title} ---")

    if len(inventory) == 0:
        print("Nenhum objeto com essa confiança mínima.")
        return

    total = 0

    for class_name in inventory:
        print(f"{class_name}: {inventory[class_name]}")
        total = total + inventory[class_name]

    print(f"\nClasses distintas: {len(inventory)}")
    print(f"Total de objetos: {total}")

# RANKING

def inventory_to_list(inventory):

    items = []

    for class_name in inventory:
        items.append((class_name, inventory[class_name]))

    return items

# Ordena em ordem DECRESCENTE pela quantidade (sorted() e .sort() são proibidos).
def bubble_sort_desc(items):

    # Copia para não alterar a original.
    ranking = items[:]

    n = len(ranking)

    for i in range(n - 1):

        for j in range(n - 1 - i):

            # Para ordem CRESCENTE, troque "<" por ">".
            if ranking[j][1] < ranking[j + 1][1]:

                ranking[j], ranking[j + 1] = ranking[j + 1], ranking[j]

    return ranking

# BUSCA REVERSA

# Índice reverso: {classe: [fotos onde ela aparece]}, só com detecções que passam no filtro. Cada foto aparece uma vez por classe.
def build_reverse_index(results, min_conf):

    index = {}

    for photo in results:

        for class_name, confidence in filter_detections(results[photo], min_conf):

            if class_name not in index:
                index[class_name] = []

            if photo not in index[class_name]:
                index[class_name].append(photo)

    return index

# Conta quantas vezes uma classe aparece em uma lista de detecções.
def count_class_in(detections, class_name):

    amount = 0

    for name, confidence in detections:

        if name == class_name:
            amount = amount + 1

    return amount

# COMPARAÇÃO DE PASTAS (CONJUNTOS)

# Conjunto (set) com as classes distintas de uma pasta.
def classes_of_folder(results, folder_photos, folder, min_conf):

    classes = set()

    for photo in folder_photos[folder]:

        for class_name, confidence in filter_detections(results[photo], min_conf):
            classes.add(class_name)

    return classes

# Ordem alfabética por inserção (sorted() é proibido e o set não tem ordem).
def sort_names(names):

    result = list(names)

    for i in range(1, len(result)):

        current = result[i]
        j = i - 1

        while j >= 0 and result[j] > current:

            result[j + 1] = result[j]
            j = j - 1

        result[j + 1] = current

    return result

def show_set(title, names):

    ordered = sort_names(names)

    if len(ordered) == 0:
        print(f"{title} (0): nenhuma")
    else:
        print(f"{title} ({len(ordered)}): " + ", ".join(ordered))

# MATRIZ PASTA x CLASSE

def build_matrix(results, folder_photos, min_conf, classes):

    matrix = []

    for folder in folder_photos:

        inventory = build_inventory(results, folder_photos[folder], min_conf)

        row = []

        for class_name in classes:

            if class_name in inventory:
                row.append(inventory[class_name])
            else:
                row.append(0)

        matrix.append(row)

    return matrix

# Soma cada linha (pasta) e cada coluna (classe).
def matrix_totals(matrix):

    row_totals = []

    for row in matrix:

        total = 0

        for value in row:
            total = total + value

        row_totals.append(total)

    column_totals = []

    for j in range(len(matrix[0])):

        total = 0

        for i in range(len(matrix)):
            total = total + matrix[i][j]

        column_totals.append(total)

    return row_totals, column_totals

# Maior valor da matriz e onde ele está (max() é proibido).
def find_largest(matrix, folders, classes):

    best_value = -1
    best_folder = ""
    best_class = ""

    for i in range(len(matrix)):

        for j in range(len(matrix[i])):

            if matrix[i][j] > best_value:

                best_value = matrix[i][j]
                best_folder = folders[i]
                best_class = classes[j]

    return best_value, best_folder, best_class

# Imprime a tabela alinhada, em blocos de 6 colunas para caber na tela.
def print_matrix(folders, classes, matrix, row_totals, column_totals):

    grand_total = 0

    for total in row_totals:
        grand_total = grand_total + total

    per_block = 6

    for start in range(0, len(classes), per_block):

        end = start + per_block

        if end > len(classes):
            end = len(classes)

        # A coluna "Total" só aparece no último bloco.
        last_block = (end == len(classes))

        header = f"{'Pasta':<14}"

        for j in range(start, end):
            header = header + f"{classes[j][:12]:>13}"

        if last_block:
            header = header + f"{'Total':>8}"

        print("\n" + header)
        print("-" * len(header))

        for i in range(len(folders)):

            line = f"{folders[i]:<14}"

            for j in range(start, end):
                line = line + f"{matrix[i][j]:>13}"

            if last_block:
                line = line + f"{row_totals[i]:>8}"

            print(line)

        line = f"{'TOTAL':<14}"

        for j in range(start, end):
            line = line + f"{column_totals[j]:>13}"

        if last_block:
            line = line + f"{grand_total:>8}"

        print(line)

# HISTOGRAMA E RELATÓRIO

# Recebe o ranking já ordenado (a primeira tupla é a maior, sem precisar de max()).Se a maior barra passar de 50 caracteres, cada "#" vale mais de um objeto.
def print_histogram(ranking):

    top = ranking[0][1]

    step = 1

    if top > 50:

        # Arredonda para cima.
        step = (top + 49) // 50

        print(f"(cada # = {step} objetos)")

    for class_name, amount in ranking:

        length = amount // step

        # Toda classe que existe ganha pelo menos um "#".
        if length == 0:
            length = 1

        print(f"{class_name:<15}| {'#' * length} ({amount})")

# Salva o inventário e o ranking em arquivo de texto.
def save_report(inventory, ranking, min_conf, path):

    with open(path, "w", encoding="utf-8") as file:

        file.write("PhotoCensus - Relatório do acervo\n")
        file.write(f"Confiança mínima: {min_conf}\n\n")

        file.write("INVENTÁRIO\n")

        for class_name in inventory:
            file.write(f"{class_name}: {inventory[class_name]}\n")

        file.write("\nRANKING\n")

        position = 1

        for class_name, amount in ranking:

            file.write(f"{position}. {class_name} - {amount}\n")

            position = position + 1

# Lê o arquivo salvo e mostra na tela; avisa se ainda não existe.
def read_report(path):

    try:

        with open(path, "r", encoding="utf-8") as file:
            content = file.read()

    except FileNotFoundError:

        print("Ainda não existe relatório salvo. Use a opção de salvar primeiro.")
        return

    print("\n--- Conteúdo do relatório ---")
    print(content)

# OPÇÕES DO MENU

# Opção 1: configura a confiança mínima e devolve o novo valor
def set_confidence(results, folder_photos, confidence_level):

    print("\n--- Configurar confiança mínima ---")

    print(f"Nível de confiança atual: {confidence_level}")

    while True:

        Atualizacao_confianca_str = input("Digite o novo valor a ser atribuído à confiança: ")

        Atualizacao_confianca_str = Atualizacao_confianca_str.strip()
        Atualizacao_confianca_str = Atualizacao_confianca_str.replace(",", ".")

        try:
            Atualizacao_confianca = float(Atualizacao_confianca_str)

        except ValueError:

            print(
                "Você digitou um valor errado. "
                "Por favor, digite um valor válido (entre 0 e 1).")

            continue

        if 0 <= Atualizacao_confianca <= 1:

            print("Valor aceito!")

            confidence_level = Atualizacao_confianca

            break

        print("Valor inválido, escolha um valor no intervalo de 0 a 1.")

    print(f"Novo nível de confiança: {confidence_level}")

    # Atualiza o resumo com a nova confiança.
    show_summary(results, folder_photos, confidence_level)

    return confidence_level

# Opção 2: analisa uma foto (usa as detecções já carregadas e o filtro de confiança)
def analyze_photo(results, confidence_level):

    print("\n--- Analisar uma foto ---")

    photo = ask_photo()

    filtered = filter_detections(results[photo], confidence_level)

    total_objs = len(filtered)

    print(f"\nFoto: {photo}")
    print(
        f"Objetos detectados (confiança >= {confidence_level}): "
        f"{total_objs}")

    if total_objs > 0:

        # Objeto com a maior confiança.
        main_obj = ""
        best_conf = 0.0

        for class_name, confidence in filtered:

            if confidence > best_conf:

                best_conf = confidence
                main_obj = class_name

        print(f"Objeto principal: {main_obj}")
        print(f"Maior confiança: {best_conf * 100:.0f}%")

    else:

        print("Nenhum objeto com essa confiança mínima.")

    print()

# Opção 3: conta uma classe em uma foto
def count_class_in_photo(confidence_level):

    print("\n--- Contar uma classe na foto ---")

    photo = ask_photo()

    show_classes()

    classe = input("Diga a classe: ").strip().lower()

    while classe == "":

        print("Você não digitou nada. Tente novamente.")

        classe = input("Diga a classe: ").strip().lower()

    print(f"Classe escolhida: [{classe}]")

    amount = count_class(photo, classe, confidence_level)

    print(
        f"Objetos da classe '{classe}' "
        f"(confiança >= {confidence_level}): {amount}")

# Opção 4: relatório da pasta (acumulador e contador)
def folder_report(confidence_level):

    print("\n--- Relatório da pasta ---")

    pasta = ask_folder()

    total_fotos = total_photos(pasta)

    total_objetos = 0
    fotos_vazias = 0

    for numero in range(1, total_fotos + 1):

        foto = photo_name(pasta, numero)

        quantidade = count_objects(foto, confidence_level)

        print(
            f"Foto {numero} | {foto} | "
            f"{quantidade} objeto(s)")

        total_objetos = total_objetos + quantidade

        if quantidade == 0:
            fotos_vazias = fotos_vazias + 1

    media = total_objetos / total_fotos

    print("\nTotal geral de objetos:", total_objetos)
    print(f"Média de objetos por foto: {media:.2f}")
    print("Fotos sem nenhum objeto:", fotos_vazias)

# Opção 5: foto mais cheia e mais vazia (max() e min() são proibidos: "melhor até agora")
def fullest_and_emptiest(confidence_level):

    print("\n--- Foto mais cheia e Foto mais vazia ---")

    pasta = ask_folder()

    total_fotos = total_photos(pasta)

    maior_quantidade = 0
    foto_mais_cheia = ""

    menor_quantidade = 0
    foto_mais_vazia = ""

    for numero in range(1, total_fotos + 1):

        foto = photo_name(pasta, numero)

        quantidade = count_objects(foto, confidence_level)

        if numero == 1:

            # A primeira foto é a maior e a menor até agora.
            maior_quantidade = quantidade
            foto_mais_cheia = foto

            menor_quantidade = quantidade
            foto_mais_vazia = foto

        else:

            if quantidade > maior_quantidade:

                maior_quantidade = quantidade
                foto_mais_cheia = foto

            if quantidade < menor_quantidade:

                menor_quantidade = quantidade
                foto_mais_vazia = foto

    print(
        f"\nFoto mais cheia: {foto_mais_cheia} "
        f"({maior_quantidade} objetos)")

    print(
        f"Foto mais vazia: {foto_mais_vazia} "
        f"({menor_quantidade} objetos)")

# Opção 6: procura uma classe na pasta (sum() é proibido: conta à mão)
def search_class_in_folder(confidence_level):

    print("\n--- Procurar uma classe na pasta ---")

    pasta = ask_folder()

    total_fotos = total_photos(pasta)

    show_classes()

    classe = input("Diga a classe (ex.: car, person): ").strip().lower()

    while classe == "":

        print("Você não digitou nada. Tente novamente.")

        classe = input("Diga a classe (ex.: car, person): ").strip().lower()

    fotos_com_classe = 0
    total_encontrado = 0

    for numero in range(1, total_fotos + 1):

        foto = photo_name(pasta, numero)

        quantidade = count_class(foto, classe, confidence_level)

        if quantidade > 0:

            fotos_com_classe = fotos_com_classe + 1

            total_encontrado = total_encontrado + quantidade

    porcentagem = fotos_com_classe / total_fotos * 100

    print(
        f"\nClasse: '{classe}' | pasta: '{pasta}' "
        f"| confiança >= {confidence_level}")

    print(
        f"Aparece em {fotos_com_classe} "
        f"de {total_fotos} fotos.")

    print(f"Quantidade total encontrada: {total_encontrado}")

    print(
        f"Porcentagem de fotos com a classe: "
        f"{porcentagem:.1f}%")

    if total_encontrado == 0:

        print(
            "Nenhum encontrado. Confira se a classe está "
            "na lista acima.")

# Opção 7: gráfico de barras em texto (usa as detecções já filtradas por confiança)
def text_bar_chart(results, confidence_level):

    print("\n--- Gráfico de barras em texto ---")

    pasta = ask_folder()

    total_fotos = total_photos(pasta)

    print(
        f"\nGráfico de objetos por foto na pasta "
        f"'{pasta}' (confiança >= {confidence_level}):\n")

    for numero in range(1, total_fotos + 1):

        foto = photo_name(pasta, numero)

        filtered = filter_detections(results[foto], confidence_level)

        quantidade = len(filtered)

        print(f"{pasta}_{numero:02d} | ", end="")

        for objeto in range(quantidade):
            print("#", end="")

        print(f" ({quantidade})")

# Opção 8: ranking Top N
def show_ranking(results, confidence_level):

    print("\n--- Ranking Top N ---")

    inventory = build_inventory(results, list(results), confidence_level)

    ranking = bubble_sort_desc(inventory_to_list(inventory))

    if len(ranking) == 0:

        print("Nenhum objeto com essa confiança mínima.")

    else:

        # Começa em 0 de propósito: 0 é inválido.
        n = 0

        while n < 1 or n > len(ranking):

            typed = input(f"Quantas classes mostrar (1 a {len(ranking)}): ").strip()

            try:
                n = int(typed)
            except ValueError:
                n = 0

            if n < 1 or n > len(ranking):
                print(
                    f"Número inválido. Digite um número "
                    f"inteiro de 1 a {len(ranking)}.")

        for position in range(n):

            class_name, amount = ranking[position]

            print(f"{position + 1}. {class_name} - {amount}")

# Opção 9: busca reversa (índice classe -> fotos)
def reverse_search(results, confidence_level):

    print("\n--- Busca reversa ---")

    show_classes()

    classe = input("Diga a classe (ex.: car, person): ").strip().lower()

    while classe == "":

        print("Você não digitou nada. Tente novamente.")

        classe = input("Diga a classe (ex.: car, person): ").strip().lower()

    index = build_reverse_index(results, confidence_level)

    if classe not in index:

        print(
            f"A classe '{classe}' não foi encontrada "
            f"com confiança >= {confidence_level}.")

    else:

        print(f"Fotos com '{classe}' (confiança >= {confidence_level}):")

        for photo in index[classe]:

            filtered = filter_detections(results[photo], confidence_level)

            amount = count_class_in(filtered, classe)

            print(f"  {photo}: {amount}")

        print(f"Total de fotos: {len(index[classe])}")

# Opção 10: comparação de duas pastas com conjuntos
def compare_folders(results, folder_photos, confidence_level):

    print("\n--- Comparar duas pastas ---")

    print("Primeira pasta:")
    pasta_a = ask_folder()

    print("Segunda pasta:")
    pasta_b = ask_folder()

    set_a = classes_of_folder(results, folder_photos, pasta_a, confidence_level)
    set_b = classes_of_folder(results, folder_photos, pasta_b, confidence_level)

    print(f"\nComparando '{pasta_a}' e '{pasta_b}' (confiança >= {confidence_level}):\n")

    show_set("Em comum", set_a & set_b)
    show_set(f"Só em {pasta_a}", set_a - set_b)
    show_set(f"Só em {pasta_b}", set_b - set_a)
    show_set("União", set_a | set_b)

# Opção 11: matriz pasta x classe
def show_matrix(results, folder_photos, confidence_level):

    print("\n--- Matriz pasta x classe ---")

    inventory = build_inventory(results, list(results), confidence_level)

    ranking = bubble_sort_desc(inventory_to_list(inventory))

    if len(ranking) == 0:

        print("Nenhum objeto com essa confiança mínima.")

    else:

        # Colunas na ordem do ranking (classe mais frequente primeiro).
        classes = []

        for class_name, amount in ranking:
            classes.append(class_name)

        folders = list(folder_photos)

        matrix = build_matrix(results, folder_photos, confidence_level, classes)

        row_totals, column_totals = matrix_totals(matrix)

        print_matrix(folders, classes, matrix, row_totals, column_totals)

        best_value, best_folder, best_class = find_largest(matrix, folders, classes)

        print(f"\nMaior valor: {best_value} (pasta: {best_folder}, classe: {best_class})")

# Opção 12: histograma do inventário
def show_histogram(results, confidence_level):

    print("\n--- Histograma do inventário ---")

    inventory = build_inventory(results, list(results), confidence_level)

    ranking = bubble_sort_desc(inventory_to_list(inventory))

    if len(ranking) == 0:

        print("Nenhum objeto com essa confiança mínima.")

    else:

        print(
            f"\nObjetos por classe (confiança >= {confidence_level}), "
            f"da mais para a menos frequente:\n")

        print_histogram(ranking)

# Opção 13: salva o relatório em arquivo
def export_report(results, confidence_level, path):

    print("\n--- Salvar relatório ---")

    inventory = build_inventory(results, list(results), confidence_level)

    ranking = bubble_sort_desc(inventory_to_list(inventory))

    save_report(inventory, ranking, confidence_level, path)

    print(f"Relatório salvo em: {path}")

# Opção 14: lê e mostra o relatório salvo
def read_saved_report(path):

    print("\n--- Ler relatório salvo ---")

    read_report(path)

# Opção 15: inventário do acervo inteiro ou de uma pasta
def inventory_option(results, folder_photos, confidence_level):

    show_folders()

    # Enter (vazio) = acervo inteiro.
    folder = input("Digite o nome da pasta (ou Enter para o acervo inteiro): ").strip()

    while folder != "" and folder not in folder_photos:

        print("Pasta inválida. Tente novamente.")

        folder = input("Digite o nome da pasta (ou Enter para o acervo inteiro): ").strip()

    if folder == "":

        photos = list(results)
        title = f"acervo inteiro (confiança >= {confidence_level})"

    else:

        photos = folder_photos[folder]
        title = f"pasta '{folder}' (confiança >= {confidence_level})"

    inventory = build_inventory(results, photos, confidence_level)

    show_inventory(inventory, title)

# MENU E FUNÇÃO PRINCIPAL

def show_menu():

    print("        Menu do PhotoCensus")
    print("""
        1 --> Configurar confiança mínima
        2 --> Analisar uma foto
        3 --> Contar uma classe na foto
        4 --> Relatório da pasta
        5 --> Foto mais cheia e mais vazia
        6 --> Procurar uma classe na pasta
        7 --> Gráfico de barras em texto
        8 --> Ranking Top N
        9 --> Busca reversa
        10 --> Comparar duas pastas
        11 --> Matriz pasta x classe
        12 --> Histograma do inventário
        13 --> Salvar relatório (report.txt)
        14 --> Ler relatório salvo
        15 --> Inventário (acervo ou pasta)
        0 --> Sair""")

def main():

    print("PhotoCensus - Group 02")

    execution = True
    confidence_level = 0.5

    # Carrega o acervo uma única vez ao iniciar.
    results, folder_photos = load_collection()

    show_summary(results, folder_photos, confidence_level)

    while execution:

        show_menu()

        decision = input("Escolha uma opção: ")

        if decision == "0":

            execution = False

        elif decision == "1":

            confidence_level = set_confidence(results, folder_photos, confidence_level)

        elif decision == "2":

            analyze_photo(results, confidence_level)

        elif decision == "3":

            count_class_in_photo(confidence_level)

        elif decision == "4":

            folder_report(confidence_level)

        elif decision == "5":

            fullest_and_emptiest(confidence_level)

        elif decision == "6":

            search_class_in_folder(confidence_level)

        elif decision == "7":

            text_bar_chart(results, confidence_level)

        elif decision == "8":

            show_ranking(results, confidence_level)

        elif decision == "9":

            reverse_search(results, confidence_level)

        elif decision == "10":

            compare_folders(results, folder_photos, confidence_level)

        elif decision == "11":

            show_matrix(results, folder_photos, confidence_level)

        elif decision == "12":

            show_histogram(results, confidence_level)

        elif decision == "13":

            export_report(results, confidence_level, REPORT_PATH)

        elif decision == "14":

            read_saved_report(REPORT_PATH)

        elif decision == "15":

            inventory_option(results, folder_photos, confidence_level)

        else:

            print("Escolha incorreta. Escolha uma opção válida\n")


if __name__ == "__main__":

    main()