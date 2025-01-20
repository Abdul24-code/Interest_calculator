# interest_calculator.py

def calculate_simple_interest(principal, rate, time):
    return (principal * rate * time) / 100

def calculate_compound_interest(principal, rate, time):
    return principal * ((1 + rate / 100) ** time - 1)

def main():
    print("Welcome to the Interest Calculator")

    # Take user input
    try:
        principal = float(input("Enter the investment amount (Principal): "))
        rate = float(input("Enter the interest rate (as a percentage): "))
        time = float(input("Enter the time period (in years): "))
    except ValueError:
        print("Invalid input. Please enter numeric values.")
        return

    print("\nChoose the type of interest:")
    print("1. Simple Interest")
    print("2. Compound Interest")

    interest_type = input("Enter 1 or 2: ")

    if interest_type == '1':
        interest = calculate_simple_interest(principal, rate, time)
        total = principal + interest
        print(f"\nSimple Interest: {interest}")
        print(f"Total amount after {time} years: {total}")
    
    elif interest_type == '2':
        interest = calculate_compound_interest(principal, rate, time)
        total = principal + interest
        print(f"\nCompound Interest: {interest}")
        print(f"Total amount after {time} years: {total}")
    
    else:
        print("Invalid choice. Please select 1 or 2.")

if __name__ == "__main__":
    main()

