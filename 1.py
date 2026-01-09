listt = ['zero']
for num, index in zip(['one', 'two', 'three', 'four', 'five'], range(1, 6)):
    listt[index] = num
print(listt)
