from pathlib import Path

import numpy as np
import pandas as pd


RANDOM_SEED = 42
N_ROWS = 10_000


def fraud_probability(score: int) -> float:
    """
    Return fraud probability based on identity risk score.

    Uses a logistic curve so fraud is low at low scores
    and increases more sharply at higher scores.
    """
    return 1 / (1 + np.exp(-(score - 600) / 100))


def build_applications(n_rows: int) -> pd.DataFrame:
    """
    Create synthetic application-level data.
    """
    return pd.DataFrame(
        {
            "application_id": range(1, n_rows + 1),
            "application_date": pd.date_range(
                start="2023-01-01",
                periods=n_rows,
                freq="h",
            ),
            "identity_risk_score": np.random.randint(0, 1000, n_rows),
        }
    )


def build_outcomes(applications: pd.DataFrame) -> pd.DataFrame:
    """
    Create synthetic outcomes tied to the application data.
    Higher scores are more likely to be fraud.
    """
    outcomes = applications[["application_id", "identity_risk_score"]].copy()

    outcomes["fraud"] = outcomes["identity_risk_score"].apply(
        lambda score: np.random.binomial(1, fraud_probability(score))
    )

    outcomes["account_status"] = np.where(
        outcomes["fraud"] == 1,
        "prevented",
        np.random.choice(["open", "closed"], size=len(outcomes), p=[0.7, 0.3]),
    )

    outcomes["charged_off"] = np.where(
        (outcomes["fraud"] == 1) & (np.random.rand(len(outcomes)) > 0.5),
        "yes",
        "no",
    )

    outcomes = outcomes.drop(columns=["identity_risk_score"])
    return outcomes


def save_data(applications: pd.DataFrame, outcomes: pd.DataFrame) -> None:
    """
    Save generated datasets into data/raw/.
    """
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    applications_path = output_dir / "applications.csv"
    outcomes_path = output_dir / "outcomes.csv"

    applications.to_csv(applications_path, index=False)
    outcomes.to_csv(outcomes_path, index=False)

    print(f"Saved applications to: {applications_path}")
    print(f"Saved outcomes to: {outcomes_path}")


def main() -> None:
    np.random.seed(RANDOM_SEED)

    applications = build_applications(N_ROWS)
    outcomes = build_outcomes(applications)

    print("Applications preview:")
    print(applications.head(), end="\n\n")

    print("Outcomes preview:")
    print(outcomes.head(), end="\n\n")

    print(f"Applications shape: {applications.shape}")
    print(f"Outcomes shape: {outcomes.shape}", end="\n\n")

    print("Fraud rate:")
    print(outcomes["fraud"].mean())

    save_data(applications, outcomes)


if __name__ == "__main__":
    main()