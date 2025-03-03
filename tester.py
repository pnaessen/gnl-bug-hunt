#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import tempfile
import sys
import time
import signal
from termcolor import colored

# Configuration
BUFFER_SIZES = [1, 5, 42, 1000, 10000000]
TIMEOUT = 5  # Timeout en secondes pour les tests

# Couleurs pour l'affichage
SUCCESS = colored("✓", "green")
FAILURE = colored("✗", "red")
WARNING = colored("!", "yellow")

def compile_gnl(buffer_size):
    """Compile get_next_line avec un BUFFER_SIZE spécifique"""
    # Create test_main.c first
    create_test_program()
    
    cmd = ["gcc", "-Wall", "-Wextra", "-Werror", f"-D", f"BUFFER_SIZE={buffer_size}", 
           "test_main.c", "get_next_line.c", "get_next_line_utils.c", "-o", "gnl_test"]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur de compilation: {e.stderr.decode('utf-8')}")
        return False

def run_with_valgrind(args):
    """Exécute le programme avec valgrind pour détecter les fuites de mémoire"""
    cmd = ["valgrind", "--leak-check=full", "--show-leak-kinds=all", "--track-origins=yes", 
           "--verbose", "--log-file=valgrind_output.txt"] + args
    
    try:
        process = subprocess.run(cmd, timeout=TIMEOUT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Analyse du rapport valgrind
        with open("valgrind_output.txt", "r") as f:
            valgrind_output = f.read()
        
        if "All heap blocks were freed -- no leaks are possible" in valgrind_output:
            leaks = False
        else:
            leaks = True
            
        return {
            "returncode": process.returncode,
            "stdout": process.stdout.decode('utf-8'),
            "stderr": process.stderr.decode('utf-8'),
            "leaks": leaks,
            "valgrind_output": valgrind_output
        }
    except subprocess.TimeoutExpired:
        print(f"{WARNING} Timeout après {TIMEOUT} secondes")
        return None

def create_test_program(test_file_path=None, stdin_test=False):
    """Crée un programme de test temporaire qui utilise get_next_line"""
    program = """
    #include "get_next_line.h"
    #include <fcntl.h>
    #include <stdio.h>
    
    int main(int argc, char **argv) {
        int fd;
        char *line;
        
        if (argc > 1) {
            fd = open(argv[1], O_RDONLY);
            if (fd < 0) {
                printf("Erreur: Impossible d'ouvrir le fichier %s\\n", argv[1]);
                return 1;
            }
        } else {
            fd = 0; // stdin
        }
        
        while ((line = get_next_line(fd)) != NULL) {
            printf("%s", line);
            free(line);
        }
        
        if (fd > 0)
            close(fd);
        return 0;
    }
    """
    
    with open("test_main.c", "w") as f:
        f.write(program)
    
    # Compilation du programme de test
    cmd = ["gcc", "-Wall", "-Wextra", "-Werror", "test_main.c", 
           "get_next_line.c", "get_next_line_utils.c", "-o", "gnl_test"]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur de compilation du programme de test: {e.stderr.decode('utf-8')}")
        return False

def run_test(test_name, test_file=None, buffer_size=42, stdin_input=None, expected_output=None):
    """Exécute un test spécifique"""
    print(f"\n--- Test: {test_name} (BUFFER_SIZE={buffer_size}) ---")
    
    # Compilation avec le BUFFER_SIZE spécifié
    if not compile_gnl(buffer_size):
        print(f"{FAILURE} Échec de la compilation")
        return False
    
    # Création du programme de test
    if not create_test_program():
        print(f"{FAILURE} Échec de la création du programme de test")
        return False
    
    # Exécution du test
    args = ["./gnl_test"]
    if test_file:
        args.append(test_file)
    
    # Si on teste l'entrée standard
    if stdin_input is not None:
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
            temp.write(stdin_input)
            temp.flush()
            temp_name = temp.name
        
        # Redirection de l'entrée standard
        with open(temp_name, 'r') as stdin_file:
            try:
                process = subprocess.run(args, stdin=stdin_file, stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE, timeout=TIMEOUT)
                output = process.stdout.decode('utf-8')
                
                # Vérification de la sortie
                if expected_output is not None and output != expected_output:
                    print(f"{FAILURE} La sortie ne correspond pas à l'attendu")
                    print(f"Attendu: {repr(expected_output)}")
                    print(f"Obtenu: {repr(output)}")
                    os.unlink(temp_name)
                    return False
                
                # Test avec valgrind
                valgrind_result = run_with_valgrind(args)
                if valgrind_result and valgrind_result["leaks"]:
                    print(f"{FAILURE} Fuites de mémoire détectées")
                    print(valgrind_result["valgrind_output"])
                    os.unlink(temp_name)
                    return False
                
                print(f"{SUCCESS} Test réussi")
                os.unlink(temp_name)
                return True
                
            except subprocess.TimeoutExpired:
                print(f"{WARNING} Timeout après {TIMEOUT} secondes")
                os.unlink(temp_name)
                return False
    else:
        # Test normal avec un fichier
        try:
            valgrind_result = run_with_valgrind(args)
            
            if valgrind_result is None:
                return False
                
            if valgrind_result["returncode"] != 0:
                print(f"{FAILURE} Le programme a retourné une erreur (code {valgrind_result['returncode']})")
                return False
                
            if valgrind_result["leaks"]:
                print(f"{FAILURE} Fuites de mémoire détectées")
                print(valgrind_result["valgrind_output"])
                return False
                
            print(f"{SUCCESS} Test réussi")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"{WARNING} Timeout après {TIMEOUT} secondes")
            return False

