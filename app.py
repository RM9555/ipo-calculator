import streamlit as st
import math
from typing import List, Dict
from collections import Counter

# Caching the factorial calculation for better performance
@st.cache_data
def calculate_combinations(n: int, r: int) -> float:
    """Calculate nCr combinations"""
    return math.factorial(n) / (math.factorial(r) * math.factorial(n - r))

@st.cache_data(ttl=0)  # Added ttl=0 to prevent caching issues
def calculate_probability(n: int, x: int, p: float) -> float:
    """
    Calculate probability of getting AT LEAST x successes in n trials
    P(at least x) = P(x) + P(x+1) + ... + P(n)
    """
    # P(at least x) = 1 - P(less than x)
    prob_less_than_x = 0
    for i in range(0, x):
        prob_i = calculate_combinations(n, i) * (p ** i) * ((1 - p) ** (n - i))
        prob_less_than_x += prob_i
    return 1 - prob_less_than_x

def calculate_expected_lots(n: int, p: float, category: str) -> int:
    """
    Calculate expected number of lots based on category
    Returns integer for retail and multiple of 14 for HNI categories
    """
    # Calculate basic expectation (n * p)
    basic_expectation = n * p
    
    if category == 'retail':
        # Round to nearest integer for retail
        return round(basic_expectation)
    else:
        # For SHNI and BHNI, round to nearest multiple of 14
        lots_per_application = 14
        applications = round(basic_expectation)  # Round the number of successful applications
        return applications * lots_per_application

def parse_application_input(input_str: str) -> List[str]:
    """Parse input string into list of categories"""
    if not input_str:
        return []
        
    categories = []
    parts = input_str.lower().split()
    
    i = 0
    while i < len(parts):
        if parts[i].isdigit() and i + 1 < len(parts):
            count = int(parts[i])
            category = parts[i + 1]
            if category not in ['retail', 'shni', 'bhni']:
                raise ValueError(f"Invalid category: {category}")
            categories.extend([category] * count)
            i += 2
        else:
            if parts[i] not in ['retail', 'shni', 'bhni']:
                raise ValueError(f"Invalid category: {parts[i]}")
            categories.append(parts[i])
            i += 1
            
    return categories

def main():
    st.title("IPO Allotment Chance Calculator")
    
    st.markdown("""
    ### Available categories:
    1. retail - Retail Individual Investor (1 lot per application)
    2. shni  - Small HNI (14 lots per application)
    3. bhni  - Big HNI (14 lots per application)
    """)
    
    # Input field for applications
    input_str = st.text_input("Enter applications (e.g., '2 retail bhni 3 shni'):", key="applications")
    
    try:
        categories = parse_application_input(input_str)
        if categories:
            st.write("You applied from these categories:", " + ".join(categories))
            
            # Get subscription details for each unique category
            unique_categories = set(categories)
            subscription_ratios = {}
            
            st.subheader("Enter subscription ratios:")
            
            # Create columns for subscription ratio inputs
            cols = st.columns(len(unique_categories))
            for idx, category in enumerate(unique_categories):
                with cols[idx]:
                    subscription_ratios[category] = st.number_input(
                        f"{category.upper()}",
                        min_value=0.1,
                        value=1.0,
                        step=0.1,
                        key=f"sub_{category}"
                    )
            
            if st.button("Calculate Probabilities"):
                # Process each category type separately
                category_counts = Counter(categories)
                
                st.subheader("Probability Calculations:")
                st.markdown("---")
                
                total_expected_lots = 0
                
                for category, count in category_counts.items():
                    effective_subscription = subscription_ratios[category]
                    if category == 'bhni':
                        effective_subscription = subscription_ratios[category] / 5
                        st.write(f"\n{category.upper()} (Adjusted subscription ratio: {effective_subscription:.2f}x)")
                    else:
                        st.write(f"\n{category.upper()} (Subscription ratio: {effective_subscription:.2f}x)")
                    
                    p = 1 / effective_subscription  # Probability of getting a lot
                    
                    # Calculate and display probability for each number of lots
                    for i in range(1, count + 1):
                        prob = calculate_probability(count, i, p) * 100
                        st.write(f"Probability of getting at least {i} lot(s): {prob:.2f}%")
                    
                    # Calculate and display expected lots
                    expected_lots = calculate_expected_lots(count, p, category)
                    total_expected_lots += expected_lots
                    
                    if category in ['shni', 'bhni']:
                        st.write(f"Expected number of lots: {expected_lots} (multiple of 14)")
                    else:
                        st.write(f"Expected number of lots: {expected_lots}")
                    
                    st.markdown("---")
                
                st.subheader("Total Expected Lots")
                st.write(f"Total expected number of lots across all categories: {total_expected_lots}")
                    
    except ValueError as e:
        st.error(f"Error: {e}")
        st.warning("Please try again using format like '2 retail bhni 3 shni'")
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
