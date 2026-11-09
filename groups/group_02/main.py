import os
import sys

# Adiciona a pasta kit ao caminho do Python
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "kit"))
from black_box import *




# ============================================================
# FUNÇÃO ask_folder
# Objetivo: pedir o nome de uma pasta e só aceitar quando ela for válida.
# Devolve (return) o nome da pasta.
# Usada nas opções 2 e 3 (e depois nas opções 4 a 7).
# ============================================================
def ask_folder():

    # [0] mostra as pastas
    show_folders()
    # [1] Pede o nome da pasta. O .strip() tira espaços das pontas
    #     (assim "  street " vira "street").
    folder = input("Digite o nome da pasta (ex: street, animals, sports): ").strip()

    # [2] Laço de validação: repete ENQUANTO a pasta for inválida.
    #     Ela é inválida se QUALQUER uma das 3 condições for verdadeira (por isso o "or"):
    #       - folder == ""                -> o usuário só apertou Enter
    #       - not folder_exists(folder)   -> a pasta não existe em images/
    #       - total_photos(folder) == 0   -> existe, mas não tem fotos (pega ".." e "kit")
    #     A ordem importa: se a primeira for verdadeira, o Python nem testa as outras.
    while folder == "" or not folder_exists(folder) or total_photos(folder) == 0:
        print("Pasta inválida. Tente novamente.")
        # [3] Pede de novo DENTRO do laço; sem isso ele repetiria para sempre.
        folder = input("Digite o nome da pasta (ex: street, animals, sports): ").strip()

    # [4] Chegou aqui = pasta válida. O "return" entrega o valor para quem chamou a função.
    return folder





# ============================================================
# FUNÇÃO ask_photo
# Objetivo: pedir pasta + número da foto (os dois validados).
# Devolve (return) o CAMINHO da foto, ex.: "images/street/street_04.jpg".
# Usada nas opções 2 e 3.
# ============================================================
def ask_photo():
    # [1] Primeiro pede a pasta, já validada, usando a função do passo 1.
    #     (uma função pode chamar outra função)
    folder = ask_folder()

    # [2] Guarda quantas fotos a pasta tem e mostra para o usuário.
    total = total_photos(folder)
    print(f"A pasta '{folder}' tem {total} fotos.")

    # [3] number começa em 0 DE PROPÓSITO: 0 é inválido, então o while entra pelo menos uma vez.
    number = 0

    # [4] Repete ENQUANTO o número estiver fora do intervalo de 1 até o total.
    while number < 1 or number > total:
        typed = input(f"Escolha o número da foto (1 a {total}): ").strip()

        # [5] int() dá ValueError se o texto não for inteiro (abc, 2.7, vazio).
        #     Em vez de quebrar, o except coloca number = 0 (inválido) e o laço repete.
        try:
            number = int(typed)
        except ValueError:
            number = 0

        # [6] Só mostra o erro se o número ficou inválido.
        if number < 1 or number > total:
            print(f"Número inválido. Digite um número inteiro de 1 a {total}.")

    # [7] Pasta e número válidos: monta e devolve o caminho da foto.
    return photo_name(folder, number)











def relatorio_da_pasta(confianca):
    """Opção 4: uma linha por foto, total geral, média e fotos vazias."""
    # ask_folder() já rejeita pasta inválida e pasta sem fotos
    pasta = ask_folder()
    total_fotos = total_photos(pasta)

    total_objetos = 0    # acumulador: soma dos objetos de todas as fotos
    fotos_vazias = 0     # contador: fotos com 0 objetos

    # for percorre todas as fotos; range(1, total + 1) porque as
    # fotos começam em 1 e o range para antes do último número
    for numero in range(1, total_fotos + 1):
        foto = photo_name(pasta, numero)
        quantidade = count_objects(foto, confianca)

        # Uma linha por foto com a quantidade de objetos
        print(f"Foto {numero} | {foto} | {quantidade} objeto(s)")

        total_objetos = total_objetos + quantidade   # acumula o total
        if quantidade == 0:
            fotos_vazias = fotos_vazias + 1          # conta foto vazia

    # total_fotos nunca é 0 aqui, pois ask_folder() rejeita pasta sem fotos
    media = total_objetos / total_fotos

    # Resumo final do relatório
    print("\nTotal geral de objetos:", total_objetos)
    print(f"Média de objetos por foto: {media:.2f}")
    print("Fotos sem nenhum objeto:", fotos_vazias)


