from pulp import *
import time

print("ТРАНСПОРТНАЯ ЗАДАЧА - ВАРИАНТ 7")

supply = [200, 200, 300, 300, 100]  
demand = [300, 200, 100, 100, 200]  

cost_matrix = [
    [4, 6, 3, 4, 1],
    [7, 3, 5, 2, 2],
    [5, 3, 2, 4, 4],
    [2, 3, 4, 6, 5],
    [1, 4, 4, 3, 3]
]

print("Дано:")
print(f"Запасы поставщиков: {supply} (сумма = {sum(supply)})")
print(f"Потребности потребителей: {demand} (сумма = {sum(demand)})")

total_supply = sum(supply)
total_demand = sum(demand)

if total_supply != total_demand:
    print(f"\nЗадача несбалансированная! Разница: {abs(total_supply - total_demand)}")
    if total_supply < total_demand: 
        supply.append(total_demand - total_supply)
        cost_matrix.append([0, 0, 0, 0, 0])
        print("Добавлен фиктивный поставщик")
    else:
        demand.append(total_supply - total_demand)
        for row in cost_matrix:
            row.append(0)
        print("Добавлен фиктивный потребитель")

m = len(supply)
n = len(demand)

print(f"\nРазмерность задачи: {m} поставщиков × {n} потребителей")

print("Решение методом PULP с HiGHS")

start_time = time.time()

variables = []
for i in range(m):
    for j in range(n):
        variables.append(LpVariable(f"x_{i+1}_{j+1}", lowBound=0)) 

problem = LpProblem("Transport_Problem", LpMinimize)

cost_coeffs = []
for i in range(m):
    for j in range(n):
        cost_coeffs.append(cost_matrix[i][j])

problem += lpDot(cost_coeffs, variables), "Total_Cost" 

for i in range(m):
    constraint_vars = variables[i*n : (i+1)*n] 
    problem += lpSum(constraint_vars) == supply[i], f"Supply_{i+1}" 

for j in range(n):
    constraint_vars = [variables[i*n + j] for i in range(m)]
    problem += lpSum(constraint_vars) == demand[j], f"Demand_{j+1}"

solver = HiGHS_CMD(path="/opt/homebrew/bin/highs")
problem.solve(solver)
pulp_time = time.time() - start_time

print("\nОПТИМАЛЬНЫЙ ПЛАН ПЕРЕВОЗОК:")

total_cost = 0
allocation_matrix = [[0 for _ in range(n)] for _ in range(m)]

for variable in problem.variables():
    if variable.varValue > 0.001: 
        parts = variable.name.split('_')
        supplier = int(parts[1])  
        consumer = int(parts[2])  
        amount = variable.varValue
        cost = amount * cost_matrix[supplier-1][consumer-1] 
        total_cost += cost
        
        allocation_matrix[supplier-1][consumer-1] = amount
        
        print(f"поставщик{supplier} → потребитель{consumer}: {amount:.1f} ед. × {cost_matrix[supplier-1][consumer-1]} = {cost:.1f}")

print(f"\nМатрица перевозок:")
for i, row in enumerate(allocation_matrix):
    print(f"Поставщик {i+1}: {[f'{x:.1f}' for x in row]}")

print(f"\nМинимальная стоимость: {total_cost:.1f}")

# Проверка выполнения ограничений
print("\nПроверка выполнения ограничений:")
for i in range(m):
    total_sent = sum(allocation_matrix[i])
    print(f"Поставщик {i+1}: отправил {total_sent:.1f} ед. (должен {supply[i]} ед.)")

for j in range(n):
    total_received = sum(allocation_matrix[i][j] for i in range(m))
    print(f"Потребитель {j+1}: получил {total_received:.1f} ед. (нужно {demand[j]} ед.)")

print(f"\nВремя выполнения: {pulp_time:.4f} сек")
print(f"Статус решения: {LpStatus[problem.status]}")