import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def generate_funnel_dataset(num_users=10000, filepath="data/raw/user_signup_funnel.csv"):
    """
    Generates synthetic user signup funnel dataset matching the assignment problem statement:
    - Stage 1: Sign Up (10,000)
    - Stage 2: Email Entered (8,000)  -> 2,000 drop (20% loss)
    - Stage 3: Password Created (6,000) -> 2,000 drop (25% loss)
    - Stage 4: Email Verified (5,000)  -> 1,000 drop (16.7% loss)
    - Stage 5: Payment Added (4,000)   -> 1,000 drop (20% loss)
    - Stage 6: First Purchase (2,000)  -> 2,000 drop (50% loss - CRITICAL BOTTLENECK)
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not os.path.exists(filepath):
        print(f"Generating synthetic funnel dataset ({num_users:,} users)...")
        user_ids = [f"USER_{i:06d}" for i in range(1, num_users + 1)]

        # Sequential binary conversion flags
        s1 = np.ones(num_users, dtype=int)
        s2 = np.array([1 if i < 8000 else 0 for i in range(num_users)])
        s3 = np.array([1 if i < 6000 else 0 for i in range(num_users)])
        s4 = np.array([1 if i < 5000 else 0 for i in range(num_users)])
        s5 = np.array([1 if i < 4000 else 0 for i in range(num_users)])
        s6 = np.array([1 if i < 2000 else 0 for i in range(num_users)])

        df_raw = pd.DataFrame({
            "user_id": user_ids,
            "signup_completed": s1,
            "email_entered": s2,
            "password_created": s3,
            "email_verified": s4,
            "payment_added": s5,
            "first_purchase": s6
        })
        df_raw.to_csv(filepath, index=False)
        print(f"Funnel dataset created successfully at {filepath}.")
    else:
        print(f"Loading existing funnel dataset from {filepath}...")
        df_raw = pd.read_csv(filepath)

    return df_raw


def task1_define_funnel_stages(df):
    """
    Task 1: Define Funnel Stages and Count Users at Each Step.
    """
    print("\n--- Task 1: Define Funnel Stages and User Volume ---")
    stage1_signup = len(df[df['signup_completed'] == 1])
    stage2_email = len(df[df['email_entered'] == 1])
    stage3_password = len(df[df['password_created'] == 1])
    stage4_verified = len(df[df['email_verified'] == 1])
    stage5_payment = len(df[df['payment_added'] == 1])
    stage6_purchase = len(df[df['first_purchase'] == 1])

    stages = {
        'Sign Up': stage1_signup,
        'Email Entered': stage2_email,
        'Password Created': stage3_password,
        'Email Verified': stage4_verified,
        'Payment Added': stage5_payment,
        'First Purchase': stage6_purchase
    }

    for stage_name, count in stages.items():
        print(f"  - {stage_name:<18}: {count:,} users")

    return stages


def task2_compute_drop_off_rates(stages):
    """
    Task 2: Compute Drop-Off Rate, Completion Rate, and Users Lost between consecutive stages.
    """
    print("\n--- Task 2: Compute Drop-Off Rates & Identify Leaks ---")
    stage_list = list(stages.values())
    stage_names = list(stages.keys())
    drop_off = []

    for i in range(len(stage_list) - 1):
        users_before = stage_list[i]
        users_after = stage_list[i + 1]
        users_lost = users_before - users_after
        drop_pct = (users_lost / users_before) * 100
        comp_pct = (users_after / users_before) * 100

        drop_off.append({
            'from_stage': stage_names[i],
            'to_stage': stage_names[i + 1],
            'users_before': users_before,
            'users_after': users_after,
            'users_lost': users_lost,
            'completion_rate': f"{comp_pct:.1f}%",
            'drop_rate': f"{drop_pct:.1f}%"
        })

    funnel_df = pd.DataFrame(drop_off)
    print(funnel_df[['from_stage', 'to_stage', 'users_lost', 'completion_rate', 'drop_rate']])

    # Find primary bottleneck by highest drop percentage (and highest user loss)
    funnel_df['drop_pct_num'] = (funnel_df['users_lost'] / funnel_df['users_before']) * 100
    biggest_drop_idx = funnel_df['drop_pct_num'].idxmax()
    biggest_drop = funnel_df.loc[biggest_drop_idx]

    print(f"\n[CRITICAL BOTTLENECK]: Highest Drop-Off Point (Percentage & Volume)")
    print(f"  - Stage Point : {biggest_drop['from_stage']} -> {biggest_drop['to_stage']}")
    print(f"  - Users Lost  : {biggest_drop['users_lost']:,}")
    print(f"  - Drop Rate   : {biggest_drop['drop_rate']}")

    return funnel_df, biggest_drop


def task3_visualize_funnel(stages):
    """
    Task 3: Render and export color-coded Funnel Bar Chart visualization.
    """
    print("\n--- Task 3: Visualize Funnel Bar Chart ---")
    os.makedirs("output", exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']
    
    bars = ax.bar(stages.keys(), stages.values(), color=colors, edgecolor='black', linewidth=0.8)
    ax.set_ylabel('Users Volume', fontsize=12, fontweight='bold')
    ax.set_xlabel('Funnel Stage', fontsize=12, fontweight='bold')
    ax.set_title('User Conversion Funnel: Volume by Sequential Stage', fontsize=14, fontweight='bold')
    ax.set_ylim(0, max(stages.values()) * 1.15)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    # Annotate exact count values above each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 150,
            f"{int(height):,}",
            ha='center',
            va='bottom',
            fontweight='bold',
            fontsize=10
        )

    plt.xticks(rotation=30, ha='right', fontsize=10)
    plt.tight_layout()

    plot_path = "output/funnel_chart.png"
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"Saved funnel chart visualization to: {plot_path}")


def task4_calculate_business_impact(funnel_df, revenue_per_customer=100):
    """
    Task 4: Calculate Revenue Impact of Each Drop-Off and Rank Bottlenecks.
    """
    print("\n--- Task 4: Revenue Impact & Bottleneck Priority Ranking ---")
    impact_analysis = []

    for idx, row in funnel_df.iterrows():
        users_lost = row['users_lost']
        revenue_lost = users_lost * revenue_per_customer
        impact_analysis.append({
            'drop_point': f"{row['from_stage']} -> {row['to_stage']}",
            'users_lost': users_lost,
            'revenue_lost_raw': revenue_lost,
            'revenue_impact': f"${revenue_lost:,.0f}",
            'priority': 'HIGH' if revenue_lost >= 100000 else 'MEDIUM'
        })

    impact_df = pd.DataFrame(impact_analysis)
    ranked_impact = impact_df.sort_values('revenue_lost_raw', ascending=False)
    print(ranked_impact[['drop_point', 'users_lost', 'revenue_impact', 'priority']])
    return ranked_impact


def task5_actionable_recommendations(funnel_df, revenue_per_customer=100):
    """
    Task 5: Formulate Actionable Recommendations & Project Financial Value of 10% Fix.
    """
    print("\n--- Task 5: Actionable Recommendation & Expected Impact ---")
    highest_impact_idx = funnel_df['drop_pct_num'].idxmax()
    highest_impact = funnel_df.loc[highest_impact_idx]
    revenue_lost_val = highest_impact['users_lost'] * revenue_per_customer
    recoverable_users = int(highest_impact['users_lost'] * 0.1)
    recoverable_revenue = recoverable_users * revenue_per_customer

    recommendation_text = f"""============================================================
