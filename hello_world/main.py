import random

def read_facts(file_path):
    with open(file_path, 'r') as file:
        facts = file.readlines()
    return [fact.strip() for fact in facts]

def main():
    facts = read_facts('facts.txt')
    interesting_fact = random.choice(facts)
    print("Hello, World! Did you know? " + interesting_fact)

if __name__ == '__main__':
    main()
