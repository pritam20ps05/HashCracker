import hashlib
import pyfiglet
from os import path
from sys import argv
import concurrent.futures

usage = f'Usage: python {argv[0]} [TARGET_HASH || TARGET_HASH_FILE] [DICTIONARY_FILE_PATH] [WORDS_PER_PROCESS]\n'

class WordListNotFound(Exception):
    def __init__(self, message: str = 'File for WordList was not found', *args: object) -> None:
        self.message = message + f'\n\n{usage}'
        super().__init__(self.message, *args)

class TargetNotFound(Exception):
    def __init__(self, message: str = 'Any Target Hash was not found', *args: object) -> None:
        self.message = message + f'\n\n{usage}'
        super().__init__(self.message, *args)
        

def checkHashMatch(target: str, wordlist: list[str]):
    for word in wordlist:
        if hashlib.sha256(word.encode()).hexdigest() == target:
            return word
        elif hashlib.sha256(word.upper().encode()).hexdigest() == target:
            return word.upper()
        elif hashlib.sha256(word.lower().encode()).hexdigest() == target:
            return word.lower()
        elif hashlib.sha256(word.capitalize().encode()).hexdigest() == target:
            return word.capitalize()
    return None


class HashCracker():
    target = ""
    wordlistfile = ""

    def __init__(self, target: str, wordlistfile: str, wordchunks: int = 50) -> None:
        target = target.strip()
        wordlistfile = wordlistfile.strip()

        self.wordchunks = wordchunks

        if path.isfile(target):
            with open(target, 'r') as f:
                self.target = f.readline().split('\n')[0]
        else:
            self.target = target
        
        if not self.target:
            raise TargetNotFound()

        if path.isfile(wordlistfile):
            self.wordlistfile = wordlistfile
        else:
            raise WordListNotFound()
        
        print(f'HashCracker inittialized in sha256 mode\n\nTarget Hash: {self.target}\nDictionary File: {self.wordlistfile}\nWords Per Process: {self.wordchunks}\n')

    def startAttack(self):
        with open(self.wordlistfile, 'r') as f:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                moreinfile = True
                results = []
                nwords = 0
                while moreinfile:
                    wordlist = []
                    for _ in range(self.wordchunks):
                        line = f.readline()
                        if line:
                            wordlist.append(line.split('\n')[0])
                        else:
                            moreinfile = False
                    if wordlist:
                        result = executor.submit(checkHashMatch, self.target, wordlist)
                        results.append(result)
                        nwords+=len(wordlist)

                nprocesses = len(results)
                print(f'Number of words in dictionary: {nwords}')
                print(f'Total number of processes spawned: {nprocesses}')
                for f in concurrent.futures.as_completed(results):
                    result = f.result()
                    if result:
                        return result
                    
    def getCrackResult(self):
        print('Started cracking...')
        result = hc.startAttack()
        if result:
            print(f'Done cracking\n\nCracked Passcode: {result}')
        else:
            print('\nCould not find any passcode with matching hash')


banner = pyfiglet.figlet_format('HashCracker')
print(f'{banner}\n')

hc: HashCracker = None
if len(argv)>1:
    if argv[1]=='-h' or argv[1]=='--help':
        print(usage)
        exit(0)
    elif len(argv)==3:
        hc = HashCracker(argv[1], argv[2])
    elif len(argv)==4:
        try:
            hc = HashCracker(argv[1], argv[2], int(argv[3]))
        except ValueError as e:
            hc = HashCracker(argv[1], argv[2])
if not hc:
    print(usage)

    target_hash = input('Enter Target Hash or Target Hash File: ')
    dict_path = input('Enter Dictionary File Path: ')
    try:
        words_pp = int(input('Enter Words Per Process: '))
        print()
        hc = HashCracker(target_hash, dict_path, words_pp)
    except ValueError as e:
        hc = HashCracker(target_hash, dict_path)


if hc:
    hc.getCrackResult()