import numpy as np
print("Вариант 7")
print("\n1. Находим седло:")
matrix = np.array([
    [6, 0, 7, 5, 4],
    [12, 11, 12, 7, 1],
    [11, 3, 4, 7, 6],
    [12, 9, 12, 11, 4],
    [4, 8, 0, 2, 2]
])

print("Матрица игры:")
print(matrix)
print()

lower_price = max([min(x) for x in matrix])
upper_price = min([max(x) for x in np.rot90(matrix)])
print(f"Нижняя цена игры (α): {lower_price}")
print(f"Верхняя цена игры (β): {upper_price}")

if lower_price == upper_price:
    print(f"седловая точка есть, ответ v={lower_price}")
else:
    print("седловой точки нет")
    print()

print("2. Расчет выигрышей:")
P = [0.0, 0.0, 0.63, 0.37, 0.0]
Q = [0.0, 0.25, 0.0, 0.0, 0.75]

buff = 0
for i, pin in zip(matrix, P):
    buff += pin * sum([x * y for x, y in zip(i, Q)])

answer = {}
answer["H(P,Q)"] = buff

for k, i in enumerate(np.rot90(matrix), 1):
    answer["H(P,B{})".format(k)] = sum([x * y for x, y in zip(i, P)])

for situation, win in answer.items():
    print(f"Ответ выигрыш игрока A в ситуации {situation} = {win:.3f}")

print("\n3. Активные стратегии:")
active_A = [f"A{i+1}" for i in range(len(P)) if P[i] > 0.001]
active_B = [f"B{i+1}" for i in range(len(Q)) if Q[i] > 0.001]
print(f"Активные стратегии A: {active_A}")
print(f"Активные стратегии B: {active_B}")

print("\n4. Итог:")
print(f"Цена игры: {answer['H(P,Q)']:.3f}")
print(f"P = {P}")
print(f"Q = {Q}")