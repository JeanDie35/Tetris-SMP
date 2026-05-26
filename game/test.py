def divide(x, y):
    try:
        result = x / y
    except Exception as e:
        print(e)
    else:
        print("result is", result)
    finally:
        print("executing finally clause")
