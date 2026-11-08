import os
import sys

# Adiciona a pasta kit ao caminho do Python
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "kit"))
from black_box import *

def main():
    print("PhotoCensus - Group 02")
    
    # Inicializando variáveis globais do programa
    execution = True
    confidence_level = 0.5  # Valor padrão de exemplo
    
    
    show_folders()

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
            print(f"Nível de confiança atual: {confidence_level}")
            
            Atualizacao_confianca_str = input ("Digite o novo valor a ser atribuído à confiança: ")
            Atualizacao_confianca_str = Atualizacao_confianca_str.strip()
            Atualizacao_confianca_str = Atualizacao_confianca_str.replace(",",".")

            Atualizacao_confianca_str = float(Atualizacao_confianca_str)

            confidence_level = Atualizacao_confianca_str
            print(f"Novo nível de confiança: {confidence_level}")


            ## nao esquecer de proteger o codigo contra valores inválidos, tipo o ABC
        elif decision == "2":
            print("\n--- Analisar uma foto ---")

            # 1) Pede a pasta até ela ser válida
            folder = input("Digite o nome da pasta (ex: street, animals, sports): ").strip()
            while folder == "" or not folder_exists(folder) or total_photos(folder) == 0:
                print("Pasta inválida. Tente novamente.")
                folder = input("Digite o nome da pasta (ex: street, animals, sports): ").strip()

            total = total_photos(folder)
            print(f"A pasta '{folder}' tem {total} fotos.")

            # 2) Pede o número da foto até ele ser válido
            number = 0
            while number < 1 or number > total:
                typed = input(f"Escolha o número da foto (1 a {total}): ").strip()
                try:
                    number = int(typed)
                except ValueError:
                    number = 0
                if number < 1 or number > total:
                    print(f"Número inválido. Digite um número inteiro de 1 a {total}.")

            # 3) Busca os dados da foto
            photo = photo_name(folder, number)
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
            
            caminho = input ("Digite o caminho das fotos:")
            classe = input ("Qual classe será analisada:  ")
            
            nova_atualizacao_da_confianca = input (f"Deseja alterar o nível de confiança? atualmente o nǘel de confiança é: {confidence_level}. digite Y para alterar e N para manter o nível atual")
            nova_atualizacao_da_confianca = nova_atualizacao_da_confianca.lower()

            if nova_atualizacao_da_confianca == "y":
                confidence_level_update = float(input("Escolha o novo nível de confiança: "))
                confidence_level = confidence_level_update
                print(f"Novo nível de confiança: {confidence_level}")

            elif nova_atualizacao_da_confianca == 'n':
                pass

            quantidade = count_class(caminho,classe,confidence_level)
            
            print (f"Foi encontrado: {quantidade} resultados para a sua pesquisa.")










        elif decision == "4":
            pass

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