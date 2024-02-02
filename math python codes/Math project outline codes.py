#1a)
import math

##1b)
while True:
    mean_value = input("Please enter a mean value, which can be between negative and positive infinity: ")
    if mean_value == "":
        mean_value = 0
        break
    try:
        mean_value = float(mean_value)
        break
    except:
        print("Please enter again due to invalid input.")


while True:    
    variance_value = input("Please enter a variance value, which must be bigger than zero: ")
    if variance_value == "":
        variance_value = 1
        break
    try:
        if float(variance_value) <= 0:
            print("Please enter value greater than zero")

        else:
            variance_value = float(variance_value)
            break
            
    except:
        print("Please enter again.")

##1c)
while True: #aka k value
    X_value = input("Please enter a X value, which can be between negative and positive infinity: ")
    try:
        X_value = float(X_value)
        break
    except:
        print("Please enter again due to invalid input.")

#d)
##def prob_density(mean_value, variance_value, X_value):
##    result = (1/(math.sqrt(2*math.pi*variance_value))) * math.exp(-((X_value - mean_value)**2)/(2*variance_value))
##    #e
##    return result
##    print("The prob density value is {}".format(result))
##
##
#1f)
def prob_density_2(mean_value, variance_value, X_value):
    result = (1/(math.sqrt(2*math.pi*variance_value))) * math.exp(-((X_value - mean_value)**2)/(2*variance_value))
    #e
    return result
##
##
##
def prob_ndr():
    step = input("Please enter alpha value: ")  #alpha value
    step = float(step)

    a_value = input("Please enter an 'a' value: ")
    k_value = X_value

    

    new_step = step
    while step.is_integer() == False:
        new_step = new_step*10
        if new_step.is_integer() == True:
            break
    multiplier = new_step/step
    new_a_value = int(float(a_value)*multiplier)
    new_k_value = int(k_value*multiplier)

    sum_inside_square_bracket = 0
    new_step = int(new_step)
    print(new_a_value, new_k_value + 1, new_step)
    for i in range(new_a_value, new_k_value + 1, new_step):
        i = i/multiplier
        print(i)
        sum_inside_square_bracket += prob_density_2(mean_value, variance_value, i)
    return step*sum_inside_square_bracket
##prob_ndr()
##        
##
##
#h

list1 = [i/10 for i in range(-50, 51)]
dictionary = {}

for element in list1:
    dictionary[element] = prob_density_2(mean_value, variance_value, element)

for i in range(-20, 21, 5):
    for key, value in dictionary.items():
        if i/10 == key:
            print((i/10, value))
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##
##    
