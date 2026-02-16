#this is a comment

class Person {
    name String
    age Int

    eat(food String) {
        print(" is eating ")
    }
}



def stuff(){
    print("I'm stuff")
}


def print_num_times(num number){
    while num > 0 {
        print(num)
        num = num - 1
    }
}


def returns_num(){
    return 190+90
}

def fails() {
    if 0 > 1 {
        fail()
    }
    return 190
}



def main(z int){
    var x = fails() catch {
        while 1 < 0 {
            print("I'm in the catch block")
        }
        ^ 1
    }
    var a = 0
    var b = 1
    var n = 10
    while n > 0 {
        b = a + b
        a = b
        n = n - 1
        print(a)
    }

    stuff()
    print("Hello World you dope")
    print(a, 2+90*78)
    print_num_times(10)
    print_num_times(30) 
    print(fails() catch {
        ^ 20+40
    })
    var temp = if 1 > 0 {
        print("1 is greater than 0")
        ^ 100
    } else {
        print("1 is not greater than 0")
        ^ 200
    }
    print(temp)

}

