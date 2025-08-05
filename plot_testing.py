import matplotlib.pyplot as plt # imports matplotlib for plotting

plt.ion() # enables interactive mode
x = 0
y = 0

graph = plt.scatter(x,y) # creates a scatter plot with initial x and y
plt.show() # displays the plot
i=0 
while i < 10: 
    y += 1
    x += 1

    graph.remove()
    graph = plt.scatter(x, y) # updates the scatter plot with new x and y values
    plt.pause(1) # pauses the plot for 1 second
    i += 1