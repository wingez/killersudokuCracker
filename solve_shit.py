import json
import asyncio

import main

filename = 'solved.json'

with open(filename, mode='r') as f:
    solved = json.load(f)

for i in range(1000, 20000):
    if str(i) in solved:
        continue
    print(i)
    did_solve = False
    try:

        asyncio.run(main.main(i))
        did_solve = True
    except Exception as e:
        did_solve = False

    solved[str(i)] = did_solve
    with open(filename, mode='w') as f:
        json.dump(solved, f)
