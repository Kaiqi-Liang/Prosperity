nodes = ["SHELL", "PIZZA", "WASABI", "SNOWBALL"]

CONVERSION = {
  "PIZZA-PIZZA": 100,
  "PIZZA-WASABI": 48,
  "PIZZA-SNOWBALL": 152,
  "PIZZA-SHELL": 71,
  "WASABI-PIZZA": 205,
  "WASABI-WASABI": 100,
  "WASABI-SNOWBALL": 326,
  "WASABI-SHELL": 156,
  "SNOWBALL-PIZZA": 64,
  "SNOWBALL-WASABI": 30,
  "SNOWBALL-SNOWBALL": 100,
  "SNOWBALL-SHELL": 46,
  "SHELL-PIZZA": 141,
  "SHELL-WASABI": 61,
  "SHELL-SNOWBALL": 208,
  "SHELL-SHELL": 100
}

# Create cycles of length 2 to 5 from "SHELL" to "SHELL"
cycles = []

# SHELL - __ - SHELL
for i in nodes:
  if i != "SHELL":
    cycles.append(["SHELL", i, "SHELL"])

# SHELL - __ - __ - SHELL
for i in nodes:
  if i != "SHELL":
    for j in nodes:
      if j != "SHELL":
        cycles.append(["SHELL", i, j, "SHELL"])

# SHELL - __ - __ - __ - SHELL
for i in nodes:
  if i != "SHELL":
    for j in nodes:
      if j != "SHELL":
        for k in nodes:
          if k != "SHELL":
            cycles.append(["SHELL", i, j, k, "SHELL"])

# SHELL - __ - __ - __ - __ - SHELL
for i in nodes:
  if i != "SHELL":
    for j in nodes:
      if j != "SHELL":
        for k in nodes:
          if k != "SHELL":
            for l in nodes:
              if l != "SHELL":
                cycles.append(["SHELL", i, j, k, l, "SHELL"])

res = []

for i in range(len(cycles)):
  curr = cycles[i]
  prev = curr[0]
  multiplied_result = 1
  for j in range(1, len(curr)):
    multiplied_result *= CONVERSION[prev + "-" + curr[j]]
    prev = curr[j]
  res.append((round(multiplied_result, 2), curr))


# Sort in reverse order
res.sort(reverse=True)

# Print the top 5 cycles
for i in range(len(res)):
  # print(f"{res[i][0]} {res[i][1]}: ")
  print(res[i])