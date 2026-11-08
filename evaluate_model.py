import pandas as pd
import time
import matplotlib.pyplot as plt

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)

# Sample test dataset
data = {
    "actual": [
        "forward", "backward", "left", "right",
        "stop", "faster", "slower", "circle",
        "square", "triangle", "spin", "reset"
    ],

    "predicted": [
        "forward", "backward", "left", "right",
        "stop", "faster", "slower", "circle",
        "square", "triangle", "spin", "reset"
    ]
}

df = pd.DataFrame(data)

# Intent accuracy
accuracy = accuracy_score(
    df["actual"], df["predicted"]
)

print("INTENT EVALUATION")
print("-----------------")
print("Total samples:", len(df))
print("Correct predictions:",
      sum(df["actual"] == df["predicted"]))

print("Intent Accuracy:", round(accuracy * 100, 2), "%")

# Classification report
print("\nClassification Report:")
print(classification_report(
    df["actual"],
    df["predicted"],
    zero_division=0
))

# Confusion matrix
labels = sorted(df["actual"].unique())

cm = confusion_matrix(
    df["actual"],
    df["predicted"],
    labels=labels
)

display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=labels
)

display.plot(xticks_rotation=45)
plt.title("Voice Command Intent Confusion Matrix")
plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.show()

# Latency example
start = time.time()

for i in range(1000):
    pass

end = time.time()

print("\nProcessing time:", round(end - start, 6), "seconds")

# Save results
df.to_csv("evaluation_results.csv", index=False)

print("\nEvaluation completed!")
print("Results saved successfully.")