def run_all_tests():
    """Exécute tous les tests avec différentes tailles de buffer"""
    results = {}
    
    # Liste des tests à exécuter
    tests = [
        {"name": "Fichier vide", "file": "test_files/empty.txt"},
        {"name": "Un seul caractère", "file": "test_files/1char.txt"},
        {"name": "Une ligne sans retour à la ligne", "file": "test_files/one_line_no_nl.txt"},
        {"name": "Seulement des retours à la ligne", "file": "test_files/only_nl.txt"},
        {"name": "Plusieurs lignes", "file": "test_files/multiple_nl.txt"},
        {"name": "Retours à la ligne variables", "file": "test_files/variable_nls.txt"},
        {"name": "Environ 10 lignes", "file": "test_files/lines_around_10.txt"},
        {"name": "Ligne géante", "file": "test_files/giant_line.txt"},
        {"name": "Entrée standard", "stdin": "Test d'entrée standard\nAvec plusieurs lignes\n"},
        {"name": "BUFFER_SIZE invalide", "file": "test_files/multiple_nl.txt", "buffer_size": -1},
    ]
    
    # Préparation du test d'erreur de lecture
    try:
        os.chmod("test_files/read_error.txt", 0o000)  # Enlever toutes les permissions
        tests.append({"name": "Erreur de lecture", "file": "test_files/read_error.txt"})
    except:
        print(f"{WARNING} Impossible de modifier les permissions pour le test d'erreur de lecture")
    
    # Exécution des tests
    for test in tests:
        buffer_size = test.get("buffer_size", 42)  # BUFFER_SIZE par défaut
        
        if "stdin" in test:
            result = run_test(test["name"], buffer_size=buffer_size, 
                             stdin_input=test["stdin"], expected_output=test["stdin"])
        else:
            result = run_test(test["name"], test_file=test["file"], buffer_size=buffer_size)
        
        results[test["name"]] = result
    
    # Restaurer les permissions
    try:
        os.chmod("test_files/read_error.txt", 0o644)
    except:
        pass
    
    # Tests avec différentes tailles de buffer
    for buffer_size in BUFFER_SIZES:
        result = run_test(f"Multiple lignes (BUFFER_SIZE={buffer_size})", 
                         test_file="test_files/multiple_nl.txt", buffer_size=buffer_size)
        results[f"BUFFER_SIZE={buffer_size}"] = result
    
    # Affichage du résumé
    print("\n=== Résumé des tests ===")
    success_count = 0
    for name, result in results.items():
        status = SUCCESS if result else FAILURE
        print(f"{status} {name}")
        if result:
            success_count += 1
    
    print(f"\nTests réussis: {success_count}/{len(results)}")
    
    # Nettoyage
    for file in ["gnl_test", "test_main.c", "valgrind_output.txt"]:
        if os.path.exists(file):
            os.remove(file)

if __name__ == "__main__":
    # Vérifier si valgrind est installé
    try:
        subprocess.run(["valgrind", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print(f"{WARNING} Valgrind n'est pas installé. Les tests de fuites de mémoire seront désactivés.")
        print("Installez valgrind avec 'brew install valgrind' sur macOS ou 'apt-get install valgrind' sur Linux.")
        sys.exit(1)
    
    run_all_tests() 