FUNNEL OPTIMIZATION & DROP-OFF ANALYSIS REPORT
============================================================

1. CRITICAL BOTTLENECK IDENTIFIED:
   - Primary Leak Point : {highest_impact['from_stage']} -> {highest_impact['to_stage']}
   - Users Lost         : {highest_impact['users_lost']:,} Users
   - Stage Drop Rate    : {highest_impact['drop_rate']}
   - Financial Impact   : ${revenue_lost_val:,.0f} Lost Potential Revenue

2. ROOT CAUSE INVESTIGATION HYPOTHESES:
   - Poor UX / Checkout Friction : First purchase checkout page has unclear CTA buttons or missing trust/security badges.
   - Excessive Form Complexity   : User is required to enter unnecessary billing fields before seeing final pricing.
   - Price Sensitivity          : Absence of first-time buyer incentives, trial offers, or introductory discounts.
   - Value Timing Mismatch       : Payment setup occurs before the user has experienced the product's core value.

3. RECOMMENDED ACTION PLAN:
   - Step 1: Execute A/B testing comparing a 1-click simplified checkout flow against the current multi-step payment page.
   - Step 2: Introduce a 14-day free trial or intro discount code on the first purchase page.
   - Step 3: Monitor daily drop-off rates post-deployment using product analytics event tracking.
   - Step 4: Roll out winning variant to 100% of user traffic if conversion improvement exceeds 5%.

4. EXPECTED FINANCIAL IMPACT (10% Conversion Improvement):
   - Additional Converted Users  : {recoverable_users:,} Users
   - Additional Recovered Revenue: ${recoverable_revenue:,.0f}
============================================================
"""
    print(recommendation_text)

    os.makedirs("output", exist_ok=True)
    report_path = "output/funnel_analysis.txt"
    with open(report_path, "w") as f:
        f.write(recommendation_text)
    print(f"Saved funnel analysis report to: {report_path}")

    return recommendation_text


def main():
    print("=" * 60)
    print("  Funnel Analysis & Drop-Off Detection Workflow")
    print("=" * 60)

    os.makedirs("output", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)

    df = generate_funnel_dataset()
    stages = task1_define_funnel_stages(df)
    funnel_df, biggest_drop = task2_compute_drop_off_rates(stages)
    task3_visualize_funnel(stages)
    ranked_impact = task4_calculate_business_impact(funnel_df)
    task5_actionable_recommendations(funnel_df)

    funnel_df.to_csv("data/processed/funnel_dropoff_metrics.csv", index=False)
    print("\n[SUCCESS] Funnel Analysis & Drop-Off Detection Workflow Completed Successfully!")


if __name__ == "__main__":
    main()
