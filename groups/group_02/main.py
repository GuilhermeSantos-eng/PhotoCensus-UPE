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
            confidence_level_update = float(input("Escolha o novo nível de confiança: "))
            confidence_level = confidence_level_update
            print(f"Novo nível de confiança: {confidence_level}")

        elif decision == "2":

            pass
            

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