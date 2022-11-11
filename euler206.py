import pulp

problem = pulp.LpProblem()
a = pulp.LpVariable('a')
b = pulp.LpVariable('b')

problem += pulp.LpConstraint(a * b == 10)
problem += pulp.LpConstraint(a + b == 10)

problem.solve()
