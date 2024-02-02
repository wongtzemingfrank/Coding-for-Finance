#!/usr/bin/env python
# coding: utf-8

# In[1]:





# In[2]:


#from pynput.mouse import Controller
#from win32api import GetSystemMetrics


# In[3]:


print("Width =", GetSystemMetrics(0))
print("Height =", GetSystemMetrics(1))


# In[4]:


half_width = round(GetSystemMetrics(0)/2)
print(half_width)

half_height = round(GetSystemMetrics(1)/2)
print(half_height)


# In[5]:


mouse = Controller()

before = mouse.position

x,y = before

print(x)
print(y)


### In[8]:
##
##
mouse = Controller()

before = mouse.position
x,y = before #Convert tuple value into integer

count = 0

def return_box(x,y):
    if x in range(0, half_width):     #1st and 3rd box
        if y in range(0, half_height):
            return "first"
        elif y in range(half_height, 2*half_height):
            return "third"

    if x in range(half_width, 2*half_width):
        if y in range(0, half_height):
            return "second"
        elif y in range(half_height, 2*half_height):
            return "forth"

counter = -1
before_box = 0
while True:
    current = mouse.position
    a,b = current
    
    current_box = return_box(a,b)
    if current_box != before_box:
        count += 1
        print(count)
    before_box = return_box(a,b)
   