def main():
    print("PhotoCensus - Group 02")
    
    # Inicializando variáveis globais do programa
    execution = True
    confidence_level = 0.5  # Valor padrão de exemplo
    

    while execution:
        print("        Menu do PhotoCensus")
        print("""
        1 --> Configurar confiança mínima
        2 --> Analisar uma foto
        3 --> Contar uma classe na foto
        4 --> Relatório da pasta 
        5 --> Foto mais cheia e mais vazia
        6 --> Procurar uma classe na pasta
        7 --> Gráfico de barras em texto
        0 --> Sair""")

        decision = input("Escolha uma opção: ")

        if decision == "0":
            execution = False
            
        elif decision == "1":

            ## 1) Mostra o valor atual da confiança
            print(f"Nível de confiança atual: {confidence_level}")

            while True :

                ##2) aqui recebmos o novo valor em str pra fazer devidas correções para não quebrar o programa
                Atualizacao_confianca_str = input ("Digite o novo valor a ser atribuído à confiança: ")
                Atualizacao_confianca_str = Atualizacao_confianca_str.strip()
                Atualizacao_confianca_str = Atualizacao_confianca_str.replace(",",".")

                ## 3)O try protege o programa contra valores inválidos impedindo o sistema quebrar
                try :
                    Atualizacao_confianca = float(Atualizacao_confianca_str)
                    confidence_level = Atualizacao_confianca
                    
                ## 4) Se o valor digitado pelo usuário der algum erro, ele cai no except e o laço é executado novamente pedindo um novo valor
                except ValueError:
                    print ("Você digitou um valor errado. Por favor,digite um valor válido (entre 0 e 1) e  não tente quebrar o programa!")
                    continue
                break

            print(f"Novo nível de confiança: {confidence_level}")


                ## NÃO ESQUECER DE CHECAR INTERVALO 0 - 1 
            


        elif decision == "2":

            print("\n--- Analisar uma foto ---")

            # [PASSO 2] Pasta + número da foto agora vêm da função ask_photo(),
            #           que devolve o CAMINHO da foto já validado.
            photo = ask_photo()

            # 3) Busca os dados da foto
            total_objs = count_objects(photo, confidence_level)

            # 4) Mostra o resultado
            print(f"\nFoto: {photo}")
            print(f"Objetos detectados (confiança >= {confidence_level}): {total_objs}")
            if total_objs > 0:
                main_obj = main_object(photo)
                best_conf = max_confidence(photo)
                print(f"Objeto principal: {main_obj}")
                print(f"Maior confiança: {best_conf * 100:.0f}%")
            else:
                print("Nenhum objeto com essa confiança mínima.")
            print()
            

        elif decision == "3":
            print ("\n--- Contar uma classe na foto ---")

            photo = ask_photo()

            # [2] Mostra as classes que o modelo reconhece (a função já imprime sozinha)
            show_classes()

            # [3] Pede a classe. .strip() tira espaços e .lower() deixa minúsculo
            classe = input("Diga a classe: ").strip().lower()

            # [4] Não aceita vazio: repete enquanto o usuário não digitar nada
            while classe == "":
                print("Você não digitou nada. Tente novamente.")
                classe = input("Diga a classe: ").strip().lower()

            # [5] Mostra a classe escolhida, entre colchetes, para conferir
            print(f"Classe escolhida: [{classe}]")

            amount = count_class(photo,classe,confidence_level)

            print(f"Objetos da classe '{classe}' (confiança >= {confidence_level}): {amount}")




        elif decision == "4":
            print("\n--- Relatório da pasta ---")
            relatorio_da_pasta(confidence_level)

        elif decision == "5":
            pass

        elif decision == "6":
            pass

        elif decision == "7":
            pass

        else:
            print("Escolha incorreta. Escolha uma opção válida\n")

if __name__ == "__main__":
    main()