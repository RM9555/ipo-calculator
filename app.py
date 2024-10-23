import streamlit as st
import math
from typing import List, Dict
from collections import Counter

# Caching the factorial calculation for better performance
@st.cache_data
def calculate_combinations(n: int, r: int) -> float:
    return math.factorial(n) / (math.factorial(r) * math.factorial(n - r))

@st.cache_data
@st.cache_data
def calculate_probability(n: int, x: int, p: float) -> float:
    """Calculate probability of getting at least x successes in n trials
    Using 1 minus P(less than x) approach which is more efficient and accurate
    """
    if x == 0:
        return 1.0
    
    # Calculate P(X < x) = P(0) + P(1) + ... + P(x-1)
    prob_less_than_x = 0
    for i in range(0, x):
        prob = calculate_combinations(n, i) * (p ** i) * ((1 - p) ** (n - i))
        prob_less_than_x += prob
    
    # P(X >= x) = 1 - P(X < x)
    return 1 - prob_less_than_x

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
    1. retail - Retail Individual Investor
    2. shni  - Small HNI
    3. bhni  - Big HNI
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
                
                for category, count in category_counts.items():
                    effective_subscription = subscription_ratios[category]
                    if category == 'bhni':
                        effective_subscription = subscription_ratios[category] / 5
                        st.write(f"\n{category.upper()} (Adjusted subscription ratio: {effective_subscription:.2f}x)")
                    else:
                        st.write(f"\n{category.upper()} (Subscription ratio: {effective_subscription:.2f}x)")
                    
                    p = 1 / effective_subscription
                    
                    for i in range(1, count + 1):
                        prob = calculate_probability(count, i, p) * 100
                        st.write(f"Probability of getting at least {i} lot(s): {prob:.2f}%")
                    
                    st.markdown("---")
                    
    except ValueError as e:
        st.error(f"Error: {e}")
        st.warning("Please try again using format like '2 retail bhni 3 shni'")
    except Exception as e:
        st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
